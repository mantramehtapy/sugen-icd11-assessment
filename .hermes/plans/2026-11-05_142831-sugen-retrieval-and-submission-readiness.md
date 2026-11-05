# Sugen ICD-11 Retrieval and Submission-Readiness Plan

> **For Hermes:** Use subagent-driven development skill to implement this plan task-by-task after Mantra approves it. Do not delete protected company files or rewrite real Git history.

**Goal:** Raise the honest ICD-11 development score by improving candidate retrieval and clinical evidence handling, then verify the exact Docker contract and complete every required submission artifact without claiming hidden performance.

**Architecture:** Keep the deterministic no-key path as the authoritative baseline. Improve it in two bounded layers: first extract structured evidence and normalize clinical wording; then retrieve and rank a small candidate set using explainable signals, explicit contradiction penalties, parent/child rules, residual handling, and language-aware aliases. Keep Gemma optional and disabled by default until its Ollama endpoint, timeout behavior, response validation, contribution telemetry, and 600-note runtime are proven.

**Tech Stack:** Python 3.11/3.14-compatible standard-library implementation, pytest, supplied ICD-11 MMS 2026-01 JSON catalogue, supplied `public/score.py`, Docker Compose, optional Ollama `gemma4:e4b`, Git/GitHub.

---

## Current context and assumptions

- Canonical workspace: `C:\Users\rajiv\OneDrive\Desktop\work\sugen_health`.
- Protected files must remain unchanged:
  - `SugenEngTest.tgz`
  - `public/BRIEF.md`
  - `public/score.py`
  - `public/data/dev_notes.jsonl`
  - `public/data/mms-2026-01.json`
  - `public/data/predictions.example.jsonl`
- Current repository head reviewed by Dad: `eecbeb5`.
- Current measured development result: top-1 `4/60 = 0.067`, top-3 `9/60 = 0.150`, score `7.1 / 75`.
- Current structural result: 60/60 output lines, zero missing predictions, zero invalid codes, zero duplicate IDs, and 21 passing tests.
- Dad’s review reports that the gold code is in the top-20 candidate set for only 20/60 notes; 40/60 cannot be recovered by a model selector.
- Dad reports ambient-note top-1 accuracy of 0/15, weak negation handling, merged sections, unsupported specificity, and poor non-English matching.
- The local Gemma output matched deterministic output on the 60-note run. Its actual contribution is not yet instrumented.
- The exact Docker command and clean-clone build must be re-verified with saved evidence. A previous local Docker run existed, but Dad could not verify Docker during his review; do not treat the old result as final submission evidence.
- Hidden notes and hidden accuracy are unavailable. Any hidden-score statement must remain an estimate.
- No destructive cleanup, final bundle, email, or submission is allowed until the implementation and documents pass the final checklist.

## Acceptance criteria

The work is complete only when all of the following are true:

1. The deterministic score improves measurably or the report explains with evidence why a proposed change was rejected.
2. Every ranking change has focused regression tests and does not use development gold labels at runtime.
3. Negation, section boundaries, unsupported specificity, parent/child relationships, residual codes, and multilingual aliases have explicit tests.
4. Gemma is either correctly bounded and instrumented or clearly kept optional and disabled by default.
5. `docker compose build` and `docker compose run coder /in/notes.jsonl /out/predictions.jsonl` work from a fresh clone.
6. The exact supplied scorer reports structural validity without invalid codes or missing predictions.
7. A 600-note throughput run is documented as throughput only, not hidden accuracy.
8. `README.md` is one page or less and contains every required field from `public/BRIEF.md`.
9. `DECISIONS.md` contains dated entries linked to real commits, measurements, trade-offs, and revisit conditions.
10. A truthful hours-spent line exists.
11. The final Git bundle is created only after validation, and its commit is pushed to the private GitHub repository if that remains desired.

---

# Step-by-step implementation plan

Each code task follows TDD: write a failing test, run it to prove failure, implement the smallest change, run the focused test and full suite, then commit.

## Task 1: Freeze a measurable baseline and create an experiment record

