# ComplexOR / P1 / qwen3.5:9b

- Canonical pipeline: `direct`
- Completed observations: 36 / 36
- Correct objectives: 17
- Accuracy over completed observations: 0.4722
- Median latency: 141.617 seconds
- Updated at: 2026-09-25T12:26:36.222848+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 18 | 9 | 0.5000 |
| few_shot | 18 | 8 | 0.4444 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 17 |
| empty_response | 18 |
| incorrect_objective | 1 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 17 |
| incorrect_objective | 1 |
| truncated_response | 18 |
