import os
import sys

import streamlit as st
import plotly.graph_objects as go

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import theme

# Couleurs locales pour les figures Plotly (cohérentes avec le thème clair)
INK = theme.COLORS["ink"]
INK2 = theme.COLORS["ink_2"]
INK3 = theme.COLORS["ink_3"]
HL = theme.COLORS["amber"]

st.title("Comment ça marche ?")
st.caption("Explication visuelle des algorithmes implementes dans Metro Efrei Dodo")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Le graphe
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("1 · Le reseau du metro comme graphe")

col_txt, col_graph = st.columns([1, 1])

with col_txt:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Modélisation</div>', unsafe_allow_html=True)
    st.markdown("""
<p style="color:#46527a;line-height:1.7;font-size:0.95rem;">
Un <strong style="color:#0a1f44">graphe</strong> est une collection de
<strong style="color:#0a1f44">sommets</strong> (les stations) reliés par des
<strong style="color:#0a1f44">arêtes</strong> (les liaisons entre stations).
<br><br>
Ici le graphe est :
</p>
""", unsafe_allow_html=True)
    for label in ["Non orienté (on peut aller dans les deux sens)", "Pondéré (chaque arête a un poids = temps en secondes)", "Connexe (toutes les stations sont accessibles)"]:
        st.markdown(f'<div class="step-box">✓ {label}</div>', unsafe_allow_html=True)
    st.markdown(f"""
<br>
<p style="color:#46527a;font-size:0.93rem;">
Le réseau compte <strong style="color:#0a1f44">{314} stations</strong> (sommets)
et environ <strong style="color:#0a1f44">{378} liaisons</strong> (arêtes).
Chaque poids est un temps de trajet entre deux stations adjacentes, exprimé en secondes.
</p>
""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_graph:
    # Petit graphe illustratif
    ex_nodes = {"A": (0,2), "B": (2,3.2), "C": (2,0.8), "D": (4,2)}
    ex_edges = [("A","B",60), ("A","C",45), ("B","D",90), ("C","D",30), ("B","C",20)]
    fig_ex = go.Figure()
    for u, v, w in ex_edges:
        x0,y0 = ex_nodes[u]; x1,y1 = ex_nodes[v]
        mx, my = (x0+x1)/2, (y0+y1)/2
        fig_ex.add_trace(go.Scatter(x=[x0,x1,None],y=[y0,y1,None],mode="lines",
            line=dict(color="#1d6cf2",width=2),hoverinfo="none",showlegend=False))
        fig_ex.add_annotation(x=mx,y=my,text=f"{w}s",showarrow=False,
            font=dict(color="#0a1f44",size=12),bgcolor="rgba(255,255,255,0.85)",borderpad=3)
    for name,(x,y) in ex_nodes.items():
        fig_ex.add_trace(go.Scatter(x=[x],y=[y],mode="markers+text",
            marker=dict(size=28,color="#003688",line=dict(width=2,color="#ffffff")),
            text=[name],textfont=dict(color="white",size=14),textposition="middle center",
            hoverinfo="none",showlegend=False))
    fig_ex.update_layout(
        height=280, margin=dict(l=10,r=10,t=10,b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False,zeroline=False,showticklabels=False,range=[-0.5,4.5]),
        yaxis=dict(showgrid=False,zeroline=False,showticklabels=False,range=[0,4]),
    )
    st.plotly_chart(fig_ex, use_container_width=True)
    st.caption("Exemple simplifié : 4 stations, 5 liaisons, poids en secondes.")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Dijkstra animé
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("2 · Dijkstra — pas a pas")

# Graphe de démo hardcodé (6 noeuds)
DEMO_POS = {
    "A": (0.0, 2.0),
    "B": (1.8, 3.2),
    "C": (1.8, 0.8),
    "D": (3.6, 3.2),
    "E": (3.6, 0.8),
    "F": (5.4, 2.0),
}
DEMO_EDGES = [
    ("A","B",4), ("A","C",2),
    ("B","C",1), ("B","D",5),
    ("C","E",8),
    ("D","E",2), ("D","F",6),
    ("E","F",3),
]

# ── Simulation Dijkstra pas à pas ─────────────────────────────────────────────

def simuler_dijkstra(nodes, edges, source, target):
    """Retourne la liste des étapes de Dijkstra."""
    import heapq
    adj = {n: [] for n in nodes}
    for u, v, w in edges:
        adj[u].append((v, w)); adj[v].append((u, w))

    dist = {n: float("inf") for n in nodes}
    dist[source] = 0
    prev = {}
    tas = [(0, source)]
    visited = set()
    steps = []

    def snap(current, updated):
        chemin_actuel = []
        if current == target or target in visited:
            s = target
            while s in prev:
                chemin_actuel.append(s); s = prev[s]
            if s == source: chemin_actuel.append(source)
            chemin_actuel.reverse()
        steps.append({
            "current": current,
            "visited": set(visited),
            "dist": dict(dist),
            "updated": set(updated),
            "chemin": list(chemin_actuel),
        })

    snap(None, [])

    while tas:
        d, u = heapq.heappop(tas)
        if u in visited: continue
        visited.add(u)
        updated = []
        if u == target:
            snap(u, [])
            break
        for v, w in adj[u]:
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd; prev[v] = u
                heapq.heappush(tas, (nd, v))
                updated.append(v)
        snap(u, updated)

    return steps

steps = simuler_dijkstra(list(DEMO_POS.keys()), DEMO_EDGES, "A", "F")

# ── Descriptions textuelles ───────────────────────────────────────────────────

DESCRIPTIONS = [
    "Etat initial. Toutes les distances sont infinies sauf A=0. On va explorer depuis A vers F.",
    "On traite A (dist=0). On met a jour ses voisins : B=4, C=2. On choisit ensuite le noeud non visité avec la plus petite distance.",
    "On traite C (dist=2, le plus petit). B passe de 4 à 3 (via A→C→B). E = 2+8 = 10.",
    "On traite B (dist=3). D = 3+5 = 8. A déjà visité, C déjà visité.",
    "On traite D (dist=8). E = min(10, 8+2) = 10 (inchangé). F = 8+6 = 14.",
    "On traite E (dist=10). F = min(14, 10+3) = 13. F mis à jour !",
    "On traite F (dist=13). Cible atteinte ! Chemin optimal : A→C→B→D→E→F en 13 unités.",
]

# ── Slider & figure ───────────────────────────────────────────────────────────

col_ctrl, col_desc = st.columns([2, 3])

with col_ctrl:
    step_idx = st.slider("Etape", 0, len(steps)-1, 0, key="dijkstra_step")
    st.markdown(f'<div class="step-box">{DESCRIPTIONS[min(step_idx, len(DESCRIPTIONS)-1)]}</div>', unsafe_allow_html=True)

with col_desc:
    step = steps[step_idx]
    dist_step = step["dist"]

    # Légende des distances
    st.markdown('<div class="card" style="padding:1rem 1.4rem;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Table des distances</div>', unsafe_allow_html=True)
    cols_dist = st.columns(6)
    for i, node in enumerate(DEMO_POS):
        d = dist_step[node]
        val = str(d) if d != float("inf") else "∞"
        style = "color:#00935f" if node in step["visited"] else ("color:#d97706" if node == step["current"] else "color:#46527a")
        cols_dist[i].markdown(
            f'<div style="text-align:center;">'
            f'<div style="font-weight:700;font-size:1.1rem;{style}">{node}</div>'
            f'<div style="color:#8b95b4;font-size:0.85rem;">{val}</div>'
            f'</div>', unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Figure Plotly de l'étape ──────────────────────────────────────────────────

def couleur_noeud(n, step):
    if step["chemin"] and n in step["chemin"] and step["current"] == step["chemin"][-1]:
        return "#00935f"  # chemin final
    if n == step["current"]:
        return "#f59e0b"  # en cours
    if n in step["visited"]:
        return "#1d6cf2"  # visité
    if n in step["updated"]:
        return "#c2185b"  # vient d'être mis à jour
    return "#94a3b8"      # non visité

def couleur_arete(u, v, step):
    chemin = step["chemin"]
    if len(chemin) >= 2:
        pairs = list(zip(chemin, chemin[1:]))
        if (u, v) in pairs or (v, u) in pairs:
            return ("#00935f", 4)
    if u in step["visited"] and v in step["visited"]:
        return ("#1d6cf2", 2)
    return ("rgba(120,134,170,0.45)", 1)

fig_dijkstra = go.Figure()

for u, v, w in DEMO_EDGES:
    x0,y0 = DEMO_POS[u]; x1,y1 = DEMO_POS[v]
    color, width = couleur_arete(u, v, step)
    fig_dijkstra.add_trace(go.Scatter(
        x=[x0,x1,None], y=[y0,y1,None], mode="lines",
        line=dict(color=color, width=width),
        hoverinfo="none", showlegend=False,
    ))
    mx, my = (x0+x1)/2, (y0+y1)/2
    fig_dijkstra.add_annotation(x=mx, y=my, text=str(w), showarrow=False,
        font=dict(color="#0a1f44", size=11), bgcolor="rgba(255,255,255,0.88)", borderpad=2)

for name, (x, y) in DEMO_POS.items():
    c = couleur_noeud(name, step)
    dist_val = dist_step[name]
    dist_txt = str(dist_val) if dist_val != float("inf") else "∞"
    fig_dijkstra.add_trace(go.Scatter(
        x=[x], y=[y], mode="markers+text",
        marker=dict(size=36, color=c, line=dict(width=2, color="white")),
        text=[name], textfont=dict(color="white", size=14),
        textposition="middle center",
        customdata=[[dist_txt]],
        hovertemplate=f"<b>{name}</b><br>dist = {dist_txt}<extra></extra>",
        showlegend=False,
    ))
    # Distance sous le noeud
    fig_dijkstra.add_annotation(
        x=x, y=y-0.35, text=dist_txt, showarrow=False,
        font=dict(color="#46527a", size=10), bgcolor="rgba(0,0,0,0)",
    )

# Légende couleurs
legende = [
    ("#94a3b8", "Non visité"),
    ("#f59e0b", "En cours de traitement"),
    ("#c2185b", "Vient d'être mis à jour"),
    ("#1d6cf2", "Visité (distance finale)"),
    ("#00935f", "Chemin optimal trouvé"),
]
for i, (color, label) in enumerate(legende):
    fig_dijkstra.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=10, color=color),
        name=label, showlegend=True,
    ))

fig_dijkstra.update_layout(
    height=340, margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 6]),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 4.2]),
    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0,
                font=dict(color="#46527a", size=11), bgcolor="rgba(0,0,0,0)"),
)

st.plotly_chart(fig_dijkstra, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — A* vs Dijkstra
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("3 · A* — Dijkstra avec du bon sens")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Dijkstra</div>', unsafe_allow_html=True)
    st.markdown(f"""
<p style="color:#46527a;font-size:0.93rem;line-height:1.7;">
Explore tous les noeuds par ordre de distance croissante depuis la source.
<br><br>
<strong style="color:#0a1f44">Optimal :</strong> toujours trouve le chemin le plus court.<br>
<strong style="color:#dc2626">Lent :</strong> explore des zones inutiles loin de la destination.
<br><br>
Complexité : {theme.COMPLEXITES['dijkstra_t']}
</p>
""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">A* (A-star)</div>', unsafe_allow_html=True)
    st.markdown(f"""
<p style="color:#46527a;font-size:0.93rem;line-height:1.7;">
Ajoute une <strong style="color:#0a1f44">heuristique
<span class="math"><i>h</i>(<i>n</i>)</span></strong> = distance euclidienne vers la
destination, multipliée par un facteur admissible (min temps/pixel sur le graphe).
<br><br>
<strong style="color:#0a1f44">Fonction d'évaluation :</strong>
</p>
<div style="text-align:center;margin:0.1rem 0 0.5rem;">
<span class="math" style="font-size:1.2em;">
  <i>f</i>(<i>n</i>) = <i>g</i>(<i>n</i>) + <i>h</i>(<i>n</i>)
</span>
</div>
<p style="color:#46527a;font-size:0.93rem;line-height:1.7;">
<span class="math"><i>g</i>(<i>n</i>)</span> = coût réel depuis la source ·
<span class="math"><i>h</i>(<i>n</i>)</span> = estimation (minorante) du reste
<br><br>
<strong style="color:#00935f">Plus rapide :</strong> explore moins de noeuds.<br>
<strong style="color:#0a1f44">Optimal :</strong> garanti si
<span class="math"><i>h</i></span> est admissible, c.-à-d.
<span class="math"><i>h</i>(<i>n</i>) ≤ <i>h</i>*(<i>n</i>)</span> (ne surestime jamais).
<br><br>
Complexité : {theme.COMPLEXITES['astar_t']} <span style="color:#8b95b4;">(même pire cas que Dijkstra, meilleur en pratique)</span>
</p>
""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Tableau comparatif
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("4 · Tableau comparatif des algorithmes")

C = theme.COMPLEXITES
_rows = [
    ("BFS",      "Connexité du graphe",          C["bfs_t"],      C["bfs_s"],      "Non"),
    ("Dijkstra", "Plus court chemin",            C["dijkstra_t"], C["dijkstra_s"], "Oui"),
    ("A*",       "Plus court chemin (guidé)",    C["astar_t"],    C["astar_s"],    "Oui"),
    ("Prim",     "Arbre couvrant minimum",       C["prim_t"],     C["prim_s"],     "Oui"),
    ("Kruskal",  "Arbre couvrant minimum",       C["kruskal_t"],  C["kruskal_s"],  "Oui"),
]
_body = ""
for i, (algo, pb, ct, cs, w) in enumerate(_rows):
    bg = "background:rgba(10,31,68,0.03);" if i % 2 else ""
    wcol = "#00935f" if w == "Oui" else "#8b95b4"
    _body += (
        f'<tr style="{bg}border-bottom:1px solid rgba(10,31,68,0.07);">'
        f'<td style="padding:8px 12px;font-weight:700;color:#003688;">{algo}</td>'
        f'<td style="padding:8px 12px;">{pb}</td>'
        f'<td style="padding:8px 12px;text-align:center;">{ct}</td>'
        f'<td style="padding:8px 12px;text-align:center;">{cs}</td>'
        f'<td style="padding:8px 12px;text-align:center;color:{wcol};font-weight:600;">{w}</td>'
        f'</tr>'
    )
st.markdown(f"""
<div class="card">
<table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
<thead><tr style="border-bottom:2px solid rgba(0,54,136,0.3);">
  <th style="padding:8px 12px;color:#46527a;text-align:left;">Algorithme</th>
  <th style="padding:8px 12px;color:#46527a;text-align:left;">Problème résolu</th>
  <th style="padding:8px 12px;color:#46527a;text-align:center;">Complexité temps</th>
  <th style="padding:8px 12px;color:#46527a;text-align:center;">Complexité espace</th>
  <th style="padding:8px 12px;color:#46527a;text-align:center;">Pondéré</th>
</tr></thead>
<tbody>{_body}</tbody>
</table>
<p style="margin:0.7rem 0 0;font-size:0.78rem;color:#8b95b4;">
  <i>S</i> = nombre de sommets (stations) · <i>A</i> = nombre d'arêtes (liaisons) ·
  complexités pour un graphe connexe avec tas binaire.
</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — ACPM
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("5 · Prim & Kruskal — l'Arbre Couvrant de Poids Minimal")

col_p, col_k = st.columns(2)

with col_p:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Prim</div>', unsafe_allow_html=True)
    st.markdown("""
<p style="color:#46527a;font-size:0.93rem;line-height:1.7;">
Part d'un sommet, et à chaque étape ajoute l'arête de moindre poids qui connecte un sommet
déjà dans l'arbre à un nouveau sommet.
<br><br>
Fonctionne comme Dijkstra mais on cherche le poids d'arête minimal, pas la distance totale.
Utilise un <strong style="color:#0a1f44">tas min</strong> pour l'efficacité.
</p>
""", unsafe_allow_html=True)
    for etape in [
        "Commencer depuis un sommet quelconque",
        "Ajouter l'arête sortante la moins chère",
        "Répéter jusqu'à avoir tous les sommets",
    ]:
        st.markdown(f'<div class="step-box">{etape}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_k:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Kruskal</div>', unsafe_allow_html=True)
    st.markdown("""
<p style="color:#46527a;font-size:0.93rem;line-height:1.7;">
Trie toutes les arêtes par poids croissant. Ajoute une arête si elle ne crée pas de cycle,
vérifié grâce à la structure <strong style="color:#0a1f44">Union-Find</strong>.
<br><br>
Approche globale vs locale pour Prim. Les deux donnent exactement le même poids total
d'ACPM (mais pas forcément les mêmes arêtes si certains poids sont identiques).
</p>
""", unsafe_allow_html=True)
    for etape in [
        "Trier toutes les arêtes par poids",
        "Pour chaque arête : ajouter si pas de cycle (Union-Find)",
        "Arrêter quand on a S-1 arêtes",
    ]:
        st.markdown(f'<div class="step-box">{etape}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;color:#8b95b4;font-weight:600;font-size:0.78rem;margin-top:2rem;">
Metro Efrei Dodo · Mohammed El Karchal · EFREI Paris · 2026
</div>
""", unsafe_allow_html=True)
