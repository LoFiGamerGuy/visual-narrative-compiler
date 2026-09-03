"""Validate CH12 default-route RenderRecords, crops, timing, and review packet."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from build_ch06_default_route_review import sha256
from build_ch12_default_route_review import (
    GROUP1_ENVELOPE_SECONDS,
    GROUP1_IDS,
    GROUP1_RECONSTRUCTED_SECONDS,
    GROUP2_EXACT_SECONDS,
    GROUP2_IDS,
    GROUP2_WALL_SECONDS,
    triage,
)
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch12-sc01-panel-plans-r1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch12-ch13-default-house-route-prompt-manifest-r1.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch12-default-house-route-execution-r1.json"
PACKET = ROOT / "production/comic/run-manifests/ch12-default-house-route-review-packet-r1.json"
ALLOWED_HASHES = {
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
}
NULL_FIELDS = (
    "model",
    "endpoint",
    "provider_request_id",
    "provider_usage",
    "monetary_cost_usd",
    "deterministic_seed",
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_pixel(row: dict[str, Any], errors: list[str], label: str, check_files: bool) -> None:
    raw = row.get("path")
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
        errors.append(f"{label}.path must be safe and relative")
        return
    if not isinstance(row.get("sha256"), str) or len(row["sha256"]) != 64:
        errors.append(f"{label}.sha256 is invalid")
        return
    if not check_files:
        return
    path = ROOT / raw
    if not path.is_file() or sha256(path) != row["sha256"]:
        errors.append(f"{label} file/hash binding failed")
        return
    with Image.open(path) as opened:
        if [opened.width, opened.height] != [row.get("width"), row.get("height")]:
            errors.append(f"{label}.dimensions mismatch")


def validate(execution: dict[str, Any], packet: dict[str, Any], *, check_files: bool) -> list[str]:
    errors: list[str] = []
    plans = sorted(load(PLANS)["plans"], key=lambda row: row["display_order"])
    expected_ids = [row["panel_id"] for row in plans]
    prompts = {row["request_id"]: row for row in load(PROMPTS)["requests"] if row["chapter"] == "CH12"}
    for label, document in (("execution", execution), ("packet", packet)):
        if document.get("planning_structure") != "ComicPanelPlan":
            errors.append(f"{label} must use ComicPanelPlan")
        if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None:
            errors.append(f"{label} cross-medium fields must be null")
    records = execution.get("records")
    if not isinstance(records, list) or len(records) != 8:
        errors.append("execution must contain eight RenderRecords")
        records = []
    observed_ids: list[str] = []
    reference_uses = 0
    observed_group2: dict[str, float] = {}
    observed_group1: dict[str, float] = {}
    for index, row in enumerate(records):
        label = f"records[{index}]"
        request_id = row.get("request_id")
        prompt = prompts.get(request_id)
        if prompt is None:
            errors.append(f"{label} is not a CH12 request")
            continue
        if row.get("panel_ids") != prompt["panel_ids"]:
            errors.append(f"{label}.panel_ids differ from preflight")
        observed_ids.extend(row.get("panel_ids", []))
        if row.get("exact_prompt") != prompt["prompt"] or row.get("prompt_sha256") != prompt["prompt_sha256"]:
            errors.append(f"{label} prompt binding differs")
        references = row.get("input_references")
        if references != prompt["reference_images"]:
            errors.append(f"{label} reference binding differs")
            references = []
        if any(reference.get("sha256") not in ALLOWED_HASHES for reference in references):
            errors.append(f"{label} reference hash is unauthorized")
        reference_uses += len(references)
        for field in NULL_FIELDS:
            if row.get(field) is not None or field not in row.get("unavailable_fields", []):
                errors.append(f"{label}.{field} must be null/unavailable")
        elapsed = row.get("elapsed_seconds")
        if request_id in GROUP1_IDS:
            if not isinstance(elapsed, (int, float)) or elapsed != GROUP1_RECONSTRUCTED_SECONDS[request_id]:
                errors.append(f"{label}.elapsed_seconds differs from timestamp reconstruction")
            else:
                observed_group1[request_id] = float(elapsed)
            if "elapsed_seconds" in row.get("unavailable_fields", []):
                errors.append(f"{label}.elapsed_seconds cannot be marked unavailable")
            if row.get("elapsed_source") != "OUTPUT_TIMESTAMP_RECONSTRUCTED_FROM_GROUP_WALL":
                errors.append(f"{label}.elapsed_source must preserve reconstruction provenance")
            if row.get("timing_group") != "parallel_group_1" or row.get("group_elapsed_envelope_seconds") != GROUP1_ENVELOPE_SECONDS:
                errors.append(f"{label} group 1 timing binding differs")
        elif request_id in GROUP2_IDS:
            if not isinstance(elapsed, (int, float)) or elapsed != GROUP2_EXACT_SECONDS[request_id]:
                errors.append(f"{label}.elapsed_seconds differs from exact wrapper interval")
            else:
                observed_group2[request_id] = float(elapsed)
            if "elapsed_seconds" in row.get("unavailable_fields", []):
                errors.append(f"{label}.elapsed_seconds cannot be marked unavailable")
            if row.get("elapsed_source") != "CLIENT_WRAPPER_DATE_NOW_AROUND_IMAGEGEN_CALL":
                errors.append(f"{label}.elapsed_source is invalid")
            if row.get("timing_group") != "parallel_group_2" or row.get("group_elapsed_envelope_seconds") != GROUP2_WALL_SECONDS:
                errors.append(f"{label} group 2 timing binding differs")
        else:
            errors.append(f"{label} has no timing group")
        if any(row.get(key) for key in ("accepted", "commercially_cleared", "exact_production_base", "reproducible")):
            errors.append(f"{label} overclaims status")
        output = row.get("output", {})
        if not str(output.get("path", "")).startswith("experiments/review-packets/ch12-default-house-route-r1/source/"):
            errors.append(f"{label}.output is outside ignored source directory")
        verify_pixel(output, errors, f"{label}.output", check_files)
    if observed_ids != expected_ids:
        errors.append("RenderRecord coverage/order differs from 40 ordered plans")
    if observed_group1 != GROUP1_RECONSTRUCTED_SECONDS:
        errors.append("group 1 reconstructed timing does not reconcile")
    if observed_group2 != GROUP2_EXACT_SECONDS:
        errors.append("group 2 exact timing does not reconcile")
    summary = execution.get("summary", {})
    reconstructed_elapsed_sum = round(sum(GROUP1_RECONSTRUCTED_SECONDS.values()), 3)
    exact_elapsed_sum = round(sum(GROUP2_EXACT_SECONDS.values()), 3)
    combined_elapsed_sum = round(reconstructed_elapsed_sum + exact_elapsed_sum, 3)
    if summary.get("sequence_outputs") != 8 or summary.get("panel_candidates") != 40 or summary.get("authorized_reference_uses") != reference_uses:
        errors.append("execution summary counts do not reconcile")
    if reference_uses != 22:
        errors.append(f"authorized reference uses must be 22, got {reference_uses}")
    if summary.get("client_observed_elapsed_seconds_sum") != combined_elapsed_sum:
        errors.append("combined overlapping elapsed sum differs")
    if summary.get("reconstructed_per_request_elapsed_seconds_sum") != reconstructed_elapsed_sum:
        errors.append("reconstructed-subset elapsed sum differs")
    if summary.get("exact_per_request_elapsed_seconds_sum_available_subset") != exact_elapsed_sum:
        errors.append("available-subset elapsed sum differs")
    if summary.get("group1_client_envelope_seconds") != GROUP1_ENVELOPE_SECONDS:
        errors.append("group 1 client envelope differs")
    if summary.get("parallel_group_wall_seconds") != [GROUP1_ENVELOPE_SECONDS, GROUP2_WALL_SECONDS]:
        errors.append("parallel wall/envelope timing differs")
    expected_timing_groups = [
        {
            "timing_group": "parallel_group_1",
            "request_ids": list(GROUP1_IDS),
            "measurement": "OUTPUT_TIMESTAMP_RECONSTRUCTED_FROM_GROUP_WALL",
            "group_elapsed_envelope_seconds": GROUP1_ENVELOPE_SECONDS,
            "per_request_elapsed_seconds_available": True,
            "per_request_elapsed_seconds": GROUP1_RECONSTRUCTED_SECONDS,
            "reconstructed": True,
        },
        {
            "timing_group": "parallel_group_2",
            "request_ids": list(GROUP2_IDS),
            "measurement": "CLIENT_WRAPPER_DATE_NOW_AROUND_IMAGEGEN_CALL",
            "group_wall_seconds": GROUP2_WALL_SECONDS,
            "per_request_elapsed_seconds_available": True,
            "per_request_elapsed_seconds": GROUP2_EXACT_SECONDS,
        },
    ]
    if execution.get("timing_groups") != expected_timing_groups:
        errors.append("timing-group evidence differs")
    if summary.get("paid_api_cloud_spend_usd") != 0 or summary.get("built_in_monetary_cost_disclosed") is not False:
        errors.append("cost state is invalid")

    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 40:
        errors.append("packet must contain 40 candidates")
        candidates = []
    if [row.get("panel_id") for row in candidates] != expected_ids or len({row.get("candidate_id") for row in candidates}) != 40:
        errors.append("candidate identity/order/uniqueness differs")
    triage_counts = {state: 0 for state in ("PASS", "WARN", "FAIL")}
    for index, row in enumerate(candidates):
        label = f"candidates[{index}]"
        state = row.get("agent_triage")
        if state not in triage_counts:
            errors.append(f"{label}.agent_triage is invalid")
        else:
            triage_counts[state] += 1
        expected_state, expected_failures, expected_note = triage(row.get("panel_id", ""))
        if (state, row.get("failure_classes"), row.get("triage_note")) != (
            expected_state,
            expected_failures,
            expected_note,
        ):
            errors.append(f"{label} differs from editable TRIAGE mapping")
        if row.get("human_review_state") != "OWNER_REVIEW_PENDING" or row.get("human_review_minutes") is not None:
            errors.append(f"{label} owner review state is invalid")
        if any(row.get(key) for key in ("accepted", "commercially_cleared", "exact_production_base")):
            errors.append(f"{label} overclaims status")
        verify_pixel(row, errors, label, check_files)
    expected_triage = {state: sum(triage(panel_id)[0] == state for panel_id in expected_ids) for state in triage_counts}
    if triage_counts != expected_triage:
        errors.append(f"triage must preserve editable mapping {expected_triage}, got {triage_counts}")
    required = {
        "contact_sheet",
        "sequence_contact_sheet",
        "complete_reading_draft",
        "phone_preview",
        "lettering_safe_zone_overlay",
    }
    artifacts = packet.get("artifacts")
    if not isinstance(artifacts, list) or {row.get("type") for row in artifacts} != required:
        errors.append("packet must contain five exact artifacts")
        artifacts = []
    for index, row in enumerate(artifacts):
        verify_pixel(row, errors, f"artifacts[{index}]", check_files)
    packet_summary = packet.get("summary", {})
    if packet_summary.get("complete_chapter") is not True or packet_summary.get("panel_plans") != 40:
        errors.append("packet is not a complete 40-panel chapter")
    if (
        packet_summary.get("triage") != triage_counts
        or packet_summary.get("targeted_repairs_executed") != 0
        or packet_summary.get("whole_chapter_alternate_arms") != 0
    ):
        errors.append("packet triage/anti-duplication does not reconcile")
    return errors


def self_test(execution: dict[str, Any], packet: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    for mutate_e, mutate_p in (
        (lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"), None),
        (lambda d: d["records"].pop(), None),
        (lambda d: d["records"][0].__setitem__("exact_prompt", "changed"), None),
        (lambda d: d["records"][0].__setitem__("elapsed_seconds", 0), None),
        (lambda d: d["records"][0]["unavailable_fields"].append("elapsed_seconds"), None),
        (lambda d: d["records"][4].__setitem__("elapsed_seconds", None), None),
        (lambda d: d["records"][4]["unavailable_fields"].append("elapsed_seconds"), None),
        (lambda d: d["records"][0].__setitem__("accepted", True), None),
        (lambda d: d["records"][0]["input_references"][0].__setitem__("sha256", "0" * 64), None),
        (lambda d: d["summary"].__setitem__("client_observed_elapsed_seconds_sum", 1), None),
        (lambda d: d["summary"].__setitem__("group1_client_envelope_seconds", 0), None),
        (lambda d: d["summary"].__setitem__("parallel_group_wall_seconds", []), None),
        (lambda d: d["timing_groups"][0].__setitem__("reconstructed", False), None),
        (lambda d: d["summary"].__setitem__("paid_api_cloud_spend_usd", 1), None),
        (None, lambda d: d.__setitem__("e_conte", {})),
        (None, lambda d: d["candidates"].pop()),
        (None, lambda d: d["candidates"][0].__setitem__("panel_id", "wrong")),
        (None, lambda d: d["candidates"][0].__setitem__("agent_triage", "FAIL")),
        (None, lambda d: d["candidates"][0].__setitem__("accepted", True)),
        (None, lambda d: d["artifacts"].pop()),
        (None, lambda d: d["summary"].__setitem__("whole_chapter_alternate_arms", 1)),
    ):
        e_copy, p_copy = copy.deepcopy(execution), copy.deepcopy(packet)
        if mutate_e:
            mutate_e(e_copy)
        if mutate_p:
            mutate_p(p_copy)
        mutations.append(bool(validate(e_copy, p_copy, check_files=False)))
    return sum(mutations), len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    execution, packet = load(EXECUTION), load(PACKET)
    errors = validate(execution, packet, check_files=True)
    result: dict[str, Any] = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "sequences": len(execution.get("records", [])),
        "candidates": len(packet.get("candidates", [])),
        "triage": packet.get("summary", {}).get("triage"),
        "group1_envelope_seconds": execution.get("summary", {}).get("group1_client_envelope_seconds"),
        "exact_elapsed_sum_available_subset": execution.get("summary", {}).get(
            "exact_per_request_elapsed_seconds_sum_available_subset"
        ),
    }
    if args.self_test and not errors:
        rejected, total = self_test(execution, packet)
        result["self_test"] = f"{rejected}/{total}"
        if rejected != total:
            result["status"] = "FAIL"
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
