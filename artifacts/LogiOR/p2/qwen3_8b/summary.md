# LogiOR / P2 / qwen3:8b

- Canonical pipeline: `code`
- Completed observations: 184 / 184
- Correct objectives: 38
- Accuracy over completed observations: 0.2065
- Median latency: 128.185 seconds
- Updated at: 2026-10-06T21:20:46.928608+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 11 | 0.1196 |
| few_shot | 92 | 27 | 0.2935 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 38 |
| empty_response | 96 |
| incorrect_objective | 16 |
| output_contract_error | 1 |
| runtime_error | 29 |
| truncated_response | 4 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 38 |
| incorrect_objective | 16 |
| output_contract_error | 1 |
| runtime_error | 29 |
| truncated_response | 100 |
