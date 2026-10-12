# ComplexOR / P2 / qwen3:8b

- Canonical pipeline: `code`
- Completed observations: 36 / 36
- Correct objectives: 18
- Accuracy over completed observations: 0.5000
- Median latency: 58.195 seconds
- Updated at: 2026-10-02T17:28:09.949720+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 18 | 8 | 0.4444 |
| few_shot | 18 | 10 | 0.5556 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 18 |
| empty_response | 9 |
| incorrect_objective | 4 |
| runtime_error | 5 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 18 |
| incorrect_objective | 4 |
| runtime_error | 5 |
| truncated_response | 9 |
