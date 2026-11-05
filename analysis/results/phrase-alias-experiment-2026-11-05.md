# Phrase-alias retrieval experiment — 2026-11-05

## Change

Added a small, documented phrase-alias set in `app/aliases.py` for common clinical language that differs from ICD-11 catalogue wording:

- viral URTI → acute upper respiratory infection
- asthma attack → asthma with exacerbation
- vaginal thrush → vulvovaginal candidosis
- chickenpox → varicella
- benign enlargement of the prostate → hyperplasia of prostate
- severe preeclampsia → severe pre-eclampsia
- underactive thyroid → hypothyroidism

## Result

```text
34 passed in 2.68s
notes 60  missing predictions 0  invalid codes 0  duplicate ids 0
slice A: n=60  top1 0.083  top3 0.200  points 9.2 / 75
SCORE 9.2 / 75
```

Compared with the frozen baseline:

| Metric | Baseline | Phrase aliases | Change |
|---|---:|---:|---:|
| Top-1 | 4/60 (6.7%) | 5/60 (8.3%) | +1 note |
| Top-3 | 10/60 (16.7%) | 12/60 (20.0%) | +2 notes |
| Top-20 candidate recall | 24/60 (40.0%) | 27/60 (45.0%) | +3 notes |
| Score | 7.1 / 75 baseline | 9.2 / 75 | +2.1 points |
| Missing predictions | 0 | 0 | unchanged |
| Invalid codes | 0 | 0 | unchanged |
| Duplicate IDs | 0 | 0 | unchanged |

The comparison uses the original frozen baseline for score context; the current pre-alias implementation was 7.5 / 75.

## Changed notes

- `dev-002`: gold `CA07.0` entered the candidate list but remained a ranking failure.
- `dev-003`: gold `CA23.30` entered the candidate list at rank 12 but remained outside top 3.
- `dev-005`: gold `1F23.10` entered the candidate list and became top-1 correct.

## Decision

Keep the phrase-alias change. It improved score, top-3, and candidate recall without structural regressions. The next work should improve ranking among newly retrieved candidates and address ambient transcripts, not broadly increase lexical weights.
