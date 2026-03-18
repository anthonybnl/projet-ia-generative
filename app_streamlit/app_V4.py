import time
import requests
import streamlit as st
import os
import json
import uuid
import datetime as dt
from charts import graphiques_metiers

from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.environ.get("GEMINI_API_KEY", None)


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


def build_JSON():
    """
    Construit un dictionnaire avec :
    - profil général
    - description libre
    - questions guidées
    - auto-évaluation
    - texte global utilisateur (user_text)
    - embedding SBERT du texte utilisateur
    """

    # Textes libres (section 2)
    desc_comp = st.session_state.get("desc_competences", "").strip()
    desc_proj = st.session_state.get("desc_projets", "").strip()
    desc_outils = st.session_state.get("desc_outils", "").strip()

    description_libre = {
        "competences": desc_comp,
        "projets": desc_proj,
        "outils": desc_outils,
    }

    # Questions guidées (section 3)
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

    # Auto-évaluation (section 4)
    auto_eval: dict = {
        "data": {"not_concerned": True},
        "management_projets": {"not_concerned": True},
        "cycle_applications": {"not_concerned": True},
    }

    nc_data = st.session_state.get("nc_data")
    if nc_data == False:
        auto_eval["data"] = {
            "not_concerned": False,
            "D.7": st.session_state.get("D.7", 0),
            "A.5": st.session_state.get("A.5", 0),
            "D.1": st.session_state.get("D.1", 0),
        }

    nc_proj = st.session_state.get("nc_proj")
    if nc_proj == False:
        auto_eval["management_projets"] = {
            "not_concerned": False,
            "D.11": st.session_state.get("D.11"),
            "E.2": st.session_state.get("E.2"),
            "A.10": st.session_state.get("A.10"),
        }

    nc_apps = st.session_state.get("nc_apps")
    if nc_apps == False:
        auto_eval["cycle_applications"] = {
            "not_concerned": False,
            "B.1": st.session_state.get("B.1"),
            "B.2": st.session_state.get("B.2"),
            "B.4": st.session_state.get("B.4"),
        }

    # Construction du payload de base
    payload = {
        "id_reponse": uuid.uuid4().hex,
        "timestamp": dt.datetime.now().isoformat(),
        "description_libre": description_libre,
        "questions_guidees": questions_guidees,
        "auto_evaluation": auto_eval,
    }

    return payload


def part1_description_libre():
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


def part2_questions_guidees():
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


def part3_auto_eval_competences():
    st.header("3. Auto-évaluation de vos compétences SI")

    st.markdown(
        """
    Pour chaque domaine ci-dessous :
    - Cochez **"Je ne suis pas concerné par ce domaine"** si ce volet ne vous correspond pas du tout.
    - Sinon, évaluez vos compétences de **0 (aucune compétence)** à **5 (niveau expert)**.
    """
    )

    # ====== LIGNE 1 : DATA + MANAGEMENT PROJETS ======
    col1, col2 = st.columns(2)

    # 1. DATA
    with col1:
        st.subheader("Domaine : Données (Data)")
        data_not_concerned = st.checkbox(
            "Je ne suis pas concerné par ce domaine (Data)", key="nc_data"
        )
        if not data_not_concerned:
            st.slider("Science des données et analyse", 0, 5, 0, key="D.7")
            st.slider("Conception de l'architecture", 0, 5, 0, key="A.5")
            st.slider(
                "Développement d'une stratégie de sécurité de l'information",
                0,
                5,
                0,
                key="D.1",
            )

    # 2. Management de projets
    with col2:
        st.subheader("Domaine : Management de projets")
        proj_not_concerned = st.checkbox(
            "Je ne suis pas concerné par ce domaine (Management de projets)",
            key="nc_proj",
        )
        if not proj_not_concerned:
            st.slider("Identification des besoins", 0, 5, 0, key="D.11")
            st.slider(
                "Gestion des projets et du portefeuille de projets",
                0,
                5,
                0,
                key="E.2",
            )
            st.slider("Expérience utilisateur", 0, 5, 0, key="A.10")

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
            st.slider("Conception et développement d'applications", 0, 5, 0, key="B.1")
            st.slider("Intégration des composants", 0, 5, 0, key="B.2")
            st.slider("Déploiement de la solution", 0, 5, 0, key="B.4")


def plan_de_progression_et_bio(json_data, api_results: list[dict]):
    st.header("✨ Analyse de votre profil par AISCA")

    input = {
        "questionnaire": json_data,
        "metiers": api_results,
    }

    with st.status("Traitement MAGIR en cours...", expanded=True) as status:

        response = requests.post(
            "http://localhost:8000/recommender_metier_llm_response/", json=input
        )
        if response.status_code == 200:

            status.update(
                label="Réponse de MAGIR reçue !",
                state="complete",
                expanded=True,
            )

            is_cached = response.json().get("cached")
            difference = response.json().get("difference")
            if is_cached:
                st.info(
                    "Le plan de progression affiché provient du cache, basé sur une recommandation similaire déjà traitée auparavant."
                )
                difference_pourcent = difference * 100
                st.info(
                    f"Différence en pourcentage avec la recommandation la plus proche en cache : {difference_pourcent:.2f}%"
                )
            else:
                st.success(
                    "Le plan de progression affiché a été généré par le LLM en réponse à votre profil unique."
                )

            st.markdown(response.json().get("response"))

        else:

            status.update(
                label="Erreur lors de la récupération du plan de progression",
                state="error",
                expanded=True,
            )
            st.error(
                f"Erreur lors de la récupération du plan de progression : {response.status_code}"
            )
            try:
                st.json(response.json())
            except Exception as e:
                pass


def on_submit():
    st.success("Le questionnaire a été soumis à MAGIR ! ✅")

    # génération du JSON et sauvegarde locale
    json_data = build_JSON()

    os.makedirs("data/responses", exist_ok=True)
    filename = f"data/responses/{int(time.time())}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    # st.info(f"Les éléments textuels ont été sauvegardés dans : `{filename}`")

    response = requests.post(
        "http://localhost:8000/recommender_metier/", json=json_data
    )
    if response.status_code == 200:
        # st.success("Réponse reçue de l'API ! ✅")

        data = response.json()

        metiers = data.get("metiers")

        with st.expander("Visuels concernant les métiers recommandés", expanded=True):
            graphiques_metiers(metiers)

        plan_de_progression_et_bio(json_data, data.get("metiers"))

        # st.divider()
        # st.json(data)
    else:
        st.error(f"Erreur lors de l'appel de l'API : {response.status_code}")


def main():
    st.set_page_config(page_title="Cartographie des compétences", layout="wide")

    st.markdown("# 🧠 MAGIR – Matching Agent for Generated IT Roles")
    st.markdown(
        "Ce questionnaire permet à **MAGIR** d’analyser votre profil, vos compétences et vos préférences, afin de recommander des métiers adaptés et de générer un plan de progression personnalisé "
    )
    st.divider()

    part1_description_libre()
    part2_questions_guidees()
    part3_auto_eval_competences()

    # --- 5. Soumission ---
    st.header("5. Soumission du questionnaire")
    Soumettre = st.button("Soumettre le questionnaire à AISCA")

    if Soumettre:
        on_submit()


if __name__ == "__main__":
    main()
