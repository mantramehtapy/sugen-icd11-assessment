# ICD-11 Retrieval Quality Improvement Plan

> **For Hermes:** Execute this plan only after Mantra explicitly approves it. Use task-by-task TDD, frequent commits, and measured scorer gates.

**Goal:** Raise ICD-11 candidate recall and coding accuracy without using development gold labels at runtime, while preserving the working Docker contract and deterministic no-key fallback.

**Architecture:** Keep the current bounded pipeline: evidence extraction → deterministic catalogue retrieval → deterministic ranking → optional constrained Gemma reranking → validation/fallback. Improve the deterministic path first because the current correct ICD-11 code is absent from the top-20 candidates for 36/60 development notes; Gemma cannot reliably fix a missing candidate. Every quality change must be evaluated against the frozen 7.5/75 baseline and retained only when the score, candidate recall, and structural validity are measured.

**Tech Stack:** Python 3.11 virtual environment, pytest, JSONL, supplied ICD-11 MMS 2026-01 catalogue, supplied `public/score.py`, Docker Compose, optional Ollama/Gemma.

---

## Current context and assumptions

- Canonical workspace: `C:\Users\rajiv\OneDrive\Desktop\work\sugen_health`
- Branch: `main`; latest known pushed commit before implementation: `df36a5c`.
- Protected files must remain unchanged:
  - `public/BRIEF.md`
  - `public/score.py`
  - `public/data/dev_notes.jsonl`
  - `public/data/mms-2026-01.json`
  - `SugenEngTest.tgz`
- The supplied development set has 60 notes.
- Current verified development result:
  - top-1: `4/60 = 0.067`
  - top-3: `10/60 = 0.167`
  - score: `7.5 / 75`
  - top-20 gold-candidate recall: `24/60`
  - structural validity: 60 lines, 0 missing, 0 invalid, 0 duplicate IDs
- Current clean-clone Docker contract passes.
- Runtime code must never read development `gold` labels.
- Do not add an external API or make Ollama/Gemma mandatory.
- Do not change Docker or submission files merely to improve a development score.
- Hidden-set accuracy is unknown; development gains must be described as development-only evidence.

## Proposed approach

1. Produce a reproducible per-note failure taxonomy before changing ranking.
2. Separate assessment, positive symptoms, history, modifiers, and negated terms in the retrieval query.
3. Add only bounded, explainable phrase aliases and clinical terminology normalization.
4. Use catalogue hierarchy and residual-code rules to rank supported specificity rather than lexical coincidence.
5. Re-run the supplied scorer after every coherent change and record results in `analysis/results/`.
6. Benchmark Gemma only after deterministic candidate recall improves; keep it optional and fully observable.
7. Re-run the exact Docker command from a fresh clone at the final commit, then create the Git bundle only after all gates pass.

---

## Step-by-step tasks

### Task 1: Reconfirm the baseline and protected-file boundary

**Objective:** Freeze the exact starting point before quality changes.

**Files:**
- Read only: `public/BRIEF.md`, `public/score.py`, `public/data/dev_notes.jsonl`, `public/data/mms-2026-01.json`
- Create: `analysis/results/retrieval-quality-baseline-2026-11-05.json`
- Create: `analysis/results/retrieval-quality-baseline-2026-11-05.md`

**Steps:**

1. Verify the working tree and protected-file hashes:

   ```bash
   git status --short --branch
   sha256sum public/BRIEF.md public/score.py public/data/dev_notes.jsonl public/data/mms-2026-01.json SugenEngTest.tgz
   ```

   Expected: clean `main` branch and five hashes printed.

2. Run the existing suite:

   ```bash
   .venv/Scripts/python.exe -m pytest -q
   ```

   Expected: at least `32 passed`.

3. Run the deterministic scorer:

   ```bash
   .venv/Scripts/python.exe -m app public/data/dev_notes.jsonl outputs/retrieval-quality-baseline.jsonl
   python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/retrieval-quality-baseline.jsonl --mms public/data/mms-2026-01.json
   ```

   Expected: `SCORE 7.5 / 75`, with 0 missing, invalid, or duplicate predictions.

4. Record the score, candidate recall, test count, commit SHA, and protected hashes in both analysis files.

