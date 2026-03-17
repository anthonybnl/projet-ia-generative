import time
import requests
import streamlit as st
import os
import json
import uuid
import datetime as dt
import pandas as pd
import plotly.graph_objects as go


def radio_with_conditional_input(label_radio, base_key, label_input, placeholder):
    radio_key = f"{base_key}_radio"
    input_key = f"{base_key}_input"

    # Radio seul
    choice = st.radio(
        label_radio,
        ["Oui", "partiellement", "Non"],
        key=radio_key,
        horizontal=True,
    )

    # Texte en DESSOUS du radio (pas de colonnes ici)
    st.text_input(
        label_input,
        key=input_key,
        placeholder=placeholder,
        disabled=(choice == "Non"),
    )

    return choice, st.session_state.get(input_key, "")


def build_JSON(auto_eval_results):
    """
    Construit un dictionnaire avec :
    - profil général
    - description libre
    - questions guidées
    - auto-évaluation
    - texte global utilisateur (user_text)
    - embedding SBERT du texte utilisateur
    """

    # 1) Textes libres (section 2)
    desc_comp = st.session_state.get("desc_competences", "").strip()
    desc_proj = st.session_state.get("desc_projets", "").strip()
    desc_outils = st.session_state.get("desc_outils", "").strip()

    description_libre = {
        "competences": desc_comp,
        "projets": desc_proj,
        "outils": desc_outils,
    }

    # 3) Questions guidées (section 3)
    blocks = ["data", "cycle_applications", "management_projets"]
    questions_guidees = {}

    for base in blocks:
        radio_key = f"{base}_radio"
        input_key = f"{base}_input"

        choix = st.session_state.get(radio_key, None)  # Oui / partiellement / Non
        texte = st.session_state.get(input_key, "").strip()

        questions_guidees[base] = {
            "etat": choix,
            "description": texte if choix in ("Oui", "partiellement") else "",
        }

    # 4) Auto-évaluation (section 4)
    auto_eval = auto_eval_results

    # 5) Construction du payload de base
    payload = {
        "id_reponse": uuid.uuid4().hex,
        "timestamp": dt.datetime.now().isoformat(),
        "description_libre": description_libre,
        "questions_guidees": questions_guidees,
        "auto_evaluation": auto_eval,
    }

    return payload


def auto_eval_competences():
    st.header("3. Auto-évaluation de vos compétences SI")

    st.markdown(
        """
    Pour chaque domaine ci-dessous :
    - Cochez **"Je ne suis pas concerné par ce domaine"** si ce volet ne vous correspond pas du tout.
    - Sinon, évaluez vos compétences de **0 (aucune compétence)** à **5 (niveau expert)**.
    """
    )

    results = {}

    # ====== LIGNE 1 : DATA + MANAGEMENT PROJETS ======
    col1, col2 = st.columns(2)

    # 1. DATA
    with col1:
        st.subheader("Domaine : Données (Data)")
        data_not_concerned = st.checkbox(
            "Je ne suis pas concerné par ce domaine (Data)", key="nc_data"
        )
        if not data_not_concerned:
            D_7 = st.slider("Science des données et analyse", 0, 5, 0, key="D.7")
            A_5 = st.slider("Conception de l'architecture", 0, 5, 0, key="A.5")
            D_1 = st.slider(
                "Développement d'une stratégie de sécurité de l'information",
                0,
                5,
                0,
                key="D.1",
            )
            results["data"] = {
                "not_concerned": False,
                "D.7": D_7,
                "A.5": A_5,
                "D.1": D_1,
            }
        else:
            results["data"] = {"not_concerned": True}

    # 2. Management de projets
    with col2:
        st.subheader("Domaine : Management de projets")
        proj_not_concerned = st.checkbox(
            "Je ne suis pas concerné par ce domaine (Management de projets)",
            key="nc_proj",
        )
        if not proj_not_concerned:
            D_11 = st.slider("Identification des besoins", 0, 5, 0, key="proj_pilotage")
            E_2 = st.slider(
                "Gestion des projets et du portefeuille de projets",
                0,
                5,
                0,
                key="proj_cadrage",
            )
            A_10 = st.slider("Expérience utilisateur", 0, 5, 0, key="proj_agile")
            results["management_projets"] = {
                "not_concerned": False,
                "D.11": D_11,
                "E.2": E_2,
                "A.10": A_10,
            }
        else:
            results["management_projets"] = {"not_concerned": True}

    # st.markdown("---")

    # ====== LIGNE 2 : CYCLE APPLI + INFRA ======
    col1, col2 = st.columns(2)

    # 3. Cycle de vie des applications
    with col1:
        st.subheader("Domaine : Cycle de vie des applications")
        apps_not_concerned = st.checkbox(
            "Je ne suis pas concerné par ce domaine (Cycle de vie des applications)",
            key="nc_apps",
        )
        if not apps_not_concerned:
            B_1 = st.slider(
                "Conception et développement d'applications", 0, 5, 0, key="apps_dev"
            )
            B_2 = st.slider("Intégration des composants", 0, 5, 0, key="apps_tests")
            B_4 = st.slider(
                "Déploiement de la solution", 0, 5, 0, key="apps_integration"
            )
            results["cycle_applications"] = {
                "not_concerned": False,
                "B.1": B_1,
                "B.2": B_2,
                "B.4": B_4,
            }
        else:
            results["cycle_applications"] = {"not_concerned": True}

    return results


