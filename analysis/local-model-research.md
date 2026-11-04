# Local-Model Research Addendum — Sugen ICD-11 Assessment

**Workspace:** `C:\Users\rajiv\OneDrive\Desktop\work\sugen_health`  
**Date:** 2026-11-04  
**Purpose:** Review local-model options before implementation. This is research, not a decision to install or use a model yet.

## Executive recommendation

Keep the submitted system **offline-first and deterministic at its core**. A local Ollama model may be tested as an optional, bounded reranker after candidate retrieval, but it must never be required for a complete run. The model must choose only from valid MMS candidates already retrieved by the application, and malformed or unavailable model responses must fall back to the deterministic result.

This preserves the Sugen requirements: no API key, predictable runtime, valid output, incremental writes, and reproducibility.

## Current local machine check

Verified on 2026-11-04:

- Ollama is installed locally, client version reported: `0.35.1`.
- Ollama had no running instance when first queried; the local Ollama service started during the local model inventory command.
- Local RAM detected: approximately 15.4 GB.
- No `nvidia-smi` command was available, so no NVIDIA GPU was confirmed.
- Existing local models include `qwen2.5:3b` (1.9 GB), `qwen2.5vl:3b` (3.2 GB), `qwen3.8-iq1:latest` (6.7 GB), `ornith-1.5:9b` (6.6 GB), and an LFM2.5-VL 3B GGUF (2.3 GB).
- No new model was pulled for this research.

The practical assumption is CPU-first inference with limited memory. Actual speed and quality must be measured locally rather than guessed.

## Candidate options from official Ollama pages

| Candidate | Official listed local size | Context | Why test it | Main concern |
|---|---:|---:|---|---|
| `qwen3.5:2b` | 2.7–3.1 GB | 256K | Safest first trial for roughly 15 GB RAM; modern instruction and multilingual capability | May be too weak for fine-grained ICD specificity |
| `qwen3.5:4b` | 3.3–4.0 GB | 256K | Stronger second trial while still plausible on CPU | Slower and more memory-intensive than 2B |
| `gemma4:e2b` | 4.6–7.5 GB | 128K | Small Gemma 4 option with text/image/audio support on the official page | Larger memory range and likely slower on this CPU-only machine |
| `llama3.2:3b` | 2.0 GB | 128K | Mature, small, multilingual baseline with straightforward Ollama support | Older model family and may be weaker for detailed clinical distinctions |
| Existing `qwen2.5:3b` | 1.9 GB local install | Local metadata to benchmark | No download needed; establishes a real local baseline | Older than the newer Qwen3.5 candidates |

The sizes and context windows above come from the official Ollama model pages. Qwen3.5 is listed as a multimodal family with 0.8B, 2B, 4B, 9B and larger variants; Gemma 4 lists E2B, E4B, 12B and larger variants; Llama 3.2 lists 1B and 3B text models. See the source list at the end.

## Critical assessment-compatibility point

Ollama is useful for local development and benchmarking, but the final submission must not assume that Sugen’s grading machine has Ollama installed or that it can download a model. The brief only permits model-API network access at run time and says any other indexes, embeddings, or downloaded data must be built ahead of time and shipped in the repository or image.

Therefore, the safe final design is:

1. deterministic catalog-based prediction as the complete no-key path;
2. local Ollama as an optional development/reranking experiment;
3. only include a local model in the final Docker image if its runtime, image size, licensing, and 600-note CPU benchmark are all acceptable;
4. never allow missing Ollama to produce missing predictions.

## Why Ollama fits the local experiment

Ollama exposes a local HTTP API and supports structured outputs. Structured output schemas can constrain a model response to an expected JSON shape, which is useful for a prediction object such as:

```json
{"codes": ["1F40.Z", "CA07.0"]}
```

The model would still not be trusted to invent codes. The application would validate every returned code against `public/data/mms-2026-01.json` and fall back if the response is invalid.

## Proposed model experiment

Do not install or pull anything until Dad reviews this addendum and the implementation plan.

After approval, benchmark in this order:

1. Existing `qwen2.5:3b` — no download; establishes local baseline.
2. `qwen3.5:2b` — smallest recommended new candidate.
3. `qwen3.5:4b` — quality/latency comparison if memory and speed are acceptable.
4. `llama3.2:3b` — mature comparison baseline.
5. `gemma4:e2b` only if the first trials justify the additional size and runtime cost.

For every model, record:

- exact model tag and local size;
- pull time and disk usage;
- cold-start time;
- average and p95 note latency over a fixed sample;
- CPU/RAM peak;
- JSON validity rate;
- candidate-selection accuracy on a held-out validation split;
- top-1 and top-3 score;
- whether the deterministic fallback was used;
- whether the model ever selected a code outside the candidate set.

The experiment must not use the same gold labels as runtime features. A model can be evaluated against gold labels, but the submitted application must not load them while predicting.

## Decision rule

Use a local model only if it improves the held-out validation result enough to justify its latency and complexity, never violates the no-key requirement, and remains within the Docker grading limits. Otherwise submit the deterministic system and document why the model was rejected.

## Sources

1. Official Ollama Qwen3.5 model page: `https://registry.ollama.com/library/qwen3.5`
2. Official Ollama Gemma 4 model page: `https://registry.ollama.com/library/gemma4`
3. Official Ollama Llama 3.2 model page: `https://ollama.com/library/llama3.2`
4. Official Ollama structured outputs documentation: `https://ollama.com/blog/structured-outputs`
5. Official Ollama launch documentation: `https://ollama.com/blog/launch`

## Open questions for Dad

1. Should we test a local Ollama reranker, or keep the final solution completely deterministic?
2. Is a CPU-only local model acceptable if it improves accuracy but increases runtime?
3. Should we keep the existing `qwen2.5:3b` as the baseline and compare newer models against it?
4. Do you approve downloading `qwen3.5:2b` and `qwen3.5:4b` into the local Ollama installation after the plan review?
