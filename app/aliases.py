from __future__ import annotations

import re
import unicodedata


ALIASES: dict[str, frozenset[str]] = {
    "htn": frozenset({"hypertension"}),
    "hipertension": frozenset({"hypertension"}),
    "dm2": frozenset({"type 2 diabetes mellitus"}),
    "t2dm": frozenset({"type 2 diabetes mellitus"}),
    "copd": frozenset({"chronic obstructive pulmonary disease"}),
    "chf": frozenset({"heart failure"}),
    "uti": frozenset({"urinary tract infection"}),
    "tb": frozenset({"tuberculosis"}),
    "hiv": frozenset({"human immunodeficiency virus disease"}),
    "sob": frozenset({"shortness of breath"}),
    "af": frozenset({"atrial fibrillation"}),
    "dvt": frozenset({"deep vein thrombosis"}),
    "pe": frozenset({"pulmonary embolism"}),
}


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def expand_aliases(text: str) -> set[str]:
    folded = _fold(text)
    expanded = {folded}
    for source, targets in ALIASES.items():
        if re.search(rf"(?<![a-z0-9]){re.escape(source)}(?![a-z0-9])", folded):
            expanded.update(targets)
    return expanded
