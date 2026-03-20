import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path.cwd() / "database" / "cache.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def clear_cache():
    with _get_conn() as conn:
        conn.execute(
            "DELETE FROM recommendation_competence;"
        )
        conn.execute("DELETE FROM recommendation;")
        conn.commit()
