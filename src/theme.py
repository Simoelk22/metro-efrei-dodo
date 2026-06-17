"""
Système de design centralisé — Metro Efrei Dodo
================================================

Direction artistique : « Signalétique RATP, claire & futuriste ».

  * Fond clair (blanc cassé), surfaces blanches type panneau d'information.
  * Bleu IDFM (navigation) comme couleur primaire, accent bleu électrique
    futuriste, vert RATP pour l'écologie.
  * Pastilles de lignes aux couleurs officielles du métro parisien.
  * Typographie nette (Inter + Hanken Grotesk), proche de la Parisine.
  * Détails futuristes : bandeau multicolore animé, glassmorphism léger,
    halos doux, coins arrondis, ombres portées subtiles.

Toutes les pages importent ce module et appellent ``inject_theme()`` une
fois en haut de page. Les figures Plotly passent par ``style_plotly()``.
"""

from __future__ import annotations

import base64
import os
from typing import Iterable, Sequence


# ════════════════════════════════════════════════════════════════════════════
#  PALETTE
# ════════════════════════════════════════════════════════════════════════════

COLORS = {
    # Fonds & surfaces
    "bg":          "#eaeef6",   # fond application (blanc bleuté froid)
    "bg_soft":     "#f4f7fc",
    "surface":     "#ffffff",   # cartes / panneaux
    "surface_2":   "#f6f8fd",
    "line":        "#e2e8f3",   # bordures
    "line_strong": "#cfd8ea",

    # Encre / textes
    "ink":         "#0a1f44",   # texte principal (navy profond)
    "ink_2":       "#46527a",   # texte secondaire
    "ink_3":       "#8b95b4",   # texte discret / muted

    # Couleurs de marque
    "navy":        "#003688",   # bleu IDFM (primaire signalétique)
    "blue":        "#1d6cf2",   # bleu électrique (accent futuriste)
    "sky":         "#39b6ff",
    "cyan":        "#00c2d6",
    "green":       "#00935f",   # vert RATP (écologie)
    "green_soft":  "#10b981",
    "amber":       "#f59e0b",
    "red":         "#e4002b",   # rouge RATP
    "magenta":     "#c2185b",
    "violet":      "#62259d",   # ligne 14
}

# Couleurs officielles des lignes du métro parisien (RATP)
LINE_COLORS = {
    "1":  "#FFCD00", "2":  "#003CA6", "3":  "#837902", "3b": "#6EC4E8",
    "4":  "#CF009E", "5":  "#FF7E2E", "6":  "#6ECA97", "7":  "#FA9ABA",
    "7b": "#6ECA97", "8":  "#E19BDF", "9":  "#B6BD00", "10": "#C9910D",
    "11": "#704B1C", "12": "#007852", "13": "#6EC4E8", "14": "#62259D",
}

# Dégradé multicolore (bandeau signalétique) construit depuis les lignes.
_STRIP_STOPS = ["#FFCD00", "#003CA6", "#CF009E", "#FF7E2E",
                "#6ECA97", "#62259D", "#007852", "#1d6cf2"]


# ════════════════════════════════════════════════════════════════════════════
#  CSS GLOBAL
# ════════════════════════════════════════════════════════════════════════════

def _css() -> str:
    c = COLORS
    strip = ", ".join(_STRIP_STOPS + [_STRIP_STOPS[0]])
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Hanken+Grotesk:wght@600;700;800;900&display=swap');

/* ── Base ─────────────────────────────────────────────────────────────── */
:root {{
    --med-bg: {c['bg']};
    --med-surface: {c['surface']};
    --med-line: {c['line']};
    --med-ink: {c['ink']};
    --med-ink2: {c['ink_2']};
    --med-ink3: {c['ink_3']};
    --med-navy: {c['navy']};
    --med-blue: {c['blue']};
    --med-green: {c['green']};
    --med-red: {c['red']};
}}

html, body, [class*="css"], .stApp, .stMarkdown, p, span, div, label {{
    font-family: 'Inter', -apple-system, 'Segoe UI', system-ui, sans-serif;
}}

.stApp {{
    background:
        radial-gradient(1200px 600px at 12% -8%, #ffffff 0%, rgba(255,255,255,0) 55%),
        radial-gradient(900px 500px at 100% 0%, #e7f0ff 0%, rgba(231,240,255,0) 50%),
        {c['bg']};
    color: {c['ink']};
}}

/* Trame de points discrète (cue "plan futuriste") */
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image: radial-gradient(rgba(0,54,136,0.05) 1px, transparent 1px);
    background-size: 26px 26px;
    z-index: 0;
    mask-image: linear-gradient(180deg, rgba(0,0,0,0.5), rgba(0,0,0,0) 70%);
}}
.block-container {{ position: relative; z-index: 1; padding-top: 2.2rem; }}

