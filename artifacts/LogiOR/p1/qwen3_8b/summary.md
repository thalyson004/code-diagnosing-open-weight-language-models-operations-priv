# LogiOR / P1 / qwen3:8b

- Canonical pipeline: `direct`
- Completed observations: 184 / 184
- Correct objectives: 29
- Accuracy over completed observations: 0.1576
- Median latency: 128.320 seconds
- Updated at: 2026-10-06T21:26:59.589958+00:00

## Prompt conditions

| Condition | Completed | Correct | Accuracy |
|---|---:|---:|---:|
| zero_shot | 92 | 17 | 0.1848 |
| few_shot | 92 | 12 | 0.1304 |

## Terminal outcomes

| Outcome | Count |
|---|---:|
| correct | 29 |
| empty_response | 125 |
| incorrect_objective | 30 |

Complete prompts, raw provider responses, formulations, generated code, execution logs, typed errors, and timing metadata are stored in `artifacts.json`.

## Uniform failure classification

The outcomes above retain archived labels. The table below uses `uniform-failure-labels-v1`. Objective scores are unchanged.

| Outcome | Count |
| --- | ---: |
| correct | 29 |
| incorrect_objective | 30 |
| truncated_response | 125 |