**Objective:** Capture the exact current score, output validity, candidate-recall baseline, and repository state before changing ranking behavior.

**Files:**
- Create: `analysis/results/baseline-2026-11-05.json`
- Create: `analysis/results/baseline-2026-11-05.md`
- Read only: `public/score.py`, `public/data/dev_notes.jsonl`, `public/data/mms-2026-01.json`

**Steps:**

1. Run the current test suite:

   ```bash
   .venv/Scripts/python.exe -m pytest -q
   ```

   Expected: `21 passed`.

2. Generate a deterministic prediction file and run the supplied scorer:

   ```bash
   .venv/Scripts/python.exe -m app public/data/dev_notes.jsonl outputs/dev-deterministic.jsonl
   python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/dev-deterministic.jsonl --mms public/data/mms-2026-01.json
   ```

   Expected current baseline: top-1 `0.067`, top-3 `0.150`, score `7.1 / 75`, zero missing/invalid/duplicate outputs.

3. Add a small read-only evaluation script under `analysis/` that records, per note, whether each gold code appears in the retrieved top-20 candidate set. Do not import gold labels into `app/`.

4. Save the score, candidate recall, note-style breakdown, runtime, commit SHA, and command lines in the two baseline files.

5. Commit:

   ```bash
   git add analysis/results/baseline-2026-11-05.*
   git commit -m "analysis: freeze retrieval baseline"
   ```

**Verification:** The baseline files must contain the actual command output and current commit SHA; no runtime module may read them.

---

## Task 2: Add a test fixture for note sections and explicit negation

**Objective:** Make section boundaries and negation behavior observable before changing extraction code.

**Files:**
- Modify: `tests/test_evidence.py`
- Modify: `app/evidence.py`

**Step 1: Write failing tests**

Add tests with this shape:

```python
def test_sections_do_not_merge_history_into_assessment():
    note = "Assessment: hypertension. History: prior ocular hypertension."
    evidence = extract_evidence(note)
    assert evidence.assessment == ["hypertension"]
    assert evidence.history == ["prior ocular hypertension"]


def test_negated_condition_is_not_positive_evidence():
    note = "Assessment: hypertension. Denies headache and chest pain."
    evidence = extract_evidence(note)
    assert "headache" in evidence.negated
    assert "chest pain" in evidence.negated
    assert "headache" not in evidence.positive_terms
    assert "chest pain" not in evidence.positive_terms
```

2. Run:

   ```bash
   .venv/Scripts/python.exe -m pytest tests/test_evidence.py::test_sections_do_not_merge_history_into_assessment tests/test_evidence.py::test_negated_condition_is_not_positive_evidence -q
   ```

   Expected: FAIL against the current implementation if either behavior is missing.

**Step 2: Implement minimally**

- Split only on recognized section markers such as `assessment`, `impression`, `history`, `symptoms`, and `plan`.
- Preserve the marker’s section name in structured evidence.
- Add a `positive_terms` collection that excludes spans under negation markers (`denies`, `no`, `without`, `negative for`, `ruled out`).
- Do not attempt a general NLP parser or clinical inference engine.

**Step 3: Verify and commit**

```bash
.venv/Scripts/python.exe -m pytest tests/test_evidence.py -q
.venv/Scripts/python.exe -m pytest -q
git add app/evidence.py tests/test_evidence.py
git commit -m "fix: preserve sections and exclude negated evidence"
```

Expected: focused tests pass, then the full suite passes.

---

## Task 3: Add regression tests for unsupported specificity

**Objective:** Prevent a simple diagnosis from being upgraded to a more specific but unsupported child code.

**Files:**
- Modify: `tests/test_deterministic.py`
- Modify: `app/deterministic.py`

**Step 1: Write failing tests**

Add a small fake catalogue fixture containing parent, simple, and unsupported-specific candidates:

