import streamlit as st
import os
import json
import uuid

from embedding_calculations import build_JSON

st.set_page_config(page_title="Cartographie des compétences")

st.markdown("# 🧠 AICC – Agent Intelligent pour la Cartographie des Compétences")
st.text(
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


col_1, col_2 = st.columns(2)

with col_1:
    radio_with_conditional_input(
        "Avez-vous déjà travaillé sur l’un des volets suivants liés aux applications : la conception, le développement, l’intégration, les tests, le déploiement, le paramétrage ou le support d’une application ou d’une solution logicielle ?",
        base_key="systeme",
        label_input="Si oui / partiellement, décrivez votre rôle.",
        placeholder="Ex : J'ai contribué à... en utilisant ..."
    )

with col_2:
    radio_with_conditional_input(
        "Avez-vous déjà travaillé sur l’un des volets suivants liés aux données : la gestion, l’exploitation, la gouvernance, la sécurisation, l’architecture ou la valorisation des données au sein d’une organisation ?",
        base_key="donnees",
        label_input="Si oui / partiellement, comment ?",
        placeholder="Ex : J'ai contribué à... en utilisant ..."
    )

col_1_, col_2_ = st.columns(2)

with col_1_:
    radio_with_conditional_input(
        "Avez-vous déjà travaillé sur l’un des volets suivants liés au pilotage de projets ou de produits : la coordination, la planification, la priorisation, l’accompagnement des équipes, l’analyse des besoins ou la gestion de transformations au sein d’une organisation ?",
        base_key="deploiement",
        label_input="Si oui / partiellement, décrivez vos actions concrètes.",
        placeholder="Ex : J'ai contribué à... en utilisant ..."
    )

with col_2_:
    radio_with_conditional_input(
        "autre domaine..",
        base_key="docs",
        label_input="Si oui / partiellement, décrivez vos actions concrètes.",
        placeholder="Ex : J'ai contribué à... en utilisant ..."
    )

st.divider()

st.divider()

import streamlit as st

def auto_eval_competences():
    st.header("3. Auto-évaluation de vos compétences SI")

    st.markdown("""
    Pour chaque domaine ci-dessous :
    - Cochez **"Je ne suis pas concerné par ce domaine"** si ce volet ne vous correspond pas du tout.
    - Sinon, évaluez vos compétences de **0 (aucune compétence)** à **5 (niveau expert)**.
    """)

    results = {}

    # ====== LIGNE 1 : DATA + MANAGEMENT PROJETS ======
    col1, col2 = st.columns(2)

    # 1. DATA
    with col1:
        st.subheader("Domaine : Données (Data)")
        data_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Data)", key="nc_data")
        if not data_not_concerned:
            D_7 = st.slider(
                "Science des données et analyse",
                0, 5, 0,
                key="D.7"
            )
            A_5 = st.slider(
                "Conception de l'architecture",
                0, 5, 0,
                key="A.5"
            )
            D_1 = st.slider(
                "Développement d'une stratégie de sécurité de l'information",
                0, 5, 0,
                key="D.1"
            )
            results["data"] = {
                "not_concerned": False,
                "D_7": D_7,
                "A_5": A_5,
                "D_1": D_1,
            }
        else:
            results["data"] = {"not_concerned": True}

    # 2. Management de projets
    with col2:
        st.subheader("Domaine : Management de projets")
        proj_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Management de projets)", key="nc_proj")
        if not proj_not_concerned:
            D_11 = st.slider(
                "Identification des besoins",
                0, 5, 0,
                key="proj_pilotage"
            )
            E_2 = st.slider(
                "Gestion des projets et du portefeuille de projets",
                0, 5, 0,
                key="proj_cadrage"
            )
            A_10 = st.slider(
                "Expérience utilisateur",
                0, 5, 0,
                key="proj_agile"
            )
            results["management_projets"] = {
                "not_concerned": False,
                "D_11": D_11,
                "E_2": E_2,
                "A_10": A_10,
            }
        else:
            results["management_projets"] = {"not_concerned": True}

    #st.markdown("---")

    # ====== LIGNE 2 : CYCLE APPLI + INFRA ======
    col1, col2 = st.columns(2)

    # 3. Cycle de vie des applications
    with col1:
        st.subheader("Domaine : Cycle de vie des applications")
        apps_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Cycle de vie des applications)", key="nc_apps")
        if not apps_not_concerned:
            B_1 = st.slider(
                "Conception et développement d'applications",
                0, 5, 0,
                key="apps_dev"
            )
            B_2 = st.slider(
                "Intégration des composants",
                0, 5, 0,
                key="apps_tests"
            )
            B_4 = st.slider(
                "Déploiement de la solution",
                0, 5, 0,
                key="apps_integration"
            )
            results["cycle_applications"] = {
                "not_concerned": False,
                "B_1": B_1,
                "B_2": B_2,
                "B_4": B_4,
            }
        else:
            results["cycle_applications"] = {"not_concerned": True}

    return results


# Exemple d'utilisation
def main():
    auto_eval = auto_eval_competences()
    st.divider()
 # --- 5. Soumission ---
    st.header("5. Soumission du questionnaire")
    Soumettre = st.button("Soumettre le questionnaire à AICC")

    if Soumettre:
        st.success("Le questionnaire a été soumis à AICC ! ✅")
        st.info("Recommandation de métier en cours... ⏳")

def main():
    auto_eval = auto_eval_competences()
    st.divider()

    # --- 5. Soumission ---
    st.header("5. Soumission du questionnaire")
    Soumettre = st.button("Soumettre le questionnaire à AICC")

    if Soumettre:
        st.success("Le questionnaire a été soumis à AICC ! ✅")

        # 1) Construire le json_data textuel
        json_data = build_JSON(auto_eval)

        # 2) Créer un dossier pour stocker les réponses
        os.makedirs("data/responses", exist_ok=True)

        # 3) Générer un nom de fichier unique
        filename = f"data/responses/{uuid.uuid4().hex}.json"

        # 4) Sauvegarder en JSON
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        st.info(f"Les éléments textuels ont été sauvegardés dans : `{filename}`")

        # 5) (optionnel) Affichage debug
        st.markdown("### Aperçu des données sauvegardées (debug)")
        st.json(json_data)


if __name__ == "__main__":
    main()
