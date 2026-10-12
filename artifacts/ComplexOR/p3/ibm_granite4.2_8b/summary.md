# ComplexOR / P3 / ibm/granite4.2:8b

- Canonical pipeline: `formulation_code`
- Completed observations: 36 / 36
- Correct objectives: 13
- Accuracy over completed observations: 0.3611
- Median latency: 146.006 seconds
- Updated at: 2026-10-09T03:11:47.064722+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 18 | 2 | 0.1111 |
| few_shot | 18 | 11 | 0.6111 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 13 |
| empty_response | 9 |
| incorrect_objective | 2 |
| output_contract_error | 1 |
| runtime_error | 9 |
| truncated_response | 2 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 13 |
| incorrect_objective | 2 |
| output_contract_error | 1 |
| runtime_error | 9 |
| truncated_response | 11 |
