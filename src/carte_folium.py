"""
Carte géographique interactive du réseau de métro parisien via Folium.

Dépend de :
  - data/stations_geo.json  (généré par scripts/build_stations_geo.py)
  - folium                  (pip install folium streamlit-folium)

Usage :
    geo = charger_geo("data/stations_geo.json")
    carte = construire_carte_reseau(graphe, geo, chemin=[...], photos={...})
    st_folium(carte, width="100%", height=550)
"""

import json
import os

import folium

# ── Import optionnel du plugin AntPath (animation de trajet) ─────────────────
try:
    from folium.plugins import AntPath
    _ANTPATH_OK = True
except ImportError:
    _ANTPATH_OK = False

# ── Couleurs officielles des lignes RATP ──────────────────────────────────────
COULEURS_LIGNES: dict[str, str] = {
    "1":  "#FFCD00",  # Jaune
    "2":  "#003CA6",  # Bleu
    "3":  "#837902",  # Olive
    "3b": "#6EC4E8",  # Bleu clair
    "4":  "#CF009E",  # Rose / Fuchsia
    "5":  "#FF7E2E",  # Orange
    "6":  "#6ECA97",  # Vert clair
    "7":  "#FA9ABA",  # Rose clair
    "7b": "#6ECA97",  # Vert clair (même que 6)
    "8":  "#E19BDF",  # Lilas
    "9":  "#B6BD00",  # Jaune-vert
    "10": "#C9910D",  # Ocre
    "11": "#704B1C",  # Marron
    "12": "#007852",  # Vert foncé
    "13": "#6EC4E8",  # Bleu clair (même que 3b)
    "14": "#62259D",  # Violet
}


# ── Fonctions publiques ───────────────────────────────────────────────────────

