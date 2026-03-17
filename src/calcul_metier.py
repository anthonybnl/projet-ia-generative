import pandas as pd


def ref_agreger_metier_competences(
    df_metier: pd.DataFrame, df_competences: pd.DataFrame
) -> dict[str, dict]:

    # on regroupe par métier les compétences associées

    metiers: dict[str, dict] = {}

    df_metier_competences = df_metier.merge(
        df_competences[["id", "titre", "compétence"]],
        left_on="id_competence",
        right_on="id",
        how="inner",
    )

    print(df_metier_competences.info())

    for index, row in df_metier_competences.iterrows():
        metier = row["métier"]
        description = row["description"]
        domaine = row["domaine de compétence"]
        id_competence = row["id_competence"]
        niveau = row["niveau"]
        titre_competence = row["titre"]
        detail_competence = row["compétence"]

        if not metier in metiers:
            metiers[metier] = {
                "metier": metier,
                "description": description,
                "compétences": [],
            }

        metiers[metier]["compétences"].append(
            {
                "id_competence": id_competence,
                "niveau": niveau,
                "domaine": domaine,
                "tittre": titre_competence,
                "compétence": detail_competence,
            }
        )
    return metiers


def agreger_score_competence_tout_ref(
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
    df_metier: pd.DataFrame,
    df_competences: pd.DataFrame,
    score_par_competence: dict[str, float],
) -> list[dict]:

    ref_metiers = ref_agreger_metier_competences(df_metier, df_competences)

    resultats = []

    for metier in ref_metiers:
        description = ref_metiers[metier]["description"]

        total_coefficient = 0
        total_score = 0

        blocs_competence = {}

        resultat_metier = {
            "metier": metier,
            "description": description,
            "compétences": [],
        }

        for competence in ref_metiers[metier]["compétences"]:
            id_competence = competence["id_competence"]
            niveau = competence["niveau"]
            domaine = competence["domaine"]
            titre_competence = competence["tittre"]
            detail_competence = competence["compétence"]

            score = score_par_competence.get(id_competence, 0)

            total_coefficient += niveau
            total_score += score * niveau

            resultat_metier["compétences"].append(
                {
                    "id_competence": id_competence,
                    "titre": titre_competence,
                    "detail": detail_competence,
                    "domaine": domaine,
                    "niveau_requis": niveau,
                    "score_competence": score,
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
    # TODO dans config
    resultats = resultats[:10]

    return resultats
