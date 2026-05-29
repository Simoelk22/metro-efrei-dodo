# Metro Efrei Dodo

Projet MasterCamp — Modélisation du réseau de métro parisien comme un graphe pondéré.

**Soutenance :** 18 juin 2026

## Fonctionnalités

| Feature | Algorithme | Status |
|---|---|---|
| Test de connexité | BFS | Done |
| Plus court chemin | Dijkstra (maison) | Done |
| Arbre couvrant minimal | Prim + Kruskal | Done |
| Mesure des performances | time + codecarbon | Done |
| Interface interactive | Streamlit + Plotly | Done |

## Lancer l'application

```bash
cd metro-efrei-dodo
streamlit run app.py
```

## Lancer les tests

```bash
python tests/test_algos.py
```

## Benchmark énergie

```bash
python src/energie.py
```

## Structure

```
metro-efrei-dodo/
├── data/
│   ├── metro.txt          # 376 stations, 473 arêtes (1998-2002)
│   ├── pospoints.txt      # coordonnées x,y de chaque station
│   └── metrof_r.png       # plan du réseau
├── src/
│   ├── graphe.py          # classe Graphe + parser
│   ├── connexite.py       # BFS + est_connexe()
│   ├── acpm.py            # Prim et Kruskal
│   ├── plus_court_chemin.py  # Dijkstra
│   ├── energie.py         # benchmark temps + CO2
│   └── visualisation.py   # graphiques Plotly
├── app.py                 # interface Streamlit
├── tests/
│   └── test_algos.py      # tests sur mini-graphe + validation networkx
├── rapport/
│   └── rapport.md
└── requirements.txt
```

## Résultats

- **Connexité :** réseau connexe (376 stations, 1 seule composante)
- **Dijkstra :** Abbesses → Nation = 20 min 26 s (19 stations, < 1 ms)
- **ACPM :** poids total = 20 362 s — Prim = Kruskal ✓

## Stack

Python 3 · Streamlit · Plotly · networkx · codecarbon
