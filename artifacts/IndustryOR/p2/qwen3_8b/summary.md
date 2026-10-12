# IndustryOR / P2 / qwen3:8b

- Canonical pipeline: `code`
- Completed observations: 164 / 164
- Correct objectives: 55
- Accuracy over completed observations: 0.3354
- Median latency: 121.959 seconds
- Updated at: 2026-10-07T15:13:36.332733+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 82 | 22 | 0.2683 |
| few_shot | 82 | 33 | 0.4024 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 55 |
| empty_response | 78 |
| incorrect_objective | 15 |
| output_contract_error | 1 |
| runtime_error | 13 |
| truncated_response | 2 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 55 |
| incorrect_objective | 15 |
| output_contract_error | 1 |
| runtime_error | 13 |
| truncated_response | 80 |
