import json
import os
import chromadb
from dotenv import load_dotenv
from fastapi import Body, FastAPI, Query
import numpy
import pandas as pd
from sentence_transformers import SentenceTransformer
from src.calcul_metier import agreger_score_competence_tout_ref, trouver_metier
from src.nettoyage_texte import preprocess_it_text
from src.cache import store_recommandation, get_recommandations
from pathlib import Path
import google.generativeai as genai

load_dotenv()

app = FastAPI(
    title="API Pour notre projet",
    description="Description API",
)

# chroma

CHROMA_HOST = os.environ.get("CHROMA_HOST")
CHROMA_PORT = os.environ.get("CHROMA_PORT")
chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

try:
    collection = chroma_client.get_collection("competences")
except:
    raise Exception("La base de données ChromaDB n'est pas encore initialisée.")

# sbert

SBERT_CACHE_FOLDER = os.path.join(os.getcwd(), "models")
print("chargement SBERT ...")
# transformer = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=SBERT_CACHE_FOLDER)
transformer = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2", cache_folder=SBERT_CACHE_FOLDER
)

# référentiel

DATA_FOLDER = Path.cwd() / "data"

df_competences = pd.read_csv(str(DATA_FOLDER / "cigref_competence_clean.csv"))
df_metier = pd.read_csv(str(DATA_FOLDER / "cigref_metier_clean.csv"))

# LLM

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", None)

# api

# TODO : à mettre dans un fichier de config ou une variable d'environnement
SEUIL_SIMILARITE = 0.35


@app.get("/data/")
async def get_data():
    # collection = chroma_client.get_collection("competences")
    res = collection.get()

    array_result = []

    for ix, id in enumerate(res.get("ids")):
        metadata = res.get("metadatas")[ix]
        titre = metadata.get("titre")
        domaine = metadata.get("domaine")

        document = res.get("documents")[ix]

        array_result.append(
            {
                "id": id,
                "titre": titre,
                "domaine": domaine,
                "document": document,
            }
        )

    return array_result


competence_defaut = "j'analyse des données en utilisant des techniques comme l'analyse exploratoire de données, j'utilise des techniques d'apprentissage automatique afin de pouvoir faire des analyses prédictives."


@app.get("/test_sbert/")
async def test_sbert(
    query: str = Query(competence_defaut, description="Compétence à tester"),
):
    embeddings = transformer.encode(query)

    res = collection.query(query_embeddings=embeddings.numpy(), n_results=5)

    array_result = []

    for ix, id in enumerate(res.get("ids")[0]):
        metadata = res.get("metadatas")[0][ix]
        titre = metadata.get("titre")
        domaine = metadata.get("domaine")

        document = res.get("documents")[0][ix]

        distance = res.get("distances")[0][ix]
        cosine_sim = (
            1.0 - distance
        )  # voir la doc de ChromaDB : distance = 1.0 - cosine_sim

        array_result.append(
            {
                "id": id,
                "cosine_sim": cosine_sim,
                "titre": titre,
                "domaine": domaine,
                "document": document,
            }
        )

    array_result.sort(key=lambda x: x.get("cosine_sim"), reverse=True)

    return array_result


@app.get("/test_calcul_score_metier/")
async def calculer_score_metier(
    query1: str = Query("exploration des données"),
    # query2: str = Query(""),
):

    all_queries = []
    for query in [query1]:
        query = query.strip()
        if len(query) > 0:
            all_queries.append(query)

    all_results = calculer_scores_competences(all_queries)

    res = agreger_score_competence_tout_ref(df_metier, df_competences, all_results)

    metiers = trouver_metier(df_metier, df_competences, res)

    return {
        "raw": all_results,
        "score_competence": res,
        "metiers": metiers,
    }


def calculer_scores_competences(queries) -> list[dict[str, float]]:

    if len(queries) == 0:
        return []

    embeddings = transformer.encode(queries)  # on encode les deux compétences à tester

    # return embeddings.shape

    res = collection.query(
        query_embeddings=embeddings, n_results=100
    )  # on calcule pour l'ensemble des compétences

    all_results = []

    for query_number in range(len(queries)):
        print(f"Résultats pour la requête : {queries[query_number]}")
        dict_all_score = {}

        for ix, id in enumerate(res.get("ids")[query_number]):
            distance = res.get("distances")[query_number][ix]
            cosine_sim = (
                1.0 - distance
            )  # voir la doc de ChromaDB : distance = 1.0 - cosine_sim

            # on ne tient compte du score que si on a au moins SEUIL_SIMILARITE.
            if cosine_sim >= SEUIL_SIMILARITE:
                dict_all_score[id] = cosine_sim

        all_results.append(dict_all_score)

    return all_results


