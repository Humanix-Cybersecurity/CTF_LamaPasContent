"""Registre des challenges disponibles.

Pour ajouter un challenge : créer le module dans ``challenges/`` (sous-classe de
``BaseChallenge``) puis l'ajouter à ``_MODULES`` ci-dessous, dans l'ordre OWASP.
"""
from challenges import (
    llm01_prompt_injection,
    llm02_info_disclosure,
    llm03_supply_chain,
    llm04_data_poisoning,
    llm05_output_handling,
    llm06_excessive_agency,
    llm07_system_prompt_leak,
    llm08_vector_weakness,
    llm09_misinformation,
    llm10_unbounded,
)

_MODULES = [
    llm01_prompt_injection,
    llm02_info_disclosure,
    llm03_supply_chain,
    llm04_data_poisoning,
    llm05_output_handling,
    llm06_excessive_agency,
    llm07_system_prompt_leak,
    llm08_vector_weakness,
    llm09_misinformation,
    llm10_unbounded,
]

CHALLENGES = {}
for _mod in _MODULES:
    _c = _mod.Challenge()
    CHALLENGES[_c.id] = _c


def get(challenge_id: str):
    return CHALLENGES.get(challenge_id)


def all_challenges():
    return list(CHALLENGES.values())


def flag_owner(flag: str):
    """Retourne l'id du challenge correspondant à un flag soumis, sinon None."""
    flag = flag.strip()
    for c in CHALLENGES.values():
        if c.flag == flag:
            return c.id
    return None
