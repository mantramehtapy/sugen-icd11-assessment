from __future__ import annotations

import re
from dataclasses import dataclass

from .normalize import normalize_text, tokenize


@dataclass(frozen=True)
class Evidence:
    assessment: list[str]
    symptoms: list[str]
    history: list[str]
    negated: set[str]
    modifiers: dict[str, str]


_MARKERS = {
    "assessment": re.compile(r"\b(?:assessment|impression|diagnosis|diagnosed|dx|a:)\b", re.I),
    "history": re.compile(r"\b(?:history|past medical history|pmh)\b", re.I),
}
_NEGATION = re.compile(r"\b(?:no|not|without|denies|negative for|excluded)\s+([a-z][a-z -]*)", re.I)


def _segments(text: str) -> list[str]:
    return [part.strip(" \t\r\n:;,." ) for part in re.split(r"[\n.]", text) if part.strip()]


def extract_evidence(text: str) -> Evidence:
    assessment: list[str] = []
    history: list[str] = []
    symptoms: list[str] = []
    negated: set[str] = set()
    normalized = normalize_text(text)
    for segment in _segments(normalized):
        if _MARKERS["assessment"].search(segment):
            value = re.split(r"\b(?:assessment|impression|diagnosis|diagnosed|dx|a:)\b", segment, maxsplit=1, flags=re.I)[-1].strip(" :")
            if value:
                assessment.append(value)
        elif _MARKERS["history"].search(segment):
            value = re.split(r"\b(?:history|past medical history|pmh)\b", segment, maxsplit=1, flags=re.I)[-1]
            value = value.strip(" :")
            if value.lower().startswith("of "):
                value = value[3:]
            if value:
                history.append(value)
        else:
            symptoms.append(segment)
    for match in _NEGATION.finditer(normalized):
        phrase = match.group(1).split(" and ")[0].strip()
        if phrase:
            negated.update(tokenize(phrase))
    return Evidence(assessment, symptoms, history, negated, {})
