"""
Tests sur un mini-graphe dont on connait les reponses a la main.

    0 --10-- 1 --5-- 2
    |                |
    4(poids)         3(poids)
    |                |
    4 ------8------- 3

Sommets : 0, 1, 2, 3, 4
Plus court chemin 0->2 : distance = 15 (0->1->2 ou 0->4->3->2 = 4+8+3 = 15)
ACPM : aretes {4-0(4), 3-2(3), 2-1(5), 4-3(8)} -> poids = 20
Connexe : oui
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.graphe import Graphe
from src.connexite import est_connexe
from src.plus_court_chemin import dijkstra
from src.acpm import prim, kruskal


def creer_mini_graphe():
    g = Graphe()
    for i in range(5):
        g.ajouter_sommet(i, f"S{i}", "test")
    g.ajouter_arete(0, 1, 10)
    g.ajouter_arete(1, 2, 5)
    g.ajouter_arete(2, 3, 3)
    g.ajouter_arete(3, 4, 8)
    g.ajouter_arete(4, 0, 4)
    return g


def test_connexite():
    g = creer_mini_graphe()
    connexe, composantes = est_connexe(g)
    assert connexe, "Le mini-graphe devrait etre connexe"
    assert len(composantes) == 1

    # Graphe non connexe
    g2 = Graphe()
    for i in range(4):
        g2.ajouter_sommet(i, f"S{i}", "test")
    g2.ajouter_arete(0, 1, 1)
    g2.ajouter_arete(2, 3, 1)
    connexe2, composantes2 = est_connexe(g2)
    assert not connexe2
    assert len(composantes2) == 2
    print("OK test_connexite")


def test_dijkstra():
    g = creer_mini_graphe()
    d, chemin = dijkstra(g, 0, 2)
    assert d == 15, f"Distance attendue 15, obtenu {d}"
    assert chemin[0] == 0 and chemin[-1] == 2

    d2, chemin2 = dijkstra(g, 0, 0)
    assert d2 == 0 and chemin2 == [0]
    print("OK test_dijkstra")


def test_acpm():
    g = creer_mini_graphe()
    poids_p, aretes_p = prim(g)
    poids_k, aretes_k = kruskal(g)

    # ACPM : aretes {4-0(4), 3-2(3), 2-1(5), 4-3(8)} = 20
    assert poids_p == poids_k, f"Prim={poids_p} Kruskal={poids_k}"
    assert len(aretes_p) == len(g.sommets) - 1
    print(f"OK test_acpm (poids ACPM = {poids_p})")


def test_dijkstra_vs_networkx():
    """Valide le Dijkstra maison contre networkx."""
    try:
        import networkx as nx
    except ImportError:
        print("networkx absent, test skipped")
        return

    g = creer_mini_graphe()
    G_nx = nx.Graph()
    for u in g.adjacence:
        for v, t in g.adjacence[u]:
            G_nx.add_edge(u, v, weight=t)

    for depart in g.sommets:
        for arrivee in g.sommets:
            d_maison, _ = dijkstra(g, depart, arrivee)
            d_nx = nx.dijkstra_path_length(G_nx, depart, arrivee, weight="weight")
            assert d_maison == d_nx, f"({depart}->{arrivee}) maison={d_maison} nx={d_nx}"

    print("OK test_dijkstra_vs_networkx (toutes paires)")


if __name__ == "__main__":
    test_connexite()
    test_dijkstra()
    test_acpm()
    test_dijkstra_vs_networkx()
    print("\nTous les tests passent !")
