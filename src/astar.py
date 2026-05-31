import heapq
import math


def _construire_positions_num(graphe, positions_noms):
    """Convertit {nom: (x,y)} en {num_sommet: (x,y)}."""
    noms_pos = {k.lower(): v for k, v in positions_noms.items()}
    pos = {}
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


def _echelle_heuristique(graphe, positions_par_num):
    """
    Calcule le ratio min(temps / distance_pixels) sur toutes les arêtes.
    Garantit que l'heuristique est admissible (ne surestime jamais).
    """
    scales = []
    for u in graphe.adjacence:
        for v, t in graphe.adjacence[u]:
            if u in positions_par_num and v in positions_par_num:
                px, py = positions_par_num[u]
                qx, qy = positions_par_num[v]
                d = math.sqrt((px - qx) ** 2 + (py - qy) ** 2)
                if d > 0:
                    scales.append(t / d)
    return min(scales) if scales else 0.0


def astar(graphe, depart, arrivee, positions_noms=None):
    """
    A* avec heuristique euclidienne (si positions fournies) ou Dijkstra pur (sinon).

    Paramètres
    ----------
    graphe        : instance de Graphe
    depart        : num_sommet de départ
    arrivee       : num_sommet d'arrivée
    positions_noms: dict {nom_station: (x, y)} issu de charger_positions()

    Retourne
    --------
    (distance_totale, chemin, nb_noeuds_explores)
    """
    # Construire les positions par numéro si disponibles
    positions_par_num = {}
    echelle = 0.0
    if positions_noms:
        positions_par_num = _construire_positions_num(graphe, positions_noms)
        echelle = _echelle_heuristique(graphe, positions_par_num)

    def h(sommet):
        if echelle == 0.0 or sommet not in positions_par_num or arrivee not in positions_par_num:
            return 0.0
        ax, ay = positions_par_num[sommet]
        bx, by = positions_par_num[arrivee]
        return echelle * math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)

    dist = {s: float("inf") for s in graphe.sommets}
    dist[depart] = 0
    precedent = {}
    nb_explores = 0

    # tas : (f = g + h, g = dist_reelle, sommet)
    tas = [(h(depart), 0, depart)]

    while tas:
        f, g, u = heapq.heappop(tas)

        if g > dist[u]:
            continue  # entrée obsolète

        nb_explores += 1

        if u == arrivee:
            break

        for voisin, temps in graphe.adjacence[u]:
            nouvelle_g = dist[u] + temps
            if nouvelle_g < dist[voisin]:
                dist[voisin] = nouvelle_g
                precedent[voisin] = u
                nouvelle_f = nouvelle_g + h(voisin)
                heapq.heappush(tas, (nouvelle_f, nouvelle_g, voisin))

    if dist[arrivee] == float("inf"):
        return float("inf"), [], nb_explores

    chemin = []
    sommet = arrivee
    while sommet != depart:
        chemin.append(sommet)
        sommet = precedent[sommet]
    chemin.append(depart)
    chemin.reverse()

    return dist[arrivee], chemin, nb_explores
