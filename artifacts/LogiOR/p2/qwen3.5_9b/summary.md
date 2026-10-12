# LogiOR / P2 / qwen3.5:9b

- Canonical pipeline: `code`
- Completed observations: 184 / 184
- Correct objectives: 50
- Accuracy over completed observations: 0.2717
- Median latency: 64.493 seconds
- Updated at: 2026-09-30T15:09:44.794314+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 21 | 0.2283 |
| few_shot | 92 | 29 | 0.3152 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| compilation_error | 3 |
| correct | 50 |
| empty_response | 60 |
| incorrect_objective | 13 |
| output_contract_error | 16 |
| runtime_error | 41 |
| truncated_response | 1 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| compilation_error | 3 |
| correct | 50 |
| incorrect_objective | 13 |
| output_contract_error | 16 |
| runtime_error | 41 |
| truncated_response | 61 |
