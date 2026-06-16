#!/usr/bin/env python3
"""
Script one-shot : construit data/stations_geo.json
en récupérant les vraies coordonnées lat/lng depuis OpenStreetMap (Overpass API).

Usage :
    python scripts/build_stations_geo.py

Le fichier généré a la forme :
    {"0": {"lat": 48.88, "lng": 2.34, "nom": "Abbesses", "ligne": "12"}, ...}
La clé est le num_sommet (string) du graphe metro.txt.
"""
import json
import re
import sys
import os
import unicodedata

import requests

# Chemin vers la racine du projet
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.graphe import charger_metro  # noqa: E402

METRO_TXT = os.path.join(ROOT, "data", "metro.txt")
OUTPUT = os.path.join(ROOT, "data", "stations_geo.json")

# Boîte englobante Paris + petite couronne
LAT_MIN, LAT_MAX = 48.70, 48.97
LNG_MIN, LNG_MAX = 2.17, 2.58


# ── Normalisation ─────────────────────────────────────────────────────────────

def normaliser(nom: str) -> str:
    """Minuscules, sans accents, sans ponctuation, espaces normalisés."""
    nom = unicodedata.normalize("NFD", nom)
    nom = "".join(c for c in nom if unicodedata.category(c) != "Mn")
    nom = nom.lower()
    nom = re.sub(r"[-,''()–]", " ", nom)
    nom = re.sub(r"\s+", " ", nom)
    return nom.strip()


def normaliser_ligne(ligne_str: str) -> str:
    """'M3B' → '3b', 'M14' → '14', '1' → '1'."""
    s = ligne_str.strip().upper()
    if s.startswith("M"):
        s = s[1:]
    return s.lower()


# ── Téléchargement depuis Overpass ────────────────────────────────────────────

# ── Corrections manuelles ─────────────────────────────────────────────────────
# Stations dont le nom dans metro.txt (1998-2002) diffère du nom OSM actuel.
# Clé : num_sommet (int)  →  {lat, lng, nom, ligne}
CORRECTIONS = {
    24:  {"lat": 48.8298, "lng": 2.3764, "nom": "Bibliotheque Francois Mitterrand", "ligne": "14"},
    37:  {"lat": 48.8424, "lng": 2.2175, "nom": "Boulogne - Pont de Saint-Cloud", "ligne": "10"},
    55:  {"lat": 48.8738, "lng": 2.2950, "nom": "Charles de Gaulle - Etoile", "ligne": "1"},
    56:  {"lat": 48.8738, "lng": 2.2950, "nom": "Charles de Gaulle - Etoile", "ligne": "2"},
    57:  {"lat": 48.8738, "lng": 2.2950, "nom": "Charles de Gaulle - Etoile", "ligne": "6"},
    89:  {"lat": 48.7831, "lng": 2.4583, "nom": "Creteil-Prefecture", "ligne": "8"},
    91:  {"lat": 48.7880, "lng": 2.4613, "nom": "Creteil-l'Echat", "ligne": "8"},
    105: {"lat": 48.8496, "lng": 2.3881, "nom": "Faidherbe-Chaligny", "ligne": "8"},
    112: {"lat": 48.9069, "lng": 2.3079, "nom": "Gabriel Peri", "ligne": "13"},
    124: {"lat": 48.8808, "lng": 2.3553, "nom": "Gare du Nord", "ligne": "4"},
    125: {"lat": 48.8808, "lng": 2.3553, "nom": "Gare du Nord", "ligne": "5"},
    130: {"lat": 48.8925, "lng": 2.2361, "nom": "La Defense (Grande Arche)", "ligne": "1"},
    145: {"lat": 48.8472, "lng": 2.2803, "nom": "Javel - Andre Citroen", "ligne": "10"},
    175: {"lat": 48.8700, "lng": 2.3248, "nom": "Madeleine", "ligne": "12"},
    176: {"lat": 48.8700, "lng": 2.3248, "nom": "Madeleine", "ligne": "14"},
    177: {"lat": 48.8700, "lng": 2.3248, "nom": "Madeleine", "ligne": "8"},
    185: {"lat": 48.8069, "lng": 2.4491, "nom": "Maisons-Alfort - Les Juilliottes", "ligne": "8"},
    186: {"lat": 48.7965, "lng": 2.4435, "nom": "Maisons-Alfort - Stade", "ligne": "8"},
    237: {"lat": 48.8244, "lng": 2.4550, "nom": "Pierre Curie", "ligne": "7"},
    240: {"lat": 48.8402, "lng": 2.2756, "nom": "Balard", "ligne": "8"},
    252: {"lat": 48.8886, "lng": 2.2556, "nom": "Pont de Neuilly", "ligne": "1"},
    264: {"lat": 48.8836, "lng": 2.2953, "nom": "Porte de Champerret", "ligne": "3"},
    295: {"lat": 48.8491, "lng": 2.3901, "nom": "Reuilly - Diderot", "ligne": "1"},
    296: {"lat": 48.8491, "lng": 2.3901, "nom": "Reuilly - Diderot", "ligne": "8"},
    303: {"lat": 48.8710, "lng": 2.3481, "nom": "Grands Boulevards", "ligne": "8"},
    # 4 stations restantes (lignes terminales/variantes)
    68:  {"lat": 48.9460, "lng": 2.3394, "nom": "Saint-Denis - Universite", "ligne": "13"},
    172: {"lat": 48.7869, "lng": 2.3661, "nom": "Mairie d'Ivry", "ligne": "7"},
    199: {"lat": 48.7943, "lng": 2.3613, "nom": "Villejuif - Louis Aragon", "ligne": "7"},
    266: {"lat": 48.8534, "lng": 2.2340, "nom": "Porte de Saint-Cloud", "ligne": "9"},
    304: {"lat": 48.8708, "lng": 2.3494, "nom": "Grands Boulevards", "ligne": "9"},
    328: {"lat": 48.8467, "lng": 2.4339, "nom": "Saint-Mande", "ligne": "1"},
    331: {"lat": 48.8543, "lng": 2.3553, "nom": "Saint-Paul", "ligne": "1"},
    365: {"lat": 48.7992, "lng": 2.3664, "nom": "Villejuif - Paul Vaillant-Couturier", "ligne": "7"},
}


