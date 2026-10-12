"""Generate a compact LaTeX accuracy table from summary.csv."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from validate_primary import validate_primary_rows


def escape(value: str) -> str:
    return value.replace("_", r"\_").replace("%", r"\%")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=Path("analysis/generated/summary.csv"))
    parser.add_argument("--output", type=Path, default=Path("analysis/generated/accuracy_table.tex"))
    parser.add_argument("--phase", default="P1")
    args = parser.parse_args()
    with args.summary.open(encoding="utf-8", newline="") as handle:
        all_rows = list(csv.DictReader(handle))
    if args.phase == "P1":
        validate_primary_rows(all_rows, Path(__file__).resolve().parents[1])
    rows = [row for row in all_rows if row["phase"] == args.phase]
    if not rows:
        raise SystemExit(f"No rows found for phase {args.phase}.")
    lines = [
        r"\begin{tabular}{lllllrr}", r"\toprule",
        r"Model & Provider & Dataset & Pipeline & Prompt & Correct/Total & Accuracy (\%) \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{escape(row['model'])} & {escape(row['provider'])} & {escape(row['dataset'])} & "
            f"{escape(row['pipeline'])} & {escape(row.get('shot_condition', 'zero_shot'))} & "
            f"{row['correct']}/{row['n']} & {100 * float(row['accuracy']):.2f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
