"""Explicit, audited transitions for a model's local context allocation."""

from __future__ import annotations

import copy
from typing import Any

from .artifacts import record_key, utc_now
from .runner import _json_sha256


def validate_context_calibration(
    report: dict[str, Any], model: str, options: dict[str, int], purpose: str,
) -> None:
    measurements = [item for item in report.get("measurements", [])
                    if item.get("context_tokens") == options["num_ctx"]
                    and item.get("gpu_layers_requested") == options["num_gpu"]
                    and item.get("full_gpu")
                    and item.get("ollama_status", {}).get("name") == model]
    if not measurements:
        raise ValueError("Configuration lacks a successful full-GPU context probe.")
    if purpose == "vram_capacity":
        if report.get("model") != model or not any(
            95 <= item["peak_vram_percent"] <= 98 for item in measurements
        ):
            raise ValueError("Configuration lacks a successful 95-98% VRAM calibration.")
    elif purpose == "common_context":
        reference = report.get("gpt_oss_inherited_context_status", {})
        if reference.get("name") != "gpt-oss:20b" or reference.get("context_length") != options["num_ctx"]:
            raise ValueError("Context must match the verified reference-model window.")
    else:
        raise ValueError("Unknown context transition purpose.")


def transition_context(
    existing: dict[str, Any], requested: dict[str, Any], records: list[dict[str, Any]],
    *, model: str, expected_fingerprint: str, previous_client_sha256: str,
    journal_sha256: str, calibration_sha256: str, previous_context_tokens: int,
    reason: str = "Explicit user-requested Granite context and GPU allocation calibration",
) -> dict[str, Any]:
    """Preserve records and archive the previous plan. Never bypass normal resume checks."""
    if existing["plan_fingerprint"] != expected_fingerprint:
        raise ValueError("Checkpoint fingerprint does not match the explicit transition request.")
    if requested["plan_fingerprint"] != _json_sha256(requested["frozen_plan"]):
        raise ValueError("Requested plan fingerprint is invalid.")
    if _json_sha256(existing["frozen_plan"]) != expected_fingerprint:
        raise ValueError("Existing frozen plan fingerprint is invalid.")
    if len({record_key(item) for item in records}) != len(records):
        raise ValueError("Duplicate journal keys.")
    if any(item["run_id"] != existing["run_id"] for item in records):
        raise ValueError("Journal run ID mismatch.")
    old = copy.deepcopy(existing["frozen_plan"])
    new = copy.deepcopy(requested["frozen_plan"])
    old_options = old["settings"].pop("ollama_runtime_options", {})
    new_options = new["settings"].pop("ollama_runtime_options", {})
    before = old_options.pop(model, {})
    after = new_options.pop(model, {})
    if before.get("num_ctx", previous_context_tokens) != previous_context_tokens:
        raise ValueError("Previous context does not match the frozen configuration.")
    if old_options != new_options or before == after:
        raise ValueError("Only the selected model's allocation options may change.")
    if set(after) != {"num_ctx", "num_gpu"}:
        raise ValueError("Transition requires explicit num_ctx and num_gpu.")
    if type(after["num_ctx"]) is not int or after["num_ctx"] <= 0:
        raise ValueError("Invalid context.")
    if type(after["num_gpu"]) is not int or after["num_gpu"] < 0:
        raise ValueError("Invalid GPU layer count.")
    matching = [entry for entry in old["models"] if entry["id"] == model]
    if len(matching) != 1 or matching[0]["provider"] != "ollama":
        raise ValueError("Transition requires an existing Ollama model.")
    if old["runtime_source_hashes"]["clients.py"] != previous_client_sha256:
        raise ValueError("Previous client implementation does not match the reviewed baseline.")
    # No global compatibility exception is added for client implementation changes.
    # This explicit operation authorizes the reviewed optional allocation arguments.
    for plan in (old, new):
        for name in ("clients.py", "runner.py"):
            plan["runtime_source_hashes"].pop(name)
    if old != new:
        raise ValueError("Dataset, model, prompt, scoring or other inference contracts changed.")
    for key in ("run_id", "phase", "planned_observations", "model_order", "dataset_order",
                "pipeline_order", "shot_condition_order", "expected_observations_per_cell"):
        if existing.get(key) != requested.get(key):
            raise ValueError(f"Transition cannot change {key}.")
    result = copy.deepcopy(existing)
    result.setdefault("inference_configuration_events", []).append({
        "captured_at_utc": utc_now(),
        "reason": reason,
        "model": model, "previous_effective_context_tokens": previous_context_tokens,
        "previous_explicit_options": before, "requested_options": after,
        "previous_plan_fingerprint": expected_fingerprint,
        "previous_frozen_plan": existing["frozen_plan"],
        "requested_plan_fingerprint": requested["plan_fingerprint"],
        "completed_observations_at_transition": len(records),
        "journal_sha256_at_transition": journal_sha256,
        "calibration_sha256": calibration_sha256,
        "previous_model_observations": sum(item["model"] == model for item in records),
        "previous_records_preserved": True,
    })
    result["frozen_plan"] = copy.deepcopy(requested["frozen_plan"])
    result["plan_fingerprint"] = requested["plan_fingerprint"]
    return result
