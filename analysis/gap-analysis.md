# Requirements Gap Analysis

Updated after the first deterministic implementation and Docker run.

| Requirement | Status | Evidence |
|---|---|---|
| Exact Docker command | PASS | `docker compose config --quiet` and `docker compose run --rm coder /in/notes.jsonl /out/predictions.jsonl` both exited 0 |
| No API key required | PASS | deterministic Docker run completed without API credentials |
| One output per input | PASS | 60 input lines produced 60 output lines |
| Valid MMS codes | PASS | supplied scorer reported 0 invalid codes |
| Clean-clone build | OPEN | clean-clone test still required |
| Supplied scorer validation | PASS | scorer completed: 0 missing, 0 invalid, 0 duplicates |
| Git bundle with real history | OPEN | repository has real commits; final bundle not created |
| Development accuracy | MEASURED | deterministic baseline: top-1 0.050, top-3 0.133, score 5.8 / 75 |
| Agentic Gemma mode | OPEN | Gemma 4 E4B download and benchmark in progress |
| Hidden generalisation score | UNKNOWN | hidden notes are unavailable |
