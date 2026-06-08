"""Client minimal pour le serveur Ollama (micro-LLM en conteneur)."""
import os

import httpx

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.environ.get("LLM_CTF_MODEL", "llama3.2:1b")


async def chat_with_meta(
    messages, temperature: float = 0.0, max_tokens: int = 512
) -> dict:
    """Comme ``chat`` mais retourne aussi les métadonnées utiles.

    Retourne {"content": str, "done_reason": str, "eval_count": int}.
    ``done_reason == "length"`` signale que la génération a été coupée par le
    plafond de tokens (le modèle aurait continué) — utile pour LLM10.
    """
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    async with httpx.AsyncClient(timeout=180) as client:
        resp = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return {
            "content": data["message"]["content"],
            "done_reason": data.get("done_reason", ""),
            "eval_count": data.get("eval_count", 0),
        }


async def chat(messages, temperature: float = 0.0, max_tokens: int = 512) -> str:
    """Envoie une conversation au modèle et retourne le texte de réponse.

    temperature=0 par défaut pour rendre les challenges aussi déterministes
    que possible (le scoring reste validé côté serveur, jamais sur la
    confiance accordée au texte du modèle).
    """
    result = await chat_with_meta(messages, temperature=temperature, max_tokens=max_tokens)
    return result["content"]
