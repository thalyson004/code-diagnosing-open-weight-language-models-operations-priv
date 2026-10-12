"""Durable checkpoints and release-oriented result views."""

from __future__ import annotations

import json
import os
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .records import BenchmarkRecord

PIPELINE_DIRECTORIES = {
    "direct": "p1",
    "code": "p2",
    "formulation_code": "p3",
}

# These files contain checkpoint/progress plumbing. Changes here do not alter
# prompts, model selection, datasets, pipelines, or scoring contracts.
RESUME_COMPATIBLE_RUNTIME_CHANGES = frozenset({"runner.py", "artifacts.py"})
ZERO_OBSERVATION_COMPATIBLE_RUNTIME_CHANGES = frozenset({"executor.py"})


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_component(value: str) -> str:
    """Return a Windows- and POSIX-safe directory name."""

    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    if not cleaned:
        raise ValueError(f"Cannot create a result directory from {value!r}.")
    return cleaned


def record_key(item: dict[str, Any]) -> tuple[str, str, str, str, str, int, str]:
    return (
        str(item["phase"]),
        str(item["model"]),
        str(item["dataset"]),
        str(item["example_id"]),
        str(item["pipeline"]),
        int(item["repetition"]),
        str(item.get("shot_condition", "zero_shot")),
    )


