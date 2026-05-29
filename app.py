import streamlit as st
import time
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.graphe import charger_metro, charger_positions
from src.connexite import est_connexe
from src.plus_court_chemin import dijkstra
from src.acpm import prim, kruskal
from src.visualisation import tracer_reseau

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
)

st.title("Metro · Efrei · Dodo")
st.caption("Graphes & Algorithmes — MasterCamp 2025-2026")

g, positions = charger_donnees()
noms_tries = sorted(g.noms.values())
noms_inv = {v: k for k, v in g.noms.items()}

# ── Sidebar : infos réseau ────────────────────────────────────────────────────

with st.sidebar:
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

tab1, tab2, tab3 = st.tabs(["Plus court chemin", "ACPM", "Performance"])

# ── Tab 1 : Plus court chemin ─────────────────────────────────────────────────

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        depart_nom = st.selectbox("Station de depart", noms_tries, index=noms_tries.index("Abbesses") if "Abbesses" in noms_tries else 0)
    with col2:
        arrivee_nom = st.selectbox("Station d'arrivee", noms_tries, index=noms_tries.index("Nation") if "Nation" in noms_tries else 1)

    if st.button("Calculer le trajet", type="primary"):
        depart = noms_inv.get(depart_nom)
        arrivee = noms_inv.get(arrivee_nom)

        if depart is None or arrivee is None:
            st.error("Station introuvable.")
        elif depart == arrivee:
            st.warning("Depart et arrivee identiques.")
        else:
            t0 = time.perf_counter()
            duree_trajet, chemin = dijkstra(g, depart, arrivee)
            t_calcul = (time.perf_counter() - t0) * 1000

            if not chemin:
                st.error("Aucun chemin trouve.")
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Duree du trajet", f"{duree_trajet//60} min {duree_trajet%60} s")
                c2.metric("Nombre de stations", len(chemin))
                c3.metric("Temps de calcul", f"{t_calcul:.2f} ms")

                with st.expander("Detail du trajet", expanded=True):
                    for i, sommet in enumerate(chemin):
                        prefixe = "Depart" if i == 0 else ("Arrivee" if i == len(chemin)-1 else f"  {i}")
                        st.write(f"**{prefixe}** — {g.noms[sommet]} *(ligne {g.lignes[sommet]})*")

                fig = tracer_reseau(g, positions, chemin=chemin)
                st.plotly_chart(fig, use_container_width=True)

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

# ── Tab 3 : Performance ───────────────────────────────────────────────────────

with tab3:
    st.subheader("Benchmark des algorithmes")
    st.write("Compare les temps de calcul sur le reseau complet.")

    if st.button("Lancer le benchmark"):
        import networkx as nx

        resultats = []

        # Connexite
        t0 = time.perf_counter()
        est_connexe(g)
        resultats.append({"Algorithme": "BFS (connexite)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3)})

        # Dijkstra maison
        depart_test = list(g.adjacence.keys())[0]
        arrivee_test = list(g.adjacence.keys())[-1]
        t0 = time.perf_counter()
        dijkstra(g, depart_test, arrivee_test)
        resultats.append({"Algorithme": "Dijkstra (maison)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3)})

        # Dijkstra networkx
        try:
            G_nx = nx.Graph()
            for u in g.adjacence:
                for v, t in g.adjacence[u]:
                    G_nx.add_edge(u, v, weight=t)
            t0 = time.perf_counter()
            nx.dijkstra_path_length(G_nx, depart_test, arrivee_test, weight="weight")
            resultats.append({"Algorithme": "Dijkstra (networkx)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3)})
        except Exception:
            pass

        # Prim
        t0 = time.perf_counter()
        prim(g)
        resultats.append({"Algorithme": "Prim (ACPM)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3)})

        # Kruskal
        t0 = time.perf_counter()
        kruskal(g)
        resultats.append({"Algorithme": "Kruskal (ACPM)", "Temps (ms)": round((time.perf_counter()-t0)*1000, 3)})

        import pandas as pd
        df = pd.DataFrame(resultats)
        st.dataframe(df, use_container_width=True)

        try:
            from codecarbon import EmissionsTracker
            st.info("codecarbon disponible — lance le benchmark depuis le terminal avec `python src/energie.py` pour mesurer l'energie.")
        except ImportError:
            st.warning("codecarbon non disponible pour la mesure energetique.")
