"""Derive uniform failure labels without changing responses or objective scores."""

import argparse
import copy
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

MODELS = ("gpt-oss:20b", "deepseek-r1:14b", "qwen3:14b", "qwen3.5:9b", "qwen3:8b", "ibm/granite4.2:8b")


def normalize(record):
    result = copy.deepcopy(record)
    original = record["terminal_outcome"]
    label = original
    for stage in record.get("stages", []):
        raw = stage.get("raw_response") or stage.get("details", {}).get("raw_response") or {}
        reason = (stage.get("finish_reason") or raw.get("done_reason") or "").casefold()
        if reason in {"length", "max_tokens"} and original in {"empty_response", "truncated_response"}:
            label = "truncated_response"
            break
    result["terminal_outcome"] = label
    result["analysis_classification"] = {"version": "uniform-failure-labels-v1",
        "archived_terminal_outcome": original, "normalized_terminal_outcome": label,
        "objective_score_changed": False}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    root=Path(__file__).resolve().parents[1]
    default_journal=root/"artifacts/journal" if (root/"artifacts/journal").is_dir() else root/"results/_state/records.jsonl"
    parser.add_argument("--journal", type=Path, default=default_journal)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "analysis/generated/normalization.csv")
    args = parser.parse_args()
    digest = hashlib.sha256()
    rows = []
    keys = set()
    counts = Counter()
    paths = sorted(args.journal.glob("records-*.jsonl")) if args.journal.is_dir() else [args.journal]
    def lines():
        for path in paths:
            with path.open("rb") as stream:
                yield from stream
    if paths:
        stream = lines()
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            if record["model"] not in MODELS or record["phase"] != "P1":
                continue
            digest.update(line)
            normalized = normalize(record)
            fields = ("run_id", "phase", "model", "dataset", "example_id", "pipeline", "shot_condition", "repetition")
            key = tuple(record[field] for field in fields)
            if key in keys:
                raise ValueError("Duplicate observation key")
            keys.add(key)
            counts[(record["model"], record["dataset"], record["pipeline"], record["shot_condition"])]+=1
            rows.append({**{field: record[field] for field in fields}, **normalized["analysis_classification"]})
    expected = {(m,d,p,s): n for m in MODELS for d,n in (("ComplexOR",18),("LogiOR",92),("IndustryOR",82))
                for p in ("direct","code","formulation_code") for s in ("zero_shot","few_shot")}
    if counts != expected:
        raise ValueError("The six-model matrix is incomplete")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer=csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"observations":len(rows), "selected_sha256":digest.hexdigest(),
        "reclassified":sum(r["archived_terminal_outcome"] != r["normalized_terminal_outcome"] for r in rows),
        "objective_scores_changed":0}))


if __name__ == "__main__":
    main()
