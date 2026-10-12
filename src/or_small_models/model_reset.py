"""Explicit removal of one model's observations after a recoverable checkpoint."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

from .artifacts import PIPELINE_DIRECTORIES, ResultStore, _write_json_atomic, record_key, safe_component, utc_now
from .runner import _json_sha256, _write_environment_summary


def filter_model_lines(contents: bytes, model: str, *, diagnostics: bool = False):
    kept, removed, records = [], [], []
    for line in contents.splitlines(keepends=True):
        if not line.strip():
            kept.append(line)
            continue
        item = json.loads(line)
        observation = item.get("observation", {}) if diagnostics else item
        if observation.get("model") == model:
            removed.append(observation)
        else:
            kept.append(line)
            records.append(observation)
    return b"".join(kept), records, removed


def _replace_bytes(path: Path, contents: bytes):
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(contents)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def reset_model_results(
    root: Path, requested: dict[str, Any], *, model: str,
    expected_fingerprint: str, expected_journal_sha256: str, backup_commit: str,
    calibration_sha256: str,
    template_change: dict[str, Any] | None = None,
    reason: str = "User requested removal of all Granite observations and restart with 32768-token context",
) -> dict[str, Any]:
    """Validate the entire scope before deleting model-specific files or journal rows."""
    root = root.resolve(strict=True)
    state = root / "_state"
    manifest_path = state / "manifest.json"
    progress_path = state / "progress.json"
    ledger = state / "records.jsonl"
    existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    progress_bytes = progress_path.read_bytes()
    progress = json.loads(progress_bytes)
    if progress["status"] not in {"interrupted", "failed", "waiting_for_credits"}:
        raise ValueError("Interrupt the benchmark safely before resetting a model.")
    if existing["plan_fingerprint"] != expected_fingerprint:
        raise ValueError("Frozen plan does not match the requested reset.")
    if _json_sha256(existing["frozen_plan"]) != expected_fingerprint:
        raise ValueError("Existing plan fingerprint is invalid.")
    if _json_sha256(requested["frozen_plan"]) != requested["plan_fingerprint"]:
        raise ValueError("Requested plan fingerprint is invalid.")
    if not isinstance(existing.get("environment"), dict):
        raise ValueError("Checkpoint environment metadata is missing.")
    old, new = copy.deepcopy(existing["frozen_plan"]), copy.deepcopy(requested["frozen_plan"])
    old_options = old["settings"].get("ollama_runtime_options", {})
    new_options = new["settings"].get("ollama_runtime_options", {})
    requested_options = new_options.get(model, {})
    if any(key not in new["settings"] for key in ("request_timeout_seconds", "retry_request_timeouts",
                                                "code_timeout_seconds", "max_transport_retries")):
        raise ValueError("Checkpoint runtime settings are incomplete.")
    if set(requested_options) != {"num_ctx", "num_gpu"}:
        raise ValueError("Reset requires explicit context and GPU options.")
    if type(requested_options["num_ctx"]) is not int or requested_options["num_ctx"] <= 0:
        raise ValueError("Invalid context size.")
    if requested_options["num_gpu"] != old_options.get(model, {}).get("num_gpu"):
        raise ValueError("Reset may change context only, not GPU allocation.")
    old_options[model] = copy.deepcopy(requested_options)
    if template_change is not None:
        # This is an explicit model reset, not a general resume exception.
        # Permit only the selected model's verified template metadata to change.
        if requested_options != existing["frozen_plan"]["settings"]["ollama_runtime_options"].get(model):
            raise ValueError("A template reset must preserve inference options.")
        if (template_change.get("model") != model
                or not template_change.get("weight_blob_before")
                or template_change.get("weight_blob_before") != template_change.get("weight_blob_after")
                or template_change.get("thinking") != "full"
                or template_change.get("additional_system_instructions") is not None):
            raise ValueError("Template reset requires identical weights and full thinking.")
        for name in ("template_before", "template_after"):
            text = template_change.get(name)
            if not isinstance(text, str) or not text:
                raise ValueError("Template provenance is incomplete.")
            if hashlib.sha256(text.encode()).hexdigest() != template_change.get(name + "_sha256"):
                raise ValueError("Template checksum mismatch.")
        before = next(entry for entry in old["models"] if entry["id"] == model)
        after = next(entry for entry in new["models"] if entry["id"] == model)
        if (before["ollama_metadata"] != template_change.get("metadata_before")
                or after["ollama_metadata"] != template_change.get("metadata_after")):
            raise ValueError("Template metadata do not match the frozen plans.")
        for field in ("format", "family", "parameter_size", "quantization_level"):
            if (before["ollama_metadata"].get("details", {}).get(field)
                    != after["ollama_metadata"].get("details", {}).get(field)):
                raise ValueError("Template reset cannot change weight metadata.")
        before["ollama_metadata"] = copy.deepcopy(after["ollama_metadata"])
    if old != new:
        raise ValueError("Only the selected model's authorized context or template metadata may change during reset.")
    if not any(item["id"] == model and item["provider"] == "ollama" for item in old["models"]):
        raise ValueError("Reset requires an existing Ollama model.")
    for key in ("run_id", "phase", "planned_observations", "model_order", "dataset_order",
                "pipeline_order", "shot_condition_order", "expected_observations_per_cell"):
        if existing.get(key) != requested.get(key):
            raise ValueError(f"Reset cannot change {key}.")
    contents = ledger.read_bytes()
    if hashlib.sha256(contents).hexdigest() != expected_journal_sha256:
        raise ValueError("Journal does not match the recoverable checkpoint.")
    kept_bytes, kept, removed = filter_model_lines(contents, model)
    if not removed:
        raise ValueError("No observations exist for the selected model.")
    keys = [record_key(item) for item in kept + removed]
    if len(set(keys)) != len(keys) or len(keys) != progress["completed_observations"]:
        raise ValueError("Journal key or progress count mismatch.")
    if any(item["run_id"] != existing["run_id"] for item in kept + removed):
        raise ValueError("Journal run ID mismatch.")

    # Resolve every recursive-delete target before any mutation. Never delete the
    # result root or a dataset/pipeline parent, and reject escaped links or collisions.
    directories = []
    for dataset in existing["dataset_order"]:
        for pipeline in existing["pipeline_order"]:
            candidate = root / safe_component(dataset) / PIPELINE_DIRECTORIES[pipeline] / safe_component(model)
            if not candidate.exists():
                continue
            resolved = candidate.resolve(strict=True)
            if not resolved.is_relative_to(root) or resolved.relative_to(root).parts != (
                safe_component(dataset), PIPELINE_DIRECTORIES[pipeline], safe_component(model)
            ):
                raise ValueError("Unsafe model result directory.")
            for child in candidate.rglob("*"):
                if not child.resolve().is_relative_to(resolved):
                    raise ValueError("Escaped link in model result directory.")
            artifact = candidate / "artifacts.json"
            if artifact.exists():
                payload = json.loads(artifact.read_text(encoding="utf-8"))
                if payload.get("model") != model or any(item.get("model") != model for item in payload.get("records", [])):
                    raise ValueError("Model directory contains another model's records.")
            directories.append(candidate)

    diagnostics_path = state / "infrastructure_errors.jsonl"
    diagnostic_bytes = diagnostics_path.read_bytes() if diagnostics_path.exists() else None
    removed_diagnostics = []
    filtered_diagnostics = None
    if diagnostic_bytes is not None:
        filtered_diagnostics, _, removed_diagnostics = filter_model_lines(diagnostic_bytes, model, diagnostics=True)

    updated = copy.deepcopy(existing)
    updated.setdefault("model_reset_events", []).append({
        "captured_at_utc": utc_now(), "model": model,
        "reason": reason,
        "backup_commit": backup_commit,
        "previous_plan_fingerprint": expected_fingerprint,
        "previous_frozen_plan": existing["frozen_plan"],
        "requested_plan_fingerprint": requested["plan_fingerprint"],
        "journal_sha256_before": expected_journal_sha256,
        "journal_sha256_after": hashlib.sha256(kept_bytes).hexdigest(),
        "removed_observations": len(removed), "removed_infrastructure_diagnostics": len(removed_diagnostics),
        "retained_observations": len(kept), "requested_options": requested_options,
        "calibration_sha256": calibration_sha256,
        **({"template_change": copy.deepcopy(template_change)} if template_change is not None else {}),
        "removed_directories": [str(path.relative_to(root)).replace("\\", "/") for path in directories],
    })
    updated["frozen_plan"] = copy.deepcopy(requested["frozen_plan"])
    updated["plan_fingerprint"] = requested["plan_fingerprint"]
    # Earlier configuration boundaries describe the archived pre-reset journal,
    # not positions in the newly filtered journal.
    event = updated["model_reset_events"][-1]
    plan = updated["frozen_plan"]
    first_dataset = plan["datasets"][0]
    repetition = plan["repetition_start"]
    current = {"model": model, "dataset": first_dataset["name"],
               "example_id": first_dataset["selected_example_ids"][0],
               "pipeline": plan["pipelines"][(repetition - 1) % len(plan["pipelines"])],
               "shot_condition": plan["shot_conditions"][0], "repetition": repetition}
    if progress_path.read_bytes() != progress_bytes or ledger.read_bytes() != contents:
        raise ValueError("Checkpoint changed while preparing the reset.")
    _replace_bytes(ledger, kept_bytes)
    _write_json_atomic(manifest_path, updated)
    if removed_diagnostics:
        _replace_bytes(diagnostics_path, filtered_diagnostics)
    for path in directories:
        shutil.rmtree(path)
    store = ResultStore(root, requested, record_resume_event=False)
    store.write_progress(status="interrupted", current=current,
                         interruption="Granite results reset by user request. Ready for manual restart of this model.")
    _write_environment_summary(root, store.manifest)
    return {"removed_observations": event["removed_observations"], "retained_observations": len(kept),
            "next_observation": current, "removed_directories": event["removed_directories"]}
