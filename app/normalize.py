from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)?", re.IGNORECASE)


def normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def tokenize(text: str) -> set[str]:
    return {match.group(0).lower() for match in _TOKEN_RE.finditer(text)}
