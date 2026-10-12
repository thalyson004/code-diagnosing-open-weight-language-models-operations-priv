# LogiOR / P3 / qwen3.5:9b

- Canonical pipeline: `formulation_code`
- Completed observations: 184 / 184
- Correct objectives: 42
- Accuracy over completed observations: 0.2283
- Median latency: 149.868 seconds
- Updated at: 2026-09-30T15:12:09.498832+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 6 | 0.0652 |
| few_shot | 92 | 36 | 0.3913 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 42 |
| empty_response | 110 |
| incorrect_objective | 3 |
| output_contract_error | 3 |
| runtime_error | 3 |
| truncated_response | 23 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 42 |
| incorrect_objective | 3 |
| output_contract_error | 3 |
| runtime_error | 3 |
| truncated_response | 133 |
