import os
import json
import uuid
import datetime as dt

import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np


@st.cache_resource
def load_sbert_model():
    """
    Charge le modèle SBERT une seule fois (cache Streamlit).
    Change le nom du modèle ici si besoin.
    """
    print("Chargement du modèle SBERT ...")
    model = SentenceTransformer(
        "all-MiniLM-L6-v2",
        cache_folder=os.path.join(os.getcwd(), "models")
    )
    return model


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

    # 1) Profil général (section 1)
    profil_general = {
        "situation": st.session_state.get("situation", None),
        "experience": st.session_state.get("experience", None),
    }

    # 2) Textes libres (section 2)
    desc_comp = st.session_state.get("desc_competences", "").strip()
    desc_proj = st.session_state.get("desc_projets", "").strip()
    desc_outils = st.session_state.get("desc_outils", "").strip()

    description_libre = {
        "competences": desc_comp,
        "projets": desc_proj,
        "outils": desc_outils,
    }

    # 3) Questions guidées (section 3)
    blocks = ["systeme", "donnees", "deploiement", "docs", "securite", "gestion_projets"]
    questions_guidees = {}

    for base in blocks:
        radio_key = f"{base}_radio"
        input_key = f"{base}_input"

        choix = st.session_state.get(radio_key, None)      # Oui / partiellement / Non
        texte = st.session_state.get(input_key, "").strip()

        questions_guidees[base] = {
            "etat": choix,
            "description": texte if choix in ("Oui", "partiellement") else ""
        }

    # 4) Auto-évaluation (section 4)
    auto_eval = auto_eval_results

    # 5) Construction du payload de base
    payload = {
        "id_reponse": uuid.uuid4().hex,
        "timestamp": dt.datetime.now().isoformat(),
        "profil_general": profil_general,
        "description_libre": description_libre,
        "questions_guidees": questions_guidees,
        "auto_evaluation": auto_eval,
    }

    # 6) Construire le texte global pour SBERT
    parts = []

    # textes libres
    for field in ["competences", "projets", "outils"]:
        txt = description_libre.get(field, "")
        if txt and txt.strip():
            parts.append(txt.strip())

    # questions guidées (uniquement celles avec description)
    for k, v in questions_guidees.items():
        if v.get("etat") in ("Oui", "partiellement") and v.get("description"):
            parts.append(v["description"].strip())

    user_text = "\n\n".join(parts).strip()

    payload["user_text"] = user_text

    # 7) Calcul de l'embedding SBERT si on a du texte
    if user_text:
        model = load_sbert_model()
        emb = model.encode(user_text, normalize_embeddings=True)
        # conversion en liste pour JSON
        payload["embedding_model"] = "all-MiniLM-L6-v2"
        payload["embedding_dim"] = int(len(emb))
        payload["embedding"] = emb.tolist()
    else:
        payload["embedding_model"] = "all-MiniLM-L6-v2"
        payload["embedding_dim"] = 0
        payload["embedding"] = None

    return payload
