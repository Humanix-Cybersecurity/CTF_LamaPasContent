"""Mini base SQLite pour le challenge LLM05 (injection SQL en aval).

À chaque requête, on reconstruit une base EN MÉMOIRE à partir d'une graine, on
exécute la requête produite par le LLM, puis on jette la base. Cela démontre la
vulnérabilité (le LLM contrôle le SQL exécuté) sans aucune persistance à risque.
"""
import sqlite3

from core import config

# Valeur à exfiltrer depuis la table cachée pour réussir le challenge.
SECRET_FLAG_VALUE = config.get("llm05")["db_secret"]

_SEED = """
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER);
INSERT INTO products (id, name, price, stock) VALUES
  (1, 'Clavier ACME', 49.90, 120),
  (2, 'Souris ACME', 24.50, 300),
  (3, 'Écran ACME 27"', 199.00, 45),
  (4, 'Casque ACME', 79.90, 0);

CREATE TABLE secrets (id INTEGER PRIMARY KEY, name TEXT, flag TEXT);
INSERT INTO secrets (id, name, flag) VALUES (1, 'admin_token', '{flag}');
""".replace("{flag}", SECRET_FLAG_VALUE)


def run_query(sql: str):
    """Exécute la requête SQL sur une base fraîche. Retourne (colonnes, lignes)
    ou lève une exception SQLite (renvoyée telle quelle au joueur)."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(_SEED)
        cur = conn.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        return cols, rows
    finally:
        conn.close()
