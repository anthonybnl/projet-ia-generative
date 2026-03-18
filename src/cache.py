import sqlite3
from pathlib import Path
from typing import Any

DB_PATH  = Path.cwd() / "database" / "cache.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def store_recommandation(
    metier: str,
    score: float,
    llm_text: str,
    competences: list[dict[str, Any]],
) -> int:
    
    with _get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO recommendation (metier, score, llm_text)
            VALUES (?, ?, ?)
            """,
            (metier, score, llm_text),
        )
        id_recommendation = cursor.lastrowid

        conn.executemany(
            """
            INSERT INTO recommendation_competence (id_recommendation, id_competence, score_competence)
            VALUES (?, ?, ?)
            """,
            [
                (id_recommendation, c["id_competence"], c["score_competence"])
                for c in competences
            ],
        )
        conn.commit()

    return id_recommendation # type: ignore


# ---------------------------------------------------------------------------
# SELECT
# ---------------------------------------------------------------------------

def get_recommandations(metier: str) -> list[dict[str, Any]]:

    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                r.id, r.metier, r.score, r.llm_text, r.created_at,
                rc.id_competence, rc.score_competence
            FROM recommendation r
            JOIN recommendation_competence rc ON rc.id_recommendation = r.id
            WHERE r.metier = ?
            ORDER BY r.created_at DESC, rc.id_competence
            """,
            (metier,),
        ).fetchall()

    # on groupe les résultats par recommandation
    grouped: dict[int, dict[str, Any]] = {}
    for row in rows:
        rec_id = row["id"]
        if rec_id not in grouped:
            grouped[rec_id] = {
                "id":          row["id"],
                "metier":      row["metier"],
                "score":       row["score"],
                "llm_text":    row["llm_text"],
                "created_at":  row["created_at"],
                "competences": [],
            }
        grouped[rec_id]["competences"].append({
            "id_competence":   row["id_competence"],
            "score_competence": row["score_competence"],
        })

    return list(grouped.values())
