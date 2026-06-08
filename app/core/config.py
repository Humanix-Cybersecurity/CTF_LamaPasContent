"""Chargement des « réponses » du CTF (flags + secrets + indices) hors du code.

Ordre de priorité (du plus prioritaire au plus secours) :
  1. Variable d'env ``CTF_SECRETS_JSON`` : le JSON complet, en ligne
     (idéal pour un secret manager / CI sans fichier sur disque).
  2. Variable d'env ``CTF_SECRETS_PATH`` : chemin vers un fichier JSON
     (idéal pour un volume monté hors du dépôt).
  3. ``app/ctf_secrets.json`` (gitignoré).
  4. ``app/ctf_secrets.example.json`` (placeholders committés) — pour que
     l'application démarre après un simple clone.

Pour déployer une vraie instance, voir private/DEPLOIEMENT.md (non publié) ou la
section « Déploiement » du README.
"""
import json
import os

_APP_DIR = os.path.dirname(os.path.dirname(__file__))  # .../app
_REAL = os.path.join(_APP_DIR, "ctf_secrets.json")
_EXAMPLE = os.path.join(_APP_DIR, "ctf_secrets.example.json")


def _load():
    inline = os.environ.get("CTF_SECRETS_JSON")
    if inline:
        return json.loads(inline), "env:CTF_SECRETS_JSON"

    env_path = os.environ.get("CTF_SECRETS_PATH")
    if env_path and os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            return json.load(f), f"env:CTF_SECRETS_PATH ({env_path})"

    if os.path.exists(_REAL):
        with open(_REAL, encoding="utf-8") as f:
            return json.load(f), "ctf_secrets.json"

    with open(_EXAMPLE, encoding="utf-8") as f:
        return json.load(f), "ctf_secrets.example.json (placeholders)"


SECRETS, SOURCE = _load()
# Vrai dès qu'on tourne sur les placeholders : utile pour afficher un avertissement.
USING_EXAMPLE = SOURCE.endswith("(placeholders)")


def get(challenge_id: str) -> dict:
    """Retourne le dictionnaire {flag, secrets..., hints} d'un challenge."""
    return SECRETS[challenge_id]
