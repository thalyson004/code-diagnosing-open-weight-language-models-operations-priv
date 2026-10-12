# IndustryOR / P1 / qwen3:8b

- Canonical pipeline: `direct`
- Completed observations: 164 / 164
- Correct objectives: 59
- Accuracy over completed observations: 0.3598
- Median latency: 126.500 seconds
- Updated at: 2026-10-07T15:11:26.911947+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 82 | 28 | 0.3415 |
| few_shot | 82 | 31 | 0.3780 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 59 |
| empty_response | 89 |
| incorrect_objective | 15 |
| truncated_response | 1 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 59 |
| incorrect_objective | 15 |
| truncated_response | 90 |
