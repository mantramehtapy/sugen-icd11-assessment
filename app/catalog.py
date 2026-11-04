from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CatalogRow:
    code: str
    title: str
    chapter: str
    leaf: bool
    residual: bool
    depth: int
    uri: str


@dataclass(frozen=True)
class Catalog:
    rows: tuple[CatalogRow, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "_by_code", {row.code.upper(): row for row in self.rows})

    def is_valid(self, code: str) -> bool:
        return code.strip().upper() in self._by_code

    def get(self, code: str) -> CatalogRow | None:
        return self._by_code.get(code.strip().upper())


def _row(raw: dict[str, Any], line: int) -> CatalogRow:
    required = ("code", "title", "chapter", "leaf", "residual", "depth", "uri")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"catalog row {line} missing fields: {', '.join(missing)}")
    return CatalogRow(
        code=str(raw["code"]).strip().upper(),
        title=str(raw["title"]).strip(),
        chapter=str(raw["chapter"]).strip(),
        leaf=bool(raw["leaf"]),
        residual=bool(raw["residual"]),
        depth=int(raw["depth"]),
        uri=str(raw["uri"]).strip(),
    )


def load_catalog(path: Path) -> Catalog:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("catalog root must be a JSON array")
    rows = tuple(_row(raw, index) for index, raw in enumerate(data, 1))
    if len({row.code for row in rows}) != len(rows):
        raise ValueError("catalog contains duplicate codes")
    return Catalog(rows)
