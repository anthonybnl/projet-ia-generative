import streamlit as st
import os
import json
import uuid

from embedding_calculations import build_JSON

st.set_page_config(page_title="Cartographie des compétences")

st.markdown("# 🧠 AISCA – Agent Intelligent pour la Cartographie des Compétences")
st.markdown(
    "##### Ce questionnaire permet à **AISCA** d’analyser votre profil, vos compétences et vos préférences, afin de recommander des métiers adaptés et de générer un plan de progression personnalisé "
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
        "Avez-vous déjà participé à la conception ou à l’analyse d’un système, d’une application, ou d’un service numérique ?",
        base_key="systeme",
        label_input="Si oui / partiellement, décrivez votre rôle.",
        placeholder="Ex : J'ai contribué à... en utilisant ..."
    )

with col_2:
    radio_with_conditional_input(
        "Avez-vous déjà manipulé, transformé, nettoyé, analysé ou exploité des données ?",
        base_key="donnees",
        label_input="Si oui / partiellement, comment ?",
        placeholder="Ex : J'ai contribué à... en utilisant ..."
    )

col_1_, col_2_ = st.columns(2)

with col_1_:
    radio_with_conditional_input(
        "Avez-vous déjà déployé, intégré, testé ou maintenu un système ou une application ?",
        base_key="deploiement",
        label_input="Si oui / partiellement, décrivez vos actions concrètes.",
        placeholder="Ex : J'ai contribué à... en utilisant ..."
    )

with col_2_:
    radio_with_conditional_input(
        "Avez-vous déjà rédigé des documents techniques, rapports, spécifications ou procédures ?",
        base_key="docs",
        label_input="Si oui / partiellement, décrivez vos actions concrètes.",
        placeholder="Ex : J'ai contribué à... en utilisant ..."
    )

col_1__, col_2__ = st.columns(2)

with col_1__:
    radio_with_conditional_input(
        "Avez-vous déjà réalisé des tâches liées à la sécurité de l’information ou à la gestion des risques ?",
        base_key="securite",
        label_input="Si oui / partiellement, décrivez vos actions concrètes.",
        placeholder="Ex : J'ai contribué à... en utilisant ..."
    )

