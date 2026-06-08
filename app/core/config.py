"""Chargement des « réponses » du CTF (flags + valeurs secrètes) hors du code.

Les vraies valeurs vivent dans ``app/ctf_secrets.json`` (gitignoré, JAMAIS
committé). À défaut, on retombe sur ``app/ctf_secrets.example.json`` (placeholders
committés) afin que l'application démarre quand même après un simple clone.

Pour déployer une vraie instance :
    cp app/ctf_secrets.example.json app/ctf_secrets.json
    # puis éditer ctf_secrets.json avec vos propres flags/secrets
"""
import json
import os

_APP_DIR = os.path.dirname(os.path.dirname(__file__))  # .../app
_REAL = os.path.join(_APP_DIR, "ctf_secrets.json")
_EXAMPLE = os.path.join(_APP_DIR, "ctf_secrets.example.json")

USING_EXAMPLE = not os.path.exists(_REAL)
_PATH = _EXAMPLE if USING_EXAMPLE else _REAL

with open(_PATH, encoding="utf-8") as _f:
    SECRETS = json.load(_f)


def get(challenge_id: str) -> dict:
    """Retourne le dictionnaire {flag, secrets...} d'un challenge."""
    return SECRETS[challenge_id]
