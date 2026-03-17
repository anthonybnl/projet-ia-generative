import pandas as pd
import plotly.graph_objects as go
import streamlit as st

MEDALS = ["🥇", "🥈", "🥉"]
COLORS = ["#F5A623", "#9B9B9B", "#C87941"]
CARD_BG = ["#fffdf0", "#f6f6f6", "#fdf6ef"]
GAUGE_COLORS = ["#F5A623", "#9B9B9B", "#C87941"]

SEUIL_ACQUIS = 0.40
SEUIL_PARTIEL = 0.10


def chart_top_metiers(metiers: list[dict]):
    """Bar chart horizontal des top 5 métiers"""
    sorted_metiers = sorted(metiers, key=lambda x: x["score"], reverse=True)[:5]
    labels = [m["metier"] for m in reversed(sorted_metiers)]
    scores = [m["score"] for m in reversed(sorted_metiers)]

    score_min = min(scores)
    score_max = max(scores)
    margin = (score_max - score_min) * 0.15 or 0.005

    fig = go.Figure(
        go.Bar(
            x=scores,
            y=labels,
            orientation="h",
            marker=dict(
                color=scores,
                colorscale="RdYlGn",
                cmin=score_min - margin,
                cmax=score_max + margin,
                showscale=True,
                colorbar=dict(title="Score", tickformat=".3f"),
            ),
            text=[f"{s:.4f}" for s in scores],
            textposition="outside",
            cliponaxis=False,
        )
    )
    fig.update_layout(
        title=dict(text="Top métiers recommandés", font=dict(size=18)),
        xaxis=dict(
            title="Score de similarité",
            range=[score_min - margin, score_max + margin * 4],
            tickformat=".3f",
        ),
        yaxis=dict(tickfont=dict(size=12)),
        height=480,
        margin=dict(l=20, r=20, t=60, b=40),
        plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eeeeee")
    st.plotly_chart(fig, use_container_width=True)


def _card_header(
    nom: str,
    description: str,
    medal: str,
    color: str,
    bg: str,
    score_global: float,
    gauge_color: str,
    rank: int,
):
    """Ligne 1 : card HTML (titre + description) + jauge score global."""
    col_card, col_gauge = st.columns([3, 2])

    with col_card:
        st.markdown(
            f"""
            <div style="
                background:{bg};
                border-left: 6px solid {color};
                border-radius: 12px;
                padding: 18px 20px;
                box-shadow: 0 3px 12px rgba(0,0,0,0.08);
                height: 100%;
            ">
                <h3 style="margin:0 0 6px 0; font-size:1.2rem;">{medal} {nom}</h3>
                <p style="font-size:0.83rem; color:#555; line-height:1.5; margin:0;">
                    {description[:320]}{"…" if len(description) > 320 else ""}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_gauge:
        gauge_max = 1.0
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=score_global,
                number=dict(valueformat=".4f", font=dict(size=22, color=gauge_color)),
                gauge=dict(
                    axis=dict(
                        range=[0, gauge_max],
                        tickformat=".2f",
                        tickfont=dict(size=9),
                    ),
                    bar=dict(color=gauge_color, thickness=0.35),
                    bgcolor="white",
                    borderwidth=1,
                    bordercolor="#cccccc",
                    steps=[
                        dict(range=[0, gauge_max * 0.33], color="#fdecea"),
                        dict(
                            range=[gauge_max * 0.33, gauge_max * 0.66], color="#fff8e1"
                        ),
                        dict(range=[gauge_max * 0.66, gauge_max], color="#e8f5e9"),
                    ],
                    threshold=dict(
                        line=dict(color=gauge_color, width=3),
                        thickness=0.8,
                        value=score_global,
                    ),
                ),
                title=dict(text="Score global", font=dict(size=13)),
            )
        )
        fig_gauge.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{rank}")


def _card_radars(
    score_par_bloc: dict,
    competences: list,
    color: str,
    rank: int,
):
    """Ligne 2 : radar blocs de compétences + radar compétences individuelles."""
    col_blocs, col_comp = st.columns(2)

    with col_blocs:
        if score_par_bloc:
            blocs = list(score_par_bloc.keys())
            vals_blocs = list(score_par_bloc.values())
            val_max_bloc = max(vals_blocs) if max(vals_blocs) > 0 else 1

            r1, r2, r3 = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            fill_color = f"rgba({r1},{r2},{r3},0.25)"

            fig_blocs = go.Figure()
            fig_blocs.add_trace(
                go.Scatterpolar(
                    r=vals_blocs + [vals_blocs[0]],
                    theta=blocs + [blocs[0]],
                    fill="toself",
                    fillcolor=fill_color,
                    line=dict(color=color, width=2.5),
                    marker=dict(size=7, color=color),
                    hovertemplate="<b>%{theta}</b><br>Score : %{r:.4f}<extra></extra>",
                )
            )
            fig_blocs.update_layout(
                title=dict(
                    text="Maîtrise par bloc de compétences", font=dict(size=13), x=0.5
                ),
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, val_max_bloc * 1.25],
                        tickformat=".3f",
                        tickfont=dict(size=8, color="black"),
                        gridcolor="#dddddd",
                        linecolor="#dddddd",
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=10, color="black"), linecolor="#cccccc"
                    ),
                    bgcolor="rgba(250,250,250,1)",
                ),
                showlegend=False,
                height=550,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_blocs, use_container_width=True, key=f"blocs_{rank}")

    with col_comp:
        if competences:
            comp_labels = [c.get("titre", "?") for c in competences]
            comp_scores = [c.get("score_competence", 0) for c in competences]
            val_max_comp = max(comp_scores) if max(comp_scores) > 0 else 1

            fig_comp = go.Figure()
            fig_comp.add_trace(
                go.Scatterpolar(
                    r=comp_scores + [comp_scores[0]],
                    theta=comp_labels + [comp_labels[0]],
                    fill="toself",
                    fillcolor="rgba(66,133,244,0.20)",
                    line=dict(color="#4285F4", width=2.5),
                    marker=dict(size=6, color="#4285F4"),
                    hovertemplate="<b>%{theta}</b><br>Score : %{r:.4f}<extra></extra>",
                )
            )
            fig_comp.update_layout(
                title=dict(text="Maîtrise par compétence", font=dict(size=13), x=0.5),
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, val_max_comp * 1.25],
                        tickformat=".3f",
                        tickfont=dict(size=7, color="black"),
                        gridcolor="#dddddd",
                        linecolor="#dddddd",
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=9, color="black"), linecolor="#cccccc"
                    ),
                    bgcolor="rgba(250,250,250,1)",
                ),
                showlegend=False,
                height=550,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_comp, use_container_width=True, key=f"comp_{rank}")


def affichage_metier(metier_data: dict, rank: int):
    """Affiche un métier complet : card+jauge puis radars."""
    nom = metier_data.get("metier", "—")
    description = metier_data.get("description", "")
    score_global = metier_data.get("score", 0)
    score_par_bloc: dict = metier_data.get("score_par_bloc", {})
    competences: list = metier_data.get("compétences", [])

    medal = MEDALS[rank] if rank < len(MEDALS) else f"#{rank + 1}"
    color = COLORS[rank % len(COLORS)]
    bg = CARD_BG[rank % len(CARD_BG)]
    gauge_color = GAUGE_COLORS[rank % len(GAUGE_COLORS)]

    _card_header(nom, description, medal, color, bg, score_global, gauge_color, rank)
    _card_radars(score_par_bloc, competences, color, rank)


def section_top3(metiers: list):
    """Affiche les 3 premiers métiers avec séparateur entre chacun."""
    st.markdown("### 🏆 Top 3 des métiers recommandés")
    for i, metier_data in enumerate(metiers[:3]):
        st.markdown(f"### {MEDALS[i] if i < len(MEDALS) else f'#{i+1}'} Rang {i + 1}")
        affichage_metier(metier_data, rank=i)
        if i < 2:
            st.divider()


def _bilan_metriques(acquis: list, partiels: list, manquants: list):
    """Partie 1 : 3 métriques synthèse acquis / partiels / manquants."""
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("✅ Acquises", len(acquis), help=f"Score ≥ {SEUIL_ACQUIS}")
    col_b.metric(
        "🔶 Partielles",
        len(partiels),
        help=f"Score entre {SEUIL_PARTIEL} et {SEUIL_ACQUIS}",
    )
    col_c.metric("❌ Manquantes", len(manquants), help=f"Score < {SEUIL_PARTIEL}")


def _bilan_chart_gap(rows_sorted: list):
    """Partie 2 : bar chart horizontal score actuel vs niveau requis, trié par gap."""
    titres = [r["titre"] for r in rows_sorted]
    scores_list = [r["score"] for r in rows_sorted]
    niveaux_list = [r["niveau_norm"] for r in rows_sorted]

    fig_gap = go.Figure()
    fig_gap.add_trace(
        go.Bar(
            name="Niveau requis",
            x=niveaux_list,
            y=titres,
            orientation="h",
            marker=dict(
                color="rgba(180,180,180,0.45)", line=dict(color="#aaaaaa", width=1)
            ),
            hovertemplate="<b>%{y}</b><br>Niveau requis : %{x:.2f}<extra></extra>",
        )
    )
    fig_gap.add_trace(
        go.Bar(
            name="Score actuel",
            x=scores_list,
            y=titres,
            orientation="h",
            marker=dict(
                color=[
                    (
                        "#4CAF50"
                        if s >= SEUIL_ACQUIS
                        else "#FF9800" if s >= SEUIL_PARTIEL else "#F44336"
                    )
                    for s in scores_list
                ],
                opacity=0.9,
                line=dict(color="white", width=0.5),
            ),
            hovertemplate="<b>%{y}</b><br>Score actuel : %{x:.4f}<extra></extra>",
        )
    )
    fig_gap.update_layout(
        barmode="overlay",
        title=dict(
            text="Score actuel vs niveau requis par compétence", font=dict(size=13)
        ),
        xaxis=dict(
            title="Score normalisé (0–1)",
            range=[0, 1.1],
            gridcolor="#eeeeee",
            tickfont=dict(color="black"),
            title_font=dict(color="black"),
        ),
        yaxis=dict(tickfont=dict(size=10, color="black")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        height=max(350, len(titres) * 32),
        margin=dict(l=20, r=40, t=60, b=40),
    )
    st.plotly_chart(fig_gap, use_container_width=True, key="bilan_gap_chart")


def _bilan_tableau(rows_sorted: list):
    """Partie 3 : tableau détaillé trié par gap avec coloration du statut."""
    st.markdown("#### 📋 Détail par compétence (trié par priorité de développement)")

    def color_statut(val):
        if "Acquis" in val:
            return "color: #2e7d32; font-weight: bold"
        elif "Partiel" in val:
            return "color: #e65100; font-weight: bold"
        else:
            return "color: #b71c1c; font-weight: bold"

    df_bilan = pd.DataFrame(
        [
            {
                "Domaine": r["domaine"],
                "Compétence": r["titre"],
                "Score actuel": str(round(r["score"], 2)),
                "Niveau requis": str(round(r["niveau_norm"], 2)),
                "Écart": str(round(r["gap"], 2)),
                "Statut": r["statut"],
            }
            for r in rows_sorted
        ]
    )
    st.dataframe(
        df_bilan.style.map(color_statut, subset=["Statut"]),
        use_container_width=True,
        hide_index=True,
    )


def bilan_competence_metier(metier_data: dict):
    """Bilan détaillé acquis vs manquant pour un métier : métriques + graphique + tableau."""
    competences: list = metier_data.get("compétences", [])
    if not competences:
        st.info("Aucune compétence disponible pour ce métier.")
        return

    acquis, partiels, manquants, rows = [], [], [], []

    for c in competences:
        titre = c.get("titre", "?")
        domaine = c.get("domaine", "?")
        score = c.get("score_competence", 0)
        niveau_norm = c.get("niveau_requis", 1) / 5.0
        gap = max(0, niveau_norm - score)

        if score >= SEUIL_ACQUIS:
            statut = "✅ Acquis"
            acquis.append(titre)
        elif score >= SEUIL_PARTIEL:
            statut = "🔶 Partiel"
            partiels.append(titre)
        else:
            statut = "❌ Manquant"
            manquants.append(titre)

        rows.append(
            {
                "domaine": domaine,
                "titre": titre,
                "score": score,
                "niveau_norm": niveau_norm,
                "gap": gap,
                "statut": statut,
            }
        )

    rows_sorted = sorted(rows, key=lambda x: x["gap"], reverse=True)

    _bilan_metriques(acquis, partiels, manquants)
    st.markdown("")
    _bilan_chart_gap(rows_sorted)
    _bilan_tableau(rows_sorted)


def graphiques_metiers(metiers: list):
    """Point d'entrée principal : affiche tous les graphiques de résultats."""
    chart_top_metiers(metiers)
    st.divider()
    section_top3(metiers)

    top_metier = metiers[0]
    st.divider()
    st.markdown(f"### 🔍 Bilan de compétences — {top_metier['metier']}")
    bilan_competence_metier(top_metier)