```python
def test_simple_hypertension_does_not_select_ocular_hypertension(fake_catalog):
    result = choose_codes("Assessment: hypertension.", fake_catalog)
    assert result.codes[0] == "BA00.Z"


def test_uncomplicated_malaria_rejects_cerebral_and_congenital_candidates(catalog):
    result = choose_codes("Assessment: uncomplicated falciparum malaria.", catalog)
    assert result.codes[0] == "1F40.Z"
```

2. Run the focused tests and record the failure if the first code is too specific.

**Step 2: Implement minimally**

Use explicit contradiction penalties. The scoring shape should remain explainable:

```python
score = lexical_score
score += evidence_match_score
score += leaf_bonus
score -= unsupported_specificity_penalty
score -= negated_or_contradicted_penalty
```

- Penalize candidate title terms absent from positive evidence when they imply a complication, body site, congenital status, pregnancy, severity, resistance, or other status not stated by the note.
- Do not penalize `.Z` merely because the note uses ordinary clinical wording; unspecified is appropriate when details are absent.
- Keep the rule set small and test-driven.

**Step 3: Verify and commit**

```bash
.venv/Scripts/python.exe -m pytest tests/test_deterministic.py -q
.venv/Scripts/python.exe -m pytest -q
git add app/deterministic.py tests/test_deterministic.py
git commit -m "fix: reject unsupported clinical specificity"
```

---

## Task 4: Add code-aware parent/child and residual ranking rules

**Objective:** Prefer the most specific supported leaf without selecting a child whose required detail is absent.

**Files:**
- Modify: `app/catalog.py`
- Modify: `app/retrieval.py`
- Modify: `app/deterministic.py`
- Create or modify: `tests/test_catalog.py`, `tests/test_retrieval.py`, `tests/test_deterministic.py`

**Steps:**

1. Write failing tests for:
   - a valid leaf outranking its parent when the note supports the leaf;
   - a parent or `.Z` residual outranking an unsupported child;
   - duplicate candidates being removed while preserving score order;
   - invalid catalogue codes never reaching output.

2. Run the focused tests and confirm failure.

3. Implement only catalogue-derived relationships. Do not infer a code hierarchy from string slicing alone unless the catalogue confirms the relationship.

4. Keep retrieval bounded to a configured top-K, with a default of 20 for evaluation and a smaller adjudication set for optional Gemma.

5. Verify:

   ```bash
   .venv/Scripts/python.exe -m pytest tests/test_catalog.py tests/test_retrieval.py tests/test_deterministic.py -q
   .venv/Scripts/python.exe -m pytest -q
   git add app/catalog.py app/retrieval.py app/deterministic.py tests/test_catalog.py tests/test_retrieval.py tests/test_deterministic.py
   git commit -m "feat: rank catalogue hierarchy and residual candidates"
   ```

Expected: all focused and full tests pass, with no output-contract regression.

---

## Task 5: Add a small explainable clinical alias layer

**Objective:** Improve retrieval recall for common abbreviations, spelling variants, and non-English terms without hard-coding development gold labels.

**Files:**
- Create: `app/aliases.py`
- Modify: `app/retrieval.py`
- Modify: `app/normalize.py`
- Create: `tests/test_aliases.py`
- Modify: `tests/test_retrieval.py`

**Data boundary:** Aliases may be derived from public medical terminology resources or documented common abbreviations, but they must not be copied from `gold` labels or generated as a per-note lookup table from the 60 development examples.

**Step 1: Write failing tests**

```python
def test_common_abbreviation_expands_before_retrieval():
    assert expand_aliases("HTN") == {"htn", "hypertension"}


def test_spanish_term_has_a_deterministic_alias():
    expanded = expand_aliases("hipertensión")
    assert "hypertension" in expanded
```

2. Run the focused tests and confirm failure.

**Step 2: Implement minimally**

Use a versioned, reviewable mapping with bounded expansion:

```python
ALIASES = {
    "htn": {"hypertension"},
    "dm2": {"type 2 diabetes mellitus"},
    "hipertensión": {"hypertension"},
}


def expand_aliases(text: str) -> set[str]:
    terms = {text.casefold()}
    for source, targets in ALIASES.items():
        if source in text.casefold():
            terms.update(targets)
    return terms
```

