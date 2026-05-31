import streamlit as st
import os

st.set_page_config(
    page_title="À propos — Metro Efrei Dodo",
    page_icon="M",
    layout="centered",
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Fond global dégradé discret */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e8e8f0;
    }

    /* Carte principale */
    .card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 18px;
        padding: 2.2rem 2.6rem;
        margin-bottom: 1.6rem;
        backdrop-filter: blur(8px);
    }

    /* Photo de profil */
    .profile-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .profile-img {
        width: 148px;
        height: 148px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #5c6bc0;
        box-shadow: 0 0 28px rgba(92,107,192,0.45);
    }
    .profile-placeholder {
        width: 148px;
        height: 148px;
        border-radius: 50%;
        background: linear-gradient(135deg, #5c6bc0, #7986cb);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3.2rem;
        border: 3px solid #5c6bc0;
        box-shadow: 0 0 28px rgba(92,107,192,0.45);
    }
    .nom {
        font-size: 1.9rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.5px;
        text-align: center;
    }
    .badge {
        display: inline-block;
        background: rgba(92,107,192,0.22);
        border: 1px solid #5c6bc0;
        color: #9fa8da;
        border-radius: 20px;
        padding: 0.25rem 0.9rem;
        font-size: 0.85rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    .section-title {
        color: #9fa8da;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
        border-bottom: 1px solid rgba(159,168,218,0.18);
        padding-bottom: 0.4rem;
    }
    .body-text {
        color: #c8cce8;
        font-size: 0.97rem;
        line-height: 1.75;
    }
    .skill-bar-bg {
        background: rgba(255,255,255,0.07);
        border-radius: 6px;
        height: 7px;
        margin-top: 4px;
        margin-bottom: 10px;
    }
    .skill-bar-fill {
        height: 7px;
        border-radius: 6px;
        background: linear-gradient(90deg, #5c6bc0, #9c27b0);
    }
    .contact-link {
        color: #9fa8da;
        text-decoration: none;
        font-size: 0.93rem;
    }
    .contact-link:hover { color: #ffffff; }
    .algo-tag {
        display: inline-block;
        background: rgba(156,39,176,0.18);
        border: 1px solid rgba(156,39,176,0.4);
        color: #ce93d8;
        border-radius: 8px;
        padding: 0.2rem 0.7rem;
        font-size: 0.82rem;
        margin: 0.2rem 0.1rem;
    }
    .quote {
        border-left: 3px solid #5c6bc0;
        padding: 0.5rem 1.1rem;
        color: #a0a4c8;
        font-style: italic;
        font-size: 0.95rem;
        margin: 0.8rem 0;
    }
</style>
""", unsafe_allow_html=True)


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
Bonjour, je m'appelle <strong style="color:#ffffff;">Mohammed El Karchal</strong>.
Je suis étudiant à l'<strong style="color:#ffffff;">EFREI Paris</strong>, école d'ingénieurs
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
L'application modélise le réseau du métro parisien sous forme de <strong style="color:#ffffff;">graphe pondéré</strong>
(les poids = temps de trajet en secondes). À partir de là, trois grandes fonctionnalités :
</div>
<br>
""", unsafe_allow_html=True)

cols_algos = [
    ("Dijkstra", "Plus court chemin entre deux stations — O((S + A) log S)"),
    ("Prim", "Arbre couvrant de poids minimal — O(A log S)"),
    ("Kruskal", "Même résultat, autre approche — O(A log A)"),
    ("BFS", "Vérification de la connexité du réseau"),
]
for nom, desc in cols_algos:
    st.markdown(
        f'<span class="algo-tag">{nom}</span> <span style="color:#9da0c0;font-size:0.88rem;">{desc}</span><br>',
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
    <div style="display:flex; justify-content:space-between; color:#c0c4e0; font-size:0.88rem; margin-top:0.5rem;">
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
    <span style="color:#c0c4e0; font-size:0.93rem;">
        École &nbsp;·&nbsp; <strong style="color:#ffffff;">EFREI Paris</strong> — Villejuif
    </span>
    <span style="color:#c0c4e0; font-size:0.93rem;">
        Promo &nbsp;·&nbsp; <strong style="color:#ffffff;">MasterCamp 2025-2026</strong>
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
            <div style="color:#ffffff;font-weight:600;font-size:0.93rem;">{titre}</div>
            <div style="color:#9da0c0;font-size:0.87rem;margin-top:0.15rem;">{desc}</div>
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
<strong style="color:#fff">from scratch</strong> sans librairie externe —
pour comprendre ce qu'on fait, pas juste appeler une fonction noire.
NetworkX est uniquement utilisé dans le benchmark pour comparer les performances.
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div style="text-align:center; color:rgba(150,150,180,0.45); font-size:0.78rem; margin-top:2rem;">'
    'Metro Efrei Dodo · Mohammed El Karchal · EFREI Paris · 2026'
    '</div>',
    unsafe_allow_html=True
)
