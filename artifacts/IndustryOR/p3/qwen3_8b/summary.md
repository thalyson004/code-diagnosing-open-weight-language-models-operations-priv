# IndustryOR / P3 / qwen3:8b

- Canonical pipeline: `formulation_code`
- Completed observations: 164 / 164
- Correct objectives: 61
- Accuracy over completed observations: 0.3720
- Median latency: 128.503 seconds
- Updated at: 2026-10-07T15:15:52.204017+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 82 | 22 | 0.2683 |
| few_shot | 82 | 39 | 0.4756 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 61 |
| empty_response | 59 |
| incorrect_objective | 19 |
| invalid_response | 1 |
| output_contract_error | 4 |
| runtime_error | 15 |
| truncated_response | 5 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 61 |
| incorrect_objective | 19 |
| invalid_response | 1 |
| output_contract_error | 4 |
| runtime_error | 15 |
| truncated_response | 64 |
