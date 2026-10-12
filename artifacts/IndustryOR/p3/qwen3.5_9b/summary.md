# IndustryOR / P3 / qwen3.5:9b

- Canonical pipeline: `formulation_code`
- Completed observations: 164 / 164
- Correct objectives: 36
- Accuracy over completed observations: 0.2195
- Median latency: 150.497 seconds
- Updated at: 2026-10-02T15:06:57.366348+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 82 | 7 | 0.0854 |
| few_shot | 82 | 29 | 0.3537 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 36 |
| empty_response | 110 |
| incorrect_objective | 2 |
| output_contract_error | 3 |
| runtime_error | 1 |
| truncated_response | 12 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 36 |
| empty_response | 1 |
| incorrect_objective | 2 |
| output_contract_error | 3 |
| runtime_error | 1 |
| truncated_response | 121 |
