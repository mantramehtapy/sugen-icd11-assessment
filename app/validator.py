from __future__ import annotations

import re

_STEM = re.compile(r"[&/]")


def validate_codes(codes: list[str], valid_codes: set[str]) -> list[str]:
    result: list[str] = []
    for code in codes:
        normalized = _STEM.split(code.strip().upper())[0].strip()
        if normalized in valid_codes and normalized not in result:
            result.append(normalized)
        if len(result) == 3:
            break
    return result
