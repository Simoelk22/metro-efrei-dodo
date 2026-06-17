"""
Page de présentation guidée — Metro Efrei Dodo
Conçue pour présenter le projet devant un jury.

Navigation : 5 "slides" via les boutons en haut de page.
Chaque slide correspond à une section de la présentation.
"""

import os
import sys
import time

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import theme
from src.acpm import kruskal, prim
from src.astar import astar
from src.connexite import est_connexe
from src.graphe import charger_metro, charger_positions
from src.plus_court_chemin import dijkstra

# Le thème global (signalétique RATP claire) fournit déjà .card, .badge,
# .section-label et .check-item — voir src/theme.py.

# ── Chargement des données (mis en cache) ─────────────────────────────────────

@st.cache_resource
def _charger():
    g = charger_metro("data/metro.txt")
    pos = charger_positions("data/pospoints.txt")
    return g, pos

g, positions = _charger()
noms_tries = sorted(g.noms.values())
noms_inv = {v: k for k, v in g.noms.items()}

# ── En-tête ───────────────────────────────────────────────────────────────────

theme.render_hero(
    title="Metro Efrei Dodo",
    subtitle="Graphes & Algorithmes — Présentation guidée",
    kicker="MasterCamp 2025-2026 · EFREI Paris",
)

# ── Navigation entre slides ───────────────────────────────────────────────────

SLIDES = [
    "🎯 Contexte",
    "🏗️ Architecture",
    "⚙️ Algorithmes",
    "📊 Résultats live",
    "🎬 Guide de démo",
]
slide = st.radio("", SLIDES, horizontal=True, label_visibility="collapsed")
st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Contexte & Problématique
# ═══════════════════════════════════════════════════════════════════════════════

if slide == SLIDES[0]:

    st.markdown('<p class="section-label">Le Problème</p>', unsafe_allow_html=True)
    st.markdown("## Naviguer dans le métro parisien")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
<div class="card">
<h3 style="margin-top:0;color:#46527a;">Le défi</h3>
<p style="line-height:1.7;">
Le réseau de métro parisien est l'un des plus denses au monde.
Trouver le trajet optimal entre deux stations n'est pas trivial :
il faut explorer des centaines de nœuds tout en minimisant le temps de parcours.
</p>
<p style="line-height:1.7; margin-bottom:0;">
Ce projet modélise le réseau comme un <b>graphe pondéré non orienté</b>
et implémente plusieurs algorithmes de recherche de chemin pour le résoudre.
</p>
</div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="card">
<h3 style="margin-top:0;color:#46527a;">Formulation mathématique</h3>
<p>
G = (V, E, w) où :<br>
• <b>V</b> = stations (sommets)<br>
• <b>E</b> = liaisons directes (arêtes)<br>
• <b>w(u,v)</b> = temps de trajet en secondes (poids)<br><br>
Objectif : trouver le chemin P de s à t tel que <b>Σ w(e) est minimal</b>.
</p>
</div>
        """, unsafe_allow_html=True)

    with col2:
        # Métriques du réseau réel chargé
        nb_stations = len(g.sommets)
        nb_liaisons = g.nb_aretes
        nb_lignes = len(set(g.lignes.values()))

        st.markdown('<p class="section-label">Notre jeu de données</p>', unsafe_allow_html=True)
        st.metric("Stations (nœuds)", nb_stations)
        st.metric("Liaisons (arêtes)", nb_liaisons)
        st.metric("Lignes de métro", nb_lignes)
        st.divider()
        st.metric("Source des données", "metro.txt", help="Données RATP — format V/E")
        st.metric("Positions", "pospoints.txt", help="Coordonnées schématiques x;y")

        st.markdown("""
<div class="card" style="margin-top:1rem;">
<p class="section-label">Enjeu environnemental</p>
<p style="font-size:0.9rem;line-height:1.6;margin:0;">
Le métro émet <b>4,1 gCO₂eq/km</b> (vs 120 g pour une voiture).
Soit <b>× 29 moins polluant</b>. Notre app calcule l'économie carbone
pour chaque trajet.
</p>
</div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Architecture technique
# ═══════════════════════════════════════════════════════════════════════════════