5. Commit:

   ```bash
   git add analysis/results/retrieval-quality-baseline-2026-11-05.json analysis/results/retrieval-quality-baseline-2026-11-05.md
   git commit -m "analysis: freeze retrieval quality baseline"
   ```

**Gate:** Do not continue if the baseline does not reproduce `7.5 / 75` and structural validity.

---

### Task 2: Add a failure-report data model and report test

**Objective:** Create a read-only analysis tool that identifies whether each failure is caused by extraction, retrieval, or ranking.

**Files:**
- Create: `analysis/failure_report.py`
- Create: `tests/test_failure_report.py`

**Step 1: Write the failing test**

Add this test:

```python
from analysis.failure_report import classify_failure


def test_classify_failure_distinguishes_retrieval_and_ranking():
    assert classify_failure(gold_in_candidates=False, predicted_top1=False) == "retrieval"
    assert classify_failure(gold_in_candidates=True, predicted_top1=False) == "ranking"
    assert classify_failure(gold_in_candidates=True, predicted_top1=True) == "correct"
```

Run:

```bash
.venv/Scripts/python.exe -m pytest tests/test_failure_report.py::test_classify_failure_distinguishes_retrieval_and_ranking -q
```

Expected: FAIL because `analysis.failure_report` does not exist.

**Step 2: Implement the minimal function**

Create `analysis/failure_report.py` with:

```python
from __future__ import annotations


def classify_failure(*, gold_in_candidates: bool, predicted_top1: bool) -> str:
    if predicted_top1:
        return "correct"
    if gold_in_candidates:
        return "ranking"
    return "retrieval"
```

**Step 3: Verify**

```bash
.venv/Scripts/python.exe -m pytest tests/test_failure_report.py -q
```

Expected: `1 passed`.

**Step 4: Commit**

```bash
git add analysis/failure_report.py tests/test_failure_report.py
git commit -m "analysis: classify retrieval failures"
```

---

### Task 3: Generate the per-note failure taxonomy

**Objective:** Produce a machine-readable report containing note text, extracted evidence, gold code, candidate rank, prediction rank, and top candidate titles.

**Files:**
- Modify: `analysis/failure_report.py`
- Create: `analysis/results/retrieval-failures-2026-11-05.json`
- Create: `analysis/results/retrieval-failures-2026-11-05.md`
- Modify: `tests/test_failure_report.py`

**Implementation requirements:**

- Import runtime modules only for extraction/retrieval/prediction.
- Read gold labels only inside `analysis/`; never import this analysis module from `app/`.
- Include these fields per note:

```json
{
  "id": "note-id",
  "classification": "retrieval|ranking|correct",
  "gold_code": "...",
  "gold_rank": null,
  "predicted_codes": ["..."],
  "assessment": [],
  "symptoms": [],
  "history": [],
  "negated": [],
  "candidates": [
    {"code": "...", "title": "...", "rank": 1}
  ]
}
```

- Print a summary with counts for `correct`, `ranking`, and `retrieval`.
- For retrieval failures, print the five most common evidence/query patterns.

**Verification:**

```bash
.venv/Scripts/python.exe -m pytest tests/test_failure_report.py -q
.venv/Scripts/python.exe analysis/failure_report.py \
  --notes public/data/dev_notes.jsonl \
  --catalog public/data/mms-2026-01.json \
  --predictions outputs/retrieval-quality-baseline.jsonl \
  --json-out analysis/results/retrieval-failures-2026-11-05.json \
  --markdown-out analysis/results/retrieval-failures-2026-11-05.md
```

Expected: 60 report rows, no runtime gold-label dependency, and counts summing to 60.

**Commit:**

```bash
git add analysis/failure_report.py tests/test_failure_report.py analysis/results/retrieval-failures-2026-11-05.*
git commit -m "analysis: add per-note retrieval failure report"
```

**Gate:** Review the report before choosing aliases or ranking rules. Do not invent mappings from uninspected patterns.

---

### Task 4: Add regression tests for positive and negated evidence weighting

**Objective:** Prove that negated symptoms do not drive retrieval and that assessment terms outrank past history.

**Files:**
- Modify: `tests/test_evidence.py`
- Modify: `tests/test_retrieval.py`

Add tests equivalent to:

