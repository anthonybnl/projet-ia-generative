import os
import chromadb
import pandas as pd

chroma_client = chromadb.HttpClient(host="localhost", port=8000)

collection: chromadb.Collection = None


def get_collection_if_exists() -> chromadb.Collection:

    try:
        collection = chroma_client.get_collection("competences")
        count = collection.count()

        if count == 0:
            return False

        return collection

    except:
        pass


def initialiser_bdd():
    df_competence = pd.read_csv(
        os.path.join(os.getcwd(), "data", "cigref_metier.csv"),
        sep=",",
        lineterminator="\n",
    )

    print(df_competence)


def main():
    try:
        chroma_client.delete_collection("competences")
    except:
        print("impossible de suppr")

    collection = get_collection_if_exists()

    if collection is not None:
        print("la base de donnée est déja initialisée 👍")
    else:
        print("la base de donnée n'est pas initialisée, initialisation en cours ...")
        initialiser_bdd()


if __name__ == "__main__":
    main()
