# Local Benchmark — Measured Results

## Deterministic baseline before retrieval improvements

Command:

```bash
.venv/Scripts/python.exe -m app public/data/dev_notes.jsonl outputs/dev-deterministic.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/dev-deterministic.jsonl --mms public/data/mms-2026-01.json
```

Observed at the frozen baseline commit:

```text
notes 60  missing predictions 0  invalid codes 0  duplicate ids 0
slice A: n=60  top1 0.067  top3 0.150  points 7.1 / 75
SCORE 7.1 / 75
```

Candidate recall analysis found the gold code in the top-20 candidate set for 20/60 notes (33.3%). The score is not being hidden or inflated with development gold labels.

## Retrieval improvement: bounded aliases and query stopwords

Commit: `d9bf3a6`

The change added a small, explainable alias map for common abbreviations and a stopword filter for retrieval queries. It does not read `gold` labels at runtime and does not add a large external model or embedding dependency.

Observed:

```text
27 passed in 2.36s
notes 60  missing predictions 0  invalid codes 0  duplicate ids 0
slice A: n=60  top1 0.067  top3 0.167  points 7.5 / 75
SCORE 7.5 / 75
```

Candidate recall improved from 20/60 (33.3%) to 24/60 (40.0%). Top-3 accuracy improved from 15.0% to 16.7%, while top-1 remained 6.7%.

The complete per-note experiment record is in `analysis/results/retrieval-alias-2026-11-05.json`.

## Docker verification status

A prior local Docker baseline existed, but the clean-clone Docker contract must be re-run and recorded after the current changes. Do not treat the historical local result as final submission evidence until the fresh-clone command completes:

```bash
docker compose config --quiet
docker compose build --no-cache coder
docker compose run coder /in/notes.jsonl /out/predictions.jsonl
```

## Gemma benchmark

The local `gemma4:e4b` run completed earlier with 60 valid predictions and the same 7.1 / 75 score as the deterministic output. Its output was identical to the deterministic output on all 60 notes. The current work should not rely on Gemma until endpoint propagation, timeout behavior, response validation, call counts, and actual model contribution are instrumented.

## Interpretation

The alias change produced a small measured gain, especially in top-3 and candidate recall, but the project remains far from submission-ready. The next quality work should improve evidence and retrieval without using development gold labels, then repeat the scorer and compare against this recorded baseline.

