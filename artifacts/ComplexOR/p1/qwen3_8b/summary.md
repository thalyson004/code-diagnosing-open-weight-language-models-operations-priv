# ComplexOR / P1 / qwen3:8b

- Canonical pipeline: `direct`
- Completed observations: 36 / 36
- Correct objectives: 23
- Accuracy over completed observations: 0.6389
- Median latency: 56.229 seconds
- Updated at: 2026-10-02T17:25:55.712340+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 18 | 13 | 0.7222 |
| few_shot | 18 | 10 | 0.5556 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 23 |
| empty_response | 7 |
| incorrect_objective | 6 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 23 |
| incorrect_objective | 6 |
| truncated_response | 7 |
