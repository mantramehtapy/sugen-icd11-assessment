# Sugen ICD-11 coder

This repository contains an offline-first ICD-11 MMS 2026-01 outpatient-note coder for the Sugen Technologies take-home assessment. It reads JSONL notes and writes one JSON object per input with up to three valid codes, best first.

## Run

From a clean clone, the required command is:

```bash
docker compose run coder /in/notes.jsonl /out/predictions.jsonl
```

The default path requires no API key and uses deterministic catalogue retrieval/ranking. An optional local Ollama/Gemma path can be enabled for development experiments; Gemma is not a required grading dependency.

## Development score

Verified with the supplied `public/score.py` on the 60 supplied development notes:

- top-1: **0.067** (4/60)
- top-3: **0.167** (10/60)
- core score: **7.5 / 75**
- structural checks: 60/60 output lines, 0 missing, 0 invalid codes, 0 duplicate IDs
- latest automated suite: **30 passed**

The score is low and the project is not submission-ready. The latest retrieval improvement increased top-20 gold-candidate recall from 20/60 to 24/60 by adding bounded clinical aliases and query stopwords.

## Hidden-score estimate

No hidden notes or hidden labels are available. A defensible hidden score cannot yet be measured. The current estimate is **below the development score until clean-clone Docker verification and broader evaluation are complete**; this is an estimate, not a result.

## Data sources

The runtime uses the supplied catalogue at `public/data/mms-2026-01.json` and the supplied brief/scorer. Development notes at `public/data/dev_notes.jsonl` are used for evaluation only; their `gold` labels are not read by runtime code. The added alias map in `app/aliases.py` is a small, explainable set of common abbreviations and spelling variants.

## Evaluation beyond the 60

A 600-note repeated-development-input run was used only to inspect throughput and output completion. It does **not** measure hidden accuracy or generalisation. A clean-clone Docker run remains open because Docker Desktop was not reachable during the latest verification attempt.

## AI-tooling error caught

The local Gemma model sometimes returned JSON inside Markdown code fences. The parser was updated to accept fenced JSON safely and a regression test was added. A separate evidence regression caught loss of the second item in a negated phrase such as “denies headache and chest pain.”

## Decision log and history

`DECISIONS.md` records architectural choices and trade-offs. The Git history is incremental and unsquashed. The deterministic path is bounded and explainable; optional Gemma calls are constrained and must fall back safely.

## Current limitations

- Candidate retrieval remains the main quality bottleneck.
- Ambient-note and multilingual performance require further evaluation.
- Gemma has not improved the measured development score and needs endpoint/timeout/contribution instrumentation before being considered for grading.
- Clean-clone Docker verification, final decision-log completion, final hours statement, and the final Git bundle remain open.

**Hours spent:** to be confirmed from the project time record before submission.

