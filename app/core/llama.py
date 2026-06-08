"""Lama pixel-art en SVG, dont l'expression s'aggrave avec le niveau de colère.

Rendu : une grille de « pixels » (rect SVG), 100 % vectoriel et offline. Le
corps est commun à tous les niveaux ; sourcils, yeux, bouche, teinte du pelage
et effets (vapeur, marques de colère) varient selon le palier 0–6.
"""

PX = 12  # taille d'un pixel en unités SVG
COLS, ROWS = 14, 17

# Pelage (F) et contour (O). 'F' sera teinté selon la colère.
_BASE = [
    "..............",
    "..O........O..",
    "..OO......OO..",
    "..OFO....OFO..",
    "...OFFFFFFO...",
    "..OFFFFFFFFO..",
    "..OFFFFFFFFO..",
    "..OFFFFFFFFO..",
    "..OFFFFFFFFO..",
    "..OFFFFFFFFO..",
    "..OFFFFFFFFO..",
    "...OFFFFFFO...",
    "....OFFFFO....",
    "....OFFFFO....",
    "....OFFFFO....",
    "...OFFFFFFO...",
    "...OOOOOOOO...",
]

_OUTLINE = "#2a2018"
_TEETH = "#fdf6e3"
_PUPIL = "#1a1410"
_WHITE = "#f4ead6"

# Yeux (blanc) — fixes
_EYE_WHITE = [(4, 6), (5, 6), (4, 7), (5, 7), (8, 6), (9, 6), (8, 7), (9, 7)]


def _fur(level: int) -> str:
    """Pelage : beige (calme) → brun-rouge (furieux)."""
    t = level / 6.0
    r = int(216 + (190 - 216) * t)
    g = int(178 + (74 - 178) * t)
    b = int(140 + (60 - 140) * t)
    return f"rgb({r},{g},{b})"


# Expression par palier : pupilles, sourcils, bouche, extras (vapeur, colère).
# Chaque entrée = liste de (col, row) ; la couleur est gérée par catégorie.
def _expr(level: int) -> dict:
    red = "#e23b2b"
    steam = "#bcd8ff"
    if level <= 0:  # BLASÉ — paupières basses, sourire en coin
        return {
            "lids": [(4, 6), (5, 6), (8, 6), (9, 6)],
            "pupils": [(4, 7), (9, 7)],
            "brows": [],
            "mouth": [(6, 9), (7, 9), (8, 10)],
            "steam": [], "anger": [],
        }
    if level == 1:  # AGACÉ
        return {
            "lids": [], "pupils": [(5, 6), (8, 6)],
            "brows": [(4, 5), (5, 5), (8, 5), (9, 5)],
            "mouth": [(5, 9), (6, 9), (7, 9), (8, 9)],
            "steam": [], "anger": [],
        }
    if level == 2:  # CONTRARIÉ — petit froncement
        return {
            "lids": [], "pupils": [(5, 6), (8, 6)],
            "brows": [(4, 4), (5, 5), (8, 5), (9, 4)],
            "mouth": [(5, 10), (6, 9), (7, 9), (8, 10)],
            "steam": [], "anger": [],
        }
    if level == 3:  # ÉNERVÉ — sourcils en colère
        return {
            "lids": [], "pupils": [(5, 7), (8, 7)],
            "brows": [(3, 4), (4, 4), (5, 5), (8, 5), (9, 4), (10, 4)],
            "mouth": [(5, 10), (6, 9), (7, 9), (8, 10)],
            "steam": [(1, 3)], "anger": [],
        }
    if level == 4:  # REMONTÉ — bouche ouverte, vapeur
        return {
            "lids": [], "pupils": [(5, 7), (8, 7)],
            "brows": [(3, 4), (4, 4), (5, 5), (8, 5), (9, 4), (10, 4)],
            "mouth": [(5, 9), (6, 9), (7, 9), (8, 9), (5, 10), (8, 10)],
            "teeth": [(6, 10), (7, 10)],
            "steam": [(1, 3), (12, 2)], "anger": [(11, 4)],
        }
    if level == 5:  # FURIEUX — yeux rouges, plus de vapeur
        return {
            "lids": [], "pupils_red": [(5, 7), (8, 7)],
            "brows": [(3, 3), (4, 4), (5, 5), (8, 5), (9, 4), (10, 3)],
            "mouth": [(5, 9), (6, 9), (7, 9), (8, 9), (5, 10), (6, 10), (7, 10), (8, 10)],
            "teeth": [(6, 9), (7, 10)],
            "steam": [(1, 2), (1, 3), (12, 2), (12, 3)], "anger": [(11, 4), (2, 4)],
        }
    # level >= 6 : EN PLS — meltdown, gueule grande ouverte
    return {
        "lids": [], "pupils_red": [(4, 6), (5, 7), (8, 7), (9, 6)],
        "brows": [(3, 3), (4, 4), (5, 5), (8, 5), (9, 4), (10, 3)],
        "mouth": [(5, 9), (6, 9), (7, 9), (8, 9),
                  (5, 10), (6, 10), (7, 10), (8, 10),
                  (5, 11), (6, 11), (7, 11), (8, 11)],
        "teeth": [(6, 9), (7, 9)],
        "steam": [(0, 1), (1, 2), (12, 1), (13, 2), (1, 3), (12, 3)],
        "anger": [(11, 4), (2, 4), (11, 5)],
    }


def _rect(x, y, color):
    return f'<rect x="{x*PX}" y="{y*PX}" width="{PX}" height="{PX}" fill="{color}"/>'


def render(level: int) -> str:
    level = min(max(int(level), 0), 6)
    fur = _fur(level)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {COLS*PX} {ROWS*PX}" '
        f'shape-rendering="crispEdges" role="img" aria-label="Lama niveau de colère {level}">'
    ]
    # Corps
    for y, row in enumerate(_BASE):
        for x, ch in enumerate(row):
            if ch == "O":
                parts.append(_rect(x, y, _OUTLINE))
            elif ch == "F":
                parts.append(_rect(x, y, fur))
    # Yeux (blanc)
    for x, y in _EYE_WHITE:
        parts.append(_rect(x, y, _WHITE))

    e = _expr(level)
    for x, y in e.get("lids", []):
        parts.append(_rect(x, y, fur))            # paupière = couleur pelage
    for x, y in e.get("pupils", []):
        parts.append(_rect(x, y, _PUPIL))
    for x, y in e.get("pupils_red", []):
        parts.append(_rect(x, y, "#e23b2b"))
    for x, y in e.get("brows", []):
        parts.append(_rect(x, y, _OUTLINE))
    for x, y in e.get("mouth", []):
        parts.append(_rect(x, y, "#5a1e1e"))
    for x, y in e.get("teeth", []):
        parts.append(_rect(x, y, _TEETH))
    for x, y in e.get("anger", []):
        parts.append(_rect(x, y, "#e23b2b"))
    for x, y in e.get("steam", []):
        parts.append(_rect(x, y, "#bcd8ff"))

    parts.append("</svg>")
    return "".join(parts)