def charger_geo(chemin: str = "data/stations_geo.json") -> dict:
    """
    Charge les coordonnées géographiques des stations depuis le fichier JSON.

    Format du fichier : {num_sommet_str: {lat, lng, nom, ligne}}

    Raises FileNotFoundError si le fichier est absent (lancer build_stations_geo.py).
    """
    if not os.path.exists(chemin):
        raise FileNotFoundError(
            f"Fichier '{chemin}' introuvable. "
            "Lancez d'abord : python scripts/build_stations_geo.py"
        )
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def construire_carte_reseau(
    graphe,
    geo: dict,
    chemin: list | None = None,
    photos: dict | None = None,
) -> folium.Map:
    """
    Construit une carte Folium interactive du réseau de métro parisien.

    Args:
        graphe  : instance de Graphe (src.graphe)
        geo     : dict issu de charger_geo() — {num_str: {lat, lng, nom, ligne}}
        chemin  : liste de num_sommets du trajet calculé (optionnel)
        photos  : dict {nom_station: url_image} pour enrichir les popups (optionnel)

    Returns:
        folium.Map configuré, prêt à être rendu par st_folium()

    Fonctionnalités :
        - Fond CartoDB Dark Matter (rendu pro)
        - Arêtes colorées par ligne RATP
        - Marqueurs de stations cliquables (popup + tooltip)
        - Trajet en rouge animé via AntPath (ou PolyLine en fallback)
        - Photos Wikipedia dans les popups des stations du trajet
        - Auto-zoom sur le trajet si fourni
    """
    # ── Initialisation de la carte ────────────────────────────────────────────
    carte = folium.Map(
        location=[48.858, 2.347],
        zoom_start=12,
        tiles="CartoDB dark_matter",
    )

    # Ensemble des numéros de sommets sur le trajet (pour personnaliser l'affichage)
    chemin_nums: set[int] = set(chemin) if chemin else set()

    # ── Arêtes du réseau (colorées par ligne) ─────────────────────────────────
    for u in graphe.adjacence:
        for v, _ in graphe.adjacence[u]:
            if u >= v:
                continue  # évite d'afficher chaque arête deux fois
            u_str, v_str = str(u), str(v)
            if u_str not in geo or v_str not in geo:
                continue

            color = COULEURS_LIGNES.get(graphe.lignes[u], "#888888")
            folium.PolyLine(
                locations=[
                    [geo[u_str]["lat"], geo[u_str]["lng"]],
                    [geo[v_str]["lat"], geo[v_str]["lng"]],
                ],
                color=color,
                weight=2,
                opacity=0.5,
            ).add_to(carte)

    # ── Marqueurs des stations ────────────────────────────────────────────────
    for num in graphe.sommets:
        num_str = str(num)
        if num_str not in geo:
            continue

        g_data = geo[num_str]
        nom = graphe.noms[num]
        ligne = graphe.lignes[num]
        color = COULEURS_LIGNES.get(ligne, "#888888")
        sur_chemin = num in chemin_nums

        # Photo Wikipedia dans le popup (uniquement pour les stations du trajet)
        photo_html = ""
        if sur_chemin and photos and photos.get(nom):
            photo_html = (
                f'<img src="{photos[nom]}" width="200" '
                f'style="border-radius:6px;margin-bottom:6px;display:block;">'
            )

        popup_html = (
            '<div style="font-family:Arial,sans-serif;min-width:160px;">'
            f"{photo_html}"
            f'<b style="font-size:13px">{nom}</b><br>'
            f'<span style="color:{color};font-weight:bold;">● Ligne {ligne}</span>'
            "</div>"
        )

        folium.CircleMarker(
            location=[g_data["lat"], g_data["lng"]],
            radius=7 if sur_chemin else 4,            # stations du trajet plus visibles
            color="#ffffff" if sur_chemin else color,  # contour blanc sur le trajet
            weight=2 if sur_chemin else 1,
            fill=True,
            fill_color=color,
            fill_opacity=0.95 if sur_chemin else 0.80,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{'→ ' if sur_chemin else ''}{nom} · Ligne {ligne}",
        ).add_to(carte)

    # ── Trajet calculé (animation + marqueurs départ/arrivée) ─────────────────
    if chemin and len(chemin) > 1:
        coords = [
            [geo[str(s)]["lat"], geo[str(s)]["lng"]]
            for s in chemin
            if str(s) in geo
        ]

        if len(coords) >= 2:
            # Ligne animée AntPath ou PolyLine classique en fallback
            if _ANTPATH_OK:
                AntPath(
                    locations=coords,
                    color="#FF4444",
                    weight=6,
                    opacity=0.9,
                    delay=600,          # vitesse de l'animation (ms)
                    dash_array=[10, 20],
                    pulse_color="#FFAAAA",
                ).add_to(carte)
            else:
                folium.PolyLine(
                    locations=coords,
                    color="#FF4444",
                    weight=6,
                    opacity=0.9,
                ).add_to(carte)

            # Marqueur départ (vert)
            folium.Marker(
                location=coords[0],
                popup=folium.Popup(
                    f"<b>Départ :</b> {graphe.noms[chemin[0]]}", max_width=180
                ),
                tooltip=f"Départ : {graphe.noms[chemin[0]]}",
                icon=folium.Icon(color="green", icon="play", prefix="fa"),
            ).add_to(carte)

            # Marqueur arrivée (rouge)
            folium.Marker(
                location=coords[-1],
                popup=folium.Popup(
                    f"<b>Arrivée :</b> {graphe.noms[chemin[-1]]}", max_width=180
                ),
                tooltip=f"Arrivée : {graphe.noms[chemin[-1]]}",
                icon=folium.Icon(color="red", icon="flag", prefix="fa"),
            ).add_to(carte)

            # Auto-zoom : cadre la vue sur le trajet complet
            carte.fit_bounds(
                [
                    [min(c[0] for c in coords), min(c[1] for c in coords)],
                    [max(c[0] for c in coords), max(c[1] for c in coords)],
                ],
                padding=[40, 40],
            )

    return carte
