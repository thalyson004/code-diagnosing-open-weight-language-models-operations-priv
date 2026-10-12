# IndustryOR / P1 / ibm/granite4.2:8b

- Canonical pipeline: `direct`
- Completed observations: 164 / 164
- Correct objectives: 36
- Accuracy over completed observations: 0.2195
- Median latency: 134.794 seconds
- Updated at: 2026-10-11T07:36:17.892306+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 82 | 17 | 0.2073 |
| few_shot | 82 | 19 | 0.2317 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 36 |
| empty_response | 126 |
| incorrect_objective | 2 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 36 |
| incorrect_objective | 2 |
| truncated_response | 126 |
