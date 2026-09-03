"""Compile execution evidence for the CH05 premium-cel targeted-repair trio."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = (
    ROOT
    / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-r1.json"
)
OUTPUT = (
    ROOT
    / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-execution-r1.json"
)
UNAVAILABLE = [
    "model",
    "endpoint",
    "provider_request_id",
    "usage",
    "cost_usd",
    "deterministic_seed",
]
RUNS: dict[int, dict[str, Any]] = {
    1: {
        "id": "exec-4d3dacc5-70fe-4be2-99c6-1b644c47d3f6",
        "sha": "505c8209f6c4c3652b7dd0e69673004cb90de29cdfb8ca26828d4aa5409f2e36",
        "width": 1536,
        "height": 1024,
        "bytes": 2636163,
    },
    32: {
        "id": "exec-6b1b8988-6eee-4098-8992-6fcf739ee3c2",
        "sha": "5b07b01c04b951b1bbdc0703cdaec82a3816512ee4cf86fc5203452562ab192d",
        "width": 1024,
        "height": 1536,
        "bytes": 2835821,
    },
    39: {
        "id": "exec-5b639804-ce1c-4658-8ae3-65d97a20fd55",
        "sha": "d7714ebe9d6646a23ee0b38f2c8e872fc18163c5297c83c288cf55211ea17281",
        "width": 1023,
        "height": 1537,
        "bytes": 2642455,
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ignored_untracked(relative: str) -> bool:
    ignored = (
        subprocess.run(
            ["git", "check-ignore", "--quiet", "--", relative], cwd=ROOT, check=False
        ).returncode
        == 0
    )
    tracked = (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )
    return ignored and not tracked


def main() -> int:
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    records = []
    for request in preflight["requests"]:
        order = request["display_order"]
        run = RUNS[order]
        path = ROOT / request["planned_output"]
        if (
            not path.is_file()
            or sha256(path) != run["sha"]
            or path.stat().st_size != run["bytes"]
        ):
            raise ValueError(f"output byte binding P{order:03d}")
        with Image.open(path) as image:
            if image.format != "PNG" or image.size != (run["width"], run["height"]):
                raise ValueError(f"output decode/dimensions P{order:03d}")
        if not ignored_untracked(request["planned_output"]):
            raise ValueError(f"output must be ignored and untracked P{order:03d}")
        records.append(
            {
                "request_id": request["request_id"],
                "panel_id": request["panel_id"],
                "display_order": order,
                "comic_panel_plan_revision_id": request["comic_panel_plan_revision_id"],
                "comic_panel_plan_canonical_sha256": request[
                    "comic_panel_plan_canonical_sha256"
                ],
                "prompt_revision_id": request["prompt_revision_id"],
                "prompt_text": request["prompt_text"],
                "prompt_sha256": request["prompt_sha256"],
                "input_references": request["input_references"],
                "reference_use_count": request["reference_use_count"],
                "cross_panel_gate_bindings": request["cross_panel_gate_bindings"],
                "lettering_safe_zones": request["lettering_safe_zones"],
                "execution": {
                    "tool_mode": "openai_builtin_imagegen_in_codex",
                    "tool_service_execution_id": run["id"],
                    "tool_service_execution_id_is_provider_request_id": False,
                    "timing_batch_id": "pc-repair-b01-parallel",
                    "elapsed_seconds": None,
                    "parallel_batch_wall_seconds": 169.0,
                    "model": None,
                    "endpoint": None,
                    "provider_request_id": None,
                    "usage": None,
                    "cost_usd": None,
                    "deterministic_seed": None,
                    "unavailable_fields": UNAVAILABLE,
                },
                "output": {
                    "path": request["planned_output"],
                    "sha256": run["sha"],
                    "width": run["width"],
                    "height": run["height"],
                    "bytes": run["bytes"],
                    "planned_dimensions": request["planned_dimensions"],
                    "planned_dimensions_match": [run["width"], run["height"]]
                    == [
                        request["planned_dimensions"]["width_px"],
                        request["planned_dimensions"]["height_px"],
                    ],
                },
                "human_review_state": "PENDING_OWNER_REVIEW",
                "human_review_minutes": None,
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
                "generation_reproducible": False,
            }
        )
    if [row["display_order"] for row in records] != [1, 32, 39] or set(RUNS) != {
        1,
        32,
        39,
    }:
        raise ValueError("targeted repair execution set differs from P001/P032/P039")
    document = {
        "record_type": "CH05PremiumCelTargetedRepairTrioExecutionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-premium-cel-targeted-repair-trio-execution-r1",
        "state": "THREE_OUTPUTS_EXECUTED_UNACCEPTED_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "preflight_manifest": {
            "path": PREFLIGHT.relative_to(ROOT).as_posix(),
            "sha256": sha256(PREFLIGHT),
        },
        "summary": {
            "standalone_outputs": 3,
            "comic_panel_plans": 3,
            "authorized_reference_uses": 6,
            "unique_timing_batches": 1,
            "overlap_adjusted_tool_call_wall_seconds": 169.0,
            "timing_scope": "One concurrent Codex ImageGen tool-call batch at 0.1-second precision; includes queue, generation, and transfer time exposed to the caller.",
            "per_output_elapsed_seconds_available": 0,
            "direct_paid_provider_api_calls": 0,
            "paid_spend_usd": 0.0,
            "human_reviewed_outputs": 0,
            "accepted_outputs": 0,
            "commercially_cleared_outputs": 0,
            "exact_production_base_outputs": 0,
        },
        "timing_batches": [
            {
                "timing_batch_id": "pc-repair-b01-parallel",
                "wall_seconds": 169.0,
                "member_panel_ids": [row["panel_id"] for row in records],
                "member_execution_ids": [
                    row["execution"]["tool_service_execution_id"] for row in records
                ],
            }
        ],
        "records": records,
        "limitations": [
            "The built-in tool exposed no model, endpoint, provider request ID, usage, monetary cost, or deterministic seed.",
            "Tool-service execution IDs are provenance aids and are not provider request IDs.",
            "Parallel execution exposes batch wall only; all three per-output elapsed times remain null.",
            "P039 decoded at 1023x1537 rather than its planned 1024x1536; exact output dimensions are preserved without resampling.",
            "Agent triage is non-gating and does not replace owner review.",
            "No output is accepted, commercially cleared, or selected as an exact production base.",
        ],
        "boundary": {
            "permitted_product": "openai_builtin_imagegen",
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "gemini_calls": 0,
            "xai_calls": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
        },
    }
    OUTPUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256(OUTPUT),
                **document["summary"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
