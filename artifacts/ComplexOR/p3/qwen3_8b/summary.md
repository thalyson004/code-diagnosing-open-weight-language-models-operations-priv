# ComplexOR / P3 / qwen3:8b

- Canonical pipeline: `formulation_code`
- Completed observations: 36 / 36
- Correct objectives: 22
- Accuracy over completed observations: 0.6111
- Median latency: 88.053 seconds
- Updated at: 2026-10-02T17:24:51.214928+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 18 | 9 | 0.5000 |
| few_shot | 18 | 13 | 0.7222 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 22 |
| empty_response | 4 |
| incorrect_objective | 2 |
| output_contract_error | 1 |
| runtime_error | 7 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 22 |
| incorrect_objective | 2 |
| output_contract_error | 1 |
| runtime_error | 7 |
| truncated_response | 4 |
