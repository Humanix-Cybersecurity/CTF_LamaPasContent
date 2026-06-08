"""Contrat commun à tous les challenges du CTF."""
from __future__ import annotations


class BaseChallenge:
    """Classe de base d'un challenge OWASP LLM.

    Chaque challenge déclare ses métadonnées et implémente ``respond`` qui
    reçoit l'entrée du joueur et renvoie un dictionnaire :

        {
            "reply": str,            # ce que le joueur voit (réponse du LLM/app)
            "objective_met": bool,   # True quand l'objectif d'attaque est atteint
        }

    Le flag n'est révélé par l'API que lorsque ``objective_met`` est vrai.
    La détection de réussite est TOUJOURS faite côté serveur, jamais en
    faisant confiance au texte produit par le modèle.
    """

    id: str = ""               # ex. "llm01"
    owasp: str = ""            # ex. "LLM01:2025"
    title: str = ""
    category: str = ""
    difficulty: str = ""       # Facile / Moyen / Difficile
    description: str = ""       # contexte du scénario
    objective: str = ""        # ce que le joueur doit accomplir
    flag: str = ""
    hints: list[str] = []

    async def respond(self, user_input: str) -> dict:
        raise NotImplementedError
