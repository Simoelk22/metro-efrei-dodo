import heapq


def dijkstra(graphe, depart, arrivee):
    """
    Dijkstra avec un tas min (heapq).
    Retourne (distance_totale, chemin_liste_de_sommets)
    ou (inf, []) si pas de chemin.
    """
    dist = {s: float("inf") for s in graphe.sommets}
    precedent = {}
    dist[depart] = 0

    # file de priorité : (distance_cumulée, sommet)
    tas = [(0, depart)]

    while tas:
        d, u = heapq.heappop(tas)

        if d > dist[u]:
            continue  # entrée obsolète dans le tas

        if u == arrivee:
            break

        for voisin, temps in graphe.adjacence[u]:
            nouvelle_dist = dist[u] + temps
            if nouvelle_dist < dist[voisin]:
                dist[voisin] = nouvelle_dist
                precedent[voisin] = u
                heapq.heappush(tas, (nouvelle_dist, voisin))

    # Reconstruction du chemin
    if dist[arrivee] == float("inf"):
        return float("inf"), []

    chemin = []
    sommet = arrivee
    while sommet != depart:
        chemin.append(sommet)
        sommet = precedent[sommet]
    chemin.append(depart)
    chemin.reverse()

    return dist[arrivee], chemin


def afficher_chemin(graphe, chemin, duree_totale):
    """Affiche le trajet de façon lisible."""
    print(f"\nTrajet ({len(chemin)} stations, {duree_totale}s = {duree_totale//60}min {duree_totale%60}s) :")
    for i, sommet in enumerate(chemin):
        prefixe = "  →" if i > 0 else "  ◉"
        print(f"{prefixe} {graphe.noms[sommet]} (ligne {graphe.lignes[sommet]})")


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from src.graphe import charger_metro

    g = charger_metro()

    # Trouver les numéros par nom
    noms_inv = {v: k for k, v in g.noms.items()}

    depart_nom = "Abbesses"
    arrivee_nom = "Nation"

    if depart_nom not in noms_inv or arrivee_nom not in noms_inv:
        print("Station introuvable.")
    else:
        d, chemin = dijkstra(g, noms_inv[depart_nom], noms_inv[arrivee_nom])
        afficher_chemin(g, chemin, d)
