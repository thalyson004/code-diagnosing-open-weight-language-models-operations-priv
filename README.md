# Diagnosing Open-Weight Language Models for Operations Research: A Paired Benchmark of Direct Answers, Formulation, and Solver-Backed Code Generation

Code, prompts, datasets and response-level records for six locally hosted models. The study contains 6,912 observations across three pipelines and two prompt conditions. API execution is an optional software capability, not part of the article.

This is a separate study repository, initially private. It contains neither an unpublished paper PDF nor LaTeX source. The earlier three-model publication has its own unchanged release.

## Installation and prerequisites

- Python 3.11 or newer, Ollama, and the six model tags below.
- Gurobi and a valid license for P2 and P3.

```powershell
python -m pip install -e ".[solver,analysis]"
Copy-Item .env.example .env
python -m unittest discover -s tests -v
```

## Environment configuration

| Variable | Value | Use |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local inference |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | Optional API endpoint |
| `OPENROUTER_API_KEY` | `sk-...` (fill locally) | Optional API authentication |

Never commit `.env`, API keys or Gurobi credentials. Ollama execution does not require an API key.

## Repository layout

| Path | Contents |
| --- | --- |
| `src/or_small_models/` | Clients, prompts, pipelines, execution and checkpointing |
| `configs/` | Six-model registry and runtime settings |
| `datasets/` | Benchmark inputs and targets |
| `artifacts/` | Raw responses, execution logs, per-cell summaries and seven journal shards |
| `analysis/` | Summaries and derived failure-label normalization |
| `tests/` | Deterministic tests |
| `run-study-ollama.ps1` | Six-model study launcher |
| `run-openrouter.ps1` | Separate optional API experiment |

## Datasets

| Dataset | File | Instances |
| --- | --- | ---: |
| ComplexOR | `datasets/ComplexOR.json` | 18 |
| LogiOR | `datasets/LogiOR.json` | 92 |
| IndustryOR | `datasets/IndustryOR.json` | 82 |

## Experimental design

| Order | Model | Role |
| ---: | --- | --- |
| 1 | `gpt-oss:20b` | Historical baseline |
| 2 | `deepseek-r1:14b` | Historical baseline |
| 3 | `qwen3:14b` | Historical baseline |
| 4 | `qwen3.5:9b` | 2026 model of record |
| 5 | `qwen3:8b` | Historical baseline |
| 6 | `ibm/granite4.2:8b` | 2026 model of record |

| Pipeline | Requested artifact | Check |
| --- | --- | --- |
| P1 `direct` | Objective value | Parse and compare with target |
| P2 `code` | Gurobi program | Check, execute and compare |
| P3 `formulation_code` | Formulation, then Gurobi program | Check, execute and compare |

All conditions use the same benchmark instances and artifact contracts. Two solved MAMO Easy demonstrations are used only in few-shot prompts. There is one attempt per instance and condition, no corrective feedback, temperature 0, requested seed 0, an 8,192-token output allowance, a 600-second request timeout and a 120-second execution timeout.

Granite uses the approved native full-thinking template in `tools/ollama/granite4.2-full-thinking.Modelfile`, with `num_ctx=32768` and `num_gpu=99`. Its previous template block is excluded from this release. Other models' historical effective context windows were not recorded per call. `artifacts/ENVIRONMENT.json` records GPU, software versions, quantization and checkpoint digests.

On a new installation, pull the six study models and install Granite's approved template before starting a fresh run:

```powershell
ollama create ibm/granite4.2:8b -f tools/ollama/granite4.2-full-thinking.Modelfile
```

This replaces the installed Granite tag's template, not its weights. Do not perform it during inference or against an existing run without an explicitly backed-up configuration transition. The released artifacts are immutable and separate from new runs.

## Usage

Preview the six-model study, then run it in its own resumable directory:

```powershell
.\run-study-ollama.ps1 -Full
.\run-study-ollama.ps1 -Full -Execute
```

New study runs use `results-study/`, separate from the immutable release under `artifacts/`. This repository contains only the six complete article blocks. The release manifest declares all 6,912 observations and their checksums.

The optional API launcher accepts provider model identifiers and writes to `results-api/`. It requires the user's API key and does not contribute to the article:

```powershell
.\run-openrouter.ps1 -Models 'provider/model-id' -Full
.\run-openrouter.ps1 -Models 'provider/model-id' -Full -Execute
```

## Outputs and resume

The journal under `_state/records.jsonl` is the checkpoint source. Per-cell `artifacts.json` and `summary.md` group results by dataset, pipeline and model. Prompts, responses, provider metadata, generated formulations and programs, execution logs and scores are retained when available. Missing fields are not imputed.

Interrupt with `Ctrl+C` and repeat the same command and output directory to resume. Existing completed observations are skipped. New study and API directories are separate from the released records.

## Timeout and error handling

Transport retries resend the same request. They do not repair mathematical or programming errors. API credit exhaustion stops before checkpointing the unfinished observation. Add credits and repeat the command to retry it.

## Analysis

```powershell
python analysis/normalize_outcomes.py
python analysis/validate_release.py
python analysis/summarize_results.py artifacts/journal --normalize-failures --output-dir analysis/generated
python analysis/validate_primary.py --summary analysis/generated/summary.csv
python analysis/manuscript/analyze_six_models.py
python analysis/manuscript/build_casebook.py
```

The manuscript generators retain raw counts in CSV/JSON and render percentages in LaTeX tables. `analysis/manuscript/validate_assets.py path/to/manuscript` checks the manuscript's publication-only inventory, exact prompts, table outputs, and case excerpts. Analysis code belongs here, not in the LaTeX repository.

This writes `analysis/generated/normalization.csv` for the 6,912 selected records. Provider end reasons `length` or `max_tokens` identify output-limit truncation even when final content is empty. Archived labels are retained alongside the derived labels. No response, execution outcome or objective score is rewritten. The six-model normalization reclassifies 2,733 failures and changes zero accuracy scores.

Generated programs execute with an AST check and timeout, not operating-system isolation. Use a dedicated environment without unrelated secrets.

## Release status

The six complete model blocks and normalization table are available. Publication metadata and the paper PDF are pending. No manuscript source or unpublished paper PDF belongs in the code-and-data release.

## Citation

Pending.

## License

Pending.