```python
def test_positive_terms_exclude_negated_items():
    evidence = extract_evidence("History: diabetes. Assessment: malaria. Denies headache and chest pain.")
    assert "malaria" in evidence.positive_terms
    assert "headache" not in evidence.positive_terms
    assert "chest" not in evidence.positive_terms
    assert "pain" not in evidence.positive_terms


def test_assessment_has_priority_over_history_for_search_text():
    result = choose_codes(
        "History: hypertension. Assessment: uncomplicated falciparum malaria.",
        catalog,
    )
    assert result.codes[0] == "1F40.Z"
```

Run the focused tests before implementation:

```bash
.venv/Scripts/python.exe -m pytest tests/test_evidence.py tests/test_retrieval.py -q
```

Expected: the new priority test fails if the current search path still allows history/noise to dominate.

Commit the tests only if they fail for the intended reason:

```bash
git add tests/test_evidence.py tests/test_retrieval.py
git commit -m "test: cover weighted clinical evidence"
```

---

### Task 5: Implement a shared weighted query builder

**Objective:** Build one explainable query representation used by retrieval and deterministic ranking instead of duplicating ad hoc term handling.

**Files:**
- Create: `app/query.py`
- Modify: `app/evidence.py` only if the existing evidence fields are insufficient
- Modify: `app/retrieval.py`
- Modify: `app/deterministic.py`
- Create: `tests/test_query.py`

**Implementation:** Create a small immutable representation:

```python
from __future__ import annotations

from dataclasses import dataclass

from .evidence import Evidence
from .normalize import tokenize


@dataclass(frozen=True)
class ClinicalQuery:
    strong_terms: frozenset[str]
    supporting_terms: frozenset[str]
    excluded_terms: frozenset[str]


def build_query(evidence: Evidence) -> ClinicalQuery:
    assessment_terms = set(tokenize(" ".join(evidence.assessment)))
    positive_terms = set(evidence.positive_terms)
    excluded_terms = {
        term for item in evidence.negated for term in tokenize(item)
    }
    supporting_terms = (positive_terms - assessment_terms) - excluded_terms
    return ClinicalQuery(
        strong_terms=frozenset(assessment_terms - excluded_terms),
        supporting_terms=frozenset(supporting_terms),
        excluded_terms=frozenset(excluded_terms),
    )
```

The implementation may extend this structure with phrase weights, but must not add model calls or hidden-label logic.

**TDD cycle:**

1. Add tests for strong assessment terms, supporting positive terms, and excluded negated terms.
2. Run:

   ```bash
   .venv/Scripts/python.exe -m pytest tests/test_query.py -q
   ```

   Expected: FAIL before `app/query.py` exists.
3. Implement the minimal module.
4. Run the focused tests and the existing evidence/retrieval tests; expected: all pass.
5. Commit:

   ```bash
   git add app/query.py app/evidence.py app/retrieval.py app/deterministic.py tests/test_query.py tests/test_evidence.py tests/test_retrieval.py
   git commit -m "feat: build weighted clinical queries"
   ```

---

### Task 6: Add bounded phrase aliases and normalization

**Objective:** Improve recall for common clinical phrases without adding an external dependency or mining development gold labels at runtime.

**Files:**
- Modify: `app/aliases.py`
- Modify: `tests/test_aliases.py`
- Modify: `tests/test_retrieval.py`

Add only mappings supported by inspected notes or common clinical terminology. The mapping format must remain explicit:

```python
_PHRASE_ALIASES = {
    "high blood pressure": "hypertension",
    "heart attack": "myocardial infarction",
    "shortness of breath": "dyspnea",
    "type 2 diabetes": "type 2 diabetes mellitus",
}
```

Do not derive aliases from `gold` labels in application code.

**TDD cycle:**

1. Add tests for phrase expansion and accent folding.
2. Run focused tests; expected: new tests fail before mappings are added.
3. Add the smallest mapping set.
4. Run:

   ```bash
   .venv/Scripts/python.exe -m pytest tests/test_aliases.py tests/test_retrieval.py -q
   ```

   Expected: all focused tests pass.
5. Commit:

   ```bash
   git add app/aliases.py tests/test_aliases.py tests/test_retrieval.py
   git commit -m "feat: expand bounded clinical phrase aliases"
   ```

**Gate:** Do not add a mapping unless it improves a recorded failure or has a clear clinical-language justification.

---

### Task 7: Implement weighted lexical retrieval

**Objective:** Score exact phrases and assessment terms above weak history/supporting terms while retaining deterministic ordering.

