# IndustryOR / P3 / ibm/granite4.2:8b

- Canonical pipeline: `formulation_code`
- Completed observations: 164 / 164
- Correct objectives: 36
- Accuracy over completed observations: 0.2195
- Median latency: 143.275 seconds
- Updated at: 2026-10-11T07:40:50.263085+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 82 | 2 | 0.0244 |
| few_shot | 82 | 34 | 0.4146 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 36 |
| empty_response | 96 |
| incorrect_objective | 2 |
| output_contract_error | 3 |
| runtime_error | 15 |
| truncated_response | 12 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 36 |
| incorrect_objective | 2 |
| output_contract_error | 3 |
| runtime_error | 15 |
| truncated_response | 108 |
