"""
Metro Efrei Dodo — Point d'entrée principal.

Ce fichier est le routeur Streamlit : il définit la navigation et applique
le thème global « signalétique RATP claire & futuriste » à toutes les pages
(centralisé dans src/theme.py).

Lancement : streamlit run app.py
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from src import theme

# ── Configuration globale de la page ─────────────────────────────────────────

st.set_page_config(
    page_title="Metro Efrei Dodo",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Thème global (clair, signalétique RATP) ──────────────────────────────────

theme.inject_theme()

# ── Initialisation de l'état global ──────────────────────────────────────────

if "r_chemin" not in st.session_state:
    st.session_state.r_chemin = []
if "r_nb_explores" not in st.session_state:
    st.session_state.r_nb_explores = 0

# ── En-tête de marque dans la sidebar ────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
<div style="display:flex;align-items:center;gap:0.7rem;padding:0.4rem 0.2rem 0.9rem;">
    <div style="width:40px;height:40px;border-radius:12px;display:flex;
                align-items:center;justify-content:center;color:#fff;
                font-family:'Hanken Grotesk',sans-serif;font-weight:900;font-size:1.2rem;
                background:linear-gradient(135deg,#1d6cf2,#003688);
                box-shadow:0 8px 18px rgba(0,54,136,0.32);">M</div>
    <div>
        <div style="font-family:'Hanken Grotesk',sans-serif;font-weight:900;
                    font-size:1.05rem;color:#0a1f44;line-height:1;">Metro Efrei Dodo</div>
        <div style="font-size:0.68rem;color:#8b95b4;font-weight:700;
                    letter-spacing:1px;text-transform:uppercase;margin-top:2px;">
            Réseau · Paris</div>
    </div>
</div>
<div style="height:4px;border-radius:4px;margin:0 0.2rem 0.4rem;
            background:linear-gradient(90deg,#FFCD00,#003CA6,#CF009E,#FF7E2E,#6ECA97,#62259D);"></div>
""",
        unsafe_allow_html=True,
    )

# ── Navigation principale ─────────────────────────────────────────────────────

pages = st.navigation(
    [
        st.Page("pages/solution.py",          title="Solution",                   icon="🚇"),
        st.Page("pages/comment_ca_marche.py", title="Explication & présentation", icon="📖"),
        st.Page("pages/presentation.py",      title="Présentation",               icon="🎤"),
        st.Page("pages/a_propos.py",          title="À propos",                   icon="👤"),
    ],
    position="sidebar",
)

pages.run()