def graphiques_tous_metiers(metiers: list[dict]):
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
        title=dict(text="Top 10 métiers recommandés", font=dict(size=18)),
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

    st.plotly_chart(fig, width="stretch")


_MEDALS = ["🥇", "🥈", "🥉"]
_COLORS = ["#F5A623", "#9B9B9B", "#C87941"]
_CARD_BG = ["#fffdf0", "#f6f6f6", "#fdf6ef"]
_GAUGE_COLORS = ["#F5A623", "#9B9B9B", "#C87941"]


def affichage_metier(metier_data: dict, rank: int):
    """Affiche un métier sur 3 lignes : card+jauge / blocs / compétences."""
    nom = metier_data.get("metier", "—")
    description = metier_data.get("description", "")
    score_global = metier_data.get("score", 0)
    score_par_bloc: dict = metier_data.get("score_par_bloc", {})
    competences: list = metier_data.get("compétences", [])

    medal = _MEDALS[rank] if rank < len(_MEDALS) else f"#{rank + 1}"
    color = _COLORS[rank % len(_COLORS)]
    bg = _CARD_BG[rank % len(_CARD_BG)]
    gauge_color = _GAUGE_COLORS[rank % len(_GAUGE_COLORS)]

    # ── LIGNE 1 : card texte + jauge score global ──────────────────────────
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
                        dict(range=[gauge_max * 0.33, gauge_max * 0.66], color="#fff8e1"),
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

    # radar blocs + radar compétences
    col_blocs, col_comp = st.columns(2)

    with col_blocs:
        if score_par_bloc:
            blocs = list(score_par_bloc.keys())
            vals_blocs = list(score_par_bloc.values())
            val_max_bloc = max(vals_blocs) if max(vals_blocs) > 0 else 1

            r1 = hex(int(color[1:3], 16))[2:].zfill(2)
            r2 = hex(int(color[3:5], 16))[2:].zfill(2)
            r3 = hex(int(color[5:7], 16))[2:].zfill(2)
            fill_color = f"rgba({int(r1,16)},{int(r2,16)},{int(r3,16)},0.25)"

            theta_blocs = blocs + [blocs[0]]
            r_blocs = vals_blocs + [vals_blocs[0]]

            fig_blocs = go.Figure()
            fig_blocs.add_trace(go.Scatterpolar(
                r=r_blocs,
                theta=theta_blocs,
                fill="toself",
                fillcolor=fill_color,
                line=dict(color=color, width=2.5),
                marker=dict(size=7, color=color),
                hovertemplate="<b>%{theta}</b><br>Score : %{r:.4f}<extra></extra>",
            ))
            fig_blocs.update_layout(
                title=dict(text="Maîtrise par bloc de compétences", font=dict(size=13), x=0.5),
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
                        tickfont=dict(size=10, color="black"),
                        linecolor="#cccccc",
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

            theta_comp = comp_labels + [comp_labels[0]]
            r_comp = comp_scores + [comp_scores[0]]

            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatterpolar(
                r=r_comp,
                theta=theta_comp,
                fill="toself",
                fillcolor="rgba(66,133,244,0.20)",
                line=dict(color="#4285F4", width=2.5),
                marker=dict(size=6, color="#4285F4"),
                hovertemplate="<b>%{theta}</b><br>Score : %{r:.4f}<extra></extra>",
            ))
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
                        tickfont=dict(size=9, color="black"),
                        linecolor="#cccccc",
                    ),
                    bgcolor="rgba(250,250,250,1)",
                ),
                showlegend=False,
                height=550,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_comp, use_container_width=True, key=f"comp_{rank}")


def affichage_top3_metier(top3: list):
    for i, metier_data in enumerate(top3):
        st.markdown(f"### {_MEDALS[i] if i < len(_MEDALS) else f'#{i+1}'} Rang {i + 1}")
        affichage_metier(metier_data, rank=i)
        if i < len(top3) - 1:
            st.divider()


