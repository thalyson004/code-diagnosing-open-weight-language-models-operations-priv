# ComplexOR / P3 / qwen3.5:9b

- Canonical pipeline: `formulation_code`
- Completed observations: 36 / 36
- Correct objectives: 13
- Accuracy over completed observations: 0.3611
- Median latency: 186.907 seconds
- Updated at: 2026-09-25T12:24:05.802647+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 18 | 3 | 0.1667 |
| few_shot | 18 | 10 | 0.5556 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 13 |
| empty_response | 15 |
| incorrect_objective | 1 |
| runtime_error | 4 |
| truncated_response | 3 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 13 |
| incorrect_objective | 1 |
| runtime_error | 4 |
| truncated_response | 18 |
