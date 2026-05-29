class Graphe:
    def __init__(self):
        self.adjacence = {}   # {num_sommet: [(voisin, temps), ...]}
        self.noms = {}        # {num_sommet: nom_station}
        self.lignes = {}      # {num_sommet: numero_ligne}

    def ajouter_sommet(self, num, nom, ligne):
        self.adjacence.setdefault(num, [])
        self.noms[num] = nom
        self.lignes[num] = ligne

    def ajouter_arete(self, u, v, temps):
        self.adjacence[u].append((v, temps))
        self.adjacence[v].append((u, temps))   # non orienté

    @property
    def sommets(self):
        return list(self.adjacence.keys())

    @property
    def nb_aretes(self):
        return sum(len(v) for v in self.adjacence.values()) // 2


def charger_metro(chemin="data/metro.txt"):
    """
    Format V : V num nom_station ;ligne ;terminus branchement
    Format E : E num1 num2 temps_secondes
    """
    g = Graphe()
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            p = ligne.split()
            if not p:
                continue
            if p[0] == "V" and len(p) >= 5:
                try:
                    num = int(p[1])
                except ValueError:
                    continue  # ligne d'entête comme "V num_sommet ..."
                # p[-3] = ';ligne', p[-2] = ';terminus', p[-1] = branchement
                # nom = tout ce qui est entre p[2] et p[-3]
                nom = " ".join(p[2:-3])
                num_ligne = p[-3].lstrip(";")
                g.ajouter_sommet(num, nom, num_ligne)
            elif p[0] == "E" and len(p) == 4:
                try:
                    g.ajouter_arete(int(p[1]), int(p[2]), int(p[3]))
                except ValueError:
                    continue  # ligne d'entête
    return g


def charger_positions(chemin="data/pospoints.txt"):
    """
    Format : x;y;nom_station  (espaces remplacés par @)
    Retourne {nom_station: (x, y)}
    """
    positions = {}
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne:
                continue
            parts = ligne.split(";")
            if len(parts) == 3:
                x, y = int(parts[0]), int(parts[1])
                nom = parts[2].replace("@", " ")
                positions[nom] = (x, y)
    return positions


if __name__ == "__main__":
    g = charger_metro()
    print(f"Stations : {len(g.sommets)}")
    print(f"Arêtes   : {g.nb_aretes}")
    n = g.sommets[0]
    print(f"Voisins de '{g.noms[n]}' (ligne {g.lignes[n]}) :")
    for voisin, temps in g.adjacence[n]:
        print(f"  -> {g.noms[voisin]} ({temps}s)")
