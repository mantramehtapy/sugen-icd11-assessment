from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .catalog import Catalog, load_catalog
from .deterministic import choose_codes
from .ollama_client import OllamaClient
from .validator import validate_codes


@dataclass(frozen=True)
class PredictionResult:
    codes: list[str]
    used_fallback: bool


class AgenticCoder:
    def __init__(
        self,
        model_client: Any | None = None,
        catalog: Catalog | None = None,
        catalog_path: Path | None = None,
    ) -> None:
        self.catalog = catalog or load_catalog(catalog_path or Path("public/data/mms-2026-01.json"))
        self.model_client = model_client

    def predict(self, note: str) -> PredictionResult:
        fallback = choose_codes(note, self.catalog)
        if self.model_client is None:
            return PredictionResult(fallback.codes, True)
        candidates = [
            {"code": row.code, "title": row.title}
            for row in self.catalog.rows
            if row.code in fallback.candidates
        ]
        proposed = self.model_client.choose(candidates, note)
        valid = validate_codes(proposed, {row.code for row in self.catalog.rows})
        candidate_codes = {row["code"] for row in candidates}
        if valid and set(valid).issubset(candidate_codes):
            return PredictionResult(valid, False)
        return PredictionResult(fallback.codes, True)


def build_coder(mode: str = "deterministic") -> AgenticCoder:
    if mode in {"gemma", "auto"}:
        return AgenticCoder(model_client=OllamaClient())
    return AgenticCoder()
