# Decisions

This log records decisions made during the Sugen Technologies take-home assessment. Times are recorded only when available from the work record; no timestamps are invented.

## 2026-11-04 — Clean rebuild boundary

- Commit: `7caa5f4`
- Decision: Preserve `SugenEngTest.tgz` and the complete `public/` tree unchanged; build implementation separately under `app/` and `tests/`.
- Options considered: modify supplied files, reorganize the supplied tree, or keep it as a protected reference.
- Evidence: `public/BRIEF.md` supplies the exact Docker command and scorer paths.
- Revisit: only if the required command proves incompatible without changing protected files.

## 2026-11-04 — Bounded Agentic RAG

- Commit: `3357836`
- Decision: Use evidence extraction, deterministic catalogue retrieval, and one constrained adjudication step rather than an unrestricted autonomous agent.
- Options considered: deterministic-only ranking, one unconstrained model prompt, or bounded Agentic RAG.
- Evidence: Dad requested Agentic RAG; the brief requires valid catalogue codes, no-key behavior, and a time limit.
- Revisit: remove the model stage if CPU benchmarks do not fit the grading budget.

## 2026-11-04 — Gemma 4 E4B is optional, not a hard dependency

- Commit: `3357836`
- Decision: Prefer local `gemma4:e4b` for development experiments, but keep deterministic prediction complete when Ollama or Gemma is unavailable.
- Options considered: require Ollama, use a cloud API, or keep Gemma optional.
- Evidence: the brief requires a no-key path and restricts runtime network access; the Gemma run later matched deterministic output at 7.1 / 75.
- Revisit: keep or remove the optional path after endpoint, timeout, contribution, and throughput evidence is complete.

## 2026-11-05 — Freeze retrieval baseline before changes

- Commit: `795cedb`
- Decision: Record per-note top-20 candidate recall and the supplied score before modifying retrieval.
- Options considered: change ranking immediately or establish a measurable baseline first.
- Evidence: gold code was present in top-20 candidates for 20/60 notes; score was 7.1 / 75.
- Revisit: compare every retrieval change against `analysis/results/baseline-2026-11-05.json`.

## 2026-11-05 — Preserve assessment/history boundaries and negated evidence

- Commit: `e6ab883`
- Decision: Keep recognized note sections separate and capture all items in a negated phrase.
- Options considered: retain the loose segment parser or add a bounded section/negation representation.
- Evidence: the regression case “denies headache and chest pain” initially captured only “headache”; four focused tests and the full suite passed after the change.
- Revisit: add broader section markers only when a failing note demonstrates the need.

## 2026-11-05 — Penalize unsupported specificity only with evidence

- Commit: `0b3f1b0`
- Decision: Penalize selected unsupported detail terms and add a narrow hypertension regression without applying a broad residual-code bonus.
- Options considered: globally prefer `.Z`, globally penalize all title terms, or use small evidence-based penalties.
- Evidence: simple hypertension initially ranked ocular hypertension; the final change preserved the 7.1 / 75 score and all 24 tests passed at that point.
- Revisit: expand the detail lexicon only after a measured failure and a regression test.

## 2026-11-05 — Bounded clinical aliases and query stopwords

- Commit: `d9bf3a6`
- Decision: Expand a small documented alias set for common abbreviations and remove generic query stopwords such as “known” and “assessment” before retrieval.
- Options considered: add a large embedding/translation dependency, hard-code development labels, or use a small explainable alias layer.
- Evidence: top-20 gold-candidate recall improved from 20/60 (33.3%) to 24/60 (40.0%); top-3 improved from 15.0% to 16.7%; score improved to 7.5 / 75; 27 tests passed.
- Revisit: add aliases only from documented public/common terminology and keep measuring hidden-risk proxies.

## 2026-11-05 — Instrument optional Gemma endpoint and failures

- Commit: `6335cbe`
- Decision: Read `OLLAMA_HOST`, normalize the endpoint, count calls/successes/parse failures/timeouts/transport failures, and return an empty proposal so the deterministic caller can fall back.
- Options considered: leave loopback hard-coded, allow unbounded retries, or add bounded observable behavior.
- Evidence: Dad’s review found that Compose set `OLLAMA_HOST` while the client ignored it; four focused client tests and 30 total tests passed after the change.
- Revisit: run a complete Gemma benchmark only after the Docker endpoint is reachable and model contribution is recorded.

## 2026-11-05 — Record Docker verification honestly

- Commit: `ed5d46b`
- Decision: Clone the private repository fresh and record Docker as blocked when the Docker daemon is unreachable rather than claiming a pass.
- Options considered: report the historical local Docker run as final, simulate the result, or preserve the blocker explicitly.
- Evidence: fresh clone reached commit `6335cbe`; `docker version` failed because the Docker Desktop Linux engine pipe was unavailable.
- Revisit: start Docker Desktop and run the exact required command from the fresh clone.

## 2026-11-05 — Complete README with verified limits

- Commit: `9887059`
- Decision: Replace the placeholder README with the current score, data boundary, throughput limitation, AI-tooling error, and open verification gates.
- Options considered: omit weaknesses or state only verified facts.
- Evidence: Dad’s review explicitly identified the placeholder README and missing required fields.
- Revisit: replace the pending commit with the real commit SHA after the documentation commit is created.

## 2026-11-05 — Final bundle remains gated

- Commit: `9887059`
- Decision: Do not create the final Git bundle until clean-clone Docker verification, final documentation, hours statement, and final tests pass.
- Options considered: create a provisional bundle now or wait for final validation.
- Evidence: Docker is currently blocked and the hidden score is unknown.
- Revisit: create `RajivMehta-Sugen-ICD11.bundle` only at the verified final tip.