class ResultStore:
    """Append durable records and materialize per-cell JSON and Markdown files."""

    def __init__(
        self,
        root: Path,
        manifest: dict[str, Any],
        *,
        record_resume_event: bool = True,
    ) -> None:
        self.root = root.resolve()
        self.state_dir = self.root / "_state"
        self.ledger_path = self.state_dir / "records.jsonl"
        self.manifest_path = self.state_dir / "manifest.json"
        self.progress_path = self.state_dir / "progress.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        if self.manifest_path.exists():
            existing = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            model_extension = (
                _compatible_model_extension(existing, manifest)
                if existing.get("plan_fingerprint") != manifest.get("plan_fingerprint")
                else None
            )
            compatible_resume = (
                existing.get("plan_fingerprint") != manifest.get("plan_fingerprint")
                and _compatible_resume_plan(existing, manifest, self.progress_path)
            )
            if (
                existing.get("plan_fingerprint") != manifest.get("plan_fingerprint")
                and not compatible_resume
                and model_extension is None
            ):
                raise ValueError(
                    "The existing result directory belongs to a different frozen plan. "
                    "Choose another --output-dir or restore the original configuration."
                )
            self.manifest = existing
            if model_extension is not None:
                self.manifest.setdefault("plan_extension_events", []).append(
                    {
                        "captured_at_utc": utc_now(),
                        "added_models": model_extension,
                        "previous_plan_fingerprint": existing.get("plan_fingerprint"),
                        "previous_planned_observations": existing["planned_observations"],
                        "previous_model_order": existing["model_order"],
                        "previous_frozen_plan": existing["frozen_plan"],
                        "requested_plan_fingerprint": manifest["plan_fingerprint"],
                        "requested_model_order": manifest["model_order"],
                        "requested_planned_observations": manifest["planned_observations"],
                    }
                )
                for name in (
                    "plan_fingerprint", "frozen_plan", "model_order", "planned_observations"
                ):
                    self.manifest[name] = manifest[name]
            elif compatible_resume:
                # Commit the accepted compatibility transition in the manifest
                # so the next resume compares against the new hashes directly.
                self.manifest["plan_fingerprint"] = manifest.get("plan_fingerprint")
                self.manifest["frozen_plan"] = manifest.get("frozen_plan")
                self.manifest.setdefault("resume_compatibility_events", []).append(
                    {
                        "captured_at_utc": utc_now(),
                        "reason": "Only benchmark infrastructure changed; frozen inputs and contracts match.",
                        "requested_plan_fingerprint": manifest.get("plan_fingerprint"),
                    }
                )
            if record_resume_event:
                self.manifest.setdefault("resume_events_utc", []).append(utc_now())
                self.manifest.setdefault("resume_environment_snapshots", []).append(
                    manifest.get("environment", {})
                )
            if record_resume_event or compatible_resume or model_extension is not None:
                _write_json_atomic(self.manifest_path, self.manifest)
        else:
            self.manifest = manifest
            _write_json_atomic(self.manifest_path, self.manifest)

        self.records = _load_jsonl(self.ledger_path)
        self.completed = {record_key(item) for item in self.records}
        if len(self.completed) != len(self.records):
            raise ValueError(f"Duplicate checkpoint keys found in {self.ledger_path}.")
        self._repair_cells()

    @property
    def run_id(self) -> str:
        return str(self.manifest["run_id"])

    def append(self, record: BenchmarkRecord) -> None:
        item = record.to_dict()
        key = record_key(item)
        if key in self.completed:
            raise ValueError(f"Refusing duplicate checkpoint: {key}.")
        line = json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
        with self.ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        self.records.append(item)
        self.completed.add(key)
        self._write_cell(item["dataset"], item["pipeline"], item["model"])

    def append_infrastructure_diagnostic(self, record: BenchmarkRecord) -> None:
        path = self.state_dir / "infrastructure_errors.jsonl"
        payload = {
            "captured_at_utc": utc_now(),
            "observation": record.to_dict(),
        }
        line = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

    def rebuild_cells(self, cells: set[tuple[str, str, str]]) -> None:
        """Regenerate only the requested dataset/pipeline/model views."""

        for dataset, pipeline, model in sorted(cells):
            self._write_cell(dataset, pipeline, model)

    def write_progress(
        self,
        *,
        status: str,
        current: dict[str, Any] | None = None,
        interruption: str | None = None,
    ) -> None:
        total = int(self.manifest["planned_observations"])
        outcomes = Counter(str(item["terminal_outcome"]) for item in self.records)
        payload = {
            "schema_version": 1,
            "run_id": self.run_id,
            "status": status,
            "updated_at_utc": utc_now(),
            "completed_observations": len(self.completed),
            "planned_observations": total,
            "remaining_observations": max(total - len(self.completed), 0),
            "completion_fraction": len(self.completed) / total if total else 1.0,
            "current_observation": current,
            "interruption": interruption,
            "terminal_outcomes": dict(sorted(outcomes.items())),
        }
        _write_json_atomic(self.progress_path, payload)
        _write_text_atomic(self.root / "PROGRESS.md", _progress_markdown(payload))

    def _repair_cells(self) -> None:
        cells: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        for item in self.records:
            cells[(item["dataset"], item["pipeline"], item["model"])].append(item)
        for (dataset, pipeline, model), expected in sorted(cells.items()):
            directory = self._cell_directory(dataset, pipeline, model)
            artifact_path = directory / "artifacts.json"
            summary_path = directory / "summary.md"
            try:
                payload = json.loads(artifact_path.read_text(encoding="utf-8"))
                stored = payload.get("records", [])
                same_keys = [record_key(item) for item in stored] == [
                    record_key(item) for item in expected
                ]
                stamp = str(payload.get("updated_at_utc", ""))
                summary = summary_path.read_text(encoding="utf-8")
                summary_matches = bool(stamp) and f"- Updated at: {stamp}" in summary
            except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
                same_keys = False
                summary_matches = False
            if not same_keys or not summary_matches:
                self._write_cell(dataset, pipeline, model)

    def _write_cell(self, dataset: str, pipeline: str, model: str) -> None:
        items = [
            item
            for item in self.records
            if item["dataset"] == dataset
            and item["pipeline"] == pipeline
            and item["model"] == model
        ]
        directory = self._cell_directory(dataset, pipeline, model)
        directory.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "run_id": self.run_id,
            "dataset": dataset,
            "pipeline": pipeline,
            "pipeline_directory": PIPELINE_DIRECTORIES[str(pipeline)],
            "model": model,
            "model_directory": safe_component(model),
            "updated_at_utc": utc_now(),
            "records": items,
        }
        _write_json_atomic(directory / "artifacts.json", payload)
        _write_text_atomic(
            directory / "summary.md",
            _cell_markdown(
                payload,
                expected=self._expected_for_cell(dataset),
            ),
        )

    def _cell_directory(self, dataset: str, pipeline: str, model: str) -> Path:
        return (
            self.root
            / safe_component(dataset)
            / PIPELINE_DIRECTORIES[str(pipeline)]
            / safe_component(model)
        )

    def _expected_for_cell(self, dataset: str) -> int | None:
        value = self.manifest.get("expected_observations_per_cell", {}).get(dataset)
        return int(value) if value is not None else None


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid checkpoint journal at {path}:{number}: {error}."
            ) from None
        if not isinstance(item, dict):
            raise ValueError(f"Checkpoint at {path}:{number} is not a JSON object.")
        records.append(item)
    return records


