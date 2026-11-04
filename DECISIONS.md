# Decisions

## 2026-11-04 — Clean rebuild boundary

- Commit: pending
- Decision: Preserve `SugenEngTest.tgz` and the complete `public/` tree unchanged; build the implementation separately under `app/` and `tests/`.
- Options considered: modify the supplied files, reorganize the supplied tree, or keep it as a protected reference. Keeping it unchanged preserves the client’s relative paths and scorer contract.
- Evidence: `public/BRIEF.md` supplies the exact Docker command and scorer paths.
- Revisit: only if the required Docker command proves incompatible without changing protected files.

## 2026-11-04 — Bounded Agentic RAG

- Commit: pending
- Decision: Use evidence extraction, deterministic catalog retrieval, and one constrained adjudication step rather than an unrestricted autonomous agent.
- Options considered: deterministic-only ranking, one unconstrained model prompt, or bounded Agentic RAG. The bounded design allows local reasoning while keeping latency, output shape, and failure behavior testable.
- Evidence: Dad requested Agentic RAG; the brief requires valid catalog codes, no-key behavior, and completion within a time limit.
- Revisit: remove the model stage if CPU benchmarks do not fit the grading budget.

## 2026-11-04 — Gemma 4 E4B is optional, not a hard dependency

- Commit: pending
- Decision: Prefer local `gemma4:e4b` for development experiments, but keep deterministic prediction complete when Ollama or Gemma is unavailable.
- Options considered: require Ollama, use a cloud API, or keep Gemma optional. A hard local-model dependency may fail on Sugen’s grading machine.
- Evidence: the brief requires a no-key path and restricts runtime network access.
- Revisit: package a model only if image size, licensing, CPU latency, and clean-clone tests justify it.
