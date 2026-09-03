"""Validate execution evidence for the CH05 premium-cel targeted-repair trio."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = (
    ROOT
    / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-execution-r1.json"
)
PREFLIGHT = (
    ROOT
    / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-r1.json"
)
UNAVAILABLE = [
    "model",
    "endpoint",
    "provider_request_id",
    "usage",
    "cost_usd",
    "deterministic_seed",
]
EXPECTED_IDS = [
    "exec-4d3dacc5-70fe-4be2-99c6-1b644c47d3f6",
    "exec-6b1b8988-6eee-4098-8992-6fcf739ee3c2",
    "exec-5b639804-ce1c-4658-8ae3-65d97a20fd55",
]


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


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    requests = preflight["requests"]
    rows = document.get("records", [])
    check(
        document.get("record_type")
        == "CH05PremiumCelTargetedRepairTrioExecutionManifest",
        "record_type",
    )
    check(
        document.get("schema_version") == "1.0"
        and document.get("record_id")
        == "ng-ch05-premium-cel-targeted-repair-trio-execution-r1",
        "identity",
    )
    check(
        document.get("state")
        == "THREE_OUTPUTS_EXECUTED_UNACCEPTED_PENDING_OWNER_REVIEW",
        "state",
    )
    check(
        document.get("medium") == "comic"
        and document.get("planning_structure") == "ComicPanelPlan",
        "comic planning",
    )
    check(
        document.get("animation_shot_plan") is None and document.get("e_conte") is None,
        "cross-medium fields",
    )
    check(
        document.get("preflight_manifest")
        == {
            "path": PREFLIGHT.relative_to(ROOT).as_posix(),
            "sha256": sha256(PREFLIGHT),
        },
        "preflight binding",
    )
    check(
        [row.get("display_order") for row in rows] == [1, 32, 39],
        "record order/denominator",
    )
    check(
        [row.get("execution", {}).get("tool_service_execution_id") for row in rows]
        == EXPECTED_IDS,
        "execution IDs",
    )
    check(
        sum(row.get("reference_use_count", 0) for row in rows) == 6
        and [len(row.get("input_references", [])) for row in rows] == [2, 2, 2],
        "reference uses",
    )
    for row, request in zip(rows, requests):
        order = row.get("display_order")
        for key in (
            "request_id",
            "panel_id",
            "display_order",
            "comic_panel_plan_revision_id",
            "comic_panel_plan_canonical_sha256",
            "prompt_revision_id",
            "prompt_text",
            "prompt_sha256",
            "input_references",
            "reference_use_count",
            "cross_panel_gate_bindings",
            "lettering_safe_zones",
        ):
            check(
                row.get(key) == request.get(key), f"preflight parity P{order:03d}:{key}"
            )
        check(
            hashlib.sha256(row.get("prompt_text", "").encode("utf-8")).hexdigest()
            == row.get("prompt_sha256"),
            f"prompt hash P{order:03d}",
        )
        execution = row.get("execution", {})
        check(
            execution.get("tool_mode") == "openai_builtin_imagegen_in_codex",
            f"tool mode P{order:03d}",
        )
        check(
            execution.get("tool_service_execution_id_is_provider_request_id") is False,
            f"ID distinction P{order:03d}",
        )
        check(
            execution.get("timing_batch_id") == "pc-repair-b01-parallel"
            and execution.get("parallel_batch_wall_seconds") == 169.0
            and execution.get("elapsed_seconds") is None,
            f"timing P{order:03d}",
        )
        check(
            execution.get("unavailable_fields") == UNAVAILABLE
            and all(execution.get(key) is None for key in UNAVAILABLE),
            f"unavailable metadata P{order:03d}",
        )
        output = row.get("output", {})
        check(
            output.get("path") == request.get("planned_output"),
            f"output path P{order:03d}",
        )
        expected_match = order != 39
        check(
            output.get("planned_dimensions") == request.get("planned_dimensions")
            and output.get("planned_dimensions_match") is expected_match,
            f"planned dimension comparison P{order:03d}",
        )
        check(
            row.get("human_review_state") == "PENDING_OWNER_REVIEW"
            and row.get("human_review_minutes") is None
            and all(
                row.get(key) is False
                for key in (
                    "accepted",
                    "commercially_cleared",
                    "exact_production_base",
                    "generation_reproducible",
                )
            ),
            f"review boundary P{order:03d}",
        )
        if verify_files:
            path = ROOT / output.get("path", "")
            check(path.is_file(), f"output exists P{order:03d}")
            if path.is_file():
                check(
                    sha256(path) == output.get("sha256")
                    and path.stat().st_size == output.get("bytes"),
                    f"output hash/bytes P{order:03d}",
                )
                with Image.open(path) as image:
                    check(
                        image.format == "PNG"
                        and [image.width, image.height]
                        == [output.get("width"), output.get("height")],
                        f"output decode/dimensions P{order:03d}",
                    )
                check(
                    ignored_untracked(output["path"]),
                    f"output ignored/untracked P{order:03d}",
                )
            for reference in row.get("input_references", []):
                ref_path = ROOT / reference.get("path", "")
                check(
                    ref_path.is_file() and sha256(ref_path) == reference.get("sha256"),
                    f"reference binding P{order:03d}",
                )
    check(
        document.get("timing_batches")
        == [
            {
                "timing_batch_id": "pc-repair-b01-parallel",
                "wall_seconds": 169.0,
                "member_panel_ids": [
                    "ng-ch05-sc01-p001",
                    "ng-ch05-sc01-p032",
                    "ng-ch05-sc01-p039",
                ],
                "member_execution_ids": EXPECTED_IDS,
            }
        ],
        "timing batch",
    )
    summary = document.get("summary", {})
    check(
        (
            summary.get("standalone_outputs"),
            summary.get("comic_panel_plans"),
            summary.get("authorized_reference_uses"),
            summary.get("unique_timing_batches"),
            summary.get("overlap_adjusted_tool_call_wall_seconds"),
            summary.get("per_output_elapsed_seconds_available"),
        )
        == (3, 3, 6, 1, 169.0, 0),
        "summary counts/timing",
    )
    check(
        summary.get("direct_paid_provider_api_calls") == 0
        and summary.get("paid_spend_usd") == 0.0,
        "paid boundary",
    )
    check(
        all(
            summary.get(key) == 0
            for key in (
                "human_reviewed_outputs",
                "accepted_outputs",
                "commercially_cleared_outputs",
                "exact_production_base_outputs",
            )
        ),
        "summary review boundary",
    )
    check(
        document.get("boundary")
        == {
            "permitted_product": "openai_builtin_imagegen",
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "gemini_calls": 0,
            "xai_calls": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
        },
        "boundary",
    )
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value["preflight_manifest"].__setitem__("sha256", "0" * 64),
        lambda value: value["records"].pop(),
        lambda value: value["records"][0].__setitem__("prompt_text", "tampered"),
        lambda value: value["records"][0]["execution"].__setitem__(
            "tool_service_execution_id", EXPECTED_IDS[1]
        ),
        lambda value: value["records"][0]["execution"].__setitem__(
            "elapsed_seconds", 169.0
        ),
        lambda value: value["records"][0]["execution"].__setitem__("model", "invented"),
        lambda value: value["records"][2]["output"].__setitem__(
            "planned_dimensions_match", True
        ),
        lambda value: value["records"][1].__setitem__("accepted", True),
        lambda value: value["timing_batches"][0]["member_panel_ids"].pop(),
        lambda value: value["summary"].__setitem__("authorized_reference_uses", 50),
        lambda value: value["summary"].__setitem__(
            "overlap_adjusted_tool_call_wall_seconds", 507.0
        ),
        lambda value: value["summary"].__setitem__("paid_spend_usd", 1.0),
        lambda value: value["boundary"].__setitem__("bfl_calls", 1),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "records": len(document.get("records", [])),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