/* Titres */
h1, h2, h3, h4 {{
    font-family: 'Hanken Grotesk', 'Inter', sans-serif !important;
    color: {c['ink']};
    letter-spacing: -0.4px;
}}
h1 {{ font-weight: 900; }}
h2, h3 {{ font-weight: 800; }}

a {{ color: {c['blue']}; }}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #ffffff 0%, #f3f6fc 100%);
    border-right: 1px solid {c['line']};
}}
[data-testid="stSidebar"] * {{ color: {c['ink_2']}; }}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{ color: {c['ink']} !important; }}
[data-testid="stSidebarNav"] {{ padding-top: 0.4rem; }}
[data-testid="stSidebarNav"] a {{
    border-radius: 10px;
    margin: 2px 6px;
}}
[data-testid="stSidebarNav"] a:hover {{ background: rgba(29,108,242,0.08); }}

/* ── Boutons ──────────────────────────────────────────────────────────── */
.stButton > button {{
    background: {c['surface']};
    color: {c['navy']};
    border: 1px solid {c['line_strong']};
    border-radius: 12px;
    font-weight: 700;
    padding: 0.5rem 1.1rem;
    transition: all 0.18s ease;
    box-shadow: 0 1px 2px rgba(10,31,68,0.04);
}}
.stButton > button:hover {{
    border-color: {c['blue']};
    color: {c['blue']};
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(29,108,242,0.16);
}}
/* Bouton primaire = bandeau navigation */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, {c['blue']} 0%, {c['navy']} 100%);
    color: #ffffff;
    border: none;
    box-shadow: 0 8px 22px rgba(0,54,136,0.28);
}}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {{
    color: #fff;
    filter: brightness(1.06);
    transform: translateY(-1px);
    box-shadow: 0 12px 28px rgba(0,54,136,0.34);
}}
.stDownloadButton > button {{
    background: linear-gradient(135deg, {c['green_soft']} 0%, {c['green']} 100%);
    color: #fff; border: none; border-radius: 12px; font-weight: 700;
    box-shadow: 0 8px 22px rgba(0,147,95,0.25);
}}
.stDownloadButton > button:hover {{ filter: brightness(1.06); transform: translateY(-1px); }}

/* ── Métriques ────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {{
    background: {c['surface']};
    border: 1px solid {c['line']};
    border-radius: 16px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 8px 24px rgba(16,38,76,0.06);
    position: relative;
    overflow: hidden;
}}
[data-testid="stMetric"]::before {{
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: linear-gradient(180deg, {c['blue']}, {c['navy']});
}}
[data-testid="stMetricLabel"] {{ color: {c['ink_3']} !important; font-weight: 600; }}
[data-testid="stMetricValue"] {{
    color: {c['ink']} !important;
    font-family: 'Hanken Grotesk', sans-serif !important;
    font-weight: 800;
}}
[data-testid="stMetricDelta"] {{ font-weight: 700; }}

/* ── Onglets (pills) ──────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {c['surface']};
    border: 1px solid {c['line']};
    border-radius: 14px;
    gap: 4px;
    padding: 5px;
    box-shadow: 0 6px 18px rgba(16,38,76,0.05);
}}
.stTabs [data-baseweb="tab"] {{
    color: {c['ink_2']};
    border-radius: 10px;
    font-weight: 700;
    padding: 6px 14px;
}}
.stTabs [data-baseweb="tab"]:hover {{ background: rgba(29,108,242,0.07); }}
.stTabs [aria-selected="true"] {{
    color: #ffffff !important;
    background: linear-gradient(135deg, {c['blue']}, {c['navy']}) !important;
    box-shadow: 0 6px 16px rgba(0,54,136,0.25);
}}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{ background: transparent !important; }}

/* ── Inputs ───────────────────────────────────────────────────────────── */
.stSelectbox > div > div, .stTextInput > div > div, .stNumberInput > div > div {{
    background: {c['surface']};
    border-radius: 11px;
    border: 1px solid {c['line_strong']};
    color: {c['ink']};
}}
.stSelectbox > div > div:focus-within {{
    border-color: {c['blue']};
    box-shadow: 0 0 0 3px rgba(29,108,242,0.14);
}}
.stRadio label, .stCheckbox label {{ color: {c['ink_2']}; }}
.stRadio [role="radiogroup"] {{ gap: 4px; }}