OVERPASS_QUERY = f"""
[out:json][timeout:40];
(
  node["station"="subway"](
    {LAT_MIN},{LNG_MIN},{LAT_MAX},{LNG_MAX}
  );
);
out body;
"""


def fetch_overpass() -> list[dict]:
    """Retourne [{nom, nom_norm, lat, lng, ligne}, ...] pour les stations métro Paris."""
    url = "https://overpass-api.de/api/interpreter"
    print("Téléchargement depuis Overpass API (OpenStreetMap)...")
    headers = {
        "User-Agent": "metro-efrei-dodo/1.0 (student project EFREI Paris)",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    r = requests.post(url, data={"data": OVERPASS_QUERY}, headers=headers, timeout=50)
    r.raise_for_status()
    data = r.json()

    stations = []
    seen: set[tuple] = set()

    for elem in data.get("elements", []):
        tags = elem.get("tags", {})
        nom = tags.get("name", "").strip()
        lat = elem.get("lat")
        lng = elem.get("lon")

        if not nom or lat is None or lng is None:
            continue

        # Filtre géographique
        if not (LAT_MIN <= lat <= LAT_MAX and LNG_MIN <= lng <= LNG_MAX):
            continue

        # Lignes desservies (tag "ref" peut contenir "1;2;3")
        ref = tags.get("ref", "")
        lignes = [l.strip() for l in ref.split(";") if l.strip()] if ref else [""]

        for ligne in lignes:
            ligne_norm = normaliser_ligne(ligne)
            key = (normaliser(nom), ligne_norm)
            if key not in seen:
                seen.add(key)
                stations.append({
                    "nom": nom,
                    "nom_norm": normaliser(nom),
                    "lat": lat,
                    "lng": lng,
                    "ligne": ligne_norm,
                })

    print(f"  -> {len(stations)} entrees recuperees (apres deduplication par ligne)")
    return stations


# ── Matching graphe ↔ Overpass ────────────────────────────────────────────────

def score_match(n1: str, n2: str) -> float:
    """Score de similarité [0,1] entre deux noms normalisés."""
    if n1 == n2:
        return 1.0
    min_len = min(len(n1), len(n2))
    if min_len == 0:
        return 0.0
    match_chars = sum(a == b for a, b in zip(n1, n2))
    return match_chars / max(len(n1), len(n2))


def matcher_stations(graphe, stations_ext: list[dict]) -> tuple[dict, list]:
    """
    Pour chaque sommet du graphe, cherche la meilleure correspondance.
    Retourne (geo_data, non_matches).
    """
    # Index : {(nom_norm, ligne_norm): [station, ...]}
    index: dict[tuple, list] = {}
    for s in stations_ext:
        key = (s["nom_norm"], s["ligne"])
        index.setdefault(key, []).append(s)

    # Index secondaire : {nom_norm: [station, ...]} (ignore la ligne)
    index_nom: dict[str, list] = {}
    for s in stations_ext:
        index_nom.setdefault(s["nom_norm"], []).append(s)

    result: dict[str, dict] = {}
    non_matches: list[tuple] = []

    for num in graphe.sommets:
        nom = graphe.noms[num]
        ligne = graphe.lignes[num]
        nom_norm = normaliser(nom)
        ligne_norm = normaliser_ligne(ligne)

        # 1) Correspondance exacte (nom + ligne)
        exact = index.get((nom_norm, ligne_norm))
        if exact:
            s = exact[0]
            result[str(num)] = {"lat": s["lat"], "lng": s["lng"], "nom": nom, "ligne": ligne}
            continue

        # 2) Correspondance partielle : même ligne, meilleur score de nom
        best, best_score = None, 0.0
        for s in stations_ext:
            if s["ligne"] != ligne_norm:
                continue
            sc = score_match(nom_norm, s["nom_norm"])
            # Bonus si l'un commence par les premiers mots de l'autre
            words_n = set(nom_norm.split())
            words_s = set(s["nom_norm"].split())
            overlap = len(words_n & words_s) / max(len(words_n | words_s), 1)
            sc = max(sc, overlap)
            if sc > best_score:
                best_score = sc
                best = s

        if best and best_score >= 0.65:
            result[str(num)] = {"lat": best["lat"], "lng": best["lng"], "nom": nom, "ligne": ligne}
            continue

        # 3) Correspondance par nom seul (toutes lignes) — dernier recours
        candidates = index_nom.get(nom_norm, [])
        if candidates:
            s = candidates[0]
            result[str(num)] = {"lat": s["lat"], "lng": s["lng"], "nom": nom, "ligne": ligne}
            continue

        non_matches.append((num, nom, ligne))

    return result, non_matches


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Construction de data/stations_geo.json")
    print("=" * 55)

    g = charger_metro(METRO_TXT)
    print(f"\nGraphe charge : {len(g.sommets)} sommets, {g.nb_aretes} aretes\n")

    try:
        stations_ext = fetch_overpass()
    except Exception as exc:
        print(f"ERREUR Overpass API : {exc}")
        sys.exit(1)

    print(f"\nMatching des {len(g.sommets)} sommets...")
    geo_data, non_matches = matcher_stations(g, stations_ext)

    # Application des corrections manuelles
    nb_corrections = 0
    for num, nom, ligne in list(non_matches):
        if num in CORRECTIONS:
            geo_data[str(num)] = CORRECTIONS[num]
            non_matches = [(n, no, l) for n, no, l in non_matches if n != num]
            nb_corrections += 1
    if nb_corrections:
        print(f"  +  {nb_corrections} corrections manuelles appliquees")

    print(f"  OK : {len(geo_data)} sommets geolocali-ses ({100 * len(geo_data) // len(g.sommets)} %)")
    print(f"  XX : {len(non_matches)} non matches")

    if non_matches:
        print("\nSommets sans correspondance :")
        for num, nom, ligne in non_matches[:25]:
            print(f"  [{num:4d}] {nom:<40} ligne {ligne}")
        if len(non_matches) > 25:
            print(f"  ... et {len(non_matches) - 25} autres")

    # Verification de coherence geographique
    lats = [d["lat"] for d in geo_data.values()]
    lngs = [d["lng"] for d in geo_data.values()]
    if lats:
        print(f"\nPlage lat : [{min(lats):.4f}, {max(lats):.4f}]  (attendu [48.70, 48.97])")
        print(f"Plage lng : [{min(lngs):.4f}, {max(lngs):.4f}]  (attendu [2.17, 2.58])")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(geo_data, f, ensure_ascii=False, indent=2)

    print(f"\nFichier ecrit : {OUTPUT}")
    print(f"  {len(geo_data)}/{len(g.sommets)} stations dans le JSON.\n")
