----------------------------------------------
---- Table des recommandations de métiers ----
----------------------------------------------

CREATE TABLE IF NOT EXISTS recommendation (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    metier      TEXT    NOT NULL,
    score       REAL    NOT NULL,
    llm_text    TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

----------------------------------------------
------ Table des scores des compétences ------
----------------------------------------------
CREATE TABLE IF NOT EXISTS recommendation_competence (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_recommendation   INTEGER NOT NULL,
    id_competence       TEXT    NOT NULL,
    score_competence    REAL    NOT NULL,
    FOREIGN KEY (id_recommendation) REFERENCES recommendation(id) ON DELETE CASCADE
);

-- Index pour retrouver rapidement toutes les compétences d'une recommandation
CREATE INDEX IF NOT EXISTS idx_rec_comp_recommendation
    ON recommendation_competence(id_recommendation);
