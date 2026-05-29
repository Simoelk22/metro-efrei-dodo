import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.graphe import charger_metro
from src.connexite import est_connexe
from src.plus_court_chemin import dijkstra
from src.acpm import prim, kruskal

try:
    from codecarbon import EmissionsTracker
    CODECARBON_OK = True
except ImportError:
    CODECARBON_OK = False


def mesurer_algo(nom, fn, *args):
    """Mesure le temps + emissions CO2 d'une fonction."""
    tracker = None
    if CODECARBON_OK:
        tracker = EmissionsTracker(project_name=nom, log_level="error", save_to_file=False)
        tracker.start()

    t0 = time.perf_counter()
    resultat = fn(*args)
    duree_ms = (time.perf_counter() - t0) * 1000

    emissions_ug = None
    if tracker:
        emissions_kg = tracker.stop()
        emissions_ug = emissions_kg * 1e9  # en microgrammes

    return resultat, duree_ms, emissions_ug


def rapport_complet(g):
    depart = g.sommets[0]
    arrivee = g.sommets[-1]

    print("=" * 55)
    print("  BENCHMARK METRO EFREI DODO")
    print("=" * 55)

    algos = [
        ("BFS connexite",      est_connexe,  (g,)),
        ("Dijkstra maison",    dijkstra,     (g, depart, arrivee)),
        ("Prim (ACPM)",        prim,         (g,)),
        ("Kruskal (ACPM)",     kruskal,      (g,)),
    ]

    try:
        import networkx as nx
        G_nx = nx.Graph()
        for u in g.adjacence:
            for v, t in g.adjacence[u]:
                G_nx.add_edge(u, v, weight=t)
        algos.append(("Dijkstra networkx", nx.dijkstra_path_length, (G_nx, depart, arrivee), {"weight": "weight"}))
    except ImportError:
        pass

    for item in algos:
        nom = item[0]
        fn = item[1]
        args = item[2]
        kwargs = item[3] if len(item) > 3 else {}

        tracker = None
        if CODECARBON_OK:
            tracker = EmissionsTracker(project_name=nom, log_level="error", save_to_file=False)
            tracker.start()

        t0 = time.perf_counter()
        fn(*args, **kwargs)
        duree_ms = (time.perf_counter() - t0) * 1000

        emissions_str = ""
        if tracker:
            emissions_kg = tracker.stop()
            emissions_str = f"  |  CO2eq : {emissions_kg*1e9:.4f} ug"

        print(f"  {nom:<22} {duree_ms:7.3f} ms{emissions_str}")

    print("=" * 55)


if __name__ == "__main__":
    g = charger_metro()
    rapport_complet(g)