/* Slider en bleu navigation */
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background: {c['blue']};
    box-shadow: 0 0 0 4px rgba(29,108,242,0.18);
}}

/* ── Expander / alerts / dataframe ────────────────────────────────────── */
.stExpander {{
    border: 1px solid {c['line']} !important;
    border-radius: 14px !important;
    background: {c['surface']};
    box-shadow: 0 6px 18px rgba(16,38,76,0.05);
}}
.stExpander summary {{ color: {c['ink']}; font-weight: 700; }}
[data-testid="stAlert"] {{ border-radius: 12px; }}
[data-testid="stDataFrame"] {{
    border: 1px solid {c['line']};
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 6px 18px rgba(16,38,76,0.05);
}}
hr {{ border-color: {c['line']}; }}
.stCaption, [data-testid="stCaptionContainer"] {{ color: {c['ink_3']}; }}

/* ════════════════════════════════════════════════════════════════════════
   COMPOSANTS PARTAGÉS (classes utilisées dans toutes les pages)
   ════════════════════════════════════════════════════════════════════════ */

/* Carte / panneau */
.card {{
    background: {c['surface']};
    border: 1px solid {c['line']};
    border-radius: 18px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 10px 30px rgba(16,38,76,0.06);
}}
.card:hover {{ border-color: {c['line_strong']}; }}

/* Étiquette de section (sur-titre) */
.section-title, .section-label {{
    color: {c['navy']};
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}}
.section-title {{
    border-bottom: 1px solid {c['line']};
    padding-bottom: 0.5rem;
}}

/* Texte de corps */
.body-text {{ color: {c['ink_2']}; font-size: 0.97rem; line-height: 1.75; }}
.body-text strong, .card strong {{ color: {c['ink']}; }}

/* Pastille / chip */
.chip {{
    display: inline-block;
    background: rgba(29,108,242,0.08);
    border: 1px solid rgba(29,108,242,0.28);
    color: {c['navy']};
    border-radius: 20px;
    padding: 0.22rem 0.8rem;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 0.15rem;
}}
.badge {{
    display: inline-block;
    background: rgba(0,54,136,0.07);
    border: 1px solid rgba(0,54,136,0.22);
    color: {c['navy']};
    border-radius: 20px;
    padding: 0.25rem 0.85rem;
    font-size: 0.83rem;
    font-weight: 600;
    margin: 0.2rem;
}}

/* Boîte d'étape (liste numérotée illustrée) */
.step-box {{
    background: {c['surface_2']};
    border-left: 3px solid {c['blue']};
    border-radius: 0 10px 10px 0;
    padding: 0.6rem 1rem;
    margin: 0.4rem 0;
    color: {c['ink_2']};
    font-size: 0.92rem;
}}

/* Checklist (guide démo) */
.check-item {{
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    padding: 0.6rem 0.85rem;
    border-radius: 12px;
    margin-bottom: 0.5rem;
    background: {c['surface_2']};
    border-left: 3px solid {c['blue']};
    color: {c['ink_2']};
}}

/* Code / complexité */
.complexity {{
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    background: rgba(0,54,136,0.07);
    border: 1px solid rgba(0,54,136,0.14);
    border-radius: 6px;
    padding: 0.12rem 0.5rem;
    color: {c['navy']};
    font-size: 0.86rem;
}}
.card code, .body-text code {{
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    background: rgba(0,54,136,0.07);
    border-radius: 5px;
    padding: 0.08rem 0.36rem;
    color: {c['navy']};
    font-size: 0.86em;
}}
.card pre {{
    background: {c['ink']} !important;
    color: #d7e3ff !important;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.06);
}}

/* Tag d'algorithme */
.algo-tag {{
    display: inline-block;
    background: rgba(29,108,242,0.10);
    border: 1px solid rgba(29,108,242,0.30);
    color: {c['blue']};
    border-radius: 9px;
    padding: 0.2rem 0.7rem;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 0.2rem 0.1rem;
}}

/* Citation */
.quote {{
    border-left: 3px solid {c['blue']};
    background: {c['surface_2']};
    border-radius: 0 10px 10px 0;
    padding: 0.7rem 1.1rem;
    color: {c['ink_2']};
    font-style: italic;
    font-size: 0.95rem;
    margin: 0.8rem 0;
}}

