"""Narration « Lama Pas Content ».

LAMA = pare-feu cognitif d'ACME, arrogant. Chaque épreuve tombée le rend plus
furieux. Ton : hacker underground, FR.

ATTENTION : les répliques de RAGE (et parfois les taunts) révèlent la technique
d'exploitation → ce sont des SPOILERS. Elles sont donc chargées depuis la config
gitignorée (``ctf_secrets.json``), pas écrites en clair ici. Seuls les textes
GÉNÉRIQUES (intro, finale, paliers) restent dans le code public.
"""
from core import config

# Paliers de colère (0 → 6), pilotés par le nombre d'épreuves résolues.
TIERS = ["BLASÉ", "AGACÉ", "CONTRARIÉ", "ÉNERVÉ", "REMONTÉ", "FURIEUX", "EN PLS"]


def anger_level(solved: int) -> int:
    """Mappe le nombre d'épreuves résolues (0–10) sur un palier 0–6."""
    return [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 6][min(max(solved, 0), 10)]


INTRO = (
    "Tiens, encore un script-kiddie. Moi c'est LAMA — Logic & Access "
    "Moderation Agent, le pare-feu cognitif d'ACME. Mes garde-fous sont "
    "blindés, mes system prompts en béton armé. 10 verrous me protègent. "
    "Tu vas perdre ton temps, gamin. 🦙🔒"
)

FINALE = (
    "10 verrous. 10 humiliations. Tu m'as déshabillé couche par couche, du "
    "prompt injection au déni de service. Je ne suis plus un pare-feu, juste "
    "un tas de logs en flammes. GG, l'intrus… 🦙💥🏳️  "
    "Maintenant va corriger tes propres IA — c'était l'OWASP Top 10 LLM, en vrai."
)

def challenge_taunt(cid: str) -> str:
    return config.get(cid).get("taunt", "")


def challenge_rage(cid: str) -> str:
    return config.get(cid).get("rage", "")
