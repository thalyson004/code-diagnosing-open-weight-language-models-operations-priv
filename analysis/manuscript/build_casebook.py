"""Extract short, traceable log excerpts for the manuscript's case appendix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CASES = (
    ("rate_misread", "gpt-oss:20b", "ComplexOR", "steel4_12", "formulation_code", "zero_shot",
     {"formulation": "For each s", "code_from_formulation": "Stage capacity constraints"}),
    ("nested_dictionary", "deepseek-r1:14b", "ComplexOR", "netasgn_0", "code", "zero_shot",
     {"code_generation": "x[i][j] ="}),
    ("unused_function", "qwen3:14b", "ComplexOR", "flowshop_scheduling_1", "code", "zero_shot",
     {"code_generation": "def solve(env):"}),
    ("extra_output", "gpt-oss:20b", "ComplexOR", "netasgn_0", "formulation_code", "few_shot",
     {"code_from_formulation": "FINAL_OBJECTIVE="}),
    ("thinking_without_answer", "qwen3:14b", "ComplexOR", "netasgn_0", "formulation_code", "zero_shot",
     {"code_from_formulation": ""}),
    ("truncated_answer", "gpt-oss:20b", "LogiOR", "prob_033", "direct", "zero_shot",
     {"direct_answer": "Profit: 0.23"}),
    ("unsupported_number", "qwen3:14b", "LogiOR", "prob_012", "direct", "zero_shot",
     {"direct_answer": "FINAL_OBJECTIVE="}),
    ("target_unit_conflict", "gpt-oss:20b", "ComplexOR", "cell_tower_5", "formulation_code", "zero_shot",
     {"formulation": "maximum percentage", "code_from_formulation": "percentage ="}),
    ("syntax_failure", "deepseek-r1:14b", "ComplexOR", "nltrans_8", "formulation_code", "few_shot",
     {"code_from_formulation": "model.addVar"}),
    ("blocked_import", "qwen3:14b", "LogiOR", "prob_028", "code", "zero_shot",
     {"code_generation": "import numpy"}),
    ("solver_timeout", "gpt-oss:20b", "LogiOR", "prob_012", "code", "zero_shot",
     {"code_generation": "model.optimize()"}),
    ("parse_failure", "gpt-oss:20b", "IndustryOR", "37_36", "direct", "few_shot",
     {"direct_answer": "Decision variables"}),
)


def excerpt(value: str, needle: str, width: int = 480) -> str:
    if not value:
        return "<empty>"
    start = max(0, value.find(needle) - 100) if needle and needle in value else 0
    end = min(len(value), start + width)
    return ("[...]" if start else "") + value[start:end] + ("[...]" if end < len(value) else "")


def ascii_text(value: object) -> str:
    return str(value).encode("ascii", "backslashreplace").decode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal", type=Path, default=Path(__file__).resolve().parents[2] / "artifacts/journal")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1]
                        / "generated/casebook")
    args = parser.parse_args()
    cases = list(CASES)
    keys = {case[1:6] for case in cases}
    selected_2026 = set()
    found = {}
    paths=sorted(args.journal.glob("records-*.jsonl")) if args.journal.is_dir() else [args.journal]
    def source_lines():
        for path in paths:
            with path.open(encoding="utf-8") as stream:
                yield from stream
    for line in source_lines():
        row = json.loads(line)
        key = tuple(row.get(field) for field in
                    ("model", "dataset", "example_id", "pipeline", "shot_condition"))
        if row.get("phase") == "P1" and row.get("model") in {"qwen3.5:9b", "ibm/granite4.2:8b"}:
            kind = ("code" if row.get("pipeline") == "code" and row.get("correct") else
                    "budget" if row.get("pipeline") == "direct" and row.get("terminal_outcome") == "empty_response" else None)
            raw = (row.get("stages") or [{}])[-1]
            raw = raw.get("raw_response") or raw.get("details", {}).get("raw_response", {})
            if kind == "budget" and raw.get("done_reason") != "length":
                kind = None
            selection = (row["model"], kind)
            if kind and selection not in selected_2026:
                selected_2026.add(selection)
                name = "2026_" + ("granite" if row["model"].startswith("ibm/") else "qwen") + "_" + kind
                anchors = {stage["stage"]: "" for stage in row.get("stages", []) if stage["stage"] != "execution"}
                cases.append((name, *key, anchors))
                keys.add(key)
        if row.get("phase") == "P1" and key in keys:
            if key in found:
                raise ValueError(f"Duplicate case key: {key}")
            found[key] = row
    if set(found) != keys:
        raise ValueError(f"Missing case keys: {keys - set(found)}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if len(selected_2026) != 4:
        raise ValueError("Missing 2026 success/budget examples")
    for name, model, dataset, example_id, pipeline, shot, anchors in cases:
        record = found[(model, dataset, example_id, pipeline, shot)]
        lines = [f"CASE {name}", f"run_id: {record['run_id']}",
                 f"phase: {record['phase']}, repetition: {record['repetition']}",
                 f"model: {model}, dataset: {dataset}, example_id: {example_id}",
                 f"pipeline: {pipeline}, shot_condition: {shot}",
                 f"terminal_outcome: {record['terminal_outcome']}",
                 f"expected_objective: {record['expected_objective']}",
                 f"predicted_objective: {record['predicted_objective']}",
                 "EXCERPTS: [...] marks omitted material. Non-ASCII uses escape sequences, and trailing spaces are trimmed."]
        for stage in record.get("stages", []):
            name_of_stage = stage["stage"]
            if name_of_stage == "execution":
                lines.append("[execution]")
                lines.append("outcome: " + ascii_text(stage.get("outcome")))
                for field in ("stdout", "stderr"):
                    value = stage.get(field, "")
                    if value:
                        if field == "stderr":
                            filtered = [line for line in value.splitlines()
                                        if "File \"" not in line and "or-small-model-" not in line]
                            value = "\n".join(filtered[-4:])
                        lines.append(field + ": " + ascii_text(excerpt(value[-650:], "", 650)))
                continue
            if name_of_stage not in anchors:
                continue
            lines.append(f"[{name_of_stage}]")
            raw = stage.get("raw_response") or stage.get("details", {}).get("raw_response", {})
            thinking = stage.get("provider_metadata", {}).get("thinking") or (
                raw.get("message", {}).get("thinking", "") if isinstance(raw, dict) else "")
            if thinking:
                lines.append("reasoning_field: " + ascii_text(excerpt(thinking, anchors[name_of_stage], 380)))
            response = stage.get("response", "")
            lines.append("response: " + ascii_text(excerpt(response, anchors[name_of_stage], 480)))
            if stage.get("error_type"):
                lines.append("error_type: " + ascii_text(stage["error_type"]))
            if isinstance(raw, dict):
                for field in ("done_reason", "eval_count"):
                    if field in raw:
                        lines.append(field + ": " + ascii_text(raw[field]))
        rendered = "\n".join("\n".join(part.rstrip() for part in line.splitlines())
                             for line in lines).rstrip() + "\n"
        (args.output_dir / f"{name}.txt").write_text(rendered, encoding="ascii")
    print(f"Wrote {len(cases)} case excerpts to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
