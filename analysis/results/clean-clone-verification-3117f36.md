# Clean-clone verification — commit `3117f36`

Date: 2026-11-05

## Fresh clone

The private GitHub repository was cloned into:

```text
C:\Users\rajiv\AppData\Local\hermes\cache\scratch\sugen-clean-3117f36
```

Verified:

- cloned from `mantramehtapy/sugen-icd11-assessment`;
- HEAD: `3117f36`;
- working tree clean after clone;
- branch `main` tracks `origin/main`.

## Docker contract

Docker Desktop was started and the server became available as version `29.6.1`.

These commands were run from the fresh clone:

```bash
docker compose config --quiet
docker compose build --no-cache coder
docker compose run --rm coder /in/notes.jsonl /out/predictions.jsonl
```

Result: all commands exited successfully. The image built from the clean clone and the exact coder command completed normally.

## Supplied scorer result

```text
notes 60  missing predictions 0  invalid codes 0  duplicate ids 0
slice A: n=60  top1 0.067  top3 0.167  points 7.5 / 75
SCORE 7.5 / 75
```

Independent output checks:

```text
lines=60
unique_ids=60
max_codes=3
```

## Status

- Fresh Git clone: **PASS**
- Docker configuration: **PASS**
- Clean-clone image build: **PASS**
- Exact required run: **PASS**
- Supplied scorer: **PASS**
- Missing predictions: **0**
- Invalid codes: **0**
- Duplicate IDs: **0**

This verifies the development contract on the current host. It does not prove hidden-set accuracy or target-machine performance.
