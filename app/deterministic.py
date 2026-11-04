from __future__ import annotations

from dataclasses import dataclass

from .catalog import Catalog
from .evidence import extract_evidence
from .retrieval import retrieve


@dataclass(frozen=True)
class DeterministicResult:
    codes: list[str]
    candidates: list[str]


def choose_codes(text: str, catalog: Catalog, limit: int = 3) -> DeterministicResult:
    evidence = extract_evidence(text)
    search_text = " ".join(evidence.assessment or [text])
    candidates = retrieve(search_text, catalog, limit=20)
    if not candidates:
        candidates = list(catalog.rows[:20])
    ranked: list[tuple[float, str]] = []
    evidence_terms = set()
    for phrase in evidence.assessment:
        evidence_terms.update(phrase.split())
    for row in candidates:
        score = 0.08 * row.depth + (0.15 if row.leaf else 0.0)
        title = row.title.lower()
        score += sum(1.5 for term in evidence_terms if term in title)
        if row.residual and any(term in {"unspecified", "unknown", "other"} for term in evidence_terms):
            score += 0.5
        ranked.append((score, row.code))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    codes = [code for _, code in ranked[:limit] if catalog.is_valid(code)]
    return DeterministicResult(codes=codes, candidates=[row.code for row in candidates])
