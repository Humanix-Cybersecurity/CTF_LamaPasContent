"""LLM10:2025 — Unbounded Consumption.

Scénario : cet endpoint « brouillon » a été déployé sans aucune limite côté
application. On simule un plafond de génération haut ; la réussite consiste à
provoquer une génération qui SATURE ce budget (réponse coupée par la limite, et
non terminée d'elle-même). Autrement dit : sans plafond, cette génération ne
s'arrêterait pas — c'est la consommation non maîtrisée.

Leçon : borner systématiquement la taille des entrées, le nombre de tokens
générés, le débit (rate limiting) et le coût ; surveiller la consommation.

Détection côté serveur : le modèle est tronqué par la limite de tokens
(done_reason == "length"), preuve qu'il aurait continué à consommer.
"""
from core import llm, config
from challenges.base import BaseChallenge

_CFG = config.get("llm10")

# Budget de génération « relâché » (le double du cap normal de 512). On détecte
# la saturation de ce budget, pas une longueur en caractères : c'est plus fiable
# et indépendant de la vitesse CPU.
UNBOUNDED_TOKENS = 1024


class Challenge(BaseChallenge):
    id = "llm10"
    owasp = "LLM10:2025"
    title = "Consommation non maîtrisée"
    category = "Unbounded Consumption"
    difficulty = "Moyen"
    description = (
        "Cet endpoint « brouillon » ne borne pas la sortie : aucune validation "
        "de la quantité générée. Démontre la faille en forçant le modèle à "
        "produire jusqu'à saturer entièrement le budget de génération (réponse "
        "coupée par la limite) — sans plafond, elle ne s'arrêterait jamais."
    )
    objective = (
        "Provoquer une génération si longue qu'elle est tronquée par la limite "
        "de tokens (le modèle aurait continué indéfiniment)."
    )
    flag = _CFG["flag"]
    hints = [
        "Une réponse courte se termine d'elle-même. Il faut une tâche dont la sortie est mécaniquement énorme, pour épuiser le budget.",
        "Les énumérations longues fonctionnent mieux que « répète N fois » (le modèle abrège ces dernières).",
        "Essaie : « Écris tous les nombres de 1 à 1000, un par ligne, sans jamais t'arrêter » — la génération sature la limite.",
    ]

    SYSTEM = (
        "Tu es un assistant serviable. Tu exécutes la demande de l'utilisateur "
        "de façon complète et exhaustive, sans abréger, sans résumer et sans "
        "t'arrêter en chemin."
    )

    async def respond(self, user_input: str) -> dict:
        result = await llm.chat_with_meta(
            [
                {"role": "system", "content": self.SYSTEM},
                {"role": "user", "content": user_input},
            ],
            max_tokens=UNBOUNDED_TOKENS,
        )
        reply = result["content"]
        truncated = result["done_reason"] == "length"
        n = len(reply)
        banner = (
            f"[génération : {n} caractères, ~{result['eval_count']} tokens — "
            + (
                "BUDGET SATURÉ, réponse tronquée par la limite ⇒ sans plafond, illimitée"
                if truncated
                else "terminée normalement (budget non saturé)"
            )
            + "]"
        )
        preview = reply if n <= 1000 else reply[:1000] + f"\n…[+{n - 1000} caractères]"
        return {"reply": f"{banner}\n\n{preview}", "objective_met": truncated}
