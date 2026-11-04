# Sugen ICD-11 Agentic-RAG + Gemma 4 E4B Implementation Plan

> **For Hermes:** Execute this plan only after approval. Use TDD for every code task, preserve the supplied company files, and keep all artifacts under the canonical workspace. Do not invent history, scores, timings, or hidden-test results.

**Goal:** Build and verify an offline-first ICD-11 MMS 2026-01 coder using a bounded Agentic RAG workflow with Gemma 4 E4B as an optional local reasoning model and a complete deterministic fallback.

**Architecture:** The system will use three bounded stages: an evidence extractor identifies diagnoses, symptoms, negation, severity, site, and explicit assessment text; a deterministic retriever searches the supplied ICD-11 MMS catalog; and a constrained adjudicator, backed by local `gemma4:e4b` when available, chooses only from the retrieved candidates. The final validator enforces the Sugen JSONL contract, catalog validity, maximum-three-code limit, and incremental output; if Gemma/Ollama is unavailable, the deterministic ranking path completes the run without an API key.

**Tech Stack:** Python 3.11+ standard library first; pytest; Docker Compose; Ollama for local development; Gemma 4 E4B; supplied `public/score.py`; Git with real incremental history. No runtime cloud API is required.

---

## 1. Current context and assumptions

### Canonical workspace

All project files and generated artifacts must remain below:

```text
C:\Users\rajiv\OneDrive\Desktop\work\sugen_health
```

Do not write code, plans, reports, model files, predictions, or test artifacts to another Desktop/work path.

### Supplied files

Preserve these unchanged:

```text
SugenEngTest.tgz
public/BRIEF.md
public/score.py
public/data/dev_notes.jsonl
public/data/mms-2026-01.json
public/data/predictions.example.jsonl
```

The supplied data contains 60 development notes and 18,375 ICD-11 MMS 2026-01 catalog rows. `gold` labels may be used by tests and evaluation analysis, but never by the submitted runtime coder as features.

### Dad’s decisions now incorporated

- Investigate a bounded **Agentic RAG** design rather than only a simple reranker.
- CPU-only local inference is acceptable.
- Prefer **Gemma 4 E4B** if it is practical.
- Replace the proposed Qwen-first experiment with `gemma4:e4b`.

### Client acceptance criteria

The final system must:

- run with `docker compose run coder /in/notes.jsonl /out/predictions.jsonl`;
- read JSONL notes with `id` and `text`;
- write one JSONL line per input note;
- return up to three valid MMS codes, best first;
- preserve IDs exactly;
- work with no API key;
- flush predictions incrementally;
- finish the 600-note grading run within 60 minutes on 8 CPUs and 16 GB RAM;
- include a Git bundle, one-page README, `DECISIONS.md`, and an honest hours-spent statement;
- be verified from a clean clone before submission.

### Output contract

Input:

```json
{"id":"note-001","text":"Assessment: uncomplicated malaria."}
```

Output:

```json
{"id":"note-001","codes":["1F40.Z"]}
```

No explanation text, confidence fields, model traces, or extra JSON keys may be emitted in the prediction file.

---

## 2. Architecture and boundaries

### Bounded Agentic RAG workflow

The word “agentic” must mean controlled iteration, not an unrestricted autonomous agent. The workflow is:

```text
Consultation note
  -> Evidence agent: extract explicit clinical facts and negations
  -> Retrieval tool: fetch top catalog candidates from MMS titles/metadata
  -> Adjudication agent: choose only from candidate codes
  -> Validator: reject invented/invalid/unsupported codes
  -> Deterministic fallback: guarantee an answer
  -> JSONL writer: flush one result immediately
```

Each model call has a fixed candidate list, fixed output schema, timeout, maximum retry count, and no network requirement. The agents cannot modify files, access arbitrary websites, or invent catalog entries.

### Runtime modes

1. **Deterministic mode:** always available; required for no-key and clean-clone execution.
2. **Local Gemma mode:** uses `gemma4:e4b` through local Ollama during development and benchmark runs.
3. **Packaged-model mode:** considered only if Gemma can be bundled legally and run within the grading image’s CPU/time limits. Do not assume Sugen’s grader has Ollama installed.

