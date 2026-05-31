import streamlit as st
import time
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.graphe import charger_metro, charger_positions
from src.connexite import est_connexe
from src.plus_court_chemin import dijkstra
from src.astar import astar
from src.acpm import prim, kruskal
from src.visualisation import tracer_reseau, tracer_heatmap
from src.pdf_export import generer_pdf_trajet

# ── Chargement des données (mis en cache) ─────────────────────────────────────

@st.cache_resource
def charger_donnees():
    g = charger_metro("data/metro.txt")
    pos = charger_positions("data/pospoints.txt")
    return g, pos

# ── Config de la page ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Metro Efrei Dodo",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Thème sombre / clair ──────────────────────────────────────────────────────

if "mode_sombre" not in st.session_state:
    st.session_state.mode_sombre = True

if st.session_state.mode_sombre:
    st.markdown("""
    <style>
    .stApp { background: #0e1117; color: #fafafa; }
    .stSidebar { background: #161b27; }
    .stTabs [data-baseweb="tab-list"] { background: #1a1f2e; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { color: #a0a4c8; }
    .stTabs [aria-selected="true"] { color: #ffffff !important; background: #2d3250 !important; border-radius: 6px; }
    .stMetric { background: #1a1f2e; border-radius: 10px; padding: 0.6rem 1rem; }
    div[data-testid="stMetricValue"] { color: #e0e4ff; }
    .stButton > button { background: #2d3250; color: #ffffff; border: 1px solid #404880; border-radius: 8px; }
    .stButton > button:hover { background: #3d4470; border-color: #5c6bc0; }
    .stSelectbox > div > div { background: #1a1f2e; color: #fafafa; }
    .stRadio label { color: #c0c4e0; }
    </style>
    """, unsafe_allow_html=True)

# ── Données ───────────────────────────────────────────────────────────────────

g, positions = charger_donnees()
noms_tries = sorted(g.noms.values())
noms_inv = {v: k for k, v in g.noms.items()}

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    # Thème
    mode_sombre_cb = st.checkbox("Mode sombre", value=st.session_state.mode_sombre)
    if mode_sombre_cb != st.session_state.mode_sombre:
        st.session_state.mode_sombre = mode_sombre_cb
        st.rerun()

    st.divider()

    st.header("Réseau")
    st.metric("Stations", len(g.sommets))
    st.metric("Liaisons", g.nb_aretes)

    st.divider()

    st.header("Connexite")
    if st.button("Tester la connexite"):
        t0 = time.perf_counter()
        connexe, composantes = est_connexe(g)
        duree = (time.perf_counter() - t0) * 1000
        if connexe:
            st.success(f"Reseau connexe ({duree:.2f} ms)")
        else:
            st.error(f"{len(composantes)} composantes isolees ({duree:.2f} ms)")

    st.divider()

    st.header("ACPM")
    algo_acpm = st.radio("Algorithme", ["Prim", "Kruskal"], horizontal=True)
    afficher_acpm = st.checkbox("Afficher l'ACPM sur la carte")

# ── Onglets principaux ────────────────────────────────────────────────────────

st.title("Metro · Efrei · Dodo")
st.caption("Graphes & Algorithmes — MasterCamp 2025-2026")

tab1, tab2, tab3, tab4 = st.tabs(["Plus court chemin", "ACPM", "Heatmap", "Performance"])

# ── Tab 1 : Plus court chemin (Dijkstra / A*) ─────────────────────────────────

