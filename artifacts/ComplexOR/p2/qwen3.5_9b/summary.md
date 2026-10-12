# ComplexOR / P2 / qwen3.5:9b

- Canonical pipeline: `code`
- Completed observations: 36 / 36
- Correct objectives: 11
- Accuracy over completed observations: 0.3056
- Median latency: 23.011 seconds
- Updated at: 2026-09-25T12:28:09.348139+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 18 | 4 | 0.2222 |
| few_shot | 18 | 7 | 0.3889 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 11 |
| empty_response | 3 |
| incorrect_objective | 4 |
| output_contract_error | 3 |
| runtime_error | 15 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 11 |
| incorrect_objective | 4 |
| output_contract_error | 3 |
| runtime_error | 15 |
| truncated_response | 3 |
