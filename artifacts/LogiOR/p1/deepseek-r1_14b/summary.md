# LogiOR / P1 / deepseek-r1:14b

- Canonical pipeline: `direct`
- Completed observations: 184 / 184
- Correct objectives: 49
- Accuracy over completed observations: 0.2663
- Median latency: 174.632 seconds
- Updated at: 2026-09-21T10:12:36.355998+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 24 | 0.2609 |
| few_shot | 92 | 25 | 0.2717 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 49 |
| empty_response | 76 |
| incorrect_objective | 53 |
| parse_error | 5 |
| truncated_response | 1 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 49 |
| incorrect_objective | 53 |
| parse_error | 5 |
| truncated_response | 77 |
