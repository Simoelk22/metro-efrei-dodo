from fpdf import FPDF
import io
import datetime


class _PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(15, 15, 40)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "  Metro Efrei Dodo - Fiche de trajet", fill=True, ln=True)
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 160)
        self.cell(0, 8, f"Metro Efrei Dodo - Mohammed El Karchal - EFREI Paris 2026  |  Page {self.page_no()}", align="C")


def generer_pdf_trajet(graphe, chemin, duree_totale, depart_nom, arrivee_nom, algo="Dijkstra", t_calcul_ms=0.0, co2_data=None):
    """
    Génère un PDF du trajet calculé.

    Retourne les bytes du PDF (prêt pour st.download_button).
    """
    pdf = _PDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── Bloc résumé ──────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 60)
    pdf.cell(0, 8, f"Trajet calcule le {now}", ln=True)
    pdf.ln(2)

    # Trois métriques en ligne
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 90)

    mins = duree_totale // 60
    secs = duree_totale % 60

    def bloc_metrique(label, valeur, x, w=60):
        pdf.set_xy(x, pdf.get_y())
        pdf.set_fill_color(235, 237, 250)
        pdf.set_draw_color(180, 185, 220)
        pdf.rect(x, pdf.get_y(), w, 18, "DF")
        pdf.set_xy(x + 2, pdf.get_y() + 2)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(110, 110, 150)
        pdf.cell(w - 4, 4, label, ln=False)
        pdf.set_xy(x + 2, pdf.get_y() + 5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(25, 25, 80)
        pdf.cell(w - 4, 7, valeur, ln=False)

    y_metriques = pdf.get_y()
    bloc_metrique("DUREE DU TRAJET", f"{mins} min {secs} s", 14, 58)
    pdf.set_y(y_metriques)
    bloc_metrique("NOMBRE DE STATIONS", str(len(chemin)), 76, 58)
    pdf.set_y(y_metriques)
    bloc_metrique("ALGORITHME", algo, 138, 58)
    pdf.set_y(y_metriques + 20)

    pdf.ln(4)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(130, 130, 160)
    pdf.cell(0, 5, f"Temps de calcul : {t_calcul_ms:.2f} ms", ln=True)
    pdf.ln(4)

    # ── Impact environnemental (si fourni) ───────────────────────────────────
    if co2_data:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(0, 100, 60)
        pdf.cell(0, 7, "Impact environnemental", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(60, 60, 90)
        pdf.cell(0, 5,
                 f"Distance estimee : {co2_data['distance_km']:.1f} km  |  "
                 f"CO2 metro : {co2_data['co2_metro_g']:.1f} g  |  "
                 f"CO2 voiture : {co2_data['co2_voiture_g']:.0f} g  |  "
                 f"Economie : {co2_data['economie_g']:.0f} g (x{co2_data['ratio']:.0f})",
                 ln=True)
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_text_color(140, 140, 160)
        pdf.cell(0, 4, "Sources : ADEME 2023 - metro 4.1 gCO2eq/km, voiture 120 g/km", ln=True)
        pdf.ln(2)

    # ── Ligne de séparation ──────────────────────────────────────────────────
    pdf.set_draw_color(200, 200, 220)
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(5)

    # ── Détail station par station ───────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 60)
    pdf.cell(0, 7, "Detail du trajet", ln=True)
    pdf.ln(2)

    COULEURS_LIGNES = {
        "1": (255, 205, 0), "2": (0, 60, 166), "3": (131, 121, 2), "3b": (110, 196, 232),
        "4": (207, 0, 158), "5": (255, 126, 46), "6": (110, 202, 151), "7": (250, 154, 186),
        "7b": (110, 202, 151), "8": (225, 155, 223), "9": (182, 189, 0), "10": (201, 145, 13),
        "11": (112, 75, 28), "12": (0, 120, 82), "13": (110, 196, 232), "14": (98, 37, 157),
    }

    for i, sommet in enumerate(chemin):
        nom = graphe.noms[sommet].encode("latin-1", errors="replace").decode("latin-1")
        ligne = graphe.lignes[sommet]

        if i == 0:
            label = "Depart"
            pdf.set_fill_color(220, 240, 220)
        elif i == len(chemin) - 1:
            label = "Arrivee"
            pdf.set_fill_color(220, 220, 240)
        else:
            label = f"  {i}"
            pdf.set_fill_color(248, 248, 252)

        pdf.set_draw_color(210, 210, 230)
        pdf.set_text_color(40, 40, 70)
        pdf.set_font("Helvetica", "", 9)

        y0 = pdf.get_y()
        pdf.rect(14, y0, 182, 8, "DF")

        # Pastille couleur de ligne
        r, g, b = COULEURS_LIGNES.get(ligne, (150, 150, 150))
        pdf.set_fill_color(r, g, b)
        pdf.rect(14, y0, 10, 8, "F")

        # Numéro de ligne
        pdf.set_xy(14, y0 + 1)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(10, 6, ligne, align="C")

        # Label étape
        pdf.set_xy(26, y0 + 1)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120, 120, 160)
        pdf.cell(20, 6, label)

        # Nom station
        pdf.set_xy(48, y0 + 1)
        pdf.set_font("Helvetica", "B" if i in (0, len(chemin) - 1) else "", 9)
        pdf.set_text_color(25, 25, 60)
        pdf.cell(148, 6, nom)

        pdf.set_y(y0 + 9)

    pdf.ln(6)
    pdf.set_draw_color(200, 200, 220)
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 180)
    depart_safe = depart_nom.encode("latin-1", errors="replace").decode("latin-1")
    arrivee_safe = arrivee_nom.encode("latin-1", errors="replace").decode("latin-1")
    pdf.cell(0, 5, f"De : {depart_safe}   ->   Vers : {arrivee_safe}", ln=True)

    # Retourner les bytes
    return bytes(pdf.output())
