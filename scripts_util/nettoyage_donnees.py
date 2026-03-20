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
from pathlib import Path

# chargement des CSV
csv_path_base = Path.cwd() / "poc-referentiel-competence"

df_metier = pd.read_csv(csv_path_base / "cigref.csv", sep=";")
df_competence = pd.read_csv(csv_path_base / "cigref compétence.csv", sep=";")

df_descriptions_metiers = pd.read_csv(
    csv_path_base / "descriptions_metiers.csv", sep=",", quotechar='"'
)

print(df_descriptions_metiers[["métier"]].head())
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
    os.path.join(os.getcwd(), "data", "cigref_competence_clean.csv"),
    sep=",",
    lineterminator="\n",
    index=False,
)

df_metier = df_metier.merge(
    df_competence, how="left", left_on="compétence_id", right_on="compétence_id"
)
df_metier = df_metier.merge(
    df_descriptions_metiers, left_on="profil métier", right_on="métier", how="left"
)

df_metier_clean = df_metier[
    ["profil métier", "domaine de compétence", "id", "niveau", "description"]
].rename(columns={"profil métier": "métier", "id": "id_competence"})


df_metier_clean.to_csv(
    os.path.join(os.getcwd(), "data", "cigref_metier_clean.csv"),
    sep=",",
    lineterminator="\n",
    index=False,
)
