# Local Benchmark — Initial Results

## Deterministic baseline

Command:

```bash
.venv/Scripts/python.exe -m app public/data/dev_notes.jsonl outputs/dev-deterministic.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/dev-deterministic.jsonl --mms public/data/mms-2026-01.json
```

Observed:

```text
notes 60  missing predictions 0  invalid codes 0  duplicate ids 0
slice A: n=60  top1 0.050  top3 0.133  points 5.8 / 75
SCORE 5.8 / 75
```

The deterministic path satisfies the output contract but its initial ranking quality is poor. This is useful evidence: the system must improve retrieval and/or adjudication before submission. The score is not being hidden or inflated with development gold labels.

## Docker verification

Command:

```bash
docker compose build --no-cache coder
docker compose run --rm coder /in/notes.jsonl /out/predictions.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/predictions.jsonl --mms public/data/mms-2026-01.json
```

Observed:

- image build exited 0;
- exact Compose run exited 0;
- 60 output lines were produced;
- 0 missing predictions;
- 0 invalid codes;
- 0 duplicate IDs;
- score 5.8 / 75.

## Gemma benchmark status

`gemma4:e4b` is not currently installed. A local Ollama pull has been started so the model can be tested without an API key. The benchmark remains incomplete until the pull finishes and the model is exercised through the bounded candidate-selection client.

The Gemma comparison must record latency, failure rate, JSON validity, candidate-subset compliance, top-1, top-3, and score. If Gemma does not improve quality within the runtime budget, the deterministic architecture must be revised rather than hiding the result.
