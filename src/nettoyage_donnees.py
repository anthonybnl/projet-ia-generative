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