**Files:**
- Modify: `app/retrieval.py`
- Modify: `tests/test_retrieval.py`

Required scoring behavior:

- exact normalized title phrase match: highest bonus;
- strong assessment-term overlap: high IDF-weighted score;
- supporting positive-term overlap: lower score;
- excluded/negated-term overlap: zero or penalty;
- generic stopwords: ignored;
- deterministic tie-break: score descending, depth descending, code ascending.

The implementation must preserve the public signature:

```python
def retrieve(text: str, catalog: Catalog, limit: int = 20) -> list[CatalogRow]:
    ...
```

If adding query-aware retrieval, provide a second internal helper and keep the public function backward-compatible.

**TDD cycle:**

1. Add tests for assessment-over-history and negation exclusion.
2. Run the focused tests and capture the intended failures.
3. Implement minimal weighted scoring.
4. Run:

   ```bash
   .venv/Scripts/python.exe -m pytest tests/test_retrieval.py tests/test_query.py -q
   ```

   Expected: focused suite passes.
5. Run the full suite:

   ```bash
   .venv/Scripts/python.exe -m pytest -q
   ```

   Expected: all existing tests plus new tests pass.
6. Commit:

   ```bash
   git add app/retrieval.py tests/test_retrieval.py
   git commit -m "feat: weight retrieval by clinical evidence"
   ```

---

### Task 8: Add ICD hierarchy-aware candidate expansion

**Objective:** Keep related parent/child candidates together so the ranker can choose supported specificity instead of unrelated lexical neighbours.

**Files:**
- Create: `app/hierarchy.py`
- Modify: `app/catalog.py` only if an index is needed
- Modify: `app/deterministic.py`
- Create: `tests/test_hierarchy.py`

**Implementation constraints:**

- Build parent relationships from the catalogue’s code structure and/or URI relationships already present in `public/data/mms-2026-01.json`.
- Do not assume every code has a simple string prefix parent.
- Keep candidate count bounded at 20 after expansion.
- Preserve valid catalogue codes only.

Required internal API:

```python
def related_codes(code: str, catalog: Catalog) -> set[str]:
    """Return bounded parent, child, and residual siblings for one valid code."""
```

**TDD cycle:**

1. Add tests using known rows such as `1A03`, `1A03.0`, `1A03.Y`, and `1A03.Z`.
2. Run focused tests; expected: FAIL before the helper exists.
3. Implement only the relationships proven by the catalogue.
4. Run:

   ```bash
   .venv/Scripts/python.exe -m pytest tests/test_hierarchy.py -q
   ```

   Expected: all hierarchy tests pass.
5. Integrate candidate expansion and run the full suite.
6. Commit:

   ```bash
   git add app/hierarchy.py app/catalog.py app/deterministic.py tests/test_hierarchy.py
   git commit -m "feat: preserve ICD hierarchy during retrieval"
   ```

---

### Task 9: Add explicit residual and unsupported-specificity rules

**Objective:** Prefer the most specific supported code without rewarding unsupported title detail.

**Files:**
- Modify: `app/deterministic.py`
- Modify: `tests/test_deterministic.py`

Add regression tests for:

- disease only → unspecified/residual code where appropriate;
- explicit subtype → subtype code;
- unrelated modifier in a title → penalty;
- “other specified” not selected when the note is simply unspecified;
- negated subtype → subtype not selected.

Run before implementation:

```bash
.venv/Scripts/python.exe -m pytest tests/test_deterministic.py -q
```

Expected: new tests fail where current ranking chooses the wrong sibling.

Implement small named scoring helpers rather than adding another large conditional block:

```python
def _specificity_adjustment(row: CatalogRow, evidence_terms: set[str]) -> float:
    if not row.residual:
        return 0.0
    if "unspecified" in row.title.lower() and evidence_terms:
        return 0.25
    return 0.0
```

The exact rule must be based on the failure report and tests; do not apply a global residual bonus.

Verify and commit:

```bash
.venv/Scripts/python.exe -m pytest tests/test_deterministic.py -q
.venv/Scripts/python.exe -m pytest -q
git add app/deterministic.py tests/test_deterministic.py
git commit -m "fix: rank only supported ICD specificity"
```

---

### Task 10: Run the measured scorer gate after deterministic changes

**Objective:** Keep only changes that improve or clearly trade off the measured development metrics.

