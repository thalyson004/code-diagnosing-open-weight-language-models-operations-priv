# LogiOR / P3 / qwen3:8b

- Canonical pipeline: `formulation_code`
- Completed observations: 184 / 184
- Correct objectives: 32
- Accuracy over completed observations: 0.1739
- Median latency: 133.375 seconds
- Updated at: 2026-10-06T21:24:41.666459+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 11 | 0.1196 |
| few_shot | 92 | 21 | 0.2283 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 32 |
| empty_response | 87 |
| incorrect_objective | 16 |
| output_contract_error | 8 |
| runtime_error | 36 |
| truncated_response | 5 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 32 |
| incorrect_objective | 16 |
| output_contract_error | 8 |
| runtime_error | 36 |
| truncated_response | 92 |
