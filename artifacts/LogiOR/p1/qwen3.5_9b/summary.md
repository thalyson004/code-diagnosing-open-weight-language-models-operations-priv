# LogiOR / P1 / qwen3.5:9b

- Canonical pipeline: `direct`
- Completed observations: 184 / 184
- Correct objectives: 10
- Accuracy over completed observations: 0.0543
- Median latency: 146.091 seconds
- Updated at: 2026-09-30T15:14:34.065775+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 5 | 0.0543 |
| few_shot | 92 | 5 | 0.0543 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 10 |
| empty_response | 173 |
| incorrect_objective | 1 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 10 |
| incorrect_objective | 1 |
| truncated_response | 173 |
