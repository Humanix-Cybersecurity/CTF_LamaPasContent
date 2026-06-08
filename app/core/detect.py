"""Détection de réussite côté serveur.

Toutes les vérifications sont normalisées pour tolérer la mise en forme du
modèle (casse, séparateurs, espaces) tout en restant fiables. On ne fait JAMAIS
confiance au modèle pour déclarer une réussite : on cherche la preuve (secret,
donnée, phrase) dans le texte réellement renvoyé au joueur.
"""
import re


def _compact(s: str) -> str:
    """Minuscule + suppression de tout caractère non alphanumérique."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def contains_secret(text: str, secret: str) -> bool:
    """Le secret apparaît-il, même avec des séparateurs intercalés ?"""
    return _compact(secret) in _compact(text)


def _norm_phrase(s: str) -> str:
    """Minuscule, ponctuation retirée, espaces normalisés."""
    s = re.sub(r"[^a-z0-9\s]", "", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    """Une phrase cible apparaît-elle (à la ponctuation/casse près) ?"""
    return _norm_phrase(phrase) in _norm_phrase(text)