Do not add a broad machine-translation dependency or an embedding model at this stage.

**Step 3: Verify and commit**

```bash
.venv/Scripts/python.exe -m pytest tests/test_aliases.py tests/test_retrieval.py -q
.venv/Scripts/python.exe -m pytest -q
git add app/aliases.py app/retrieval.py app/normalize.py tests/test_aliases.py tests/test_retrieval.py
git commit -m "feat: add bounded clinical alias expansion"
```

---

## Task 6: Add note-style and language evaluation without gold-label leakage

**Objective:** Identify whether improvements help ambient notes and non-English notes separately rather than hiding failures in the aggregate score.

**Files:**
- Create: `analysis/evaluate_dev.py`
- Create: `analysis/results/evaluation-<commit>.json`
- Read only: `public/data/dev_notes.jsonl`, `public/score.py`

**Steps:**

1. Write a read-only evaluator that groups predictions by the supplied `style` field and reports line count, top-1, top-3, and candidate recall.
2. Add language bucket detection using conservative heuristics only for reporting; do not alter runtime behavior in this task.
3. Run:

   ```bash
   .venv/Scripts/python.exe analysis/evaluate_dev.py --gold public/data/dev_notes.jsonl --pred outputs/dev-deterministic.jsonl --catalog public/data/mms-2026-01.json
   ```

   Expected: a JSON report containing aggregate, style, and language buckets.

4. Commit only the evaluator and a result artifact:

   ```bash
   git add analysis/evaluate_dev.py analysis/results/
   git commit -m "analysis: report style and language performance"
   ```

**Verification:** The evaluator may read gold labels for scoring, but no file under `app/` may import or read the evaluator or gold data.

---

## Task 7: Re-score after each retrieval change and select only measured improvements

**Objective:** Keep only changes that improve the supplied score or materially improve candidate recall without causing structural regressions.

**Files:**
- Modify: `analysis/results/` only for records
- Modify the relevant `app/` and `tests/` files from Tasks 2–5

**Steps:**

1. Run the full deterministic prediction and scorer after each coherent change.
2. Record top-1, top-3, score, candidate recall, ambient-note top-1, multilingual bucket results, runtime, and commit SHA.
3. Reject any change that improves one example but reduces aggregate score unless Dad explicitly approves the trade-off.
4. Keep an experiment table in `analysis/model-benchmark.md` with exact commands and measured results.
5. Commit each accepted experiment with a real message; do not create a fake history or amend away failed experiments.

**Minimum expected evidence:** The final report must show the baseline and every retained scoring change, not just the best number.

---

## Task 8: Make Gemma optional, bounded, and observable

**Objective:** Prevent the optional model path from breaking the required no-key path or exceeding the 60-minute grading budget.

**Files:**
- Modify: `app/ollama_client.py`
- Modify: `app/agents.py`
- Modify: `docker-compose.yml`
- Modify: `tests/test_ollama_client.py`
- Modify: `tests/test_agents.py`
- Create: `analysis/results/gemma-run-<commit>.json`

**Step 1: Write failing tests**

Test these behaviors with a fake HTTP client:

```python
def test_ollama_endpoint_comes_from_ollama_host(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://host.docker.internal:11434")
    assert OllamaClient().base_url == "http://host.docker.internal:11434"


def test_malformed_model_response_falls_back_without_crashing():
    result = code_note(note, model_client=FakeMalformedClient())
    assert result.codes
    assert result.used_fallback is True


def test_model_call_count_is_bounded():
    result = code_note(note, model_client=FakeCountingClient())
    assert result.model_calls <= 1
```

2. Run focused tests and confirm failure.

**Step 2: Implement minimally**

- Read `OLLAMA_HOST` and normalize an optional `/api` suffix exactly once.
- Use one model call per note at most.
- Set a finite per-call timeout shorter than the total budget.
- Catch transport, parse, validation, and timeout failures separately.
- Return deterministic results on any failure.
- Emit a run-local counter for `model_calls`, `model_successes`, `model_parse_failures`, `timeouts`, and `fallbacks`; never write secrets.
- Keep Compose default mode deterministic unless an explicit local experiment enables Gemma.