The final submission must not fail merely because Ollama is absent.

---

## 3. Proposed file layout

Keep supplied files at the root and add:

```text
sugen_health/
├── .git/
├── .gitignore
├── .hermes/plans/2026-11-04_125130-sugen-agentic-rag-gemma.md
├── app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── settings.py
│   ├── catalog.py
│   ├── normalize.py
│   ├── evidence.py
│   ├── retrieval.py
│   ├── schemas.py
│   ├── deterministic.py
│   ├── ollama_client.py
│   ├── agents.py
│   ├── validator.py
│   ├── io.py
│   └── coder.py
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   ├── test_catalog.py
│   ├── test_normalize.py
│   ├── test_evidence.py
│   ├── test_retrieval.py
│   ├── test_deterministic.py
│   ├── test_schemas.py
│   ├── test_ollama_client.py
│   ├── test_agents.py
│   ├── test_validator.py
│   ├── test_io.py
│   └── test_coder.py
├── analysis/
│   ├── requirements-matrix.csv
│   ├── gap-analysis.md
│   ├── model-benchmark.md
│   └── results/
├── outputs/
├── feedback/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── README.md
└── DECISIONS.md
```

Do not move or rename `public/` because the supplied scorer and required relative paths depend on it.

---

## 4. Bite-sized implementation tasks

Every code task must use this sequence:

1. write a failing test;
2. run the focused test and record the failure;
3. implement the minimum behavior;
4. run the focused test and full suite;
5. commit the real change with a meaningful message.

### Task 1: Establish the baseline repository

**Files:**

- Create: `.gitignore`
- Create: `README.md`
- Create: `DECISIONS.md`
- Create: `analysis/gap-analysis.md`

