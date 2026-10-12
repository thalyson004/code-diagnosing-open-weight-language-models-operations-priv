"""Calculate manuscript rates and paired contrasts without changing records."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

MODELS = ("gpt-oss:20b", "deepseek-r1:14b", "qwen3:14b", "qwen3.5:9b", "qwen3:8b", "ibm/granite4.2:8b")
DATASETS = {"ComplexOR": 18, "LogiOR": 92, "IndustryOR": 82}
PIPELINES = ("direct", "code", "formulation_code")
SHOTS = ("zero_shot", "few_shot")
MODEL_NAMES = {"gpt-oss:20b":"GPT-OSS-20B", "deepseek-r1:14b":"DeepSeek-R1-14B",
               "qwen3:14b":"Qwen3-14B", "qwen3.5:9b":"Qwen3.5-9B",
               "qwen3:8b":"Qwen3-8B", "ibm/granite4.2:8b":"Granite4.2-8B"}


def load_records(path: Path) -> tuple[list[dict], str]:
    digest = hashlib.sha256()
    selected = []
    seen = set()
    paths = sorted(path.glob("records-*.jsonl")) if path.is_dir() else [path]
    def source_lines():
        for source in paths:
            with source.open("rb") as handle:
                yield from handle
    if paths:
        handle = source_lines()
        for line_number, raw_line in enumerate(handle, 1):
            if not raw_line.strip():
                continue
            record = json.loads(raw_line)
            if record.get("phase") != "P1" or record.get("model") not in MODELS:
                continue
            digest.update(raw_line)
            key = tuple(record.get(field) for field in (
                "model", "dataset", "example_id", "pipeline", "shot_condition", "repetition"
            ))
            if key in seen:
                raise ValueError(f"Duplicate selected observation at line {line_number}: {key}")
            seen.add(key)
            selected.append(record)
    return selected, digest.hexdigest()


def validate(records: list[dict]) -> None:
    groups = Counter((r["model"], r["dataset"], r["pipeline"], r["shot_condition"])
                     for r in records)
    expected = {
        (model, dataset, pipeline, shot): size
        for model in MODELS for dataset, size in DATASETS.items()
        for pipeline in PIPELINES for shot in SHOTS
    }
    if groups != expected:
        problems = [(key, groups.get(key, 0), count) for key, count in expected.items()
                    if groups.get(key, 0) != count]
        raise ValueError(f"Incomplete selected matrix: {problems[:20]}")
    if any(r.get("repetition") != 1 for r in records):
        raise ValueError("Unexpected repetition in the selected matrix")
    for model in MODELS:
        for dataset, size in DATASETS.items():
            ids = {r["example_id"] for r in records if r["model"] == model and r["dataset"] == dataset}
            if len(ids) != size:
                raise ValueError(f"Unexpected instance count for {model}/{dataset}: {len(ids)}")


def summarize(records: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for record in records:
        grouped[(record["model"], record["dataset"], record["pipeline"],
                 record["shot_condition"])].append(record)
    rows = []
    for (model, dataset, pipeline, shot), items in sorted(grouped.items()):
        outcomes = Counter(r["terminal_outcome"] for r in items)
        rows.append({
            "model": model, "dataset": dataset, "pipeline": pipeline, "shot_condition": shot,
            "n": len(items), "correct": sum(r["correct"] is True for r in items),
            "outcomes": dict(sorted(outcomes.items())),
            "thinking_available": sum(any(
                bool(stage.get("provider_metadata", {}).get("thinking") or
                     (stage.get("raw_response") or stage.get("details", {}).get("raw_response") or {}).get("message", {}).get("thinking"))
                for stage in r.get("stages", [])) for r in items),
        })
    return rows


def observable_mechanisms(records: list[dict]) -> list[dict]:
    """Count observable signatures. Semantic causes require manual case review."""
    counts = Counter()
    for record in records:
        outcome = record["terminal_outcome"]
        stages = record.get("stages", [])
        last = stages[-1] if stages else {}
        signature = None
        if outcome == "empty_response":
            raw = last.get("details", {}).get("raw_response", {})
            thinking = bool(raw.get("message", {}).get("thinking"))
            if raw.get("done_reason") == "length" and raw.get("eval_count") == 8192 and thinking:
                signature = "output_cap_reached_in_thinking_without_content"
            elif thinking:
                signature = "thinking_present_without_content_other"
            else:
                signature = "no_content_or_thinking_recorded"
        elif outcome == "truncated_response":
            raw = last.get("raw_response") or last.get("details", {}).get("raw_response") or {}
            reason = last.get("finish_reason") or raw.get("done_reason")
            content = last.get("response") or raw.get("message", {}).get("content") or ""
            if reason in {"length", "max_tokens"}:
                signature = "output_cap_reached_after_partial_content" if content.strip() else "output_cap_reached_without_final_content"
            else:
                signature = "truncation_metadata_unclassified"
        elif outcome == "runtime_error":
            stderr = last.get("stderr", "")
            matches = re.findall(r"(?m)^([A-Za-z_][A-Za-z_0-9]*(?:Error|Exception)):", stderr)
            signature = matches[-1] if matches else "runtime_exception_unclassified"
        elif outcome == "output_contract_error":
            stdout = last.get("stdout", "")
            if "FINAL_OBJECTIVE=" in stdout:
                signature = "marker_present_but_invalid_contract"
            elif "Model is infeasible" in stdout:
                signature = "infeasible_no_marker"
            else:
                signature = "no_objective_marker"
        elif outcome in {"blocked_import", "compilation_error", "parse_error", "invalid_response",
                         "request_timeout", "timeout"}:
            signature = outcome
        if signature:
            counts[(record["model"], outcome, signature)] += 1
    return [dict(model=model, outcome=outcome, signature=signature, count=count)
            for (model, outcome, signature), count in sorted(counts.items())]


def paired(records: list[dict], factor: str, left: str, right: str) -> list[dict]:
    results = []
    for model in MODELS:
        for dataset in DATASETS:
            for other in (PIPELINES if factor == "shot_condition" else SHOTS):
                subset = [r for r in records if r["model"] == model and r["dataset"] == dataset
                          and r["pipeline" if factor == "shot_condition" else "shot_condition"] == other]
                pairs = defaultdict(dict)
                for r in subset:
                    pairs[r["example_id"]][r[factor]] = r
                if any(left not in pair or right not in pair for pair in pairs.values()):
                    raise ValueError(f"Unpaired observations: {model}/{dataset}/{other}")
                counts = Counter((pair[left]["correct"], pair[right]["correct"])
                                 for pair in pairs.values())
                results.append({
                    "model": model, "dataset": dataset,
                    "pipeline" if factor == "shot_condition" else "shot_condition": other,
                    "comparison": f"{right} minus {left}", "both_correct": counts[(True, True)],
                    "left_only": counts[(True, False)], "right_only": counts[(False, True)],
                    "both_wrong": counts[(False, False)],
                })
    return results


def write_latex_tables(report: dict, output_dir: Path) -> None:
    cells = {(r["model"], r["dataset"], r["pipeline"], r["shot_condition"]): r
             for r in report["cells"]}
    for dataset in DATASETS:
        lines = [r"\begin{tabular}{llccc}", r"\toprule",
                 r"Model & Prompt & Direct & Code & Formulation + code \\", r"\midrule"]
        for model in MODELS:
            for shot in SHOTS:
                values = [f'{100*cells[(model, dataset, pipeline, shot)]["correct"]/DATASETS[dataset]:.2f}'
                          for pipeline in PIPELINES]
                label = MODEL_NAMES[model]
                lines.append(f'{label} & {"Zero" if shot == "zero_shot" else "Few"} & '
                             + " & ".join(values) + r" \\")
                lines.append(r"\midrule")
        lines.extend([r"\bottomrule", r"\end{tabular}"])
        (output_dir / f"accuracy_{dataset}.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    outcomes = Counter()
    for record in report["cells"]:
        for outcome, count in record["outcomes"].items():
            outcomes[(record["model"], record["pipeline"], outcome)] += count
    lines = [r"\begin{tabular}{llrrrrrrr}", r"\toprule",
             r"Model & Pipeline & Correct & Wrong & Empty & Truncated & Runtime & Output & Other \\",
             r"\midrule"]
    for model in MODELS:
        for pipeline, label in zip(PIPELINES, ("P1", "P2", "P3")):
            get = lambda outcome: outcomes[(model, pipeline, outcome)]
            other = 384 - sum(get(o) for o in ("correct", "incorrect_objective", "empty_response", "truncated_response",
                                                "runtime_error", "output_contract_error"))
            row = [f'{100*get(outcome)/384:.2f}' for outcome in
                   ("correct", "incorrect_objective", "empty_response", "truncated_response", "runtime_error", "output_contract_error")]
            row.append(f'{100*other/384:.2f}')
            name = MODEL_NAMES[model]
            lines.append(f"{name} & {label} & " + " & ".join(row) + r" \\")
            lines.append(r"\midrule")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (output_dir / "failure_composition.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def paired_contrast_rows(report: dict) -> list[dict]:
    """Return descriptive instance-paired contrasts in a stable, explicit order."""
    rows = []
    pipeline_names = {
        "direct": "P1",
        "code": "P2",
        "formulation_code": "P3",
    }
    for row in report["pipeline_pairs"]:
        contrast = row["comparison"]
        if contrast == "code minus direct":
            first, second = "P1", "P2"
        elif contrast == "formulation_code minus code":
            first, second = "P2", "P3"
        else:
            raise ValueError(f"Unexpected pipeline contrast: {contrast}")
        rows.append({
            "dataset": row["dataset"], "model": row["model"],
            "contrast": f"{first} vs. {second}",
            "condition": row["shot_condition"],
            "first_only": row["left_only"], "second_only": row["right_only"],
            "both_correct": row["both_correct"], "neither": row["both_wrong"],
            "n": row["both_correct"] + row["left_only"] + row["right_only"] + row["both_wrong"],
        })
    for row in report["shot_pairs"]:
        pipeline = pipeline_names[row["pipeline"]]
        rows.append({
            "dataset": row["dataset"], "model": row["model"],
            "contrast": "zero-shot vs. few-shot", "condition": pipeline,
            "first_only": row["left_only"], "second_only": row["right_only"],
            "both_correct": row["both_correct"], "neither": row["both_wrong"],
            "n": row["both_correct"] + row["left_only"] + row["right_only"] + row["both_wrong"],
        })
    expected_n = {"ComplexOR": 18, "LogiOR": 92, "IndustryOR": 82}
    expected_rows = len(MODELS) * len(DATASETS) * (2 * len(SHOTS) + len(PIPELINES))
    if len(rows) != expected_rows:
        raise ValueError(f"Expected {expected_rows} paired contrasts, found {len(rows)}")
    if any(row["n"] != expected_n[row["dataset"]] for row in rows):
        raise ValueError("Paired contrast denominator does not match the dataset size")
    keys = [(r["dataset"], r["model"], r["contrast"], r["condition"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate paired contrast key")
    return rows


def write_paired_contrasts(report: dict, output_dir: Path) -> None:
    rows = paired_contrast_rows(report)
    csv_path = output_dir / "paired_contrasts.csv"
    fields = ["dataset", "model", "contrast", "condition", "n", "both_correct",
              "first_only", "second_only", "neither"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    model_names = {
        "gpt-oss:20b": "GPT-OSS-20B",
        "deepseek-r1:14b": "DeepSeek-R1-14B",
        "qwen3:14b": "Qwen3-14B",
    }
    for dataset in DATASETS:
        table_specs = (
            ("pipeline", f"paired_pipeline_contrasts_{dataset}.tex",
             lambda r: r["contrast"] != "zero-shot vs. few-shot"),
            ("prompt", f"paired_prompt_contrasts_{dataset}.tex",
             lambda r: r["contrast"] == "zero-shot vs. few-shot"),
        )
        for table_type, filename, include in table_specs:
            lines = [
                r"\begin{tabularx}{\textwidth}{llXrrrr}", r"\toprule",
                r"Model & Contrast & Condition & Both & First only & Second only & Neither \\",
                r"\midrule",
            ]
            for row in rows:
                if row["dataset"] != dataset or not include(row):
                    continue
                condition = row["condition"].replace("zero_shot", "zero-shot").replace("few_shot", "few-shot")
                lines.append(
                    f"{MODEL_NAMES[row['model']]} & {row['contrast']} & {condition} & "
                    f"{100*row['both_correct']/row['n']:.2f} & {100*row['first_only']/row['n']:.2f} & {100*row['second_only']/row['n']:.2f} & {100*row['neither']/row['n']:.2f} \\\\")
                lines.append(r"\midrule")
            lines.extend([r"\bottomrule", r"\end{tabularx}"])
            note = ("First/second-only shares follow the order in the contrast label. "
                    if table_type == "pipeline" else
                    "First/second-only shares follow zero-shot/few-shot order. ")
            lines.append(r"\par\smallskip\footnotesize " + note +
                         "Percentages use the dataset instances as denominator. Rounding may affect row totals.")
            (output_dir / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal", type=Path, default=Path(__file__).resolve().parents[2] / "artifacts/journal")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1]
                        / "generated/six_model_raw_audit.json")
    args = parser.parse_args()
    records, digest = load_records(args.journal)
    validate(records)
    report = {
        "selected_records_sha256": digest, "selected_models": list(MODELS),
        "selected_observations": len(records), "cells": summarize(records),
        "observable_mechanisms": observable_mechanisms(records),
        "shot_pairs": paired(records, "shot_condition", "zero_shot", "few_shot"),
        "pipeline_pairs": (
            paired(records, "pipeline", "direct", "code")
            + paired(records, "pipeline", "code", "formulation_code")
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_latex_tables(report, args.output.parent)
    write_paired_contrasts(report, args.output.parent)
    print(f"Validated {len(records)} observations, selected records SHA-256 {digest}")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