with tab1:
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        depart_nom = st.selectbox(
            "Station de depart", noms_tries,
            index=noms_tries.index("Abbesses") if "Abbesses" in noms_tries else 0
        )
    with col2:
        arrivee_nom = st.selectbox(
            "Station d'arrivee", noms_tries,
            index=noms_tries.index("Nation") if "Nation" in noms_tries else 1
        )
    with col3:
        algo_chemin = st.radio("Algorithme", ["Dijkstra", "A*"], horizontal=False)

    if st.button("Calculer le trajet", type="primary"):
        depart = noms_inv.get(depart_nom)
        arrivee = noms_inv.get(arrivee_nom)

        if depart is None or arrivee is None:
            st.error("Station introuvable.")
        elif depart == arrivee:
            st.warning("Depart et arrivee identiques.")
        else:
            if algo_chemin == "Dijkstra":
                t0 = time.perf_counter()
                duree_trajet, chemin = dijkstra(g, depart, arrivee)
                t_calcul = (time.perf_counter() - t0) * 1000
                nb_explores = len(g.sommets)  # Dijkstra explore tout
            else:
                t0 = time.perf_counter()
                duree_trajet, chemin, nb_explores = astar(g, depart, arrivee, positions)
                t_calcul = (time.perf_counter() - t0) * 1000

            if not chemin:
                st.error("Aucun chemin trouve.")
            else:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Duree du trajet", f"{duree_trajet//60} min {duree_trajet%60} s")
                c2.metric("Nombre de stations", len(chemin))
                c3.metric("Temps de calcul", f"{t_calcul:.2f} ms")
                c4.metric("Noeuds explores", nb_explores)

                with st.expander("Detail du trajet", expanded=True):
                    for i, sommet in enumerate(chemin):
                        if i == 0:
                            prefixe = "Depart"
                        elif i == len(chemin) - 1:
                            prefixe = "Arrivee"
                        else:
                            prefixe = f"  {i}"
                        st.write(f"**{prefixe}** — {g.noms[sommet]} *(ligne {g.lignes[sommet]})*")

                fig = tracer_reseau(g, positions, chemin=chemin)
                st.plotly_chart(fig, use_container_width=True)

                # ── Export PDF ────────────────────────────────────────────────
                st.divider()
                col_pdf1, col_pdf2 = st.columns([1, 3])
                with col_pdf1:
                    pdf_bytes = generer_pdf_trajet(
                        g, chemin, duree_trajet,
                        depart_nom, arrivee_nom,
                        algo=algo_chemin, t_calcul_ms=t_calcul
                    )
                    st.download_button(
                        label="Telecharger le trajet (PDF)",
                        data=pdf_bytes,
                        file_name=f"trajet_{depart_nom[:8]}_{arrivee_nom[:8]}.pdf",
                        mime="application/pdf",
                    )

# ── Tab 2 : ACPM ─────────────────────────────────────────────────────────────

with tab2:
    if st.button("Calculer l'ACPM", type="primary"):
        t0 = time.perf_counter()
        if algo_acpm == "Prim":
            poids, aretes = prim(g)
        else:
            poids, aretes = kruskal(g)
        t_calcul = (time.perf_counter() - t0) * 1000

        c1, c2, c3 = st.columns(3)
        c1.metric("Poids total ACPM", f"{poids//60} min {poids%60} s")
        c2.metric("Aretes dans l'ACPM", len(aretes))
        c3.metric("Temps de calcul", f"{t_calcul:.2f} ms")

        st.info(f"Algorithme : **{algo_acpm}** | {len(aretes)} aretes pour {len(g.sommets)} stations")

        fig = tracer_reseau(g, positions, acpm_aretes=aretes)
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 3 : Heatmap ───────────────────────────────────────────────────────────

with tab3:
    st.subheader("Heatmap des connexions")
    st.caption("Taille et couleur proportionnelles au nombre de liaisons directes de chaque station.")

    fig_heat, degres = tracer_heatmap(g, positions)
    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()
    st.subheader("Top 10 — stations les plus connectees")

    top10 = sorted(degres.items(), key=lambda x: x[1], reverse=True)[:10]
    col_top = st.columns(5)
    for i, (num, deg) in enumerate(top10):
        col_top[i % 5].metric(g.noms[num], f"{deg} liaisons", f"Ligne {g.lignes[num]}")

# ── Tab 4 : Performance ───────────────────────────────────────────────────────

with tab4:
    st.subheader("Benchmark des algorithmes")
    st.write("Compare les temps de calcul sur le reseau complet.")

    if st.button("Lancer le benchmark"):
        import networkx as nx
        import pandas as pd

        resultats = []

        # Connexite
        t0 = time.perf_counter()
        est_connexe(g)
        resultats.append({"Algorithme": "BFS (connexite)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3), "Noeuds explores": len(g.sommets)})

        depart_test = list(g.adjacence.keys())[0]
        arrivee_test = list(g.adjacence.keys())[-1]

        # Dijkstra maison
        t0 = time.perf_counter()
        dijkstra(g, depart_test, arrivee_test)
        resultats.append({"Algorithme": "Dijkstra (maison)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3), "Noeuds explores": len(g.sommets)})

        # A* maison
        t0 = time.perf_counter()
        _, _, nb = astar(g, depart_test, arrivee_test, positions)
        resultats.append({"Algorithme": "A* (maison)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3), "Noeuds explores": nb})

        # Dijkstra networkx
        try:
            G_nx = nx.Graph()
            for u in g.adjacence:
                for v, t in g.adjacence[u]:
                    G_nx.add_edge(u, v, weight=t)
            t0 = time.perf_counter()
            nx.dijkstra_path_length(G_nx, depart_test, arrivee_test, weight="weight")
            resultats.append({"Algorithme": "Dijkstra (networkx)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3), "Noeuds explores": "—"})
        except Exception:
            pass

        # Prim
        t0 = time.perf_counter()
        prim(g)
        resultats.append({"Algorithme": "Prim (ACPM)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3), "Noeuds explores": len(g.sommets)})

        # Kruskal
        t0 = time.perf_counter()
        kruskal(g)
        resultats.append({"Algorithme": "Kruskal (ACPM)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3), "Noeuds explores": g.nb_aretes})

        df = pd.DataFrame(resultats)
        st.dataframe(df, use_container_width=True)

        try:
            from codecarbon import EmissionsTracker
            st.info("codecarbon disponible — lance depuis le terminal avec `python src/energie.py` pour mesurer l'energie.")
        except ImportError:
            st.warning("codecarbon non disponible pour la mesure energetique.")
