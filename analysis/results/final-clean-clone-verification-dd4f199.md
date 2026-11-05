# Final clean-clone Docker verification — commit `dd4f199`

Date: 2026-11-05

A fresh clone of the private GitHub repository at commit `dd4f199` was tested after Docker Desktop was started.

Commands:

```bash
git rev-parse HEAD
docker compose config --quiet
docker compose build --no-cache coder
docker compose run --rm coder /in/notes.jsonl /out/predictions.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/predictions.jsonl --mms public/data/mms-2026-01.json
```

Result:

```text
HEAD: dd4f199
all Docker commands: exit 0
notes 60  missing predictions 0  invalid codes 0  duplicate ids 0
slice A: n=60  top1 0.067  top3 0.167  points 7.5 / 75
SCORE 7.5 / 75
```

The current final repository therefore passes the clean-clone Docker/output contract on this host. This verifies the development slice only; hidden accuracy and target-machine performance remain unknown.