**Files:**
- Create: `analysis/results/retrieval-quality-experiment-<short-sha>.json`
- Create: `analysis/results/retrieval-quality-experiment-<short-sha>.md`
- Create/update: `outputs/dev-retrieval-improved.jsonl`

Run:

```bash
.venv/Scripts/python.exe -m app public/data/dev_notes.jsonl outputs/dev-retrieval-improved.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/dev-retrieval-improved.jsonl --mms public/data/mms-2026-01.json
.venv/Scripts/python.exe analysis/failure_report.py \
  --notes public/data/dev_notes.jsonl \
  --catalog public/data/mms-2026-01.json \
  --predictions outputs/dev-retrieval-improved.jsonl \
  --json-out analysis/results/retrieval-failures-improved.json \
  --markdown-out analysis/results/retrieval-failures-improved.md
```

Record:

- top-1 and top-3;
- score;
- top-20 candidate recall;
- count of retrieval/ranking/correct cases;
- structural validity;
- test count;
- exact commit SHA.

**Decision gate:**

- Keep a change if candidate recall or score improves without structural regressions.
- Revert a change if score decreases and no explicit trade-off is justified.
- Do not claim hidden-set improvement.

Commit the experiment record only after the result is reproducible:

```bash
git add analysis/results/ outputs/dev-retrieval-improved.jsonl
git commit -m "analysis: measure retrieval quality improvements"
```

---

### Task 11: Benchmark optional Gemma as a constrained reranker

**Objective:** Determine whether Gemma improves ranking after deterministic retrieval has a stronger candidate set.

**Files:**
- Modify: `app/ollama_client.py` only if tests identify a missing bound
- Modify: `app/agents.py` only if telemetry is missing
- Create: `tests/test_agent_telemetry.py` if needed
- Create: `analysis/results/gemma-rerank-<short-sha>.json`
- Create: `analysis/results/gemma-rerank-<short-sha>.md`

Requirements:

- Candidate list only; no unrestricted catalogue search.
- Maximum one model call per note.
- Fixed timeout.
- Validate returned codes against candidate codes and catalogue codes.
- Fall back deterministically on timeout, malformed JSON, invalid code, or out-of-candidate response.
- Record calls, successes, fallbacks, parse failures, timeouts, and changed predictions.

Run only after the deterministic gate passes:

```bash
.venv/Scripts/python.exe -m app public/data/dev_notes.jsonl outputs/dev-gemma-rerank.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/dev-gemma-rerank.jsonl --mms public/data/mms-2026-01.json
```

Expected: a score plus telemetry proving whether Gemma changed any predictions. Keep Gemma optional if it does not improve the deterministic score.

Commit only the benchmark evidence and necessary bounded client changes:

```bash
git add app/ollama_client.py app/agents.py tests/ analysis/results/ outputs/dev-gemma-rerank.jsonl
git commit -m "analysis: benchmark bounded Gemma reranking"
```

---

### Task 12: Update documentation and decision records

**Objective:** Make the final quality result, limitations, and remaining uncertainty explicit.

**Files:**
- Modify: `README.md`
- Modify: `DECISIONS.md`
- Modify: `analysis/model-benchmark.md`
- Create: `analysis/results/retrieval-quality-summary.md`

Document:

- baseline versus final development score;
- candidate recall change;
- failure taxonomy counts;
- whether Gemma helped;
- no-key deterministic behavior;
- no runtime gold-label usage;
- hidden-score uncertainty;
- exact Docker verification status;
- honest hours-spent statement only from available time records.

Add/update documentation tests if required:

```bash
.venv/Scripts/python.exe -m pytest tests/test_readme_requirements.py tests/test_decisions_log.py -q
```

Expected: all documentation tests pass.

Commit:

```bash
git add README.md DECISIONS.md analysis/model-benchmark.md analysis/results/retrieval-quality-summary.md tests/
git commit -m "docs: record retrieval quality results and limits"
```

---

### Task 13: Run final full validation from the final commit

**Objective:** Prove that the final repository remains reproducible after quality changes.

**Files:**
- Create: `analysis/results/final-validation-<short-sha>.md`

Run from the canonical workspace:

```bash
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m app public/data/dev_notes.jsonl outputs/final-deterministic.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/final-deterministic.jsonl --mms public/data/mms-2026-01.json
git status --short --branch
```

