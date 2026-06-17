"""
Page principale — Solution de navigation du métro parisien.
Contient les 4 onglets : Plus court chemin, ACPM, Heatmap, Performance.
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
from src.co2_calculateur import calculer_co2, estimer_distance_km
from src.connexite import est_connexe
from src.graphe import charger_metro, charger_positions
from src.pdf_export import generer_pdf_trajet
from src.plus_court_chemin import dijkstra
from src.visualisation import tracer_heatmap, tracer_reseau

# Support Folium optionnel (carte géographique OpenStreetMap)
try:
    from src.carte_folium import charger_geo, construire_carte_reseau
    from streamlit_folium import st_folium
    FOLIUM_OK = True
except ImportError:
    FOLIUM_OK = False

# Support photos Wikipedia optionnel
try:
    from src.wikipedia_photos import get_photos_batch
    PHOTOS_OK = True
except ImportError:
    PHOTOS_OK = False

# ── Chargement des données (mis en cache) ─────────────────────────────────────

@st.cache_resource
def charger_donnees():
    g = charger_metro("data/metro.txt")
    pos = charger_positions("data/pospoints.txt")
    return g, pos

@st.cache_resource
def charger_donnees_geo():
    if FOLIUM_OK and os.path.exists("data/stations_geo.json"):
        return charger_geo("data/stations_geo.json")
    return None

g, positions = charger_donnees()
geo = charger_donnees_geo()
noms_tries = sorted(g.noms.values())
noms_inv = {v: k for k, v in g.noms.items()}

# ── Image du plan métro pour le header ────────────────────────────────────────
_map_path = os.path.join(os.path.dirname(__file__), "..", "assets", "metro_map_small.png")
_MAP_B64 = theme.load_image_b64(_map_path)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.divider()

    st.markdown("### 📊 Réseau")
    st.metric("Stations", len(g.sommets))
    st.metric("Liaisons", g.nb_aretes)
    st.metric("Lignes", len(set(g.lignes.values())))

    st.divider()

    st.markdown("### 🔗 Connexité")
    if st.button("Tester la connexité", use_container_width=True):
        t0 = time.perf_counter()
        connexe, composantes = est_connexe(g)
        duree = (time.perf_counter() - t0) * 1000
        if connexe:
            st.success(f"Réseau connexe ✓  ({duree:.2f} ms)")
        else:
            st.error(f"{len(composantes)} composantes isolées ({duree:.2f} ms)")

    st.divider()

    st.markdown("### 🌲 ACPM")
    algo_acpm = st.radio("Algorithme", ["Prim", "Kruskal"], horizontal=True)

# ── Hero banner ───────────────────────────────────────────────────────────────

theme.render_hero(
    title="Metro Efrei Dodo",
    subtitle="Navigateur de réseau — Métro Parisien",
    kicker="Graphes & Algorithmes · MasterCamp 2025-2026 · EFREI Paris",
    stats=[
        (len(g.sommets),              "Stations"),
        (g.nb_aretes,                 "Liaisons"),
        (len(set(g.lignes.values())), "Lignes"),
        ("×29",                       "Moins CO₂", "eco"),
    ],
    map_b64=_MAP_B64,
)

# ── Onglets principaux ────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️  Plus court chemin",
    "🌲  ACPM",
    "🔥  Heatmap",
    "⚡  Performance",
])

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — Plus court chemin (Dijkstra / A*)
# ══════════════════════════════════════════════════════════════════════════════

with tab1:
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        depart_nom = st.selectbox(
            "Station de départ", noms_tries,
            index=noms_tries.index("Abbesses") if "Abbesses" in noms_tries else 0,
        )
    with col2:
        arrivee_nom = st.selectbox(
            "Station d'arrivée", noms_tries,
            index=noms_tries.index("Nation") if "Nation" in noms_tries else 1,
        )
    with col3:
        algo_chemin = st.radio("Algorithme", ["Dijkstra", "A*"], horizontal=False)

    if st.button("Calculer le trajet", type="primary", use_container_width=True):
        depart = noms_inv.get(depart_nom)
        arrivee = noms_inv.get(arrivee_nom)

        if depart is None or arrivee is None:
            st.error("Station introuvable.")
        elif depart == arrivee:
            st.warning("Départ et arrivée identiques.")
        else:
            if algo_chemin == "Dijkstra":
                t0 = time.perf_counter()
                duree_trajet, chemin = dijkstra(g, depart, arrivee)
                t_calcul = (time.perf_counter() - t0) * 1000
                nb_explores = len(g.sommets)
            else:
                t0 = time.perf_counter()
                duree_trajet, chemin, nb_explores = astar(g, depart, arrivee, positions)
                t_calcul = (time.perf_counter() - t0) * 1000

            if not chemin:
                st.error("Aucun chemin trouvé.")
            else:
                st.session_state["r_chemin"] = chemin
                st.session_state["r_duree"] = duree_trajet
                st.session_state["r_depart"] = depart_nom
                st.session_state["r_arrivee"] = arrivee_nom
                st.session_state["r_algo"] = algo_chemin
                st.session_state["r_t_calcul"] = t_calcul
                st.session_state["r_nb_explores"] = nb_explores

    # ── Résultats (persistés en session_state) ────────────────────────────────
    if st.session_state.get("r_chemin"):
        chemin = st.session_state["r_chemin"]
        duree_trajet = st.session_state["r_duree"]
        res_depart = st.session_state["r_depart"]
        res_arrivee = st.session_state["r_arrivee"]
        res_algo = st.session_state["r_algo"]
        t_calcul = st.session_state["r_t_calcul"]
        nb_explores = st.session_state["r_nb_explores"]

        # Métriques principales
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Durée du trajet", f"{duree_trajet // 60} min {duree_trajet % 60} s")
        c2.metric("Nombre de stations", len(chemin))
        c3.metric("Temps de calcul", f"{t_calcul:.2f} ms")
        c4.metric("Nœuds explorés", nb_explores)

        # ── Impact CO₂ ────────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("🌿 Impact environnemental")
        co2 = calculer_co2(estimer_distance_km(duree_trajet))
        ce1, ce2, ce3, ce4 = st.columns(4)
        ce1.metric(
            "Distance estimée", f"{co2['distance_km']:.1f} km",
            help="Vitesse commerciale moyenne : 25 km/h",
        )
        ce2.metric(
            "CO₂ métro", f"{co2['co2_metro_g']:.1f} g",
            help="ADEME 2023 — 4.1 gCO2eq / passager.km",
        )
        ce3.metric(
            "CO₂ voiture", f"{co2['co2_voiture_g']:.0f} g",
            help="ADEME 2023 — 120 g/km voiture moyenne France",
        )
        ce4.metric(
            "Économie CO₂", f"{co2['economie_g']:.0f} g",
            delta=f"× {co2['ratio']:.0f} moins polluant",
        )

        # ── Détail du trajet ──────────────────────────────────────────────────
        with st.expander("📋 Détail du trajet", expanded=True):
            for i, sommet in enumerate(chemin):
                if i == 0:
                    prefixe = "🟢 Départ"
                elif i == len(chemin) - 1:
                    prefixe = "🔴 Arrivée"
                else:
                    prefixe = f"  {i}"
                st.write(f"**{prefixe}** — {g.noms[sommet]} *(ligne {g.lignes[sommet]})*")

        # ── Cartes ────────────────────────────────────────────────────────────
        if FOLIUM_OK and geo is not None:
            carte_schema_tab, carte_geo_tab = st.tabs(
                ["Carte schématique", "Carte géographique (OpenStreetMap)"]
            )
            with carte_schema_tab:
                fig = tracer_reseau(g, positions, chemin=chemin)
                st.plotly_chart(fig, use_container_width=True)
            with carte_geo_tab:
                with st.spinner("Chargement de la carte géographique..."):
                    carte_folium = construire_carte_reseau(g, geo, chemin=chemin)
                    st_folium(carte_folium, width="100%", height=550, returned_objects=[])
        else:
            fig = tracer_reseau(g, positions, chemin=chemin)
            st.plotly_chart(fig, use_container_width=True)
            if not FOLIUM_OK:
                st.caption(
                    "Carte géographique non disponible. "
                    "Installez : `pip install folium streamlit-folium` "
                    "puis : `python scripts/build_stations_geo.py`."
                )

        # ── Photos Wikipedia des stations du trajet ───────────────────────────
        if PHOTOS_OK:
            with st.expander("📸 Photos des stations du trajet (Wikipedia)", expanded=False):
                noms_chemin = [g.noms[s] for s in chemin]
                with st.spinner("Chargement des photos..."):
                    photos = get_photos_batch(noms_chemin, max_photos=9)
                if photos:
                    cols_ph = st.columns(min(3, len(photos)))
                    for i, (nom_ph, url_ph) in enumerate(photos.items()):
                        with cols_ph[i % 3]:
                            st.image(url_ph, caption=nom_ph, use_container_width=True)
                else:
                    st.caption("Aucune photo trouvée pour ces stations.")

        # ── Comparaison Dijkstra vs A* ────────────────────────────────────────
        with st.expander("⚡ Comparer Dijkstra vs A*", expanded=True):
            dep_id = noms_inv.get(res_depart)
            arr_id = noms_inv.get(res_arrivee)
            if dep_id is not None and arr_id is not None and dep_id != arr_id:
                t0 = time.perf_counter()
                dur_d, _ = dijkstra(g, dep_id, arr_id)
                t_d = (time.perf_counter() - t0) * 1000
                nb_d = len(g.sommets)

                t0 = time.perf_counter()
                dur_a, _, nb_a = astar(g, dep_id, arr_id, positions)
                t_a = (time.perf_counter() - t0) * 1000

                col_d, col_a = st.columns(2)
                with col_d:
                    st.markdown("**Dijkstra**")
                    st.metric("Temps de calcul", f"{t_d:.3f} ms")
                    st.metric("Nœuds explorés", nb_d)
                    st.metric("Durée trajet", f"{dur_d // 60}m {dur_d % 60}s")
                with col_a:
                    delta_t = f"{((t_a - t_d) / t_d * 100):+.0f}%" if t_d > 0 else "—"
                    st.markdown("**A\\***")
                    st.metric("Temps de calcul", f"{t_a:.3f} ms", delta=delta_t)
                    st.metric("Nœuds explorés", nb_a, delta=f"-{nb_d - nb_a}")
                    st.metric("Durée trajet", f"{dur_a // 60}m {dur_a % 60}s")

                fig_comp = go.Figure(data=[
                    go.Bar(
                        name="Dijkstra",
                        x=["Temps (ms)", "Nœuds explorés"],
                        y=[t_d, nb_d],
                        marker_color=theme.COLORS["blue"],
                    ),
                    go.Bar(
                        name="A*",
                        x=["Temps (ms)", "Nœuds explorés"],
                        y=[t_a, nb_a],
                        marker_color=theme.COLORS["amber"],
                    ),
                ])
                fig_comp.update_layout(barmode="group")
                theme.style_plotly(fig_comp, height=280, legend=True)
                st.plotly_chart(fig_comp, use_container_width=True)
                st.caption(
                    "Les deux algorithmes trouvent le même chemin optimal. "
                    "A* explore moins de nœuds grâce à son heuristique euclidienne."
                )

        # ── Export PDF ─────────────────────────────────────────────────────────
        st.divider()
        col_pdf1, col_pdf2 = st.columns([1, 3])
        with col_pdf1:
            co2_pdf = calculer_co2(estimer_distance_km(duree_trajet))
            pdf_bytes = generer_pdf_trajet(
                g, chemin, duree_trajet,
                res_depart, res_arrivee,
                algo=res_algo,
                t_calcul_ms=t_calcul,
                co2_data=co2_pdf,
            )
            st.download_button(
                label="📄 Télécharger le trajet (PDF)",
                data=pdf_bytes,
                file_name=f"trajet_{res_depart[:8]}_{res_arrivee[:8]}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — ACPM (Prim / Kruskal)
# ══════════════════════════════════════════════════════════════════════════════

with tab2:
    st.markdown("#### Arbre Couvrant de Poids Minimal")
    st.caption(
        "L'ACPM connecte toutes les stations avec le minimum de temps de trajet total. "
        "Le fond de carte montre le plan officiel du métro pour situer les connexions."
    )

    if st.button("Calculer l'ACPM", type="primary", use_container_width=True):
        t0 = time.perf_counter()
        if algo_acpm == "Prim":
            poids, aretes = prim(g)
        else:
            poids, aretes = kruskal(g)
        t_calcul_acpm = (time.perf_counter() - t0) * 1000

        c1, c2, c3 = st.columns(3)
        c1.metric("Poids total ACPM", f"{poids // 60} min {poids % 60} s")
        c2.metric("Arêtes dans l'ACPM", len(aretes))
        c3.metric("Temps de calcul", f"{t_calcul_acpm:.2f} ms")

        st.info(
            f"Algorithme : **{algo_acpm}** | "
            f"{len(aretes)} arêtes pour {len(g.sommets)} stations"
        )

        fig = tracer_reseau(g, positions, acpm_aretes=aretes)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — Heatmap des connexions
# ══════════════════════════════════════════════════════════════════════════════

with tab3:
    st.markdown("#### Heatmap des connexions")
    st.caption(
        "Taille et couleur proportionnelles au nombre de liaisons directes de chaque station. "
        "Le fond de carte montre le plan officiel du métro parisien."
    )

    fig_heat, degres = tracer_heatmap(g, positions)
    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()
    st.markdown("#### 🏆 Top 10 — Stations les plus connectées")

    top10 = sorted(degres.items(), key=lambda x: x[1], reverse=True)[:10]
    col_top = st.columns(5)
    for i, (num, deg) in enumerate(top10):
        col_top[i % 5].metric(g.noms[num], f"{deg} liaisons", f"Ligne {g.lignes[num]}")

# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 4 — Performance & Benchmark
# ══════════════════════════════════════════════════════════════════════════════

with tab4:
    st.markdown("#### Benchmark des algorithmes")
    st.caption(
        "Compare les temps de calcul de tous les algorithmes "
        "sur le réseau complet (376 stations, 473 arêtes)."
    )

    if st.button("Lancer le benchmark", type="primary", use_container_width=True):
        import pandas as pd

        resultats = []

        # BFS — Connexité
        t0 = time.perf_counter()
        est_connexe(g)
        resultats.append({
            "Algorithme": "BFS (connexité)",
            "Temps (ms)": round((time.perf_counter() - t0) * 1000, 3),
            "Nœuds explorés": len(g.sommets),
        })

        dep_test = list(g.adjacence.keys())[0]
        arr_test = list(g.adjacence.keys())[-1]

        # Dijkstra maison
        t0 = time.perf_counter()
        dijkstra(g, dep_test, arr_test)
        resultats.append({
            "Algorithme": "Dijkstra (maison)",
            "Temps (ms)": round((time.perf_counter() - t0) * 1000, 3),
            "Nœuds explorés": len(g.sommets),
        })

        # A* maison
        t0 = time.perf_counter()
        _, _, nb = astar(g, dep_test, arr_test, positions)
        resultats.append({
            "Algorithme": "A* (maison)",
            "Temps (ms)": round((time.perf_counter() - t0) * 1000, 3),
            "Nœuds explorés": nb,
        })

        # Dijkstra NetworkX (comparaison)
        try:
            import networkx as nx
            G_nx = nx.Graph()
            for u in g.adjacence:
                for v, t in g.adjacence[u]:
                    G_nx.add_edge(u, v, weight=t)
            t0 = time.perf_counter()
            nx.dijkstra_path_length(G_nx, dep_test, arr_test, weight="weight")
            resultats.append({
                "Algorithme": "Dijkstra (NetworkX)",
                "Temps (ms)": round((time.perf_counter() - t0) * 1000, 3),
                "Nœuds explorés": "—",
            })
        except Exception:
            pass

        # Prim
        t0 = time.perf_counter()
        prim(g)
        resultats.append({
            "Algorithme": "Prim (ACPM)",
            "Temps (ms)": round((time.perf_counter() - t0) * 1000, 3),
            "Nœuds explorés": len(g.sommets),
        })

        # Kruskal
        t0 = time.perf_counter()
        kruskal(g)
        resultats.append({
            "Algorithme": "Kruskal (ACPM)",
            "Temps (ms)": round((time.perf_counter() - t0) * 1000, 3),
            "Nœuds explorés": g.nb_aretes,
        })

        df = pd.DataFrame(resultats)
        st.dataframe(df, use_container_width=True)

        try:
            from codecarbon import EmissionsTracker  # noqa: F401
            st.info(
                "codecarbon disponible — lance depuis le terminal avec "
                "`python src/energie.py` pour mesurer la consommation énergétique."
            )
        except ImportError:
            st.warning("codecarbon non disponible pour la mesure énergétique.")