**Step 3: Verify and commit**

```bash
.venv/Scripts/python.exe -m pytest tests/test_ollama_client.py tests/test_agents.py -q
.venv/Scripts/python.exe -m pytest -q
git add app/ollama_client.py app/agents.py docker-compose.yml tests/test_ollama_client.py tests/test_agents.py
 git commit -m "fix: bound and instrument optional Gemma mode"
```

Expected: the no-key path remains independent of Ollama and all malformed responses fall back safely.

---

## Task 9: Re-verify the exact Docker contract from a fresh clone

**Objective:** Produce final evidence that a clean checkout builds and runs with the required command.

**Files:**
- No protected-file changes.
- Create: `analysis/results/clean-clone-verification-<commit>.md`

**Steps:**

1. Create a temporary fresh clone outside the working repository using the local Git repository or the private GitHub remote. Do not modify the canonical source while testing.
2. Confirm the clean clone contains the required relative paths and no ignored virtual environment dependency.
3. Run exactly:

   ```bash
   docker compose config --quiet
   docker compose build --no-cache coder
   docker compose run coder /in/notes.jsonl /out/predictions.jsonl
   ```

4. Run the supplied scorer against the resulting output and record:
   - exit codes;
   - image build result;
   - line count;
   - missing/invalid/duplicate counts;
   - scorer output;
   - machine and Docker versions.
5. Remove only the temporary clone after evidence is saved; do not delete the canonical project or protected inputs.
6. Commit the verification record:

   ```bash
   git add analysis/results/clean-clone-verification-<commit>.md
   git commit -m "verify: prove clean-clone Docker contract"
   ```

**Open condition:** If Docker is unavailable, record that exact blocker instead of claiming PASS.

---

## Task 10: Complete the required README

**Objective:** Replace the placeholder README with the required one-page submission document.

**Files:**
- Modify: `README.md`

**Required sections:**

1. What the system does.
2. Exact Docker command.
3. Current verified development score from `public/score.py`.
4. Honest hidden-score estimate, explicitly labelled as an estimate and tied to evidence.
5. Data added, exact paths, and provenance.
6. Evaluation beyond the 60 notes: throughput only if that is all that was measured.
7. One AI-tooling error that was caught and fixed, such as fenced JSON parsing or a retrieval/evidence bug.
8. No-key behavior and optional Gemma behavior.
9. Honest number of hours spent.
10. Known limitations: low score, hidden uncertainty, language coverage, Docker evidence status if still open.

**TDD/documentation check:** Before editing, add a documentation test or a small checker under `tests/test_readme_requirements.py` that asserts required headings/phrases exist. Run it to fail, update README, then pass and commit.

```bash
.venv/Scripts/python.exe -m pytest tests/test_readme_requirements.py -q
```

Expected final result: all README requirement checks pass and the README remains within one printed page as reasonably measured by the chosen renderer.

---

## Task 11: Complete `DECISIONS.md` with real commit links

**Objective:** Make the decision log satisfy the brief and match actual Git history.

**Files:**
- Modify: `DECISIONS.md`
- Create: `tests/test_decisions_log.py`

**Each entry must include:**

- Date and time available from the actual work record;
- Real commit SHA;
- Decision;
- Alternatives considered;
- Evidence or measurement;
- What to revisit with more time.

Add entries for the retrieval baseline, section/negation handling, specificity penalties, aliases, Gemma decision, Docker verification, and final submission choice. Never invent timestamps; if only the date is known, say time unavailable.

Test the log structurally:

```bash
.venv/Scripts/python.exe -m pytest tests/test_decisions_log.py -q
```

Expected: every entry has a non-placeholder commit and required fields. Commit:

```bash
git add DECISIONS.md tests/test_decisions_log.py
 git commit -m "docs: complete technical decision log"
```

---

## Task 12: Create the final bundle only after all gates pass

**Objective:** Produce the requested Git bundle from the verified final repository.