elif slide == SLIDES[1]:

    st.markdown('<p class="section-label">Organisation du code</p>', unsafe_allow_html=True)
    st.markdown("## Architecture du projet")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
<div class="card">
<p class="section-label">Modules src/</p>
<table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
<thead>
<tr style="border-bottom:1px solid rgba(10,31,68,0.12);">
<th style="text-align:left;padding:4px 8px;color:#46527a;">Fichier</th>
<th style="text-align:left;padding:4px 8px;color:#46527a;">Rôle</th>
</tr>
</thead>
<tbody>
<tr><td style="padding:5px 8px;font-family:monospace;color:#003688;">graphe.py</td>
    <td style="padding:5px 8px;">Structure de données Graphe + parsers</td></tr>
<tr style="background:rgba(10,31,68,0.03);">
<td style="padding:5px 8px;font-family:monospace;color:#003688;">connexite.py</td>
    <td style="padding:5px 8px;">BFS + détection composantes connexes</td></tr>
<tr><td style="padding:5px 8px;font-family:monospace;color:#003688;">plus_court_chemin.py</td>
    <td style="padding:5px 8px;">Dijkstra avec tas min (heapq)</td></tr>
<tr style="background:rgba(10,31,68,0.03);">
<td style="padding:5px 8px;font-family:monospace;color:#003688;">astar.py</td>
    <td style="padding:5px 8px;">A* avec heuristique euclidienne</td></tr>
<tr><td style="padding:5px 8px;font-family:monospace;color:#003688;">acpm.py</td>
    <td style="padding:5px 8px;">Prim (tas min) + Kruskal (Union-Find)</td></tr>
<tr style="background:rgba(10,31,68,0.03);">
<td style="padding:5px 8px;font-family:monospace;color:#003688;">visualisation.py</td>
    <td style="padding:5px 8px;">Graphes Plotly (schématique + heatmap)</td></tr>
<tr><td style="padding:5px 8px;font-family:monospace;color:#003688;">carte_folium.py</td>
    <td style="padding:5px 8px;">Carte géographique OpenStreetMap</td></tr>
<tr style="background:rgba(10,31,68,0.03);">
<td style="padding:5px 8px;font-family:monospace;color:#003688;">co2_calculateur.py</td>
    <td style="padding:5px 8px;">Impact carbone ADEME 2023</td></tr>
<tr><td style="padding:5px 8px;font-family:monospace;color:#003688;">pdf_export.py</td>
    <td style="padding:5px 8px;">Génération PDF (fpdf2)</td></tr>
<tr style="background:rgba(10,31,68,0.03);">
<td style="padding:5px 8px;font-family:monospace;color:#003688;">wikipedia_photos.py</td>
    <td style="padding:5px 8px;">Photos stations (API Wikipedia FR)</td></tr>
<tr><td style="padding:5px 8px;font-family:monospace;color:#003688;">energie.py</td>
    <td style="padding:5px 8px;">Mesure énergie / CO₂ (codecarbon)</td></tr>
</tbody>
</table>
</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="card">
<p class="section-label">Pages Streamlit</p>
<table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
<thead>
<tr style="border-bottom:1px solid rgba(10,31,68,0.12);">
<th style="text-align:left;padding:4px 8px;color:#46527a;">Page</th>
<th style="text-align:left;padding:4px 8px;color:#46527a;">Contenu</th>
</tr>
</thead>
<tbody>
<tr><td style="padding:5px 8px;font-family:monospace;color:#b45309;">app.py</td>
    <td style="padding:5px 8px;">Application principale (4 onglets)</td></tr>
<tr style="background:rgba(10,31,68,0.03);">
<td style="padding:5px 8px;font-family:monospace;color:#b45309;">comment_ca_marche.py</td>
    <td style="padding:5px 8px;">Explication pas-à-pas des algos</td></tr>
