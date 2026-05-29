import heapq


# ── Prim ──────────────────────────────────────────────────────────────────────

def prim(graphe):
    """
    Algorithme de Prim avec un tas min.
    Retourne (poids_total, liste_d_aretes) où chaque arête = (u, v, temps).
    """
    depart = graphe.sommets[0]
    dans_arbre = set()
    dans_arbre.add(depart)

    # tas : (poids, sommet_source, sommet_destination)
    tas = []
    for voisin, temps in graphe.adjacence[depart]:
        heapq.heappush(tas, (temps, depart, voisin))

    aretes_acpm = []
    poids_total = 0

    while tas and len(dans_arbre) < len(graphe.sommets):
        poids, u, v = heapq.heappop(tas)

        if v in dans_arbre:
            continue  # crée un cycle, on ignore

        dans_arbre.add(v)
        aretes_acpm.append((u, v, poids))
        poids_total += poids

        for voisin, temps in graphe.adjacence[v]:
            if voisin not in dans_arbre:
                heapq.heappush(tas, (temps, v, voisin))

    return poids_total, aretes_acpm


# ── Kruskal (avec union-find) ─────────────────────────────────────────────────

class UnionFind:
    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.rang = {e: 0 for e in elements}

    def trouver(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.trouver(self.parent[x])  # compression
        return self.parent[x]

    def unir(self, x, y):
        rx, ry = self.trouver(x), self.trouver(y)
        if rx == ry:
            return False  # déjà dans le même ensemble
        if self.rang[rx] < self.rang[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rang[rx] == self.rang[ry]:
            self.rang[rx] += 1
        return True


def kruskal(graphe):
    """
    Algorithme de Kruskal.
    Retourne (poids_total, liste_d_aretes) où chaque arête = (u, v, temps).
    """
    # Collecter toutes les arêtes sans doublon
    aretes = set()
    for u in graphe.adjacence:
        for v, temps in graphe.adjacence[u]:
            aretes.add((temps, min(u, v), max(u, v)))

    aretes = sorted(aretes)  # tri par poids croissant

    uf = UnionFind(graphe.sommets)
    aretes_acpm = []
    poids_total = 0

    for temps, u, v in aretes:
        if uf.unir(u, v):
            aretes_acpm.append((u, v, temps))
            poids_total += temps
            if len(aretes_acpm) == len(graphe.sommets) - 1:
                break  # arbre complet

    return poids_total, aretes_acpm


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from src.graphe import charger_metro

    g = charger_metro()

    poids_prim, aretes_prim = prim(g)
    print(f"Prim   — poids total : {poids_prim}s ({poids_prim//60} min)  |  {len(aretes_prim)} arêtes")

    poids_kruskal, aretes_kruskal = kruskal(g)
    print(f"Kruskal— poids total : {poids_kruskal}s ({poids_kruskal//60} min)  |  {len(aretes_kruskal)} arêtes")

    assert poids_prim == poids_kruskal, "Les deux algos donnent des poids différents !"
    print("✓ Prim et Kruskal donnent le même poids total.")
