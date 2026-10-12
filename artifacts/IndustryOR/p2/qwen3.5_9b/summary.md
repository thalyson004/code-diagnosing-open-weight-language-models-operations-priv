# IndustryOR / P2 / qwen3.5:9b

- Canonical pipeline: `code`
- Completed observations: 164 / 164
- Correct objectives: 52
- Accuracy over completed observations: 0.3171
- Median latency: 115.124 seconds
- Updated at: 2026-10-02T15:04:32.224034+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 82 | 20 | 0.2439 |
| few_shot | 82 | 32 | 0.3902 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| compilation_error | 1 |
| correct | 52 |
| empty_response | 71 |
| incorrect_objective | 9 |
| output_contract_error | 9 |
| runtime_error | 22 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| compilation_error | 1 |
| correct | 52 |
| incorrect_objective | 9 |
| output_contract_error | 9 |
| runtime_error | 22 |
| truncated_response | 71 |
