import os
import chromadb
import numpy
from sentence_transformers import SentenceTransformer


SBERT_CACHE_FOLDER = os.path.join(os.getcwd(), "models")

client = chromadb.HttpClient(host="localhost", port=8000)

collection = client.get_collection("competences")

# res = collection.get(ids='D.7', include=["embeddings", "metadatas"])
# print(res)

# user_sentence = "je suis compétent en science des données. je sélectionnes des données structurées ou non structurées , modélise et valorise la donnée et extrait des informations pertinente. Je selectionne les modèles les plus adaptés pour analyser les données."

user_sentence = """
Je possède des compétences solides en data engineering, notamment dans la conception, la mise en place et la maintenance de pipelines de données. J’ai travaillé sur des projets impliquant la collecte de données depuis différentes sources (fichiers Excel, CSV, APIs), leur nettoyage, transformation et stockage dans des bases de données relationnelles et NoSQL. J’ai l’habitude de structurer des flux ETL robustes, d’automatiser les traitements de données et d’optimiser la qualité, la cohérence et la traçabilité des données. J’interviens également sur la modélisation des données, la gestion des schémas, ainsi que sur l’industrialisation des scripts pour un usage collaboratif et reproductible. J’ai participé à plusieurs projets de data engineering, notamment la création d’une base de données centralisée pour des essais techniques, avec ingestion automatique de fichiers structurés et semi-structurés. J’ai conçu des scripts ETL permettant de parcourir des répertoires, extraire des métadonnées, nettoyer les données, calculer des indicateurs et charger les résultats dans une base PostgreSQL. J’ai également travaillé sur des projets académiques de data analysis et de data integration impliquant des volumes de données hétérogènes, avec restitution sous forme de tableaux de bord ou de rapports analytiques. Outils techniques et languages que je maitrise : Python, SQL, PostgreSQL, MongoDB, BigQuery, Pandas, NumPy, Git, Docker (bases), Linux, Streamlit, APIs REST, Excel, YAML, JSON J’ai participé à la conception de systèmes de gestion de données, en analysant les besoins fonctionnels et techniques, en définissant l’architecture des flux de données et en contribuant à la modélisation des bases de données. J’ai également pris part à la structuration d’applications orientées données, en lien avec les utilisateurs finaux. J’ai déployé et maintenu des scripts ETL en environnement de travail collaboratif, assuré leur bon fonctionnement dans le temps, corrigé des anomalies et amélioré les performances. J’ai également testé les pipelines de données afin de garantir la fiabilité et la cohérence des résultats produits. J’ai rédigé des documentations techniques décrivant l’architecture des pipelines, les schémas de bases de données, les règles de transformation des données et les procédures d’exécution. Ces documents visaient à faciliter la maintenance, la reprise et la compréhension des systèmes par d’autres collaborateurs. J’ai coordonné certaines tâches techniques dans le cadre de projets de groupe ou professionnels, planifié les étapes de réalisation, suivi l’avancement des livrables et veillé au respect des délais. J’ai également assuré la cohérence entre les différentes parties du projet et la qualité des livrables produits.
"""

# chargement SBERT

print("chargement du modèle SBERT ...")

transformer = SentenceTransformer(
    "all-MiniLM-L6-v2", cache_folder=SBERT_CACHE_FOLDER
)

# calcul des embeddings

print("calcul des embeddings")

embeddings: numpy.ndarray = transformer.encode(user_sentence)

print("recherche dans la base de donnée vectorielle ...")

result = collection.query(query_embeddings=embeddings, n_results=100)


# print(result)

ids = result["ids"][0]
distances = result["distances"][0]
cosinesim = []
for distance in distances:
    cosinesim.append(1 - distance)

print({ "ids" : ids, "cosinesim": cosinesim})