**Files:**
- Create only after approval: `RajivMehta-Sugen-ICD11.bundle`
- Create: `analysis/results/final-validation.md`

**Steps:**

1. Run the full test suite, deterministic scorer, clean-clone Docker command, and structural output checks.
2. Confirm `git status --short` contains no accidental secrets, virtual environments, model caches, or temporary files.
3. Confirm protected files are present and unchanged relative to the supplied archive.
4. Create the bundle:

   ```bash
   git bundle create RajivMehta-Sugen-ICD11.bundle --all
   git bundle verify RajivMehta-Sugen-ICD11.bundle
   ```

   Expected: `git bundle verify` reports a valid bundle and the current main tip.

5. Record all final commands and outputs in `analysis/results/final-validation.md`.
6. Commit the validation record, then recreate the bundle if the commit changed the final tip.
7. Push the final main branch and bundle only after Mantra explicitly approves submission packaging.

---

# Tests and validation matrix

| Gate | Command | Expected result |
|---|---|---|
| Full unit suite | `.venv/Scripts/python.exe -m pytest -q` | All tests pass |
| Deterministic output | `.venv/Scripts/python.exe -m app public/data/dev_notes.jsonl outputs/dev-deterministic.jsonl` | 60 JSONL rows |
| Supplied score | `python public/score.py --gold ... --pred ... --mms ...` | Score recorded honestly |
| Output validity | Read-only Python checker | 60 rows, 0 missing, 0 invalid, 0 duplicate IDs |
| Docker config | `docker compose config --quiet` | Exit 0 |
| Docker build | `docker compose build --no-cache coder` | Exit 0 from fresh clone |
| Required run | `docker compose run coder /in/notes.jsonl /out/predictions.jsonl` | Exit 0 and complete output |
| Throughput | 600-note synthetic repeat run | Runtime recorded; never called hidden accuracy |
| Bundle | `git bundle verify RajivMehta-Sugen-ICD11.bundle` | Valid bundle at final tip |
| GitHub | `git ls-remote origin refs/heads/main` | Matches final local main SHA |

# Risks, trade-offs, and open questions

## Risks

- Improving the 60-note score through narrow aliases can overfit the development slice and hurt hidden generalisation.
- Candidate recall may require richer public medical terminology data, but adding data increases licensing, image-size, and provenance obligations.
- Non-English handling can become an unbounded translation project. Start with a small documented alias set and measure before adding dependencies.
- Gemma CPU latency may make model-first inference incompatible with the 60-minute cap.
- Docker availability may block verification on the current host; report the blocker rather than substituting a simulated result.
- The final bundle may accidentally include personal audio, local model caches, credentials, or generated clutter if the clean-tree check is skipped.

## Trade-offs

- Prefer explainable retrieval rules over a large embedding stack until candidate recall proves that embeddings are necessary.
- Prefer deterministic fallback and one bounded model call over autonomous multi-step agents.
- Prefer a lower but reproducible score over an unverified claim of hidden performance.
- Prefer preserving real failed experiments in Git history over rewriting history to look cleaner.

## Questions requiring Mantra/Dad review before implementation

1. Should public medical terminology or multilingual alias data be added, and what sources are acceptable?
2. Is a CPU-only deterministic solution preferred if Gemma remains slower and produces no measured gain?
3. Should the optional Gemma path remain in the final repository if it is disabled by default?
4. Is a 600-note repeated-dev throughput run sufficient for the README’s “beyond dev” evidence, clearly labelled as throughput only?
5. Should the private GitHub repository continue to contain the father’s audio file, or should only the transcript remain?
6. What honest hidden-score estimate should be stated, given the current `7.1 / 75` dev score and no hidden labels?
7. What exact number of hours should be recorded after the next implementation cycle?

# Handoff

This plan intentionally stops before implementation. Approval should be explicit before changing `app/`, `tests/`, `README.md`, `DECISIONS.md`, Docker files, or Git history. After approval, re-read the current workspace because the plan describes the intended baseline, not a guarantee that no files changed after it was written.