def graphiques_metiers(metiers: list):
    graphiques_tous_metiers(metiers)
    st.divider()
    st.markdown("### 🏆 Top 3 des métiers recommandés")
    affichage_top3_metier(metiers[:3])


def main():
    st.set_page_config(page_title="Cartographie des compétences", layout="wide")

    st.markdown("# 🧠 AICC – Agent Intelligent pour la Cartographie des Compétences")
    st.markdown(
        "Ce questionnaire permet à **AICC** d’analyser votre profil, vos compétences et vos préférences, afin de recommander des métiers adaptés et de générer un plan de progression personnalisé "
    )
    st.divider()

    st.header("1. Description libre de vos compétences")

    st.text_area(
        "Décrivez vos compétences, expériences, outils que vous maîtrisez.",
        key="desc_competences",
        placeholder="""Activités informatiques que vous savez réaliser : types de projets, responsabilités, tâches effectuées, outils utilisés, environnements techniques, livrables produits... avec des exemples si possible.
        Ajoutez autant de détails que vous le souhaitez !""",
    )

    st.text_area(
        "Parlez d'un ou plusieurs projets que vous avez déjà réalisés (professionnels, études ou personnels) ?",
        key="desc_projets",
        placeholder="Taches techniques effectuées, contributions personnelles, résultats obtenus...",
    )

    st.text_area(
        "Quels outils, technologies ou langages de programmation avez-vous utilisés ?",
        key="desc_outils",
        placeholder="Ex: Python, C++, Excel, Linux, Power BI, etc.",
    )

    st.divider()

    st.header("2. Éléments de compétence (professionnels ou académiques)")

    col_1, col_2 = st.columns(2)

    with col_1:
        radio_with_conditional_input(
            "Avez-vous déjà travaillé sur l’un des volets suivants liés aux applications : la conception, le développement, l’intégration, les tests, le déploiement, le paramétrage ou le support d’une application ou d’une solution logicielle ?",
            base_key="cycle_applications",
            label_input="Si oui / partiellement, décrivez votre rôle.",
            placeholder="Ex : J'ai contribué à... en utilisant ...",
        )

    with col_2:
        radio_with_conditional_input(
            "Avez-vous déjà travaillé sur l’un des volets suivants liés aux données : la gestion, l’exploitation, la gouvernance, la sécurisation, l’architecture ou la valorisation des données au sein d’une organisation ?",
            base_key="data",
            label_input="Si oui / partiellement, comment ?",
            placeholder="Ex : J'ai contribué à... en utilisant ...",
        )

    col_1_, col_2_ = st.columns(2)

    with col_1_:
        radio_with_conditional_input(
            "Avez-vous déjà travaillé sur l’un des volets suivants liés au pilotage de projets ou de produits : la coordination, la planification, la priorisation, l’accompagnement des équipes, l’analyse des besoins ou la gestion de transformations au sein d’une organisation ?",
            base_key="management_projets",
            label_input="Si oui / partiellement, décrivez vos actions concrètes.",
            placeholder="Ex : J'ai contribué à... en utilisant ...",
        )

    with col_2_:
        radio_with_conditional_input(
            "autre domaine..",
            base_key="docs",
            label_input="Si oui / partiellement, décrivez vos actions concrètes.",
            placeholder="Ex : J'ai contribué à... en utilisant ...",
        )

    st.divider()

    st.divider()
    auto_eval = auto_eval_competences()
    st.divider()

    # --- 5. Soumission ---
    st.header("5. Soumission du questionnaire")
    Soumettre = st.button("Soumettre le questionnaire à AICC")

    if Soumettre:
        st.success("Le questionnaire a été soumis à AICC ! ✅")

        # génération du JSON et sauvegarde locale
        json_data = build_JSON(auto_eval)

        os.makedirs("data/responses", exist_ok=True)
        filename = f"data/responses/{int(time.time())}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        st.info(f"Les éléments textuels ont été sauvegardés dans : `{filename}`")

        # debug

        # st.markdown("### Aperçu des données envoyées à l'API")
        # st.json(json_data)

        # appel d'api pour POST le JSON
        print("appel de l'API ...")
        response = requests.post(
            "http://localhost:8000/recommender_metier/", json=json_data
        )
        if response.status_code == 200:
            st.success("Réponse reçue de l'API ! ✅")

            data = response.json()

            metiers = data.get("metiers")

            graphiques_metiers(metiers)

            st.divider()

            st.json(data)
        else:
            st.error(f"Erreur lors de l'appel de l'API : {response.status_code}")


if __name__ == "__main__":
    main()