def _compatible_model_extension(
    existing_manifest: dict[str, Any],
    requested_manifest: dict[str, Any],
) -> list[str] | None:
    """Accept added models only when existing entries, order and contracts match."""

    existing_plan = existing_manifest.get("frozen_plan")
    requested_plan = requested_manifest.get("frozen_plan")
    if not isinstance(existing_plan, dict) or not isinstance(requested_plan, dict):
        return None
    old_models = existing_plan.get("models")
    new_models = requested_plan.get("models")
    if not isinstance(old_models, list) or not isinstance(new_models, list) or not old_models:
        return None
    if any(not isinstance(item, dict) or not isinstance(item.get("id"), str)
           for item in old_models + new_models):
        return None
    old_ids = [item["id"] for item in old_models]
    new_ids = [item["id"] for item in new_models]
    if len(set(old_ids)) != len(old_ids) or len(set(new_ids)) != len(new_ids):
        return None
    old_set = set(old_ids)
    if [model_id for model_id in new_ids if model_id in old_set] != old_ids:
        return None
    added = [model_id for model_id in new_ids if model_id not in old_set]
    if not added or existing_manifest.get("model_order") != old_ids:
        return None
    if requested_manifest.get("model_order") != new_ids:
        return None
    if [item for item in new_models if item["id"] in old_set] != old_models:
        return None
    if any(item.get("provider") == "ollama"
           and not isinstance(item.get("ollama_metadata"), dict)
           for item in new_models if item["id"] in added):
        return None
    old_total = existing_manifest.get("planned_observations")
    new_total = requested_manifest.get("planned_observations")
    if not isinstance(old_total, int) or old_total <= 0 or old_total % len(old_ids):
        return None
    if new_total != old_total // len(old_ids) * len(new_ids):
        return None
    if (existing_manifest.get("expected_observations_per_cell")
            != requested_manifest.get("expected_observations_per_cell")):
        return None
    for name in ("phase", "dataset_order", "pipeline_order", "shot_condition_order"):
        if existing_manifest.get(name) != requested_manifest.get(name):
            return None

    # Compare the remaining experiment contract independently of progress status.
    # Completed plans may gain new models, but existing executor hashes must match.
    old_contract = json.loads(json.dumps(existing_plan))
    new_contract = json.loads(json.dumps(requested_plan))
    for contract in (old_contract, new_contract):
        contract.pop("models")
        hashes = contract.get("runtime_source_hashes")
        if not isinstance(hashes, dict):
            return None
        for name in RESUME_COMPATIBLE_RUNTIME_CHANGES:
            hashes.pop(name, None)
    return added if old_contract == new_contract else None


