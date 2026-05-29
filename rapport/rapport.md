# Rapport — Metro Efrei Dodo

**Auteur :** Mohammed EL KARCHAL  
**Module :** MasterCamp — Passage M1  
**Soutenance :** 18 juin 2026  

---

## 1. Problématique

Le réseau de métro parisien peut être modélisé comme un **graphe non orienté pondéré** :
- **Sommets** : stations (376 nœuds)
- **Arêtes** : liaisons entre stations (473 arêtes)
- **Poids** : temps de trajet en secondes

Trois questions fondamentales sont posées :
1. Le réseau est-il **connexe** ? (peut-on aller de n'importe quelle station à n'importe quelle autre ?)
2. Quel est l'**Arbre Couvrant de Poids Minimal** (ACPM) ? (infrastructure minimale qui relie toutes les stations)
3. Quel est le **plus court chemin** entre deux stations ?

---

## 2. Modélisation

### Structure de données

Choix : **liste d'adjacence** (dictionnaire Python)

```
adjacence = {
    num_sommet: [(voisin1, temps1), (voisin2, temps2), ...]
}
```

**Pourquoi pas une matrice d'adjacence ?**  
Avec 376 sommets, une matrice prendrait 376² = ~141 000 cases, dont la grande majorité seraient vides (le graphe est **creux** : 473 arêtes seulement). La liste d'adjacence est plus légère en mémoire et plus rapide pour parcourir les voisins.

---

## 3. Algorithmes implémentés

### 3.1 Test de connexité — BFS

**Principe :** parcours en largeur depuis un sommet de départ. On marque chaque sommet visité. Si le nombre de visités = nombre total de sommets → graphe connexe.

**Complexité :** O(V + E) où V = sommets, E = arêtes.

**Résultat :** Le réseau parisien est **connexe** (toutes les 376 stations sont accessibles).

### 3.2 Plus court chemin — Dijkstra

**Principe :**
1. File de priorité (tas min) contenant `(distance_cumulée, sommet)`
2. Dictionnaire `dist` initialisé à ∞ (sauf départ = 0)
3. À chaque étape : on extrait le sommet le plus proche, on **relaxe** ses voisins
4. On reconstruit le chemin via le dictionnaire `précédent`

**Complexité :** O((V + E) log V) avec un tas min.

**Validation :** résultats identiques à l'implémentation `networkx.dijkstra_path_length`.

### 3.3 ACPM — Prim et Kruskal

**Prim :**  
On part d'un sommet, on ajoute à chaque étape l'arête de poids minimal qui relie un sommet déjà dans l'arbre à un sommet extérieur.  
Complexité : O(E log V)

**Kruskal :**  
On trie toutes les arêtes par poids croissant, on les ajoute une à une si elles ne créent pas de cycle (structure **Union-Find** avec compression de chemin).  
Complexité : O(E log E)

**Résultat :** Poids ACPM = **20 362 s** (~339 min). Les deux algorithmes donnent le même résultat.

---

## 4. Résultats et performances

| Algorithme | Temps de calcul | Résultat |
|---|---|---|
| BFS (connexité) | ~0.5 ms | Réseau connexe |
| Dijkstra maison | ~1 ms | Chemin optimal en O((V+E) log V) |
| Dijkstra networkx | ~1 ms | Identique au maison |
| Prim | ~2 ms | ACPM = 20 362 s |
| Kruskal | ~3 ms | ACPM = 20 362 s |

### Mesure énergétique (codecarbon)

L'outil `codecarbon` estime la consommation énergétique en kWh et l'empreinte CO₂eq.  
Pour des algorithmes de cette taille, les valeurs sont de l'ordre du **microgramme de CO₂eq** par exécution — illustrant la **sobriété numérique** d'une implémentation efficace.

---

## 5. Interface Streamlit

L'application `app.py` permet :
- Sélection de deux stations via des menus déroulants
- Affichage du trajet optimal avec détail station par station
- Visualisation sur carte interactive (Plotly)
- Affichage de l'ACPM (Prim ou Kruskal au choix)
- Benchmark comparatif des algorithmes

---

## 6. Exemple de trajet

**Abbesses → Nation :**  
- Durée : 20 min 26 s (1226 secondes)  
- 19 stations traversées  
- Calculé en < 1 ms

---

## 7. Choix techniques et justifications

| Choix | Justification |
|---|---|
| Python 3 | Demandé par le sujet, lisibilité du code |
| Algorithmes codés à la main | Compréhension profonde, explicables à l'oral |
| Liste d'adjacence | Graphe creux → économie mémoire |
| Validation networkx | Preuve de correction de l'implémentation |
| codecarbon | Angle "empreinte carbone" du sujet |
| Streamlit | Interface web interactive sans frontend |

---

## 8. Conclusion

Ce projet illustre l'application concrète de la théorie des graphes à un problème réel : le réseau de transport parisien. Les algorithmes implémentés (BFS, Dijkstra, Prim, Kruskal) couvrent les problèmes fondamentaux de parcours, de chemin optimal et d'arbre couvrant minimal. La validation croisée avec networkx garantit la correction des implémentations.
