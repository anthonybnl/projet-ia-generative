import sqlite3
from pathlib import Path

BASE_DIR    = Path.cwd() / "database"
DB_PATH     = BASE_DIR / "cache.db"
SCHEMA_PATH = BASE_DIR / "cache_schema.sql"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Base de données : {DB_PATH}")
    print(f"Schéma          : {SCHEMA_PATH}")

    if DB_PATH.exists():
        print("La base de données existe déjà, initialisation ignorée.")
        return

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DB_PATH) as conn:
        # Active les clés étrangères (désactivées par défaut dans SQLite)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_sql)
        conn.commit()

    print("Initialisation terminée.")


if __name__ == "__main__":
    main()