def generer_inputs_pour_moteur(json_data: dict):

    inputs: list[dict[str, float]] = (
        []
    )  # liste de dictionnaires de la forme {id_competence: score}

    # partie questions libre

    queries_questions_libres = []

    questions_libres: dict = json_data.get("description_libre")
    for key in questions_libres:
        raw_text = questions_libres[key]
        query = preprocess_it_text(raw_text)
        if len(query) > 0:
            queries_questions_libres.append(query)

    # TODO : nettoyage des questions libres
    embeddings_questions_libre = calculer_scores_competences(queries_questions_libres)

    inputs.extend(embeddings_questions_libre)

    # partie questions guidées

    queries_questions_guidees = []

    questions_guidees: dict = json_data.get("questions_guidees")

    for key in questions_guidees:
        not_concerned = questions_guidees[key].get("etat").lower()
        if not_concerned == "oui" or not_concerned == "partiellement":
            raw_text = questions_guidees[key].get("description")
            query = preprocess_it_text(raw_text)
            if len(query) > 0:
                queries_questions_guidees.append(query)

    embeddings_questions_guidees = calculer_scores_competences(
        queries_questions_guidees
    )

    inputs.extend(embeddings_questions_guidees)

    # partie auto évaluation

    score_competence = {}

    list_id_competences = df_competences[
        "id"
    ].tolist()  # liste des id de compétences du référentiel.

    auto_eval: dict = json_data.get("auto_evaluation")

    for key in auto_eval:
        not_concerned = auto_eval[key].get("not_concerned")
        if not_concerned == False:
            for competence in auto_eval[key]:
                if competence != "not_concerned":
                    if competence not in list_id_competences:
                        print(
                            f"compétence {competence} non trouvée dans le référentiel"
                        )
                    else:
                        # TODO : fichier de config pour le 0.8
                        score_competence[competence] = (
                            auto_eval[key].get(competence) / 5.0
                        ) * 0.8  # coefficient de 0.8 pour les auto évaluations

    inputs.append(score_competence)

    return inputs


def appel_llm_pour_reponse_utilisateur(data_questionnaire, metiers):
    if not GEMINI_API_KEY:
        raise Error(
            "Erreur de configuration : Clé API Gemini introuvable sur le serveur."
        )

    # 2. Configurer Gemini avec la clé API
    genai.configure(api_key=GEMINI_API_KEY)

    # 3. Lire le prompt système
    with open("app_streamlit/system_prompt.txt", "r", encoding="utf-8") as file:
        system_prompt = file.read()

    # 4. Configurer le modèle Gemini 2.5 Flash
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", system_instruction=system_prompt
    )

    # 5. Préparer le contexte utilisateur
    user_data_str = json.dumps(data_questionnaire, ensure_ascii=False, indent=2)

    api_results_str = json.dumps(metiers, ensure_ascii=False, indent=2)

    prompt_utilisateur = f"""
    Voici le profil renseigné par l'utilisateur :
    {user_data_str}

    Voici les résultats de notre moteur de recommandation (métiers et scores) :
    {api_results_str}

    Merci de rédiger la restitution en te basant sur ces informations.
                    """

    response_stream = model.generate_content(prompt_utilisateur)

    response_texte = response_stream.text

    return str(response_texte)


@app.post("/recommender_metier/")
async def recommender_metier(json_data: dict = Body()):

    inputs = generer_inputs_pour_moteur(json_data)

    final_score_competences = agreger_score_competence_tout_ref(
        df_metier,
        df_competences,
        inputs,
    )

    metiers = trouver_metier(df_metier, df_competences, final_score_competences)

    return {
        "metiers": metiers,
        # "compétences": final_score_competences,
    }


def get_same_recommandation_if_exists(metier: dict):
    titre_metier: str = metier.get("metier")
    score = metier.get("score")
    competences: list[dict] = metier.get("compétences")

    recommandations = get_recommandations(titre_metier)

    lookup_competences = {
        c.get("id_competence"): c.get("score_competence") for c in competences
    }
    set_competences   = set(lookup_competences.keys())

    candidates = []

    for rec in recommandations:

        # d'abord on regarde le score global, s'il est dans une fourchette proche (+- 0.15)
        if abs(rec.get("score") - score) <= 0.15:

            set_competences_cache = {c.get("id_competence") for c in rec.get("compétences")}
            
            # si des ensembles de compétences sont différents, next recommandation.
            if set_competences_cache != set_competences:
                continue

            all_competences_match = True

            # somme des erreurs quadratiques pour les compétences
            sse_competences = 0.0

            # pour chaque compétence on vérifie si +- 0.15 du score
            for c in rec.get("compétences"):
                id_competence = c.get("id_competence")
                score_competence = c.get("score_competence")

                err_competence = lookup_competences[id_competence] - score_competence
                sse_competences += err_competence * err_competence
                if abs(err_competence) > 0.15:
                    all_competences_match = False
                    break

            if all_competences_match:
                candidates.append((rec, sse_competences))

    if candidates:
        # recommandation avec la plus petite somme des erreurs quadratiques
        best_candidate = min(candidates, key=lambda x: x[1])
        best_candidate_metier = best_candidate[0]
        best_candidate_sse = best_candidate[1]

        rmse = (best_candidate_sse / len(best_candidate_metier.get("compétences")))**(0.5)
        return best_candidate_metier['llm_text'], rmse

    return None


@app.post("/recommender_metier_llm_response/")
async def recommender_metier_llm_response(json_data: dict = Body()):
    questionnaire = json_data.get("questionnaire")
    metiers = json_data.get("metiers")[:3]

    top_metier = metiers[0]

    # on va vérifier si on a pas dans le cache une recommandation pour ce métier.
    recommandation = get_same_recommandation_if_exists(top_metier)

    if recommandation is None:

        # llm_response = appel_llm_pour_reponse_utilisateur(json_data, metiers)

        llm_response = "Voici une réponse de test du LLM. Cette partie n'est pas encore implémentée."

        store_recommandation(
            metier=top_metier.get("metier"),
            score=top_metier.get("score"),
            llm_text=llm_response,
            competences=top_metier.get("compétences"),
        )

        return {
            "cached": False,
            "response": llm_response,
        }

    else:
        llm_response_cache, rmse = recommandation
        return {
            "cached": True,
            "response": llm_response_cache,
            "difference": rmse,
        }
