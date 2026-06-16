"""
Récupère les photos des stations de métro via l'API Wikipedia (FR).

Usage :
    from src.wikipedia_photos import get_photo_url
    url = get_photo_url("Abbesses")   # → str | None

Les résultats sont mis en cache en mémoire pour éviter les requêtes répétées.
"""

import json
import re
import urllib.parse
import urllib.request


# ── Cache mémoire (persist pendant toute la session Python) ──────────────────
_cache: dict[str, str | None] = {}


def get_photo_url(nom_station: str, largeur: int = 280) -> str | None:
    """
    Retourne l'URL du thumbnail Wikipedia pour une station de métro.

    Stratégie de recherche (dans l'ordre) :
    1. "Nom (métro de Paris)"  — ex: "Abbesses (métro de Paris)"
    2. "Nom" seul              — ex: "Abbesses"

    Retourne None si aucune image n'est trouvée ou en cas d'erreur réseau.
    """
    if nom_station in _cache:
        return _cache[nom_station]

    # Titres candidats à essayer
    candidats = [f"{nom_station} (métro de Paris)", nom_station]

    for titre in candidats:
        slug = urllib.parse.quote(titre.replace(" ", "_"))
        url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{slug}"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "MetroEfreiDodo/1.0 (efrei-project)"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            if "thumbnail" in data:
                src = data["thumbnail"]["source"]
                # Adapte la résolution du thumbnail à la largeur souhaitée
                src = re.sub(r"/\d+px-", f"/{largeur}px-", src)
                _cache[nom_station] = src
                return src

        except Exception:
            continue  # essaie le prochain candidat

    _cache[nom_station] = None
    return None


def get_photos_batch(noms: list[str], max_photos: int = 9) -> dict[str, str]:
    """
    Récupère les photos d'une liste de stations en limitant le nombre de requêtes.

    Priorise le départ, l'arrivée, et des stations intermédiaires régulièrement espacées.
    Retourne {nom_station: url} pour les stations où une photo a été trouvée.
    """
    if not noms:
        return {}

    # Sélectionne les stations les plus représentatives
    if len(noms) <= max_photos:
        a_afficher = noms
    else:
        # Départ + arrivée + stations intermédiaires espacées
        step = max(1, len(noms) // (max_photos - 2))
        intermediaires = noms[1:-1:step][: max_photos - 2]
        a_afficher = [noms[0]] + intermediaires + [noms[-1]]
        # Déduplique en gardant l'ordre
        seen: set[str] = set()
        a_afficher = [n for n in a_afficher if not (n in seen or seen.add(n))]

    photos: dict[str, str] = {}
    for nom in a_afficher:
        url = get_photo_url(nom)
        if url:
            photos[nom] = url

    return photos