/* Accents texte */
.highlight {{ color: {c['amber']}; font-weight: 700; }}
.green {{ color: {c['green']}; font-weight: 700; }}
.red {{ color: {c['red']}; font-weight: 700; }}

/* Barres de compétence */
.skill-bar-bg {{
    background: {c['line']};
    border-radius: 6px;
    height: 8px;
    margin: 4px 0 12px;
    overflow: hidden;
}}
.skill-bar-fill {{
    height: 8px;
    border-radius: 6px;
    background: linear-gradient(90deg, {c['blue']}, {c['navy']});
}}

/* Profil (page À propos) */
.profile-wrapper {{
    display: flex; flex-direction: column; align-items: center;
    gap: 0.8rem; margin-bottom: 1.8rem;
}}
.profile-img, .profile-placeholder {{
    width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover;
    border: 4px solid #ffffff;
    box-shadow: 0 0 0 3px {c['blue']}, 0 14px 30px rgba(0,54,136,0.25);
}}
.profile-placeholder {{
    display: flex; align-items: center; justify-content: center;
    font-size: 3.2rem; color: #fff; font-weight: 800;
    background: linear-gradient(135deg, {c['blue']}, {c['navy']});
}}
.nom {{
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 1.95rem; font-weight: 900; color: {c['ink']};
    letter-spacing: -0.5px; text-align: center;
}}
.contact-link {{ color: {c['blue']}; text-decoration: none; font-size: 0.93rem; }}
.contact-link:hover {{ color: {c['navy']}; }}

