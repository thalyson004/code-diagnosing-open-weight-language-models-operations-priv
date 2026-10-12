# LogiOR / P3 / ibm/granite4.2:8b

- Canonical pipeline: `formulation_code`
- Completed observations: 184 / 184
- Correct objectives: 24
- Accuracy over completed observations: 0.1304
- Median latency: 147.203 seconds
- Updated at: 2026-10-10T12:12:56.970227+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 3 | 0.0326 |
| few_shot | 92 | 21 | 0.2283 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 24 |
| empty_response | 124 |
| output_contract_error | 2 |
| runtime_error | 10 |
| truncated_response | 24 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 24 |
| output_contract_error | 2 |
| runtime_error | 10 |
| truncated_response | 148 |