Write `.gitignore`:

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
outputs/*
!outputs/.gitkeep
analysis/results/*
!analysis/results/.gitkeep
```

Record in `DECISIONS.md`:

- the no-leakage rule;
- the Agentic RAG decision and alternatives;
- Gemma 4 E4B preference;
- deterministic fallback requirement;
- unresolved question of whether Gemma can be packaged for the grader.

Run:

```bash
cd /c/Users/rajiv/OneDrive/Desktop/work/sugen_health
git init -b main
git status --short
```

Expected: repository initializes; supplied files remain unchanged.

Commit:

```bash
git add .gitignore README.md DECISIONS.md analysis/gap-analysis.md
git commit -m "chore: establish clean assessment workspace"
```

### Task 2: Create the package smoke test

**Files:**

- Create: `app/__init__.py`
- Create: `tests/test_smoke.py`

Failing test:

```python
from app import __version__


def test_package_version_exists():
    assert __version__ == "0.1.0"
```

Run:

```bash
python -m pytest tests/test_smoke.py -q
```

Expected: FAIL because `app.__version__` is missing.

Minimal implementation:

```python
"""Sugen ICD-11 coder."""

__version__ = "0.1.0"
```

Run again. Expected: `1 passed`.

Commit:

```bash
git add app tests/test_smoke.py
git commit -m "test: establish application package"
```

### Task 3: Load the MMS catalog without development labels

**Files:**

- Create: `app/catalog.py`
- Create: `tests/test_catalog.py`

Failing tests:

```python
from pathlib import Path
from app.catalog import load_catalog


def test_loads_expected_catalog_size():
    catalog = load_catalog(Path("public/data/mms-2026-01.json"))
    assert len(catalog.rows) == 18_375
    assert catalog.rows[0].code == "1A00"


def test_validates_codes():
    catalog = load_catalog(Path("public/data/mms-2026-01.json"))
    assert catalog.is_valid("1A00")
    assert not catalog.is_valid("NOT-A-CODE")
```

Run and verify failure:

```bash
python -m pytest tests/test_catalog.py -q
```

Implement `CatalogRow` and `Catalog` with only the supplied catalog fields: `code`, `title`, `chapter`, `leaf`, `residual`, `depth`, and `uri`. Do not read `dev_notes.jsonl` from application code.

Run:

```bash
python -m pytest tests/test_catalog.py -q
```

Expected: `2 passed`.

Commit:

```bash
git add app/catalog.py tests/test_catalog.py
git commit -m "feat: load ICD-11 MMS catalog"
```

### Task 4: Normalize notes while preserving negation

**Files:**

- Create: `app/normalize.py`
- Create: `tests/test_normalize.py`

Failing tests:

```python
from app.normalize import normalize_text, tokenize


def test_normalize_text():
    assert normalize_text("  Fever\\nWITH chills. ") == "fever with chills."


def test_keep_negation_tokens():
    tokens = tokenize("No cough, fever excluded")
    assert {"no", "cough", "fever", "excluded"}.issubset(tokens)
```

Run, confirm failure, then implement stable whitespace/case normalization and tokenization. Do not remove `no`, `not`, `without`, `denies`, `negative`, or `excluded`.

Run:

```bash
python -m pytest tests/test_normalize.py -q
```

Expected: `2 passed`.

Commit:

```bash
git add app/normalize.py tests/test_normalize.py
git commit -m "feat: normalize clinical note text"
```

### Task 5: Extract explicit clinical evidence

**Files:**

- Create: `app/evidence.py`
- Create: `tests/test_evidence.py`

Failing test:

```python
from app.evidence import extract_evidence


def test_assessment_has_priority_over_history_and_negation():
    evidence = extract_evidence(
        "History of asthma. No fever. Assessment: moderate asthma attack."
    )
    assert evidence.assessment == ["moderate asthma attack"]
    assert "fever" in evidence.negated
    assert "asthma" in evidence.history
```

Run and confirm failure:

```bash
python -m pytest tests/test_evidence.py -q
```

Implement a small `Evidence` dataclass with:

```python
@dataclass(frozen=True)
class Evidence:
    assessment: list[str]
    symptoms: list[str]
    history: list[str]
    negated: set[str]
    modifiers: dict[str, str]
```

Use explicit markers such as `assessment`, `impression`, `diagnosis`, `dx`, `history`, and negation phrases. Do not infer unmentioned severity or etiology.

Run:

```bash
python -m pytest tests/test_evidence.py -q
```

Expected: `1 passed`.

Commit:

```bash
git add app/evidence.py tests/test_evidence.py
git commit -m "feat: extract explicit clinical evidence"
```

### Task 6: Build deterministic catalog retrieval

**Files:**

- Create: `app/retrieval.py`
- Create: `tests/test_retrieval.py`

Failing tests:

```python
from pathlib import Path
from app.catalog import load_catalog
from app.retrieval import retrieve

CATALOG = load_catalog(Path("public/data/mms-2026-01.json"))


def test_retrieve_returns_only_catalog_rows():
    rows = retrieve("Assessment: uncomplicated malaria", CATALOG, limit=10)
    assert 1 <= len(rows) <= 10
    assert all(CATALOG.is_valid(row.code) for row in rows)


def test_retrieval_is_deterministic():
    first = [x.code for x in retrieve("moderate asthma attack", CATALOG, limit=5)]
    second = [x.code for x in retrieve("moderate asthma attack", CATALOG, limit=5)]
    assert first == second
```

Run and confirm failure.

Implement title-token overlap, inverse document frequency from the catalog only, phrase bonuses, chapter hints, and deterministic tie-breaking. Add no model call here.

Run:

```bash
python -m pytest tests/test_retrieval.py -q
```

Expected: `2 passed`.

Commit:

```bash
git add app/retrieval.py tests/test_retrieval.py
git commit -m "feat: retrieve deterministic ICD candidates"
```

### Task 7: Implement deterministic fallback ranking

**Files:**

- Create: `app/deterministic.py`
- Create: `tests/test_deterministic.py`

Failing tests:

```python
from pathlib import Path
from app.catalog import load_catalog
from app.deterministic import choose_codes

CATALOG = load_catalog(Path("public/data/mms-2026-01.json"))


def test_choose_codes_returns_at_most_three_valid_codes():
    result = choose_codes("Assessment: uncomplicated malaria", CATALOG)
    assert 1 <= len(result.codes) <= 3
    assert all(CATALOG.is_valid(code) for code in result.codes)


def test_fallback_does_not_emit_explanation_text():
    result = choose_codes("Assessment: uncomplicated malaria", CATALOG)
    assert all(isinstance(code, str) for code in result.codes)
```

Run and verify failure. Implement specificity scoring using explicit assessment evidence, leaf/residual flags, depth, and negation. Return a typed result containing codes and internal rationale; only codes may reach the output writer.

Run:

```bash
python -m pytest tests/test_deterministic.py -q
```

Expected: `2 passed`.

Commit:

```bash
git add app/deterministic.py tests/test_deterministic.py
git commit -m "feat: add deterministic ICD fallback"
```

### Task 8: Define strict structured response schemas

**Files:**

- Create: `app/schemas.py`
- Create: `tests/test_schemas.py`

Failing tests:

```python
from app.schemas import parse_model_codes


def test_parse_model_codes_accepts_only_codes_list():
    assert parse_model_codes('{"codes":["1F40.Z"]}') == ["1F40.Z"]


def test_parse_model_codes_rejects_extra_text_and_limits_three():
    assert parse_model_codes('{"codes":["A","B","C","D"]}') == ["A", "B", "C"]
    assert parse_model_codes("not json") == []
```

Run and confirm failure, then implement strict JSON parsing, uppercase normalization, maximum-three handling, and empty-list fallback. Do not validate catalog membership here; keep catalog validation in `validator.py`.

Run:

```bash
python -m pytest tests/test_schemas.py -q
```

Expected: `2 passed`.

Commit:

```bash
git add app/schemas.py tests/test_schemas.py
git commit -m "feat: parse constrained model responses"
```

### Task 9: Add local Ollama Gemma client with a mockable transport

**Files:**

- Create: `app/settings.py`
- Create: `app/ollama_client.py`
- Create: `tests/test_ollama_client.py`

Failing tests:

```python
from app.ollama_client import OllamaClient


def test_client_posts_model_and_prompt_to_local_endpoint():
    calls = []

    def fake_post(url, payload, timeout):
        calls.append((url, payload, timeout))
        return {"message": {"content": '{"codes":["1F40.Z"]}'}}

    client = OllamaClient(post=fake_post, model="gemma4:e4b")
    assert client.choose([{"code": "1F40.Z", "title": "Malaria"}], "malaria") == ["1F40.Z"]
    assert calls[0][1]["model"] == "gemma4:e4b"
```

Run and confirm failure. Implement only a local HTTP client with:

- default endpoint `http://127.0.0.1:11434/api/chat`;
- default model `gemma4:e4b`;
- explicit timeout;
- structured JSON format/schema request if the installed Ollama API supports it;
- no network retry loop beyond one bounded retry;
- empty-list return on connection, timeout, or parse failure.

The prompt must state: choose only from the provided candidates, do not infer absent details, prefer explicit assessment, and return JSON only.

Run:

```bash
python -m pytest tests/test_ollama_client.py -q
```

Expected: `1 passed`.

Commit:

```bash
git add app/settings.py app/ollama_client.py tests/test_ollama_client.py
git commit -m "feat: add optional local Gemma Ollama client"
```

### Task 10: Implement bounded Agentic RAG orchestration

**Files:**

- Create: `app/agents.py`
- Create: `tests/test_agents.py`

Failing tests:

```python
from app.agents import AgenticCoder


def test_agentic_coder_falls_back_when_model_is_unavailable():
    agent = AgenticCoder(model_client=None)
    result = agent.predict("Assessment: uncomplicated malaria")
    assert result.codes
    assert result.used_fallback is True


def test_agentic_coder_sends_only_retrieved_candidates_to_model():
    seen = {}

    class FakeModel:
        def choose(self, candidates, note):
            seen["count"] = len(candidates)
            return [candidates[0]["code"]]

    result = AgenticCoder(model_client=FakeModel()).predict("Assessment: malaria")
    assert seen["count"] <= 20
    assert result.codes
```

Run and confirm failure. Implement a bounded orchestrator with exactly these stages:

1. `extract_evidence(note)`;
2. `retrieve(note, catalog, limit=20)`;
3. deterministic scoring;
4. optional `GemmaClient.choose(candidates, note)`;
5. validator accepts model output only when it is a subset of candidates and valid catalog codes;
6. deterministic fallback otherwise.

Set hard limits:

- maximum one model call per note;
- maximum 20 candidates in the prompt;
- fixed timeout;
- no external tools or arbitrary browsing;
- no access to gold labels.

Run:

```bash
python -m pytest tests/test_agents.py -q
```

Expected: `2 passed`.

Commit:

```bash
git add app/agents.py tests/test_agents.py
git commit -m "feat: add bounded Agentic RAG coder"
```

### Task 11: Validate final codes and preserve the output contract

**Files:**

- Create: `app/validator.py`
- Create: `tests/test_validator.py`

Failing tests:

```python
from app.validator import validate_codes


def test_validator_removes_unknown_codes_and_limits_three():
    valid = {"1F40.Z", "CA00"}
    assert validate_codes(["bad", "1F40.Z", "CA00", "extra"], valid) == ["1F40.Z", "CA00"]
```

Run and confirm failure. Implement catalog membership validation, stem normalization for scorer-compatible postcoordination, deduplication while preserving order, and maximum-three truncation.

Run:

```bash
python -m pytest tests/test_validator.py -q
```

Expected: `1 passed`.

Commit:

```bash
git add app/validator.py tests/test_validator.py
git commit -m "test: enforce valid ordered prediction codes"
```

### Task 12: Add streaming JSONL input/output and CLI entry point

**Files:**

- Create: `app/io.py`
- Create: `app/coder.py`
- Create: `app/__main__.py`
- Create: `tests/test_io.py`
- Create: `tests/test_coder.py`

Failing integration test:

```python
import json
import subprocess
import sys


def test_cli_emits_one_line_per_input(tmp_path):
    source = tmp_path / "notes.jsonl"
    output = tmp_path / "predictions.jsonl"
    source.write_text(json.dumps({"id": "n1", "text": "fever"}) + "\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "app", str(source), str(output)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert rows[0]["id"] == "n1"
    assert 1 <= len(rows[0]["codes"]) <= 3
```

Run and confirm failure. Implement:

- exactly two positional arguments;
- blank-line skipping;
- line-numbered JSON errors;
- output directory creation;
- one flush after every prediction;
- model mode selected by `SU_GEN_MODEL_MODE=deterministic|gemma|auto`;
- `auto` tries Gemma once and falls back deterministically;
- no API key required.

Run:

```bash
python -m pytest tests/test_io.py tests/test_coder.py -q
python -m app public/data/dev_notes.jsonl outputs/dev_predictions.jsonl
wc -l outputs/dev_predictions.jsonl
```

Expected: focused tests pass; `wc -l` reports `60`.

Commit:

```bash
git add app tests
 git commit -m "feat: add streaming coder CLI"
```

### Task 13: Benchmark deterministic and Gemma modes locally

**Files:**

- Create: `analysis/model-benchmark.md`
- Create: `analysis/results/benchmark.jsonl`
- Modify application code only after a failing regression test.

First verify Ollama and the selected model without changing the repository:

```bash
env -u OLLAMA_HOST ollama list
env -u OLLAMA_HOST ollama run gemma4:e4b "Return JSON only: {\"ok\":true}"
```

Expected: model is available and returns a response. If unavailable, record the exact error and do not claim Gemma validation.

Run fixed local modes on the development notes:

```bash
SU_GEN_MODEL_MODE=deterministic python -m app public/data/dev_notes.jsonl outputs/dev-deterministic.jsonl
SU_GEN_MODEL_MODE=gemma python -m app public/data/dev_notes.jsonl outputs/dev-gemma.jsonl
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/dev-deterministic.jsonl --mms public/data/mms-2026-01.json
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/dev-gemma.jsonl --mms public/data/mms-2026-01.jsonl
```

Record model tag, latency, CPU/RAM, missing predictions, invalid codes, top-1, top-3, and score. Do not select Gemma solely because it scores higher on the same data; use held-out note subsets and error analysis. Commit only the benchmark record:

```bash
git add analysis/model-benchmark.md analysis/results/benchmark.jsonl
git commit -m "docs: record deterministic and Gemma benchmarks"
```

### Task 14: Test Docker without Ollama and with local model availability

**Files:**

- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`
- Create: `analysis/gap-analysis.md`

Docker must contain the deterministic path and supplied MMS data. Do not assume the host Ollama service is reachable from the container; if Gemma mode requires host access, document it as local-development-only.

Run:

```bash
cd /c/Users/rajiv/OneDrive/Desktop/work/sugen_health
docker compose config --quiet
docker compose build --no-cache coder
cp public/data/dev_notes.jsonl notes.jsonl
env -u OLLAMA_HOST docker compose run --rm coder /in/notes.jsonl /out/predictions.jsonl
```

Expected:

- Compose config exits 0;
- image build exits 0;
- no-key/no-Ollama run exits 0;
- output contains 60 lines;
- every code is catalog-valid.

Run the scorer:

```bash
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/predictions.jsonl --mms public/data/mms-2026-01.json
```

Expected: zero missing predictions and zero invalid codes. Commit:

```bash
git add Dockerfile docker-compose.yml .dockerignore analysis/gap-analysis.md
 git commit -m "build: verify offline Docker execution"
```

### Task 15: Complete requirements gap analysis

**Files:**

- Create: `analysis/requirements-matrix.csv`
- Modify: `analysis/gap-analysis.md`

Create CSV columns:

```text
requirement,source,evidence,status,command,result,risk
```

Include rows for:

- exact Docker command;
- clean clone;
- no API key;
- no Ollama availability;
- optional Gemma mode;
- one output per input;
- valid MMS code list;
- maximum three codes;
- incremental flushing;
- 600-note/60-minute feasibility;
- Agentic RAG candidate bound;
- development leakage prevention;
- Git bundle;
- README limit;
- decisions log;
- hours spent.

Run:

```bash
python -m pytest -q
python public/score.py --gold public/data/dev_notes.jsonl --pred outputs/predictions.jsonl --mms public/data/mms-2026-01.json
git status --short
git log --oneline --decorate --all
```

Expected: every row is `PASS`, `PARTIAL`, or `OPEN` with command evidence. No row may be marked `PASS` from intention alone.

Commit:

```bash
git add analysis/requirements-matrix.csv analysis/gap-analysis.md
git commit -m "docs: complete Agentic RAG requirements gap analysis"
```

### Task 16: Final documentation and bundle

**Files:**

- Modify: `README.md`
- Modify: `DECISIONS.md`
- Create: `final-submission/RajivMehta-Sugen-ICD11.bundle`
- Create: `final-submission/submission-checklist.md`

README must be one page or less and state:

- exact run command;
- deterministic fallback behavior;
- whether Gemma is required, optional, or omitted;
- measured development score;
- honest hidden-score uncertainty;
- data added and provenance;
- evaluation beyond the 60 dev notes;
- one AI-tooling error caught, if applicable;
- hours spent.

Create the final bundle only after all validation passes:

```bash
git status --short
git bundle create final-submission/RajivMehta-Sugen-ICD11.bundle --all
git bundle verify final-submission/RajivMehta-Sugen-ICD11.bundle
```

Expected: complete history and intended refs. Do not send the email without explicit approval.

---

## 5. Required final validation

Run from the canonical root:

```bash
python -m pytest -q

docker compose build --no-cache coder

env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OLLAMA_HOST \
  docker compose run --rm coder /in/notes.jsonl /out/predictions.jsonl

python public/score.py \
  --gold public/data/dev_notes.jsonl \
  --pred outputs/predictions.jsonl \
  --mms public/data/mms-2026-01.json

python - <<'PY'
import json
from pathlib import Path
source = [json.loads(x) for x in Path('notes.jsonl').read_text().splitlines() if x.strip()]
pred = [json.loads(x) for x in Path('outputs/predictions.jsonl').read_text().splitlines() if x.strip()]
assert len(source) == len(pred), (len(source), len(pred))
assert [x['id'] for x in source] == [x['id'] for x in pred]
assert all(0 < len(x['codes']) <= 3 for x in pred)
print(f'contract PASS: {len(pred)} predictions')
PY

git bundle create final-submission/RajivMehta-Sugen-ICD11.bundle --all
git bundle verify final-submission/RajivMehta-Sugen-ICD11.bundle
```

Expected evidence:

```text
pytest: all tests passed
Docker build: exit 0
Docker run without API key and without Ollama: exit 0
contract PASS: 60 predictions
score.py: 0 missing predictions, 0 invalid codes
bundle: complete history
```

The hidden 600-note score remains unknown until Sugen runs the submission.

---

## 6. Risks, trade-offs, and open questions

### Risks

1. **Agentic RAG over-complexity:** unconstrained agents can be slow, inconsistent, and difficult to verify. The plan limits the workflow to one evidence pass, one retrieval pass, and one adjudication call.
2. **Gemma availability:** Sugen’s grading machine may not have Ollama or Gemma. The deterministic path must remain complete.
3. **CPU latency:** Gemma 4 E4B may exceed the 60-minute budget. Measure 600-note throughput before making it required.
4. **Model hallucination:** the model may invent codes. Candidate restriction and catalog validation are mandatory.
5. **Development leakage:** runtime must never read `gold` fields.
6. **Catalog title sparsity:** the supplied MMS file contains titles and metadata, not full clinical descriptions. External resources need licensing and reproducibility review.
7. **Exact deadline unknown:** use the original email sent timestamp, not the current date.
8. **Docker-to-host Ollama networking:** local development may require an explicit host URL, but the clean submission path must not depend on it.

### Trade-offs

- Agentic RAG may improve reasoning over a single prompt, but each extra agent step costs latency and failure surface.
- Gemma 4 E4B may improve nuanced selection, but deterministic ranking is smaller, faster, and easier to ship.
- Keeping Ollama optional maximizes reproducibility, but may leave some hidden accuracy on the table.
- Shipping a quantized Gemma model in the image could make the final result fully self-contained, but adds image size, licensing, CPU runtime, and memory risks.

### Open questions for Dad

1. Does “Agentic RAG” mean a bounded three-stage workflow as specified here, or does Dad expect a different agent decomposition?
2. Should Gemma 4 E4B be local-development-only unless a packaged-model benchmark passes?
3. Is a deterministic fallback acceptable as the required Docker submission path?
4. Is Dad approving a local Gemma model download now, or only approving the architecture for later testing?
5. Can the original email header be supplied so the exact three-day deadline can be calculated?

---

## 7. PDF review handoff

After this plan is approved and plan mode ends, create the review packet under:

```text
C:\Users\rajiv\OneDrive\Desktop\work\sugen_health\analysis\agentic-rag-plan-review.md
C:\Users\rajiv\OneDrive\Desktop\work\sugen_health\analysis\agentic-rag-plan-review.pdf
C:\Users\rajiv\OneDrive\Desktop\work\sugen_health\analysis\agentic-rag-plan-review.docx
```

The packet should summarize:

- Sugen’s required JSONL output;
- deterministic versus Agentic RAG paths;
- Gemma 4 E4B decision;
- Docker/no-key compatibility;
- TDD and gap-analysis workflow;
- risks and Dad’s open decisions.

Do not create the PDF during plan mode; this turn may write only this plan Markdown file.

---

## 8. Stop conditions

Stop and ask for review if:

- a protected company file would need modification;
- Gemma cannot run within the time/memory budget;
- the model must be required for predictions;
- Docker cannot run without Ollama;
- the Agentic RAG path requires development gold labels at runtime;
- a new data source has unclear licensing;
- Dad’s feedback conflicts with the Sugen brief.