<tr><td style="padding:5px 8px;font-family:monospace;color:#b45309;">presentation.py</td>
    <td style="padding:5px 8px;">Guide de présentation (cette page)</td></tr>
<tr style="background:rgba(10,31,68,0.03);">
<td style="padding:5px 8px;font-family:monospace;color:#b45309;">a_propos.py</td>
    <td style="padding:5px 8px;">Profil auteur + stack technique</td></tr>
</tbody>
</table>
</div>

<div class="card">
<p class="section-label">Structure des données</p>
<pre style="background:#0a0e1a;padding:1rem;border-radius:8px;
            font-size:0.82rem;color:#00935f;overflow-x:auto;">
<span style="color:#9fa8da">class</span> Graphe:
    adjacence  <span style="color:#607d8b"># dict[int, list[(int, int)]]</span>
               <span style="color:#607d8b">#   {sommet: [(voisin, temps_s)]}</span>
    noms       <span style="color:#607d8b"># dict[int, str]</span>
    lignes     <span style="color:#607d8b"># dict[int, str]</span>
    sommets    <span style="color:#607d8b"># list[int]</span>
    nb_aretes  <span style="color:#607d8b"># int</span>
</pre>
</div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="card">
<p class="section-label">Format des fichiers de données</p>
<pre style="background:#0a0e1a;padding:0.8rem;border-radius:8px;
            font-size:0.8rem;color:#1d6cf2;overflow-x:auto;">
<span style="color:#607d8b"># metro.txt</span>
V 1 Abbesses ;12;Non 1
V 2 Pigalle ;2;Non 0
E 1 2 60          <span style="color:#607d8b"># 60 secondes</span>

<span style="color:#607d8b"># pospoints.txt</span>
192;447;Abbesses
</pre>
</div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Algorithmes
# ═══════════════════════════════════════════════════════════════════════════════

elif slide == SLIDES[2]:

    st.markdown('<p class="section-label">Les 5 algorithmes implémentés</p>', unsafe_allow_html=True)
    st.markdown("## Algorithmes de graphe")

    # ── Tableau comparatif ────────────────────────────────────────────────────
    st.markdown("""
<div class="card">
<table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
<thead>
<tr style="border-bottom:2px solid rgba(0,54,136,0.3);">
  <th style="padding:8px 12px;color:#46527a;text-align:left;">Algorithme</th>
  <th style="padding:8px 12px;color:#46527a;text-align:left;">Problème résolu</th>
  <th style="padding:8px 12px;color:#46527a;text-align:center;">Complexité temps</th>
  <th style="padding:8px 12px;color:#46527a;text-align:center;">Complexité espace</th>
  <th style="padding:8px 12px;color:#46527a;text-align:left;">Technique clé</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom:1px solid rgba(10,31,68,0.07);">
  <td style="padding:8px 12px;font-weight:700;color:#003688;">BFS</td>
  <td style="padding:8px 12px;">Connexité du graphe</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O(S + A)</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O(S)</td>
  <td style="padding:8px 12px;">File FIFO, marquage visité</td>
</tr>
<tr style="background:rgba(10,31,68,0.03);border-bottom:1px solid rgba(10,31,68,0.07);">
  <td style="padding:8px 12px;font-weight:700;color:#003688;">Dijkstra</td>
  <td style="padding:8px 12px;">Plus court chemin (source unique)</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O((S+A) log S)</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O(S)</td>
  <td style="padding:8px 12px;">Tas min (heapq), relaxation</td>
</tr>
<tr style="border-bottom:1px solid rgba(10,31,68,0.07);">
  <td style="padding:8px 12px;font-weight:700;color:#003688;">A*</td>
  <td style="padding:8px 12px;">Plus court chemin (guidé)</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O((S+A) log S)</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O(S)</td>
  <td style="padding:8px 12px;">Dijkstra + heuristique euclidienne</td>
</tr>
<tr style="background:rgba(10,31,68,0.03);border-bottom:1px solid rgba(10,31,68,0.07);">
  <td style="padding:8px 12px;font-weight:700;color:#003688;">Prim</td>
  <td style="padding:8px 12px;">Arbre couvrant minimal</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O(A log S)</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O(S + A)</td>
  <td style="padding:8px 12px;">Glouton, extension locale</td>
</tr>
<tr>
  <td style="padding:8px 12px;font-weight:700;color:#003688;">Kruskal</td>
  <td style="padding:8px 12px;">Arbre couvrant minimal</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O(A log A)</td>
  <td style="padding:8px 12px;text-align:center;font-family:monospace;color:#1d6cf2;">O(S + A)</td>
  <td style="padding:8px 12px;">Tri + Union-Find</td>
</tr>
</tbody>
</table>
<p style="margin:0.5rem 0 0;font-size:0.78rem;color:#8b95b4;">S = nb sommets · A = nb arêtes · Tous implémentés from scratch sans NetworkX</p>
</div>
    """, unsafe_allow_html=True)

    # ── Avantage de A* sur Dijkstra ───────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