Expected:

- all tests pass;
- scorer reports 60 notes, 0 missing, 0 invalid, 0 duplicates;
- score and candidate recall match the recorded final experiment;
- clean working tree.

Start/check Docker only if needed:

```bash
docker version --format '{{.Server.Version}}'
```

From a fresh clone at the final commit:

```bash
gh repo clone mantramehtapy/sugen-icd11-assessment C:/Users/rajiv/AppData/Local/hermes/cache/scratch/sugen-final-<short-sha>
cd C:/Users/rajiv/AppData/Local/hermes/cache/scratch/sugen-final-<short-sha>
docker compose config --quiet
docker compose build --no-cache coder
docker compose run --rm coder /in/notes.jsonl /out/predictions.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/predictions.jsonl --mms public/data/mms-2026-01.json
```

Expected: all commands exit 0 and the supplied scorer reports the final measured result.

Commit the validation record:

```bash
git add analysis/results/final-validation-<short-sha>.md
git commit -m "verify: record final quality and Docker validation"
git push origin main
```

---

### Task 14: Create the final Git bundle only after approval

**Objective:** Produce the requested offline repository bundle from the verified final tip.

**Files:**
- Create: `RajivMehta-Sugen-ICD11.bundle`

Do not perform this task until Mantra approves the final measured score and submission state.

Run:

```bash
git bundle create RajivMehta-Sugen-ICD11.bundle main
 git bundle verify RajivMehta-Sugen-ICD11.bundle
```

Expected: `Bundle ... is OK` and the bundle contains the final `main` tip.

Verify file existence and size:

```bash
python - <<'PY'
from pathlib import Path
p = Path('RajivMehta-Sugen-ICD11.bundle')
print('exists=', p.exists(), 'bytes=', p.stat().st_size)
PY
```

Commit and push the bundle only if the assessment submission policy permits storing it in the private repository:

```bash
git add RajivMehta-Sugen-ICD11.bundle
git commit -m "build: add verified final Git bundle"
git push origin main
```

---

## Tests and validation summary

Every code task follows this cycle:

1. Add a focused failing test.
2. Run that test and verify the intended failure.
3. Implement the smallest change.
4. Run focused tests and verify pass.
5. Run the full suite.
6. Run the supplied scorer.
7. Record metrics before committing.

Required final checks:

```bash
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m app public/data/dev_notes.jsonl outputs/final-deterministic.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/final-deterministic.jsonl --mms public/data/mms-2026-01.json
git status --short --branch
```

The final clean clone must also pass:

```bash
docker compose config --quiet
docker compose build --no-cache coder
docker compose run coder /in/notes.jsonl /out/predictions.jsonl
```

No task is complete based only on a passing unit test. The scorer and output-structure checks are required for every retrieval/ranking change.

## Risks, tradeoffs, and open questions

### Risks

- The 60-note development set may not represent hidden notes; improvements may overfit.
- Manually added aliases can introduce false positives if they are too broad.
- Hierarchy inference can be wrong for irregular ICD-11 code relationships; catalogue evidence must drive the implementation.
- More retrieval candidates can increase false positives and model latency.
- Gemma may appear helpful on development notes while reducing reliability under time/network limits.
- Mining development gold labels to create runtime rules would contaminate the evaluation and is prohibited.

### Tradeoffs

- Prefer explainable lexical and hierarchy rules over a large embedding dependency because the grader may have restricted network access and limited runtime.
- Keep the deterministic path authoritative even if Gemma occasionally improves individual notes.
- Accept a slightly lower score only when the change materially improves robustness and the trade-off is documented; otherwise revert.
- Keep candidate limits bounded to protect the 60-minute hidden evaluation budget.

### Open questions for approval

1. Should the implementation remain deterministic-first even if Gemma improves development top-3 but adds substantial runtime?
2. Are manually curated common clinical phrase aliases acceptable if they are documented and not generated from gold labels?
3. What honest hours-spent value should be recorded in `README.md` and the final submission?
4. Should the final Git bundle be stored in the private GitHub repository, or only delivered as a local artifact?
5. What minimum development score or candidate-recall threshold should trigger a submission decision?

## Approval gate

No application-code changes, scorer runs for new experiments, commits, pushes, Docker rebuilds, or Git-bundle creation should begin until Mantra explicitly approves this plan.
