"""Validate CH07 default-route RenderRecords, crops, timing, and review artifacts."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from build_ch06_default_route_review import sha256
from build_ch07_default_route_review import ELAPSED_SECONDS
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch07-sc01-panel-plans-r1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch06-ch07-default-house-route-prompt-manifest-r1.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch07-default-house-route-execution-r1.json"
PACKET = ROOT / "production/comic/run-manifests/ch07-default-house-route-review-packet-r1.json"
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


def verify_pixel(row: dict[str, Any], errors: list[str], label: str, *, check_files: bool) -> None:
    raw = row.get("path")
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
        errors.append(f"{label}.path must be safe and project-relative")
        return
    if not isinstance(row.get("sha256"), str) or len(row["sha256"]) != 64:
        errors.append(f"{label}.sha256 is invalid")
        return
    path = ROOT / raw
    if not check_files:
        return
    if not path.is_file() or sha256(path) != row["sha256"]:
        errors.append(f"{label} file/hash binding failed")
        return
    with Image.open(path) as opened:
        if [opened.width, opened.height] != [row.get("width"), row.get("height")]:
            errors.append(f"{label}.dimensions mismatch")


def validate(execution: dict[str, Any], packet: dict[str, Any], *, check_files: bool) -> list[str]:
    errors: list[str] = []
    expected_ids = [row["panel_id"] for row in sorted(load(PLANS)["plans"], key=lambda row: row["display_order"])]
    prompts = {row["request_id"]: row for row in load(PROMPTS)["requests"] if row["chapter"] == "CH07"}
    for label, document in (("execution", execution), ("packet", packet)):
        if document.get("planning_structure") != "ComicPanelPlan":
            errors.append(f"{label} planning structure must be ComicPanelPlan")
        if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None:
            errors.append(f"{label} cross-medium fields must remain null")

    records = execution.get("records")
    if not isinstance(records, list) or len(records) != 8:
        errors.append("execution must contain eight RenderRecords")
        records = []
    observed_ids: list[str] = []
    reference_uses = 0
    observed_elapsed: dict[str, float] = {}
    for index, row in enumerate(records):
        label = f"records[{index}]"
        request_id = row.get("request_id")
        prompt = prompts.get(request_id)
        if prompt is None:
            errors.append(f"{label} is not a CH07 preflight request")
            continue
        if row.get("panel_ids") != prompt["panel_ids"]:
            errors.append(f"{label}.panel_ids differ from preflight")
        observed_ids.extend(row.get("panel_ids", []))
        if row.get("exact_prompt") != prompt["prompt"] or row.get("prompt_sha256") != prompt["prompt_sha256"]:
            errors.append(f"{label} exact prompt binding differs from preflight")
        references = row.get("input_references")
        if references != prompt["reference_images"]:
            errors.append(f"{label} input references differ from preflight")
            references = []
        if any(ref.get("sha256") not in ALLOWED_HASHES for ref in references):
            errors.append(f"{label} uses a reference outside the exact authorized set")
        reference_uses += len(references)
        for field in NULL_FIELDS:
            if row.get(field) is not None or field not in row.get("unavailable_fields", []):
                errors.append(f"{label}.{field} must be null and declared unavailable")
        elapsed = row.get("elapsed_seconds")
        if not isinstance(elapsed, (int, float)) or elapsed <= 0 or elapsed != ELAPSED_SECONDS.get(request_id):
            errors.append(f"{label}.elapsed_seconds differs from the exact client observation")
        else:
            observed_elapsed[request_id] = float(elapsed)
        if row.get("elapsed_source") != "CLIENT_WRAPPER_DATE_NOW_AROUND_IMAGEGEN_CALL":
            errors.append(f"{label}.elapsed_source is invalid")
        if any(row.get(key) for key in ("accepted", "commercially_cleared", "exact_production_base", "reproducible")):
            errors.append(f"{label} overclaims acceptance, rights, exact-base, or reproducibility")
        output = row.get("output")
        if not isinstance(output, dict):
            errors.append(f"{label}.output must be an object")
        else:
            if not str(output.get("path", "")).startswith("experiments/review-packets/ch07-default-house-route-r1/source/"):
                errors.append(f"{label}.output is outside the ignored source directory")
            verify_pixel(output, errors, f"{label}.output", check_files=check_files)
    if observed_ids != expected_ids:
        errors.append("RenderRecord coverage/order differs from all 40 ordered plans")
    summary = execution.get("summary", {})
    expected_sum = round(sum(ELAPSED_SECONDS.values()), 3)
    if summary.get("sequence_outputs") != 8 or summary.get("panel_candidates") != 40 or summary.get("authorized_reference_uses") != reference_uses:
        errors.append("execution summary counts do not reconcile")
    if reference_uses != 21:
        errors.append(f"CH07 must have exactly 21 authorized reference uses, got {reference_uses}")
    if summary.get("client_observed_elapsed_seconds_sum") != expected_sum or observed_elapsed != ELAPSED_SECONDS:
        errors.append("client-observed timing does not reconcile")
    if summary.get("parallel_group_wall_seconds") != [497.196, 460.672]:
        errors.append("parallel group wall timing differs from observation")
    if summary.get("paid_api_cloud_spend_usd") != 0 or summary.get("built_in_monetary_cost_disclosed") is not False:
        errors.append("cost fields must preserve $0 paid API/cloud and unavailable built-in cost")

    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 40:
        errors.append("packet must contain 40 candidate crops")
        candidates = []
    if [row.get("panel_id") for row in candidates] != expected_ids or len({row.get("candidate_id") for row in candidates}) != 40:
        errors.append("candidate identity/order/uniqueness differs from all 40 plans")
    triage = {state: 0 for state in ("PASS", "WARN", "FAIL")}
    for index, row in enumerate(candidates):
        label = f"candidates[{index}]"
        state = row.get("agent_triage")
        if state not in triage:
            errors.append(f"{label}.agent_triage is invalid")
        else:
            triage[state] += 1
        if row.get("human_review_state") != "OWNER_REVIEW_PENDING" or row.get("human_review_minutes") is not None:
            errors.append(f"{label} owner review state is invalid")
        if any(row.get(key) for key in ("accepted", "commercially_cleared", "exact_production_base")):
            errors.append(f"{label} overclaims acceptance, clearance, or exact-base state")
        if not str(row.get("path", "")).startswith("experiments/review-packets/ch07-default-house-route-r1/crops/"):
            errors.append(f"{label}.path is outside the ignored crops directory")
        verify_pixel(row, errors, label, check_files=check_files)
    expected_triage = {"PASS": 37, "WARN": 1, "FAIL": 2}
    if triage != expected_triage:
        errors.append(f"triage must preserve 37/1/2, got {triage}")
    expected_failures = {
        8: ["TAMSIN_HAIR_CONTINUITY_DRIFT"],
        29: ["UNREQUESTED_RENDERED_TEXT"],
        39: ["WARDENS_REACH_FORM_DRIFT"],
    }
    for index, failure_classes in expected_failures.items():
        if len(candidates) > index and candidates[index].get("failure_classes") != failure_classes:
            errors.append(f"candidate P{index + 1:03d} must preserve {failure_classes}")

    required_types = {
        "contact_sheet",
        "sequence_contact_sheet",
        "complete_reading_draft",
        "phone_preview",
        "lettering_safe_zone_overlay",
    }
    artifacts = packet.get("artifacts")
    if not isinstance(artifacts, list) or {row.get("type") for row in artifacts} != required_types:
        errors.append("packet must contain all five required artifact types exactly once")
        artifacts = []
    for index, row in enumerate(artifacts):
        if not str(row.get("path", "")).startswith("experiments/review-packets/ch07-default-house-route-r1/"):
            errors.append(f"artifacts[{index}] is outside the ignored review packet")
        verify_pixel(row, errors, f"artifacts[{index}]", check_files=check_files)
    packet_summary = packet.get("summary", {})
    if packet_summary.get("complete_chapter") is not True or packet_summary.get("panel_plans") != 40:
        errors.append("packet summary must declare a complete 40-panel chapter")
    if packet_summary.get("triage") != triage or packet_summary.get("targeted_repairs_executed") != 0 or packet_summary.get("whole_chapter_alternate_arms") != 0:
        errors.append("packet triage/anti-duplication summary does not reconcile")
    return errors


def self_test(execution: dict[str, Any], packet: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    for mutate_execution, mutate_packet in (
        (lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"), None),
        (lambda d: d["records"].pop(), None),
        (lambda d: d["records"][0].__setitem__("exact_prompt", "changed"), None),
        (lambda d: d["records"][0].__setitem__("elapsed_seconds", 0), None),
        (lambda d: d["records"][0].__setitem__("accepted", True), None),
        (lambda d: d["records"][0]["input_references"][0].__setitem__("sha256", "0" * 64), None),
        (lambda d: d["summary"].__setitem__("parallel_group_wall_seconds", []), None),
        (lambda d: d["summary"].__setitem__("paid_api_cloud_spend_usd", 1), None),
        (None, lambda d: d.__setitem__("e_conte", {})),
        (None, lambda d: d["candidates"].pop()),
        (None, lambda d: d["candidates"][0].__setitem__("panel_id", "wrong")),
        (None, lambda d: d["candidates"][0].__setitem__("accepted", True)),
        (None, lambda d: d["candidates"][8].__setitem__("failure_classes", [])),
        (None, lambda d: d["candidates"][29].__setitem__("agent_triage", "PASS")),
        (None, lambda d: d["candidates"][39].__setitem__("failure_classes", [])),
        (None, lambda d: d["artifacts"].pop()),
        (None, lambda d: d["summary"].__setitem__("whole_chapter_alternate_arms", 1)),
    ):
        e_copy = copy.deepcopy(execution)
        p_copy = copy.deepcopy(packet)
        if mutate_execution:
            mutate_execution(e_copy)
        if mutate_packet:
            mutate_packet(p_copy)
        mutations.append(bool(validate(e_copy, p_copy, check_files=False)))
    return sum(mutations), len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    execution = load(EXECUTION)
    packet = load(PACKET)
    errors = validate(execution, packet, check_files=True)
    result: dict[str, Any] = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "sequences": len(execution.get("records", [])),
        "candidates": len(packet.get("candidates", [])),
        "triage": packet.get("summary", {}).get("triage"),
        "elapsed_sum": execution.get("summary", {}).get("client_observed_elapsed_seconds_sum"),
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
