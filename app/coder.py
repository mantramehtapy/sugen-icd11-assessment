from __future__ import annotations

import argparse
import os
from pathlib import Path

from .agents import build_coder
from .io import iter_notes, write_prediction


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict ICD-11 codes for JSONL notes")
    parser.add_argument("input_jsonl", type=Path)
    parser.add_argument("output_jsonl", type=Path)
    args = parser.parse_args()
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    args.output_jsonl.write_text("", encoding="utf-8")
    mode = os.getenv("SU_GEN_MODEL_MODE", "deterministic").lower()
    coder = build_coder(mode)
    for note in iter_notes(args.input_jsonl):
        result = coder.predict(str(note.get("text", "")))
        write_prediction(args.output_jsonl, note["id"], result.codes)


if __name__ == "__main__":
    main()
