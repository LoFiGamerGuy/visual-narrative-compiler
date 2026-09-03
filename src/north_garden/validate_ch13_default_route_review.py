"""Validate CH13 default-route RenderRecords, crops, timing, and review packet."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from build_ch06_default_route_review import sha256
from build_ch13_default_route_review import ELAPSED_SECONDS, GROUP_WALL_SECONDS, triage
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch13-sc01-panel-plans-r1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch12-ch13-default-house-route-prompt-manifest-r1.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch13-default-house-route-execution-r1.json"
PACKET = ROOT / "production/comic/run-manifests/ch13-default-house-route-review-packet-r1.json"
ALLOWED = {"cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d", "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a", "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb"}
NULL_FIELDS = ("model", "endpoint", "provider_request_id", "provider_usage", "monetary_cost_usd", "deterministic_seed")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pixel(row: dict[str, Any], errors: list[str], label: str, files: bool) -> None:
    raw = row.get("path")
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
        errors.append(f"{label} unsafe path")
        return
    if not isinstance(row.get("sha256"), str) or len(row["sha256"]) != 64:
        errors.append(f"{label} invalid hash")
        return
    if files:
        path = ROOT / raw
        if not path.is_file() or sha256(path) != row["sha256"]:
            errors.append(f"{label} file/hash")
        else:
            with Image.open(path) as opened:
                if [opened.width, opened.height] != [row.get("width"), row.get("height")]:
                    errors.append(f"{label} dimensions")


def validate(execution: dict[str, Any], packet: dict[str, Any], *, files: bool) -> list[str]:
    errors: list[str] = []
    plans = sorted(load(PLANS)["plans"], key=lambda p: p["display_order"])
    expected_ids = [p["panel_id"] for p in plans]
    prompts = {r["request_id"]: r for r in load(PROMPTS)["requests"] if r["chapter"] == "CH13"}
    for label, doc in (("execution", execution), ("packet", packet)):
        if doc.get("planning_structure") != "ComicPanelPlan" or doc.get("animation_shot_plan") is not None or doc.get("e_conte") is not None:
            errors.append(f"{label} medium boundary")
    records = execution.get("records", [])
    if len(records) != 8:
        errors.append("eight RenderRecords required")
    observed_ids, observed_times, refs = [], {}, 0
    for index, row in enumerate(records):
        label, request_id = f"records[{index}]", row.get("request_id")
        prompt = prompts.get(request_id)
        if prompt is None:
            errors.append(f"{label} request binding")
            continue
        observed_ids.extend(row.get("panel_ids", []))
        if row.get("panel_ids") != prompt["panel_ids"] or row.get("exact_prompt") != prompt["prompt"] or row.get("prompt_sha256") != prompt["prompt_sha256"]:
            errors.append(f"{label} prompt/panel binding")
        references = row.get("input_references", [])
        if references != prompt["reference_images"] or any(r.get("sha256") not in ALLOWED for r in references):
            errors.append(f"{label} reference boundary")
        refs += len(references)
        for field in NULL_FIELDS:
            if row.get(field) is not None or field not in row.get("unavailable_fields", []):
                errors.append(f"{label} null/unavailable {field}")
        elapsed = row.get("elapsed_seconds")
        if elapsed != ELAPSED_SECONDS.get(request_id) or row.get("elapsed_source") != "CLIENT_WRAPPER_DATE_NOW_AROUND_IMAGEGEN_CALL":
            errors.append(f"{label} exact timing")
        else:
            observed_times[request_id] = elapsed
        if any(row.get(k) for k in ("accepted", "commercially_cleared", "exact_production_base", "reproducible")):
            errors.append(f"{label} status overclaim")
        output = row.get("output", {})
        if not str(output.get("path", "")).startswith("experiments/review-packets/ch13-default-house-route-r1/source/"):
            errors.append(f"{label} source scope")
        pixel(output, errors, f"{label}.output", files)
    if observed_ids != expected_ids:
        errors.append("ordered 40-panel coverage")
    if observed_times != ELAPSED_SECONDS:
        errors.append("exact timing reconciliation")
    summary = execution.get("summary", {})
    elapsed_sum = round(sum(ELAPSED_SECONDS.values()), 3)
    if (summary.get("sequence_outputs"), summary.get("panel_candidates"), summary.get("authorized_reference_uses")) != (8, 40, refs) or refs != 22:
        errors.append("execution count/reference reconciliation")
    if summary.get("client_observed_elapsed_seconds_sum") != elapsed_sum or summary.get("parallel_group_wall_seconds") != GROUP_WALL_SECONDS:
        errors.append("timing summary")
    if summary.get("paid_api_cloud_spend_usd") != 0 or summary.get("built_in_monetary_cost_disclosed") is not False:
        errors.append("cost state")
    candidates = packet.get("candidates", [])
    if len(candidates) != 40 or [c.get("panel_id") for c in candidates] != expected_ids or len({c.get("candidate_id") for c in candidates}) != 40:
        errors.append("candidate coverage/identity")
    counts = {state: 0 for state in ("PASS", "WARN", "FAIL")}
    for index, row in enumerate(candidates):
        label = f"candidates[{index}]"
        state = row.get("agent_triage")
        if state in counts:
            counts[state] += 1
        else:
            errors.append(f"{label} triage state")
        if (state, row.get("failure_classes"), row.get("triage_note")) != triage(row.get("panel_id", "")):
            errors.append(f"{label} editable TRIAGE binding")
        if row.get("human_review_state") != "OWNER_REVIEW_PENDING" or row.get("human_review_minutes") is not None or any(row.get(k) for k in ("accepted", "commercially_cleared", "exact_production_base")):
            errors.append(f"{label} review/status")
        pixel(row, errors, label, files)
    expected_counts = {state: sum(triage(panel_id)[0] == state for panel_id in expected_ids) for state in counts}
    if counts != expected_counts:
        errors.append("triage count mapping")
    required = {"contact_sheet", "sequence_contact_sheet", "complete_reading_draft", "phone_preview", "lettering_safe_zone_overlay"}
    artifacts = packet.get("artifacts", [])
    if {a.get("type") for a in artifacts} != required or len(artifacts) != 5:
        errors.append("five artifact contract")
    for index, row in enumerate(artifacts):
        pixel(row, errors, f"artifacts[{index}]", files)
    packet_summary = packet.get("summary", {})
    if packet_summary.get("complete_chapter") is not True or packet_summary.get("panel_plans") != 40 or packet_summary.get("triage") != counts or packet_summary.get("targeted_repairs_executed") != 0 or packet_summary.get("whole_chapter_alternate_arms") != 0:
        errors.append("packet summary")
    return errors


def self_test(execution: dict[str, Any], packet: dict[str, Any]) -> tuple[int, int]:
    mutations = (
        (lambda d: d.update(planning_structure="AnimationShotPlan"), None), (lambda d: d["records"].pop(), None),
        (lambda d: d["records"][0].update(exact_prompt="changed"), None), (lambda d: d["records"][0].update(elapsed_seconds=0), None),
        (lambda d: d["records"][0].update(accepted=True), None), (lambda d: d["records"][0]["input_references"][0].update(sha256="0" * 64), None),
        (lambda d: d["summary"].update(parallel_group_wall_seconds=[]), None), (lambda d: d["summary"].update(paid_api_cloud_spend_usd=1), None),
        (None, lambda d: d.update(e_conte={})), (None, lambda d: d["candidates"].pop()),
        (None, lambda d: d["candidates"][0].update(panel_id="wrong")), (None, lambda d: d["candidates"][0].update(agent_triage="FAIL")),
        (None, lambda d: d["candidates"][0].update(accepted=True)), (None, lambda d: d["artifacts"].pop()),
        (None, lambda d: d["summary"].update(whole_chapter_alternate_arms=1)),
    )
    caught = 0
    for mutate_e, mutate_p in mutations:
        e_copy, p_copy = copy.deepcopy(execution), copy.deepcopy(packet)
        if mutate_e:
            mutate_e(e_copy)
        if mutate_p:
            mutate_p(p_copy)
        caught += bool(validate(e_copy, p_copy, files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    execution, packet = load(EXECUTION), load(PACKET)
    errors = validate(execution, packet, files=True)
    result = {"status": "PASS" if not errors else "FAIL", "errors": errors, "sequences": len(execution.get("records", [])), "candidates": len(packet.get("candidates", [])), "triage": packet.get("summary", {}).get("triage"), "elapsed_sum": execution.get("summary", {}).get("client_observed_elapsed_seconds_sum")}
    if args.self_test and not errors:
        caught, total = self_test(execution, packet)
        result["self_test"] = f"{caught}/{total}"
        if caught != total:
            result["status"] = "FAIL"
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
