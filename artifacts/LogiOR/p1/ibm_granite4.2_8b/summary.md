# LogiOR / P1 / ibm/granite4.2:8b

- Canonical pipeline: `direct`
- Completed observations: 184 / 184
- Correct objectives: 21
- Accuracy over completed observations: 0.1141
- Median latency: 135.072 seconds
- Updated at: 2026-10-10T12:15:12.872535+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 11 | 0.1196 |
| few_shot | 92 | 10 | 0.1087 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 21 |
| empty_response | 161 |
| incorrect_objective | 2 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 21 |
| incorrect_objective | 2 |
| truncated_response | 161 |
