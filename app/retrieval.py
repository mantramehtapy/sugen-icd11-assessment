from __future__ import annotations

import math
from collections import Counter

from .catalog import Catalog, CatalogRow
from .normalize import normalize_text, tokenize


def _terms(row: CatalogRow) -> set[str]:
    return tokenize(row.title)


def retrieve(text: str, catalog: Catalog, limit: int = 20) -> list[CatalogRow]:
    query = tokenize(text)
    if not query:
        return list(catalog.rows[:limit])
    document_frequency = Counter()
    row_terms: dict[str, set[str]] = {}
    for row in catalog.rows:
        terms = _terms(row)
        row_terms[row.code] = terms
        document_frequency.update(terms)
    total = len(catalog.rows)
    normalized_query = normalize_text(text)
    scored: list[tuple[float, CatalogRow]] = []
    for row in catalog.rows:
        terms = row_terms[row.code]
        overlap = query & terms
        score = sum(math.log((total + 1) / (document_frequency[token] + 1)) for token in overlap)
        if normalize_text(row.title) in normalized_query:
            score += 8.0
        score += 0.08 * row.depth
        if row.leaf:
            score += 0.05
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], -item[1].depth, item[1].code))
    return [row for _, row in scored[:limit]]