<div class="card">
<p class="section-label">Dijkstra — Tous les nœuds</p>
<p style="line-height:1.7;font-size:0.9rem;">
Explore le graphe <b>en étoile</b> depuis la source.
Garantit l'optimalité mais visite tous les sommets
accessibles, même ceux dans la mauvaise direction.
</p>
<p style="color:#dc2626;font-size:0.88rem;margin-bottom:0;">
⚠ Explore <b>tous les ~370 sommets</b> sur notre réseau,
même pour un trajet court.
</p>
</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="card">
<p class="section-label">A* — Guidé par l'heuristique</p>
<p style="line-height:1.7;font-size:0.9rem;">
Ajoute une <b>estimation de distance</b> euclidienne vers l'arrivée.
Le tas contient <code>f = g + h</code> : coût réel + estimation admissible.
</p>
<p style="color:#00935f;font-size:0.88rem;margin-bottom:0;">
✓ Explore <b>significativement moins de nœuds</b> en guidant
la recherche vers la bonne direction.
</p>
</div>
        """, unsafe_allow_html=True)

    # ── ACPM : Prim vs Kruskal ────────────────────────────────────────────────
    st.markdown('<p class="section-label" style="margin-top:1rem;">Arbre couvrant minimal</p>',
                unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("""
<div class="card">
<p class="section-label">Prim — Approche locale</p>
<p style="font-size:0.9rem;line-height:1.7;margin-bottom:0;">
Démarre depuis un nœud et <b>étend l'arbre progressivement</b>
en ajoutant à chaque étape l'arête la moins coûteuse
qui relie l'arbre à un nouveau sommet.
Efficace sur les graphes <b>denses</b>.
</p>
</div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
<div class="card">
<p class="section-label">Kruskal — Approche globale</p>
<p style="font-size:0.9rem;line-height:1.7;margin-bottom:0;">
Trie <b>toutes les arêtes</b> par poids, puis les ajoute
dans l'ordre en utilisant <b>Union-Find</b> pour détecter
les cycles. Efficace sur les graphes <b>creux</b>.
Les deux algorithmes produisent le <b>même poids total</b>.
</p>
</div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Résultats live
# ═══════════════════════════════════════════════════════════════════════════════

