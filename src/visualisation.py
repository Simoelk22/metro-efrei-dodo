"""
Fonctions de visualisation Plotly du réseau de métro.

Deux fonctions principales :
  - tracer_reseau()   : carte schématique du réseau (+ chemin + ACPM)
  - tracer_heatmap()  : carte de chaleur par degré de connexion

Le fond des deux cartes affiche le plan officiel du métro parisien
si le fichier assets/metro_map_bg.png est présent.
"""

import base64
import os

import plotly.graph_objects as go


# ── Couleurs officielles des lignes RATP ──────────────────────────────────────
COULEURS_LIGNES = {
    "1":  "#FFCD00", "2":  "#003CA6", "3":  "#837902", "3b": "#6EC4E8",
    "4":  "#CF009E", "5":  "#FF7E2E", "6":  "#6ECA97", "7":  "#FA9ABA",
    "7b": "#6ECA97", "8":  "#E19BDF", "9":  "#B6BD00", "10": "#C9910D",
    "11": "#704B1C", "12": "#007852", "13": "#6EC4E8", "14": "#62259D",
}

# Cache de l'image de fond (chargée une seule fois)
_METRO_MAP_B64: str | None = None


def _charger_metro_map() -> str | None:
    """
    Charge assets/metro_map_bg.png en base64 (mis en cache).
    Retourne None si le fichier est absent.
    """
    global _METRO_MAP_B64
    if _METRO_MAP_B64 is not None:
        return _METRO_MAP_B64
    chemin = "assets/metro_map_bg.png"
    if not os.path.exists(chemin):
        _METRO_MAP_B64 = ""  # marque comme "introuvable" pour ne pas retester
        return None
    with open(chemin, "rb") as f:
        _METRO_MAP_B64 = base64.b64encode(f.read()).decode()
    return _METRO_MAP_B64


def _ajouter_fond_metro(fig: go.Figure, x_min: float, x_max: float,
                         y_min: float, y_max: float, opacite: float = 0.18) -> None:
    """
    Superpose le plan de métro en fond du graphique Plotly.
    Le plan est étiré pour couvrir toute la zone de données.
    """
    b64 = _charger_metro_map()
    if not b64:
        return
    fig.add_layout_image(
        dict(
            source=f"data:image/png;base64,{b64}",
            xref="x",
            yref="y",
            x=x_min,
            y=y_max,
            sizex=x_max - x_min,
            sizey=y_max - y_min,
            sizing="stretch",
            opacity=opacite,
            layer="below",
        )
    )


def _positions_par_num(graphe, positions_noms: dict) -> dict:
    """
    Construit {num_sommet: (x, y)} depuis {nom_station: (x, y)}.
    Matching exact puis partiel (startswith 6 premiers caractères).
    """
    pos = {}
    noms_pos = {k.lower(): v for k, v in positions_noms.items()}

    for num, nom in graphe.noms.items():
        cle = nom.lower()
        if cle in noms_pos:
            pos[num] = noms_pos[cle]
        else:
            for k, v in noms_pos.items():
                if k.startswith(cle[:6]) or cle.startswith(k[:6]):
                    pos[num] = v
                    break

    return pos


