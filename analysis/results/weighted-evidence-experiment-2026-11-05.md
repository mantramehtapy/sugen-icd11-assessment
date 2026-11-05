# Weighted evidence retrieval experiment — reverted

Date: 2026-11-05

## Change tested

A temporary shared query representation separated assessment terms, supporting positive terms, and negated terms. Retrieval was changed to weight assessment overlap above supporting overlap and to penalize negated title terms.

## Verification

```text
36 passed in 2.75s
notes 60  missing predictions 0  invalid codes 0  duplicate ids 0
slice A: n=60  top1 0.067  top3 0.167  points 7.5 / 75
SCORE 7.5 / 75
```

Candidate recall changed from the frozen baseline:

```text
baseline: 24/60
weighted experiment: 22/60
```

Failure classification changed from `4 correct / 20 ranking / 36 retrieval` to `4 correct / 18 ranking / 38 retrieval`.

## Decision

Reverted the temporary runtime change because it did not improve score or top-20 candidate recall and increased retrieval failures. The failure report, tests used for the experiment, and output are retained as negative evidence. The next implementation should focus on phrase matching and catalogue hierarchy rather than simply increasing lexical evidence weights.
