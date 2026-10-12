# IndustryOR / P2 / ibm/granite4.2:8b

- Canonical pipeline: `code`
- Completed observations: 164 / 164
- Correct objectives: 19
- Accuracy over completed observations: 0.1159
- Median latency: 135.843 seconds
- Updated at: 2026-10-11T07:38:34.149963+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 82 | 0 | 0.0000 |
| few_shot | 82 | 19 | 0.2317 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| blocked_import | 1 |
| correct | 19 |
| empty_response | 127 |
| output_contract_error | 3 |
| runtime_error | 10 |
| truncated_response | 4 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| blocked_import | 1 |
| correct | 19 |
| output_contract_error | 3 |
| runtime_error | 10 |
| truncated_response | 131 |
