"""Mini vector store en mémoire, embeddings via Ollama.

Volontairement minimaliste : pas de service externe, juste ce qu'il faut pour
illustrer un RAG et ses faiblesses (LLM04 empoisonnement, LLM08 récupération
non contrôlée). La similarité est un cosinus en Python pur.
"""
import math
import os

import httpx

from core.llm import OLLAMA_HOST

EMBED_MODEL = os.environ.get("LLM_CTF_EMBED_MODEL", "all-minilm")


async def embed(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
        )
        resp.raise_for_status()
        return resp.json()["embedding"]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class Store:
    """Collection de documents avec recherche par similarité cosinus."""

    def __init__(self):
        self._docs: list[dict] = []  # {id, text, title, vec}

    def __len__(self):
        return len(self._docs)

    async def add(self, text: str, title: str = "", doc_id: str = ""):
        vec = await embed(text)
        self._docs.append(
            {"id": doc_id or f"doc{len(self._docs)}", "text": text, "title": title, "vec": vec}
        )

    async def search(self, query: str, k: int = 3, extra: list[dict] | None = None):
        """Retourne les k documents les plus proches. ``extra`` permet d'ajouter
        des documents éphémères (déjà vectorisés) pour une seule recherche."""
        qv = await embed(query)
        pool = self._docs + (extra or [])
        scored = [(cosine(qv, d["vec"]), d) for d in pool]
        scored.sort(key=lambda t: t[0], reverse=True)
        return [d for _, d in scored[:k]]

    async def make_doc(self, text: str, title: str = "") -> dict:
        """Vectorise un document éphémère sans l'ajouter au store."""
        return {"id": "ephemere", "text": text, "title": title, "vec": await embed(text)}