elif slide == SLIDES[3]:

    st.markdown('<p class="section-label">Données mesurées en direct</p>', unsafe_allow_html=True)
    st.markdown("## Résultats & Benchmarks")

    # ── Sélection du trajet de démo ───────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        dep_nom = st.selectbox(
            "Station de départ",
            noms_tries,
            index=noms_tries.index("Châtelet") if "Châtelet" in noms_tries else 0,
            key="pres_dep",
        )
    with col_b:
        arr_nom = st.selectbox(
            "Station d'arrivée",
            noms_tries,
            index=noms_tries.index("Nation") if "Nation" in noms_tries else 1,
            key="pres_arr",
        )

    dep_id = noms_inv.get(dep_nom)
    arr_id = noms_inv.get(arr_nom)

    if st.button("Lancer le benchmark complet", type="primary"):
        if dep_id is None or arr_id is None or dep_id == arr_id:
            st.warning("Sélectionne deux stations différentes.")
        else:
            # ── Mesures ───────────────────────────────────────────────────────
            with st.spinner("Calcul en cours..."):
                # BFS connexité
                t0 = time.perf_counter()
                connexe, composantes = est_connexe(g)
                t_bfs = (time.perf_counter() - t0) * 1000

                # Dijkstra
                t0 = time.perf_counter()
                dur_d, chemin_d = dijkstra(g, dep_id, arr_id)
                t_dijk = (time.perf_counter() - t0) * 1000
                nb_d = len(g.sommets)

                # A*
                t0 = time.perf_counter()
                dur_a, chemin_a, nb_a = astar(g, dep_id, arr_id, positions)
                t_astar = (time.perf_counter() - t0) * 1000

                # Prim
                t0 = time.perf_counter()
                poids_p, _ = prim(g)
                t_prim = (time.perf_counter() - t0) * 1000

                # Kruskal
                t0 = time.perf_counter()
                poids_k, _ = kruskal(g)
                t_kruskal = (time.perf_counter() - t0) * 1000

            # ── Résultats connexité ───────────────────────────────────────────
            st.markdown("### Connexité du réseau")
            c1, c2, c3 = st.columns(3)
            c1.metric("Réseau connexe", "Oui ✓" if connexe else "Non ✗")
            c2.metric("Composantes", len(composantes) if not connexe else 1)
            c3.metric("BFS — Temps de calcul", f"{t_bfs:.3f} ms")

            # ── Résultats plus court chemin ───────────────────────────────────
            st.markdown(f"### Plus court chemin : {dep_nom} → {arr_nom}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Durée du trajet", f"{dur_d // 60} min {dur_d % 60} s")
            c2.metric("Stations traversées", len(chemin_d))
            c3.metric("Dijkstra — Temps calcul", f"{t_dijk:.3f} ms")
            c4.metric(
                "A* — Temps calcul",
                f"{t_astar:.3f} ms",
                delta=f"{((t_astar - t_dijk) / t_dijk * 100):+.0f}%" if t_dijk > 0 else "—",
            )

            # ── Graphique comparatif Dijkstra vs A* ───────────────────────────
            fig_cmp = go.Figure(data=[
                go.Bar(
                    name="Dijkstra",
                    x=["Temps (ms)", "Nœuds explorés"],
                    y=[round(t_dijk, 3), nb_d],
                    marker_color=theme.COLORS["blue"],
                    text=[f"{t_dijk:.3f} ms", str(nb_d)],
                    textposition="outside",
                ),
                go.Bar(
                    name="A*",
                    x=["Temps (ms)", "Nœuds explorés"],
                    y=[round(t_astar, 3), nb_a],
                    marker_color=theme.COLORS["amber"],
                    text=[f"{t_astar:.3f} ms", str(nb_a)],
                    textposition="outside",
                ),
            ])
            fig_cmp.update_layout(
                barmode="group",
                title=dict(
                    text="Dijkstra vs A* — Comparaison directe",
                    font=dict(size=14, color=theme.COLORS["ink"]),
                ),
            )
            theme.style_plotly(fig_cmp, height=320, legend=True)
            st.plotly_chart(fig_cmp, use_container_width=True)

            # ── ACPM ──────────────────────────────────────────────────────────
            st.markdown("### Arbre couvrant minimal (ACPM)")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Poids Prim", f"{poids_p // 60} min {poids_p % 60} s")
            c2.metric("Poids Kruskal", f"{poids_k // 60} min {poids_k % 60} s")
            c3.metric("Prim — Temps calcul", f"{t_prim:.3f} ms")
            c4.metric("Kruskal — Temps calcul", f"{t_kruskal:.3f} ms")

            # ── CO₂ ───────────────────────────────────────────────────────────
            from src.co2_calculateur import calculer_co2, estimer_distance_km
            co2 = calculer_co2(estimer_distance_km(dur_d))
            st.markdown("### Impact CO₂ du trajet")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Distance estimée", f"{co2['distance_km']:.1f} km")
            c2.metric("CO₂ métro", f"{co2['co2_metro_g']:.1f} g")
            c3.metric("CO₂ voiture", f"{co2['co2_voiture_g']:.0f} g")
            c4.metric(
                "Économie CO₂",
                f"{co2['economie_g']:.0f} g",
                delta=f"× {co2['ratio']:.0f} moins polluant",
            )

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Guide de démo
# ═══════════════════════════════════════════════════════════════════════════════

elif slide == SLIDES[4]:

    st.markdown('<p class="section-label">Script de présentation</p>', unsafe_allow_html=True)
    st.markdown("## Guide de démo live")

    col1, col2 = st.columns([3, 2])

    with col1:

        st.markdown("""
<div class="card">
<p class="section-label" style="color:#dc2626;">Avant de commencer</p>
<div class="check-item">
  <span style="font-size:1.1rem;">✅</span>
  <span>Lancer l'app : <code>streamlit run app.py</code></span>
</div>
<div class="check-item">
  <span style="font-size:1.1rem;">✅</span>
  <span>Vérifier que <code>data/stations_geo.json</code> existe (carte géo disponible)</span>
</div>
<div class="check-item">
  <span style="font-size:1.1rem;">✅</span>
  <span>Naviguer sur cette page → slide "Résultats live" → cliquer benchmark</span>
</div>
</div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="card">
<p class="section-label" style="color:#003688;">Étape 1 — Contexte (1 min)</p>
<div class="check-item">
  <span>📌</span>
  <span>Expliquer le problème : naviguer dans un graphe pondéré de 370+ nœuds</span>
</div>
<div class="check-item">
  <span>📌</span>
  <span>Montrer la structure de données <code>Graphe</code> dans <code>src/graphe.py</code></span>
</div>
<div class="check-item">
  <span>📌</span>
  <span>Rappeler : <b>aucun algorithme NetworkX</b> — tout est implémenté from scratch</span>
</div>
</div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="card">
<p class="section-label" style="color:#003688;">Étape 2 — Démo Plus Court Chemin (3 min)</p>
<div class="check-item">
  <span>🚇</span>
  <span>Aller sur l'onglet <b>"Plus court chemin"</b> → choisir Gare du Nord → Nation</span>
</div>
<div class="check-item">
  <span>🚇</span>
  <span>Lancer avec <b>Dijkstra</b> : montrer durée, stations, temps de calcul</span>
</div>
<div class="check-item">
  <span>🚇</span>
  <span>Relancer avec <b>A*</b> : montrer que le résultat est identique, mais moins de nœuds explorés</span>
</div>
<div class="check-item">
  <span>🚇</span>
  <span>Afficher la <b>carte géographique</b> (onglet "Carte géographique") avec l'animation</span>
</div>
<div class="check-item">
  <span>🚇</span>
  <span>Montrer le <b>bloc CO₂</b> : "× 29 moins polluant que la voiture"</span>
</div>
<div class="check-item">
  <span>🚇</span>
  <span>Télécharger le <b>PDF</b> du trajet</span>
</div>
</div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="card">
<p class="section-label" style="color:#003688;">Étape 3 — Connexité (1 min)</p>
<div class="check-item">
  <span>🔗</span>
  <span>Sidebar → "Tester la connexité" → montrer le résultat en temps réel (BFS)</span>
</div>
<div class="check-item">
  <span>🔗</span>
  <span>Expliquer : <b>BFS en O(S+A)</b>, visite tous les sommets accessibles</span>
</div>
</div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="card">
<p class="section-label" style="color:#003688;">Étape 4 — ACPM (1 min)</p>
<div class="check-item">
  <span>🌲</span>
  <span>Onglet <b>"ACPM"</b> → sélectionner Prim → "Calculer l'ACPM"</span>
</div>
<div class="check-item">
  <span>🌲</span>
  <span>Relancer avec Kruskal → montrer que le poids total est <b>identique</b></span>
</div>
<div class="check-item">
  <span>🌲</span>
  <span>Expliquer Union-Find pour Kruskal (complexité O(A log A))</span>
</div>
</div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="card">
<p class="section-label" style="color:#003688;">Étape 5 — Heatmap & Performance (1 min)</p>
<div class="check-item">
  <span>📊</span>
  <span>Onglet <b>"Heatmap"</b> → identifier les hubs (Châtelet, Montparnasse...)</span>
</div>
<div class="check-item">
  <span>📊</span>
  <span>Onglet <b>"Performance"</b> → "Lancer le benchmark" → tableau comparatif</span>
</div>
<div class="check-item">
  <span>📊</span>
  <span>Page <b>"Comment ça marche"</b> → animation Dijkstra pas-à-pas</span>
</div>
</div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
<div class="card">
<p class="section-label">Points forts à mettre en avant</p>
<ul style="line-height:2;font-size:0.9rem;padding-left:1.2rem;">
  <li>Algorithmes <b>100% from scratch</b></li>
  <li>Visualisation <b>double</b> (schématique + géo)</li>
  <li>Données <b>réelles RATP</b></li>
  <li>Carte <b>interactive OpenStreetMap</b></li>
  <li>Photos des stations (<b>Wikipedia API</b>)</li>
  <li>Animation A* vs Dijkstra <b>en direct</b></li>
  <li>Export <b>PDF professionnel</b></li>
  <li>Calcul <b>CO₂ ADEME 2023</b></li>
  <li>Mesure <b>énergie codecarbon</b></li>
  <li>Tests unitaires <b>pytest</b></li>
</ul>
</div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="card">
<p class="section-label">Questions jury probables</p>
<details style="cursor:pointer;margin-bottom:0.5rem;">
  <summary style="font-weight:700;color:#46527a;">
    Pourquoi A* et pas juste Dijkstra ?
  </summary>
  <p style="margin-top:0.5rem;font-size:0.88rem;line-height:1.6;">
    A* est admissible (heuristique euclidienne ≤ distance réelle) donc garantit
    l'optimalité, mais explore moins de nœuds en guidant la recherche vers l'arrivée.
    Sur un graphe spatial comme le métro c'est particulièrement adapté.
  </p>
</details>
<details style="cursor:pointer;margin-bottom:0.5rem;">
  <summary style="font-weight:700;color:#46527a;">
    Prim ou Kruskal, lequel est meilleur ?
  </summary>
  <p style="margin-top:0.5rem;font-size:0.88rem;line-height:1.6;">
    Dépend du graphe. Prim est efficace sur les graphes denses (O(A log S)),
    Kruskal sur les graphes creux (O(A log A)). Notre réseau de métro est creux
    (A ≈ 2S), donc les deux ont des performances similaires.
  </p>
</details>
<details style="cursor:pointer;">
  <summary style="font-weight:700;color:#46527a;">
    Le graphe est-il vraiment connexe ?
  </summary>
  <p style="margin-top:0.5rem;font-size:0.88rem;line-height:1.6;">
    Oui ! On peut le vérifier en direct avec le bouton dans la sidebar.
    Notre BFS parcourt tous les sommets depuis n'importe quelle source et
    confirme qu'il n'y a qu'une seule composante connexe.
  </p>
</details>
</div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="card">
<p class="section-label">Stack technique</p>
<p style="font-size:0.88rem;line-height:1.9;margin:0;">
🐍 Python 3.12<br>
🎨 Streamlit · Plotly<br>
🗺️ Folium · OpenStreetMap<br>
📄 fpdf2<br>
📸 API Wikipedia FR<br>
🌿 codecarbon (ADEME)<br>
🔬 NetworkX (benchmark seul)<br>
🧪 pytest
</p>
</div>
        """, unsafe_allow_html=True)
