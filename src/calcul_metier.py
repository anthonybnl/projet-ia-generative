import pandas as pd


def calcul_score_competence(
    df_metier: pd.DataFrame, df_competences: pd.DataFrame, data: list[dict]
) -> dict[str, float]:

    ids_competences = df_competences["id"].tolist()

    score_par_competence = {}

    for competence in ids_competences:
        score_pour_cette_competence = []

        for item in data:
            if competence in item:
                score_pour_cette_competence.append(item[competence])

        if score_pour_cette_competence:
            score_par_competence[competence] = sum(score_pour_cette_competence) / len(
                score_pour_cette_competence
            )
        else:
            score_par_competence[competence] = 0

    return score_par_competence


def trouver_metier(
    df_metier: pd.DataFrame, score_par_competence: dict[str, float]
) -> list[dict]:

    # on regroupe par métier

    metiers: dict[str, list[dict]] = {}

    for index, row in df_metier.iterrows():
        metier = row["métier"]
        domaine = row["domaine de compétence"]
        id_competence = row["id_competence"]
        niveau = row["niveau"]

        if not metier in metiers:
            metiers[metier] = []

        metiers[metier].append(
            {
                "id_competence": id_competence,
                "niveau": niveau,
                "domaine": domaine,
            }
        )

    resultats = []

    for metier in metiers:
        total_coefficient = 0
        total_score = 0

        blocs_competence = {}

        resultat_metier = {"metier": metier, "compétences": []}

        for competence in metiers[metier]:
            id_competence = competence["id_competence"]
            niveau = competence["niveau"]
            domaine = competence["domaine"]

            score = score_par_competence.get(id_competence, 0)

            total_coefficient += niveau
            total_score += score * niveau

            resultat_metier["compétences"].append(
                {
                    "id_competence": id_competence,
                    "niveau_requis": niveau,
                    "score_competence": score,
                    "domaine": domaine,
                }
            )

            # gestion du score par bloc de compétence
            if domaine not in blocs_competence:
                blocs_competence[domaine] = {"total_score": 0, "total_coefficient": 0}
            blocs_competence[domaine]["total_score"] += score * niveau
            blocs_competence[domaine]["total_coefficient"] += niveau

        metier_score = total_score / total_coefficient if total_coefficient > 0 else 0

        resultat_metier["score"] = metier_score

        # score par bloc de compétence
        resultat_metier["score_par_bloc"] = {}
        for domaine in blocs_competence:
            total_score = blocs_competence[domaine]["total_score"]
            total_coefficient = blocs_competence[domaine]["total_coefficient"]
            score_bloc = total_score / total_coefficient if total_coefficient > 0 else 0
            resultat_metier["score_par_bloc"][domaine] = score_bloc

        resultats.append(resultat_metier)

    resultats.sort(key=lambda x: x.get("score"), reverse=True)

    # top 3 des métiers
    resultats = resultats[:3]
    
    return resultats