def tracer_reseau(graphe, positions_noms: dict,
                  chemin: list | None = None,
                  acpm_aretes: list | None = None) -> go.Figure:
    """
    Retourne une figure Plotly du réseau de métro schématique.

    Args:
        graphe         : instance de Graphe (src.graphe)
        positions_noms : dict {nom_station: (x, y)} depuis charger_positions()
        chemin         : liste de num_sommets du plus court chemin (rouge)
        acpm_aretes    : liste de (u, v, poids) de l'ACPM (vert)

    Le fond affiche le plan officiel du métro parisien (opacité 18%).
    """
    pos = _positions_par_num(graphe, positions_noms)

    fig = go.Figure()

    # ── Calcul des bornes pour le fond de carte ───────────────────────────────
    if pos:
        xs = [v[0] for v in pos.values()]
        ys = [-v[1] for v in pos.values()]
        x_min, x_max = min(xs) - 20, max(xs) + 20
        y_min, y_max = min(ys) - 20, max(ys) + 20
        _ajouter_fond_metro(fig, x_min, x_max, y_min, y_max, opacite=0.45)

    # ── Arêtes du réseau (gris bleuté discret) ────────────────────────────────
    for u in graphe.adjacence:
        for v, _ in graphe.adjacence[u]:
            if u < v and u in pos and v in pos:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                fig.add_trace(go.Scatter(
                    x=[x0, x1, None],
                    y=[-y0, -y1, None],
                    mode="lines",
                    line=dict(color="rgba(120,134,170,0.45)", width=1),
                    hoverinfo="none",
                    showlegend=False,
                ))

    # ── ACPM (vert vif) ───────────────────────────────────────────────────────
    if acpm_aretes:
        for u, v, _ in acpm_aretes:
            if u in pos and v in pos:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                fig.add_trace(go.Scatter(
                    x=[x0, x1, None],
                    y=[-y0, -y1, None],
                    mode="lines",
                    line=dict(color="#00e676", width=3),
                    hoverinfo="none",
                    showlegend=False,
                ))

    # ── Plus court chemin (rouge RATP) ────────────────────────────────────────
    if chemin and len(chemin) > 1:
        cx = [pos[s][0] for s in chemin if s in pos]
        cy = [-pos[s][1] for s in chemin if s in pos]
        fig.add_trace(go.Scatter(
            x=cx,
            y=cy,
            mode="lines+markers",
            line=dict(color="#e4002b", width=4),
            marker=dict(size=9, color="#e4002b",
                        line=dict(width=1.5, color="#ffffff")),
            hoverinfo="none",
            showlegend=False,
        ))

    # ── Sommets (colorés par ligne) ───────────────────────────────────────────
    sx, sy, textes, couleurs = [], [], [], []
    for num in graphe.sommets:
        if num in pos:
            x, y = pos[num]
            sx.append(x)
            sy.append(-y)
            textes.append(graphe.noms[num])
            couleurs.append(COULEURS_LIGNES.get(graphe.lignes[num], "#888888"))

    fig.add_trace(go.Scatter(
        x=sx,
        y=sy,
        mode="markers",
        marker=dict(
            size=7,
            color=couleurs,
            line=dict(width=0.8, color="rgba(10,31,68,0.35)"),
        ),
        text=textes,
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   scaleanchor="x"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
    )

    return fig


def tracer_heatmap(graphe, positions_noms: dict) -> tuple[go.Figure, dict]:
    """
    Retourne une figure Plotly heatmap des stations + le dict de degrés.

    La taille et la couleur des marqueurs sont proportionnelles au degré
    (nombre de liaisons directes) de chaque station.
    Le fond affiche le plan officiel du métro parisien (opacité 15%).

    Returns:
        (figure, {num_sommet: degre})
    """
    pos = _positions_par_num(graphe, positions_noms)

    degres = {num: len(graphe.adjacence[num]) for num in graphe.sommets}
    max_degre = max(degres.values()) if degres else 1

    sx, sy, textes, tailles, couleurs, infos = [], [], [], [], [], []
    for num in graphe.sommets:
        if num not in pos:
            continue
        x, y = pos[num]
        d = degres[num]
        sx.append(x)
        sy.append(-y)
        textes.append(graphe.noms[num])
        tailles.append(6 + d * 4)
        couleurs.append(d)
        infos.append(
            f"{graphe.noms[num]}<br>Ligne {graphe.lignes[num]}<br>{d} connexion(s)"
        )

    fig = go.Figure()

    # ── Fond de carte : plan du métro ─────────────────────────────────────────
    if pos:
        xs = [v[0] for v in pos.values()]
        ys = [-v[1] for v in pos.values()]
        x_min, x_max = min(xs) - 20, max(xs) + 20
        y_min, y_max = min(ys) - 20, max(ys) + 20
        _ajouter_fond_metro(fig, x_min, x_max, y_min, y_max, opacite=0.35)

    # ── Arêtes (très discrètes) ───────────────────────────────────────────────
    for u in graphe.adjacence:
        for v, _ in graphe.adjacence[u]:
            if u < v and u in pos and v in pos:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                fig.add_trace(go.Scatter(
                    x=[x0, x1, None],
                    y=[-y0, -y1, None],
                    mode="lines",
                    line=dict(color="rgba(120,134,170,0.28)", width=1),
                    hoverinfo="none",
                    showlegend=False,
                ))

    # ── Nœuds heatmap ─────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=sx,
        y=sy,
        mode="markers",
        marker=dict(
            size=tailles,
            color=couleurs,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(
                title=dict(text="Connexions", side="right"),
                tickfont=dict(size=11, color="#0a1f44"),
                outlinewidth=0,
            ),
            line=dict(width=0.8, color="rgba(255,255,255,0.85)"),
        ),
        text=infos,
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   scaleanchor="x"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
    )

    return fig, degres
