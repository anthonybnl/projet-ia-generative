import json
import chromadb
import numpy
import pandas as pd
import os
from sentence_transformers import SentenceTransformer, util
from chromadb import (
    Documents,
    EmbeddingFunction,
    Embeddings,
    HttpClient as ChromaHttpClient,
)

# chargement des CSV
csv_path_base = os.path.join(os.getcwd(), "poc-referentiel-competence")

df_metier = pd.read_csv(os.path.join(csv_path_base, "cigref.csv"), sep=";")
df_competence = pd.read_csv(
    os.path.join(csv_path_base, "cigref compétence.csv"), sep=";"
)

# nettoyage des données

df_competence["id"] = df_competence["compétence_id"].apply(
    lambda x: x.split(" ")[0].removesuffix(".")
)
df_competence["titre"] = df_competence["compétence_id"].apply(
    lambda x: " ".join(x.split(" ")[1:])
)

df_competence_clean = df_competence[
    ["id", "titre", "domaine de compétence", "compétence"]
]

df_competence_clean.to_csv(
    os.path.join(os.getcwd(), "data", "cigref_competence.csv"),
    sep=",",
    lineterminator="\n",
    index=False,
)

df_metier = df_metier.merge(
    df_competence, how="left", left_on="compétence_id", right_on="compétence_id"
)

df_metier_clean = df_metier[["profil métier", "domaine de compétence", "id"]].rename(
    columns={"profil métier": "métier", "id": "id_competence"}
)

df_metier_clean.to_csv(
    os.path.join(os.getcwd(), "data", "cigref_metier.csv"),
    sep=",",
    lineterminator="\n",
    index=False,
)

df_competence_clean["competence_text"] = (
    df_competence_clean["titre"] + " : " + df_competence_clean["compétence"]
)

# organisation de la métadonnée (titre + domaine)

metadatas = []
for item in df_competence_clean.itertuples():
    metadatas.append({"titre": item.titre, "domaine": item[3]})

# chargement du modèle SBERT

print("chargement du modèle SBERT ...")

transformer = SentenceTransformer(
    "all-MiniLM-L6-v2", cache_folder=os.path.join(os.getcwd(), "models")
)

# calcul des embeddings

print("Calcul des embeddings des compétences ...")

embeddings: numpy.ndarray = transformer.encode(df_competence_clean["competence_text"])

print(f"embeddings shape : {embeddings.shape}")

# stockage dans la DB Chroma

client = ChromaHttpClient(host="localhost", port=8000)

collections = client.list_collections()

print(collections)

try:
    collection = client.get_collection("competences")

    # # Si la collection existe, on la supprime (TODO a fin de test)
    # client.delete_collection("competences")
except:

    # stockage des embeddings

    collection = client.create_collection(
        "competences",
        embedding_function=None,
        configuration={
            "hnsw": {"space": "cosine"},
        },
    )

    collection.add(
        ids=df_competence_clean["id"].to_list(),
        embeddings=embeddings,
        metadatas=metadatas,
        documents=df_competence_clean["competence_text"].to_list(),
    )

test_sentence = "Anticipe les besoins métier à long terme, influence l'amélioration de l'efficacité des processus de l'organisation. Détermine le modèle SI et l'architecture d'entreprise en maintenant la cohérence avec la politique de l'organisation et en garantissant un environnement sécurisé. Reconnaît les risques potentiels et les exigences métiers pour assurer la résilience dans l'alignement des systèmes et des services par rapport à la stratégie métier. Prend, en matière de SI, des décisions stratégiques pour l'entreprise y compris en termes de stratégies d'approvisionnement."

test_embedding = transformer.encode([test_sentence])

# print(test_embedding.shape)

test_embedding = test_embedding[0]

# print(test_embedding.shape)


research = collection.query(query_embeddings=test_embedding)

print(research)

test_embeddingssss  = []

for id in ["E.2", "A.1", "A.3", "D.3", "D.9", "A.4", "D.11", "E.1", "D.10", "C.4"]:
    ix = df_competence_clean[df_competence_clean["id"] == id].index.to_list()
    ix = ix[0]
    my_embedding_competence = embeddings[ix]

    cossim = util.cos_sim(test_embedding, my_embedding_competence)

    print(f"{ix}\t - {df_competence_clean.iat[ix, 0]} - {cossim}")

# for id in ["E.2", "A.1", "A.3", "D.3", "D.9", "A.4", "D.11", "E.1", "D.10", "C.4"]:
#     res = df_competence_clean[df_competence_clean["id"] == id].index.to_list()
#     res = res[0]

#     embedding = embeddings[res]

#     print(util.cos_sim(numpy.concat([test_embedding]), numpy.concat([embedding])))

