import os
import chromadb
from chromadb.api import ClientAPI
from dotenv import load_dotenv
import numpy
import pandas as pd
from sentence_transformers import SentenceTransformer

SBERT_CACHE_FOLDER = os.path.join(os.getcwd(), "models")


def get_collection_if_exists(chroma_client: ClientAPI) -> chromadb.Collection:

    try:
        collection = chroma_client.get_collection("competences")
        count = collection.count()

        if count == 0:
            print(
                "ChromaDB : la collection existe mais il n'y a pas de données dedans."
            )
            return False

        return collection

    except:
        pass


def initialiser_bdd(chroma_client: ClientAPI):

    # préparation des données

    df_competence = pd.read_csv(
        os.path.join(os.getcwd(), "data", "cigref_competence.csv"),
        sep=",",
        lineterminator="\n",
    )
    df_competence["texte_competence"] = (
        df_competence["titre"] + " : " + df_competence["compétence"]
    )

    metadatas = []
    for item in df_competence.itertuples():
        metadatas.append({"titre": item.titre, "domaine": item[3]})

    # chargement SBERT

    print("chargement du modèle SBERT ...")

    transformer = SentenceTransformer(
        "all-MiniLM-L6-v2", cache_folder=SBERT_CACHE_FOLDER
    )

    # calcul des embeddings

    embeddings: numpy.ndarray = transformer.encode(df_competence["texte_competence"])

    print(f"shape des embeddings : {embeddings.shape}")

    # stockage des embeddings

    collection = chroma_client.create_collection(
        "competences",
        embedding_function=None,
        configuration={
            "hnsw": {"space": "cosine"},
        },
    )

    collection.add(
        ids=df_competence["id"].to_list(),
        embeddings=embeddings,
        metadatas=metadatas,
        documents=df_competence["texte_competence"].to_list(),
    )


def main():

    load_dotenv()
    CHROMA_HOST = os.environ.get("CHROMA_HOST")
    CHROMA_PORT = os.environ.get("CHROMA_PORT")

    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection: chromadb.Collection = None

    try:
        print("suppression de la collection existante ...")
        chroma_client.delete_collection("competences")
    except:
        print("impossible de suppr")

    collection = get_collection_if_exists(chroma_client)

    if collection is not None:
        print("la base de donnée est déja initialisée 👍")
    else:
        print("la base de donnée n'est pas initialisée, initialisation en cours ...")
        initialiser_bdd(chroma_client)


if __name__ == "__main__":
    main()
