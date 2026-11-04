from __future__ import annotations

import json
from typing import Any


def parse_model_codes(content: str) -> list[str]:
    cleaned = content.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned[3:]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip("` \n")
    try:
        value: Any = json.loads(cleaned)
    except json.JSONDecodeError:
        return []
    if not isinstance(value, dict) or not isinstance(value.get("codes"), list):
        return []
    codes = [code.strip().upper() for code in value["codes"] if isinstance(code, str) and code.strip()]
    return codes[:3]