with col_2__:
    radio_with_conditional_input(
        "Avez-vous déjà coordonné des tâches, piloté un projet, ou géré des livrables ?",
        base_key="gestion_projets",
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
            ml_stats = st.slider(
                "Compétences en machine learning / statistiques",
                0, 5, 0,
                key="data_ml_stats"
            )
            data_transform = st.slider(
                "Manipulation et transformation de données (ETL, SQL, etc.)",
                0, 5, 0,
                key="data_transform"
            )
            dataviz = st.slider(
                "Visualisation de données / tableaux de bord (BI, DataViz)",
                0, 5, 0,
                key="data_dataviz"
            )
            results["data"] = {
                "not_concerned": False,
                "ml_stats": ml_stats,
                "data_transform": data_transform,
                "dataviz": dataviz,
            }
        else:
            results["data"] = {"not_concerned": True}

    # 2. Management de projets
    with col2:
        st.subheader("Domaine : Management de projets")
        proj_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Management de projets)", key="nc_proj")
        if not proj_not_concerned:
            proj_pilotage = st.slider(
                "Gestion et pilotage de projets (planning, risques, coordination)",
                0, 5, 0,
                key="proj_pilotage"
            )
            proj_cadrage = st.slider(
                "Analyse des besoins / cadrage fonctionnel",
                0, 5, 0,
                key="proj_cadrage"
            )
            proj_agile = st.slider(
                "Animation et accompagnement agile (Scrum, rituels, etc.)",
                0, 5, 0,
                key="proj_agile"
            )
            results["management_projets"] = {
                "not_concerned": False,
                "pilotage": proj_pilotage,
                "cadrage": proj_cadrage,
                "agile": proj_agile,
            }
        else:
            results["management_projets"] = {"not_concerned": True}

    st.markdown("---")

    # ====== LIGNE 2 : CYCLE APPLI + INFRA ======
    col1, col2 = st.columns(2)

    # 3. Cycle de vie des applications
    with col1:
        st.subheader("Domaine : Cycle de vie des applications")
        apps_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Applications)", key="nc_apps")
        if not apps_not_concerned:
            dev = st.slider(
                "Développement / programmation",
                0, 5, 0,
                key="apps_dev"
            )
            tests = st.slider(
                "Tests logiciels (unitaires, fonctionnels, automatisés)",
                0, 5, 0,
                key="apps_tests"
            )
            integration = st.slider(
                "Intégration et déploiement applicatif",
                0, 5, 0,
                key="apps_integration"
            )
            results["cycle_applications"] = {
                "not_concerned": False,
                "developpement": dev,
                "tests": tests,
                "integration_deploiement": integration,
            }
        else:
            results["cycle_applications"] = {"not_concerned": True}

    # 4. Infrastructures & MCO
    with col2:
        st.subheader("Domaine : Infrastructures & Exploitation (MCO)")
        infra_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Infrastructures)", key="nc_infra")
        if not infra_not_concerned:
            admin_sys = st.slider(
                "Administration systèmes / réseaux / serveurs",
                0, 5, 0,
                key="infra_admin_sys"
            )
            mco = st.slider(
                "Supervision / exploitation / gestion d'incidents techniques",
                0, 5, 0,
                key="infra_mco"
            )
            admin_db = st.slider(
                "Administration de bases de données",
                0, 5, 0,
                key="infra_admin_db"
            )
            results["infrastructures"] = {
                "not_concerned": False,
                "admin_systemes_reseaux": admin_sys,
                "exploitation_mco": mco,
                "admin_bases_donnees": admin_db,
            }
        else:
            results["infrastructures"] = {"not_concerned": True}

    st.markdown("---")

    # ====== LIGNE 3 : SUPPORT + SECURITE ======
    col1, col2 = st.columns(2)

    # 5. Support & Assistance
    with col1:
        st.subheader("Domaine : Support & Assistance")
        support_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Support)", key="nc_support")
        if not support_not_concerned:
            support_users = st.slider(
                "Support utilisateurs (diagnostic, incidents)",
                0, 5, 0,
                key="support_users"
            )
            support_fonc = st.slider(
                "Support fonctionnel (accompagnement des métiers, paramétrage)",
                0, 5, 0,
                key="support_fonc"
            )
            doc_proc = st.slider(
                "Rédaction de documentation / procédures",
                0, 5, 0,
                key="support_doc"
            )
            results["support_assistance"] = {
                "not_concerned": False,
                "support_utilisateurs": support_users,
                "support_fonctionnel": support_fonc,
                "documentation_procedures": doc_proc,
            }
        else:
            results["support_assistance"] = {"not_concerned": True}

    # 6. Sécurité
    with col2:
        st.subheader("Domaine : Sécurité des SI / Cybersécurité")
        sec_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Sécurité)", key="nc_secu")
        if not sec_not_concerned:
            risque_ssi = st.slider(
                "Analyse et gestion des risques SSI",
                0, 5, 0,
                key="secu_risque"
            )
            sec_ops = st.slider(
                "Sécurité opérationnelle (vulnérabilités, durcissement, contrôles)",
                0, 5, 0,
                key="secu_ops"
            )
            gouvernance_ssi = st.slider(
                "Conformité / audit / gouvernance SSI",
                0, 5, 0,
                key="secu_gouv"
            )
            results["securite"] = {
                "not_concerned": False,
                "analyse_risques": risque_ssi,
                "securite_operationnelle": sec_ops,
                "gouvernance_ssi": gouvernance_ssi,
            }
        else:
            results["securite"] = {"not_concerned": True}

    st.markdown("---")

    # ====== LIGNE 4 : MANAGEMENT OP + ORGA / ARCHI ======
    col1, col2 = st.columns(2)

    # 7. Management opérationnel
    with col1:
        st.subheader("Domaine : Management opérationnel de la DSI")
        mgmt_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Management opérationnel)", key="nc_mgmt")
        if not mgmt_not_concerned:
            pilotage_services = st.slider(
                "Pilotage d'activités / services IT",
                0, 5, 0,
                key="mgmt_pilotage"
            )
            management_equipe = st.slider(
                "Management d'équipe (organisation, suivi, feedback)",
                0, 5, 0,
                key="mgmt_equipe"
            )
            strat_transfo = st.slider(
                "Gestion stratégique et transformation digitale",
                0, 5, 0,
                key="mgmt_strat"
            )
            results["management_operationnel"] = {
                "not_concerned": False,
                "pilotage_services": pilotage_services,
                "management_equipe": management_equipe,
                "strategie_transformation": strat_transfo,
            }
        else:
            results["management_operationnel"] = {"not_concerned": True}

    # 8. Organisation & Architecture du SI
    with col2:
        st.subheader("Domaine : Organisation & Architecture du SI")
        org_not_concerned = st.checkbox("Je ne suis pas concerné par ce domaine (Organisation & Architecture)", key="nc_org")
        if not org_not_concerned:
            analyse_process = st.slider(
                "Analyse des processus métiers et des besoins organisationnels",
                0, 5, 0,
                key="org_analyse"
            )
            archi_si = st.slider(
                "Conception / architecture du SI (fonctionnelle, applicative, data)",
                0, 5, 0,
                key="org_archi"
            )
            urbanisation = st.slider(
                "Urbanisation du SI / schémas directeurs",
                0, 5, 0,
                key="org_urban"
            )
            results["organisation_architecture"] = {
                "not_concerned": False,
                "analyse_processus": analyse_process,
                "architecture_si": archi_si,
                "urbanisation_si": urbanisation,
            }
        else:
            results["organisation_architecture"] = {"not_concerned": True}

    return results


# Exemple d'utilisation
def main():
    auto_eval = auto_eval_competences()
    st.divider()
 # --- 5. Soumission ---
    st.header("5. Soumission du questionnaire")
    Soumettre = st.button("Soumettre le questionnaire à AISCA")

    if Soumettre:
        st.success("Le questionnaire a été soumis à AISCA ! ✅")
        st.info("Recommandation de métier en cours... ⏳")

def main():
    auto_eval = auto_eval_competences()
    st.divider()

    # --- 5. Soumission ---
    st.header("5. Soumission du questionnaire")
    Soumettre = st.button("Soumettre le questionnaire à AISCA")

    if Soumettre:
        st.success("Le questionnaire a été soumis à AISCA ! ✅")

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
