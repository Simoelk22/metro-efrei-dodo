from collections import deque


def bfs(graphe, depart):
    """BFS depuis 'depart'. Retourne l'ensemble des sommets visités."""
    visites = set()
    file = deque([depart])
    visites.add(depart)
    while file:
        sommet = file.popleft()
        for voisin, _ in graphe.adjacence[sommet]:
            if voisin not in visites:
                visites.add(voisin)
                file.append(voisin)
    return visites


def est_connexe(graphe):
    """
    Retourne (bool, composantes) :
    - True si le graphe est connexe (une seule composante)
    - La liste des composantes connexes (liste de sets)
    """
    non_visites = set(graphe.sommets)
    composantes = []

    while non_visites:
        depart = next(iter(non_visites))
        composante = bfs(graphe, depart)
        composantes.append(composante)
        non_visites -= composante

    return len(composantes) == 1, composantes


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from src.graphe import charger_metro

    g = charger_metro()
    connexe, composantes = est_connexe(g)

    if connexe:
        print(f"Le réseau est CONNEXE ({len(g.sommets)} stations toutes reliées).")
    else:
        print(f"Le réseau N'EST PAS connexe : {len(composantes)} composantes.")
        for i, comp in enumerate(composantes):
            noms = [g.noms[s] for s in list(comp)[:5]]
            print(f"  Composante {i+1} ({len(comp)} stations) : {noms}...")
