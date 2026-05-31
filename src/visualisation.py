import plotly.graph_objects as go


def _positions_par_num(graphe, positions_noms):
    """
    Construit {num_sommet: (x, y)} en faisant correspondre
    g.noms[num] avec les clés du dict positions_noms.
    Les noms dans pospoints peuvent avoir des variantes — on fait
    un matching exact puis approximatif (startswith).
    """
    pos = {}
    noms_pos = {k.lower(): v for k, v in positions_noms.items()}

    for num, nom in graphe.noms.items():
        cle = nom.lower()
        if cle in noms_pos:
            pos[num] = noms_pos[cle]
        else:
            # matching partiel : on prend le premier qui commence pareil
            for k, v in noms_pos.items():
                if k.startswith(cle[:6]) or cle.startswith(k[:6]):
                    pos[num] = v
                    break

    return pos


COULEURS_LIGNES = {
    "1": "#FFCD00", "2": "#003CA6", "3": "#837902", "3b": "#6EC4E8",
    "4": "#CF009E", "5": "#FF7E2E", "6": "#6ECA97", "7": "#FA9ABA",
    "7b": "#6ECA97", "8": "#E19BDF", "9": "#B6BD00", "10": "#C9910D",
    "11": "#704B1C", "12": "#007852", "13": "#6EC4E8", "14": "#62259D",
}


def tracer_reseau(graphe, positions_noms, chemin=None, acpm_aretes=None):
    """
    Retourne une figure Plotly du réseau de métro.
    - chemin : liste de num_sommets (plus court chemin à surligner)
    - acpm_aretes : liste de (u, v, poids) (ACPM à afficher)
    """
    pos = _positions_par_num(graphe, positions_noms)

    fig = go.Figure()

    # ── Arêtes du réseau ──────────────────────────────────────────────────────
    for u in graphe.adjacence:
        for v, _ in graphe.adjacence[u]:
            if u < v and u in pos and v in pos:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                fig.add_trace(go.Scatter(
                    x=[x0, x1, None], y=[-y0, -y1, None],
                    mode="lines",
                    line=dict(color="#cccccc", width=1),
                    hoverinfo="none",
                    showlegend=False,
                ))

    # ── ACPM (si demandé) ─────────────────────────────────────────────────────
    if acpm_aretes:
        for u, v, _ in acpm_aretes:
            if u in pos and v in pos:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                fig.add_trace(go.Scatter(
                    x=[x0, x1, None], y=[-y0, -y1, None],
                    mode="lines",
                    line=dict(color="#00cc44", width=3),
                    hoverinfo="none",
                    showlegend=False,
                ))

    # ── Plus court chemin (si demandé) ────────────────────────────────────────
    if chemin and len(chemin) > 1:
        cx = [pos[s][0] for s in chemin if s in pos]
        cy = [-pos[s][1] for s in chemin if s in pos]
        fig.add_trace(go.Scatter(
            x=cx, y=cy,
            mode="lines+markers",
            line=dict(color="#FF3333", width=4),
            marker=dict(size=8, color="#FF3333"),
            hoverinfo="none",
            showlegend=False,
        ))

    # ── Sommets ───────────────────────────────────────────────────────────────
    sx, sy, textes, couleurs = [], [], [], []
    for num in graphe.sommets:
        if num in pos:
            x, y = pos[num]
            sx.append(x)
            sy.append(-y)
            textes.append(graphe.noms[num])
            couleurs.append(COULEURS_LIGNES.get(graphe.lignes[num], "#888888"))

    fig.add_trace(go.Scatter(
        x=sx, y=sy,
        mode="markers",
        marker=dict(size=6, color=couleurs, line=dict(width=0.5, color="white")),
        text=textes,
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white",
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
    )

    return fig


def tracer_heatmap(graphe, positions_noms):
    """
    Heatmap des stations : taille et couleur proportionnelles au degré (nombre de connexions).
    """
    pos = _positions_par_num(graphe, positions_noms)

    # Calcul du degré de chaque station
    degres = {num: len(graphe.adjacence[num]) for num in graphe.sommets}
    max_degre = max(degres.values()) if degres else 1

    sx, sy, textes, tailles, couleurs, infos = [], [], [], [], [], []
    for num in graphe.sommets:
        if num not in pos:
            continue
        x, y = pos[num]
        d = degres[num]
        sx.append(x)
        sy.append(-y)
        textes.append(graphe.noms[num])
        tailles.append(6 + d * 4)
        couleurs.append(d)
        infos.append(f"{graphe.noms[num]}<br>Ligne {graphe.lignes[num]}<br>{d} connexion(s)")

    fig = go.Figure()

    # Arêtes en fond, très discrètes
    for u in graphe.adjacence:
        for v, _ in graphe.adjacence[u]:
            if u < v and u in pos and v in pos:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                fig.add_trace(go.Scatter(
                    x=[x0, x1, None], y=[-y0, -y1, None],
                    mode="lines",
                    line=dict(color="rgba(150,150,180,0.15)", width=1),
                    hoverinfo="none",
                    showlegend=False,
                ))

    # Noeuds avec heatmap
    fig.add_trace(go.Scatter(
        x=sx, y=sy,
        mode="markers",
        marker=dict(
            size=tailles,
            color=couleurs,
            colorscale="Plasma",
            showscale=True,
            colorbar=dict(
                title=dict(text="Connexions", side="right"),
                tickfont=dict(size=11),
            ),
            line=dict(width=0.5, color="white"),
        ),
        text=infos,
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#f8f8fc",
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
    )

    return fig, degres