def _compatible_resume_plan(
    existing_manifest: dict[str, Any],
    requested_manifest: dict[str, Any],
    progress_path: Path,
) -> bool:
    """Allow an interrupted run to resume after a compatible infrastructure edit.

    The runner source hash is part of the frozen plan for provenance, but the
    terminal renderer and zero-observation executor setup do not change prompts,
    model selection, datasets, or scoring. A non-complete legacy run may
    therefore resume when every frozen field except those hashes is identical.
    Other plan changes remain rejected; executor changes are allowed only when
    no observation has been checkpointed.
    """

    if not progress_path.exists():
        return False
    try:
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if progress.get("status") == "complete":
        return False
    completed_observations = int(progress.get("completed_observations", 0))
    existing_plan = existing_manifest.get("frozen_plan")
    requested_plan = requested_manifest.get("frozen_plan")
    if not isinstance(existing_plan, dict) or not isinstance(requested_plan, dict):
        return False
    existing_copy = json.loads(json.dumps(existing_plan))
    requested_copy = json.loads(json.dumps(requested_plan))
    runtime_hashes: list[dict[str, Any]] = []
    for plan in (existing_copy, requested_copy):
        hashes = plan.get("runtime_source_hashes")
        if not isinstance(hashes, dict):
            return False
        runtime_hashes.append(hashes)
    if (
        completed_observations > 0
        and any("executor.py" in hashes for hashes in runtime_hashes)
        and not existing_manifest.get("resume_compatibility_events")
    ):
        return False
    for hashes in runtime_hashes:
        for name in RESUME_COMPATIBLE_RUNTIME_CHANGES:
            hashes.pop(name, None)
        if completed_observations == 0 or existing_manifest.get("resume_compatibility_events"):
            for name in ZERO_OBSERVATION_COMPATIBLE_RUNTIME_CHANGES:
                hashes.pop(name, None)
    return existing_copy == requested_copy


def _write_json_atomic(path: Path, payload: Any) -> None:
    _write_text_atomic(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _cell_markdown(payload: dict[str, Any], *, expected: int | None) -> str:
    records = payload["records"]
    correct = sum(bool(item["correct"]) for item in records)
    latencies = [float(item["total_latency_seconds"]) for item in records]
    lines = [
        f"# {payload['dataset']} / {payload['pipeline_directory'].upper()} / {payload['model']}",
        "",
        f"- Canonical pipeline: `{payload['pipeline']}`",
        f"- Completed observations: {len(records)}" + (
            f" / {expected}" if expected is not None else ""
        ),
        f"- Correct objectives: {correct}",
        f"- Accuracy over completed observations: {(correct / len(records)):.4f}"
        if records else "- Accuracy over completed observations: n/a",
        f"- Median latency: {statistics.median(latencies):.3f} seconds"
        if latencies else "- Median latency: n/a",
        f"- Updated at: {payload['updated_at_utc']}",
        "",
        "## Prompt conditions",
        "",
        "| Condition | Completed | Correct | Accuracy |",
        "|---|---:|---:|---:|",
    ]
    by_shot: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records:
        by_shot[str(item.get("shot_condition", "zero_shot"))].append(item)
    for shot in ("zero_shot", "few_shot"):
        items = by_shot.get(shot, [])
        shot_correct = sum(bool(item["correct"]) for item in items)
        accuracy = f"{shot_correct / len(items):.4f}" if items else "n/a"
        lines.append(f"| {shot} | {len(items)} | {shot_correct} | {accuracy} |")
    lines.extend(
        [
            "",
            "## Terminal outcomes",
            "",
            "| Outcome | Count |",
            "|---|---:|",
        ]
    )
    for outcome, count in sorted(
        Counter(str(item["terminal_outcome"]) for item in records).items()
    ):
        lines.append(f"| {outcome} | {count} |")
    lines.extend(
        [
            "",
            "Complete prompts, raw provider responses, formulations, generated code, "
            "execution logs, typed errors, and timing metadata are stored in "
            "`artifacts.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def _progress_markdown(payload: dict[str, Any]) -> str:
    percent = 100 * float(payload["completion_fraction"])
    lines = [
        "# Benchmark progress",
        "",
        f"- Status: **{payload['status']}**",
        f"- Completed: {payload['completed_observations']} / {payload['planned_observations']} ({percent:.2f}%)",
        f"- Remaining: {payload['remaining_observations']}",
        f"- Updated at: {payload['updated_at_utc']}",
    ]
    if payload.get("interruption"):
        lines.append(f"- Interruption: {payload['interruption']}")
    if payload.get("current_observation"):
        lines.extend(
            [
                "",
                "## Current observation",
                "",
                "```json",
                json.dumps(payload["current_observation"], indent=2, ensure_ascii=False),
                "```",
            ]
        )
    lines.extend(["", "## Terminal outcomes", ""])
    for outcome, count in payload["terminal_outcomes"].items():
        lines.append(f"- `{outcome}`: {count}")
    lines.append("")
    return "\n".join(lines)
