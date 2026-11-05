from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.catalog import load_catalog
from app.deterministic import choose_codes
from app.evidence import extract_evidence


def classify_failure(*, gold_in_candidates: bool, predicted_top1: bool) -> str:
    if predicted_top1:
        return "correct"
    if gold_in_candidates:
        return "ranking"
    return "retrieval"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def build_report(
    notes_path: Path,
    catalog_path: Path,
    predictions_path: Path,
) -> list[dict[str, Any]]:
    notes = _read_jsonl(notes_path)
    predictions = {row["id"]: row for row in _read_jsonl(predictions_path)}
    catalog = load_catalog(catalog_path)
    rows: list[dict[str, Any]] = []

    for note in notes:
        note_id = str(note["id"])
        text = str(note.get("text", ""))
        gold = [str(code).strip().upper() for code in note.get("gold", [])]
        prediction = predictions.get(note_id, {})
        predicted_codes = [str(code).strip().upper() for code in prediction.get("codes", [])]
        result = choose_codes(text, catalog)
        evidence = extract_evidence(text)
        candidate_rows = [catalog.get(code) for code in result.candidates]
        candidate_rows = [row for row in candidate_rows if row is not None]
        candidate_codes = [row.code for row in candidate_rows]
        gold_rank = next((candidate_codes.index(code) + 1 for code in gold if code in candidate_codes), None)
        classification = classify_failure(
            gold_in_candidates=gold_rank is not None,
            predicted_top1=bool(predicted_codes and gold and predicted_codes[0] == gold[0]),
        )
        rows.append(
            {
                "id": note_id,
                "style": note.get("style", ""),
                "classification": classification,
                "gold_code": gold[0] if gold else None,
                "gold_rank": gold_rank,
                "predicted_codes": predicted_codes,
                "assessment": evidence.assessment,
                "symptoms": evidence.symptoms,
                "history": evidence.history,
                "negated": sorted(evidence.negated),
                "candidates": [
                    {"code": row.code, "title": row.title, "rank": rank}
                    for rank, row in enumerate(candidate_rows, 1)
                ],
            }
        )
    return rows


def _write_markdown(rows: list[dict[str, Any]], path: Path) -> None:
    counts = Counter(row["classification"] for row in rows)
    lines = [
        "# Retrieval failure report",
        "",
        f"Notes analysed: {len(rows)}",
        "",
        "## Classification counts",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {counts.get(name, 0)} |" for name in ("correct", "ranking", "retrieval"))
    lines.extend(["", "## Retrieval misses", ""])
    misses = [row for row in rows if row["classification"] == "retrieval"]
    for row in misses:
        top = ", ".join(f"{item['code']} {item['title']}" for item in row["candidates"][:5])
        lines.append(f"- `{row['id']}` gold `{row['gold_code']}`; assessment: {' | '.join(row['assessment']) or '(none)'}; top candidates: {top}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notes", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()
    rows = build_report(args.notes, args.catalog, args.predictions)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_markdown(rows, args.markdown_out)
    counts = Counter(row["classification"] for row in rows)
    print(json.dumps({"notes": len(rows), "counts": counts}, default=dict))


if __name__ == "__main__":
    main()