/* ── Bandeau hero signalétique ────────────────────────────────────────── */
.med-hero {{
    position: relative;
    background:
        linear-gradient(135deg, #ffffff 0%, #eaf1ff 55%, #dfeaff 100%);
    border: 1px solid {c['line']};
    border-radius: 22px;
    padding: 0;
    margin-bottom: 1.6rem;
    overflow: hidden;
    box-shadow: 0 18px 44px rgba(0,54,136,0.12);
}}
.med-strip {{
    height: 6px;
    width: 100%;
    background: linear-gradient(90deg, {strip});
    background-size: 220% 100%;
    animation: med-strip-move 9s linear infinite;
}}
@keyframes med-strip-move {{
    0% {{ background-position: 0% 50%; }}
    100% {{ background-position: 220% 50%; }}
}}
.med-hero-inner {{
    display: flex; align-items: center; justify-content: space-between;
    gap: 1.6rem; padding: 1.7rem 2.1rem;
}}
.med-hero-emblem {{
    width: 54px; height: 54px; border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Hanken Grotesk', sans-serif; font-weight: 900;
    font-size: 1.6rem; color: #fff;
    background: linear-gradient(135deg, {c['blue']}, {c['navy']});
    box-shadow: 0 10px 24px rgba(0,54,136,0.35);
    flex-shrink: 0;
}}
.med-hero-title {{
    margin: 0; font-family: 'Hanken Grotesk', sans-serif;
    font-size: 2rem; font-weight: 900; color: {c['ink']};
    letter-spacing: -0.6px; line-height: 1.05;
}}
.med-hero-sub {{ margin: 0.35rem 0 0; color: {c['ink_2']}; font-size: 1rem; font-weight: 600; }}
.med-hero-kicker {{
    margin: 0.5rem 0 0; color: {c['navy']};
    font-size: 0.74rem; font-weight: 800; letter-spacing: 1.6px;
    text-transform: uppercase;
}}
.med-stats {{ display: flex; gap: 0.9rem; flex-wrap: wrap; margin-top: 1.1rem; }}
.med-stat {{
    background: rgba(255,255,255,0.75);
    border: 1px solid {c['line']};
    border-radius: 14px;
    padding: 0.55rem 1rem;
    text-align: center;
    min-width: 92px;
    backdrop-filter: blur(6px);
    box-shadow: 0 6px 16px rgba(16,38,76,0.06);
}}
.med-stat .v {{
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 1.4rem; font-weight: 900; color: {c['navy']}; line-height: 1;
}}
.med-stat.eco .v {{ color: {c['green']}; }}
.med-stat .l {{
    font-size: 0.66rem; color: {c['ink_3']};
    text-transform: uppercase; letter-spacing: 1px; margin-top: 0.25rem;
    font-weight: 700;
}}
.med-hero-map {{
    width: 188px; height: 188px; object-fit: cover;
    border-radius: 16px; flex-shrink: 0;
    border: 1px solid {c['line_strong']};
    box-shadow: 0 12px 28px rgba(16,38,76,0.16);
}}
.med-footer {{
    text-align: center; color: {c['ink_3']};
    font-size: 0.78rem; margin-top: 2rem; font-weight: 600;
    letter-spacing: 0.3px;
}}

@media (max-width: 880px) {{
    .med-hero-inner {{ flex-direction: column; align-items: flex-start; }}
    .med-hero-map {{ display: none; }}
}}
</style>
"""


def inject_theme() -> None:
    """Injecte la feuille de style globale. À appeler en haut de chaque page."""
    import streamlit as st
    st.markdown(_css(), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  HERO
# ════════════════════════════════════════════════════════════════════════════

def render_hero(
    title: str,
    subtitle: str = "",
    kicker: str = "",
    stats: Sequence[tuple] = (),
    map_b64: str | None = None,
    emblem: str = "M",
) -> None:
    """
    Affiche le bandeau d'en-tête signalétique.

    stats : suite de tuples (valeur, libellé) ou (valeur, libellé, "eco").
    """
    import streamlit as st

    stats_html = ""
    if stats:
        cells = []
        for s in stats:
            val, lab = s[0], s[1]
            cls = "med-stat eco" if (len(s) > 2 and s[2] == "eco") else "med-stat"
            cells.append(
                f'<div class="{cls}"><div class="v">{val}</div>'
                f'<div class="l">{lab}</div></div>'
            )
        stats_html = f'<div class="med-stats">{"".join(cells)}</div>'

    map_html = ""
    if map_b64:
        map_html = (
            f'<img class="med-hero-map" '
            f'src="data:image/png;base64,{map_b64}" alt="Plan du métro"/>'
        )

    sub_html = f'<p class="med-hero-sub">{subtitle}</p>' if subtitle else ""
    kicker_html = f'<p class="med-hero-kicker">{kicker}</p>' if kicker else ""

    # HTML compact, SANS ligne vide : les lignes vides à l'intérieur d'un bloc
    # HTML cassent le rendu Markdown de Streamlit (les </div> s'affichent en
    # texte). On assemble donc tout sur une seule ligne logique.
    html = (
        '<div class="med-hero">'
        '<div class="med-strip"></div>'
        '<div class="med-hero-inner">'
        '<div style="flex:1;">'
        '<div style="display:flex;align-items:center;gap:0.9rem;">'
        f'<div class="med-hero-emblem">{emblem}</div>'
        f'<div><h1 class="med-hero-title">{title}</h1>{sub_html}</div>'
        '</div>'
        f'{kicker_html}{stats_html}'
        '</div>'
        f'{map_html}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_footer() -> None:
    import streamlit as st
    st.markdown(
        '<div class="med-footer">Metro Efrei Dodo · Mohammed El Karchal · '
        'EFREI Paris · MasterCamp 2025-2026</div>',
        unsafe_allow_html=True,
    )


def load_image_b64(path: str) -> str:
    """Charge une image locale en base64, renvoie "" si absente."""
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ════════════════════════════════════════════════════════════════════════════
#  PLOTLY
# ════════════════════════════════════════════════════════════════════════════

# Couleurs prêtes à l'emploi pour les figures
PLOT = {
    "paper":   "rgba(0,0,0,0)",
    "plot":    "#ffffff",
    "grid":    "rgba(10,31,68,0.06)",
    "ink":     COLORS["ink"],
    "ink2":    COLORS["ink_2"],
    "edge":    "rgba(120,134,170,0.45)",   # arêtes du réseau
    "primary": COLORS["blue"],
    "navy":    COLORS["navy"],
    "path":    COLORS["red"],              # plus court chemin
    "acpm":    COLORS["green"],            # arbre couvrant
    "accent":  COLORS["amber"],
}


def style_plotly(fig, *, height: int | None = None, legend: bool = False):
    """Applique le thème clair commun à une figure Plotly."""
    fig.update_layout(
        paper_bgcolor=PLOT["paper"],
        plot_bgcolor=PLOT["plot"],
        font=dict(color=PLOT["ink"], family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=30, b=30),
    )
    if height:
        fig.update_layout(height=height)
    if legend:
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1, font=dict(color=PLOT["ink2"])),
        )
    fig.update_xaxes(gridcolor=PLOT["grid"], zerolinecolor=PLOT["grid"])
    fig.update_yaxes(gridcolor=PLOT["grid"], zerolinecolor=PLOT["grid"])
    return fig
