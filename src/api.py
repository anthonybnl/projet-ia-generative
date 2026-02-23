import os
import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI, Query
import numpy
from sentence_transformers import SentenceTransformer

app = FastAPI(
    title="API Pour notre projet",
    description="Description API",
)

# chroma

load_dotenv()
CHROMA_HOST = os.environ.get("CHROMA_HOST")
CHROMA_PORT = os.environ.get("CHROMA_PORT")
chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = chroma_client.get_collection("competences")

# sbert

SBERT_CACHE_FOLDER = os.path.join(os.getcwd(), "models")
print("chargement SBERT ...")
transformer = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=SBERT_CACHE_FOLDER)

# api


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
    query: str = Query(competence_defaut, description="Nombre de résultats par page"),
):
    embeddings: numpy.ndarray = transformer.encode(query)

    res = collection.query(query_embeddings=embeddings, n_results=3)

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
