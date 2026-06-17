import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import theme

# Le thème global (signalétique RATP claire) fournit déjà toutes les classes
# utilisées ici (.card, .profile-img, .badge, .section-title, .body-text,
# .skill-bar-*, .contact-link, .algo-tag, .quote) — voir src/theme.py.

# ── En-tête avec photo ────────────────────────────────────────────────────────

photo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "photo.jpg")

st.markdown('<div class="profile-wrapper">', unsafe_allow_html=True)

if os.path.exists(photo_path):
    with open(photo_path, "rb") as f:
        import base64
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<img class="profile-img" src="data:image/jpeg;base64,{b64}" alt="Mohammed El Karchal"/>',
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="profile-placeholder">M</div>', unsafe_allow_html=True)

st.markdown("""
<div class="nom">Mohammed El Karchal</div>
<div style="text-align:center; margin-top: 0.5rem;">
    <span class="badge">Étudiant EFREI Paris</span>
    <span class="badge">Big Data & Machine Learning</span>
    <span class="badge">MasterCamp 2025-2026</span>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ── Présentation ──────────────────────────────────────────────────────────────

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Qui suis-je</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text">
Bonjour, je m'appelle <strong style="color:#0a1f44;">Mohammed El Karchal</strong>.
Je suis étudiant à l'<strong style="color:#0a1f44;">EFREI Paris</strong>, école d'ingénieurs
spécialisée en informatique. Ce projet est né dans le cadre du MasterCamp, un sprint
intensif où chaque équipe conçoit et code une application complète en quelques jours —
genre hackathon, mais avec des vraies contraintes académiques en plus.
<br><br>
J'ai toujours trouvé les graphes fascinants : c'est l'un des rares domaines en informatique
où un problème concret (trouver le meilleur trajet dans le métro) se résout avec une
structure mathématique abstraite. Ce projet m'a donné l'occasion de creuser ça sérieusement,
d'implémenter Dijkstra et Prim de zéro, et de tout envelopper dans une interface
qui soit vraiment utilisable.
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ── Ce projet ─────────────────────────────────────────────────────────────────

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Metro Efrei Dodo — le projet</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text">
L'application modélise le réseau du métro parisien sous forme de <strong style="color:#0a1f44;">graphe pondéré</strong>
(les poids = temps de trajet en secondes). À partir de là, trois grandes fonctionnalités :
</div>
<br>
""", unsafe_allow_html=True)

cols_algos = [
    ("Dijkstra", f"Plus court chemin entre deux stations — {theme.COMPLEXITES['dijkstra_t']}"),
    ("Prim", f"Arbre couvrant de poids minimal — {theme.COMPLEXITES['prim_t']}"),
    ("Kruskal", f"Même résultat, autre approche — {theme.COMPLEXITES['kruskal_t']}"),
    ("BFS", "Vérification de la connexité du réseau"),
]
for nom, desc in cols_algos:
    st.markdown(
        f'<span class="algo-tag">{nom}</span> <span style="color:#46527a;font-size:0.88rem;">{desc}</span><br>',
        unsafe_allow_html=True,
    )

st.markdown("""
<br>
<div class="quote">
    Tout est codé from scratch en Python — pas de NetworkX pour les algos, juste les structures
    de données de base et une bonne dose de patience.
</div>
</div>
""", unsafe_allow_html=True)


# ── Compétences ───────────────────────────────────────────────────────────────

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Compétences mobilisées</div>', unsafe_allow_html=True)

skills = [
    ("Python", 88),
    ("Algorithmique & Graphes", 80),
    ("Visualisation (Plotly)", 72),
    ("Streamlit", 75),
    ("Git & Collaboration", 82),
]
for label, pct in skills:
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; color:#46527a; font-size:0.88rem; margin-top:0.5rem;">
        <span>{label}</span><span>{pct}%</span>
    </div>
    <div class="skill-bar-bg">
        <div class="skill-bar-fill" style="width:{pct}%;"></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ── Anecdote projet ───────────────────────────────────────────────────────────

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Anecdote</div>', unsafe_allow_html=True)
st.markdown("""
<div class="body-text">
Le bug le plus long à corriger ? La lecture du fichier <code>metro.txt</code>.
Le format est un peu capricieux — les noms de stations peuvent contenir des espaces et
le séparateur n'est pas toujours cohérent. J'ai passé plus de temps à parser ce fichier
qu'à implémenter Dijkstra lui-même. Morale : les données réelles, c'est rarement propre.
<br><br>
Le nom <em>Metro Efrei Dodo</em> ? C'est sorti à 2h du matin pendant une session de
débogage. Il est resté.
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ── Contact ───────────────────────────────────────────────────────────────────

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Contact</div>', unsafe_allow_html=True)
st.markdown("""
<div style="display:flex; flex-direction:column; gap:0.5rem;">
    <span style="color:#46527a; font-size:0.93rem;">
        École &nbsp;·&nbsp; <strong style="color:#0a1f44;">EFREI Paris</strong> — Villejuif
    </span>
    <span style="color:#46527a; font-size:0.93rem;">
        Promo &nbsp;·&nbsp; <strong style="color:#0a1f44;">MasterCamp 2025-2026</strong>
    </span>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── Démo fonctionnalités ──────────────────────────────────────────────────────

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Ce que l\'app fait concrètement</div>', unsafe_allow_html=True)

fonctionnalites = [
    ("Plus court chemin", "Dijkstra & A*", "Calcule le trajet optimal entre deux stations avec export PDF du résultat."),
    ("Arbre couvrant minimal", "Prim & Kruskal", "Trouve le sous-réseau minimal qui relie toutes les stations — utile pour optimiser l'infrastructure."),
    ("Heatmap des connexions", "Analyse de degré", "Visualise quelles stations sont les plus connectées — les hubs du réseau parisien."),
    ("Dijkstra animé", "Pédagogie", "Explication pas à pas de l'algorithme sur un exemple interactif avec slider."),
    ("Benchmark", "Performance", "Compare les temps d'exécution de chaque algo sur le réseau complet."),
]

for titre, tag, desc in fonctionnalites:
    st.markdown(f"""
    <div style="display:flex;align-items:flex-start;gap:0.8rem;margin-bottom:0.9rem;">
        <div style="flex-shrink:0;">
            <span class="algo-tag">{tag}</span>
        </div>
        <div>
            <div style="color:#0a1f44;font-weight:600;font-size:0.93rem;">{titre}</div>
            <div style="color:#46527a;font-size:0.87rem;margin-top:0.15rem;">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── Stack technique ───────────────────────────────────────────────────────────

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Stack technique</div>', unsafe_allow_html=True)
st.markdown("""
<div style="display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:0.8rem;">
    <span class="badge">Python 3.12</span>
    <span class="badge">Streamlit</span>
    <span class="badge">Plotly</span>
    <span class="badge">fpdf2</span>
    <span class="badge">NetworkX (benchmark)</span>
    <span class="badge">Git</span>
</div>
<div class="body-text" style="font-size:0.9rem;">
Les algorithmes principaux (Dijkstra, A*, Prim, Kruskal, BFS) sont codés
<strong style="color:#0a1f44">from scratch</strong> sans librairie externe —
pour comprendre ce qu'on fait, pas juste appeler une fonction noire.
NetworkX est uniquement utilisé dans le benchmark pour comparer les performances.
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div style="text-align:center; color:#8b95b4; font-size:0.78rem; margin-top:2rem; font-weight:600;">'
    'Metro Efrei Dodo · Mohammed El Karchal · EFREI Paris · 2026'
    '</div>',
    unsafe_allow_html=True
)
