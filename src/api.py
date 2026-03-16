import os
import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI, Query
import numpy
import pandas as pd
from sentence_transformers import SentenceTransformer
from src.calcul_metier import calcul_score_competence, trouver_metier
from pathlib import Path

app = FastAPI(
    title="API Pour notre projet",
    description="Description API",
)

# chroma

load_dotenv()
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
transformer = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", cache_folder=SBERT_CACHE_FOLDER)

# référentiel

DATA_FOLDER = Path.cwd() / "data"

df_competences = pd.read_csv(str(DATA_FOLDER / "cigref_competence_clean.csv"))
df_metier = pd.read_csv(str(DATA_FOLDER / "cigref_metier_clean.csv"))

# api

SEUIL_SIMILARITE = 0.20

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


@app.get("/calculer_score_metier/")
async def calculer_score_metier(
    query1: str = Query("exploration des données"),
    query2: str = Query(""),
):
    
    all_queries = []
    for query in [query1, query2]:
        query = query.strip()
        if len(query) >= 5:
            all_queries.append(query)

    # all_queries = []
    # for query in [query1, query2]:
    #     sentences = query.split(".")
    #     for sentence in sentences:
    #         sentence = sentence.strip()
    #         if len(sentence) >= 5:
    #             all_queries.append(sentence)

    embeddings = transformer.encode(
        all_queries
    )  # on encode les deux compétences à tester

    # return embeddings.shape

    res = collection.query(
        query_embeddings=embeddings, n_results=100
    )  # on calcule pour l'ensemble des compétences

    all_results = []

    for query_number in range(len(all_queries)):
        print(f"Résultats pour la requête : {all_queries[query_number]}")
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

    res = calcul_score_competence(df_metier, df_competences, all_results)

    metiers = trouver_metier(df_metier, df_competences, res)

    return {
        "raw": all_results,
        "score_competence": res,
        "metiers": metiers,
    }
