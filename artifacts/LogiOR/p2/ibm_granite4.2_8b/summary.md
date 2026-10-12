# LogiOR / P2 / ibm/granite4.2:8b

- Canonical pipeline: `code`
- Completed observations: 184 / 184
- Correct objectives: 21
- Accuracy over completed observations: 0.1141
- Median latency: 135.427 seconds
- Updated at: 2026-10-10T12:10:40.378197+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 0 | 0.0000 |
| few_shot | 92 | 21 | 0.2283 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 21 |
| empty_response | 154 |
| incorrect_objective | 1 |
| runtime_error | 7 |
| truncated_response | 1 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 21 |
| incorrect_objective | 1 |
| runtime_error | 7 |
| truncated_response | 155 |
