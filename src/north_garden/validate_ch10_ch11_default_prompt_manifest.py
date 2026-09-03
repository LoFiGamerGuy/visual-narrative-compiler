"""Validate the one-route CH10-CH11 built-in ImageGen prompt manifest."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch10-ch11-default-house-route-prompt-manifest-r1.json"
PLANS = {
    "CH10": ROOT / "production/comic/ch10-sc01-panel-plans-r1.json",
    "CH11": ROOT / "production/comic/ch11-sc01-panel-plans-r1.json",
}
ALLOWED_HASHES = {
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
}
REQUIRED_PHRASES = (
    "Use case: illustration-story",
    "exactly five clearly separated panels",
    "one row only",
    "Do not add visible panel numbers",
    "clearly fictional adult",
    "never black or bright blond",
    "never blond or loose red curls",
    "medium chestnut-brown hair in one practical braid",
    "padded rigid quarry brace",
    "never a gun, firearm, crossbow, spear-gun, or complex machine",
    "owned compact recurved bow",
    "MIREBACKS are mature quadrupedal peat-root-and-slate creatures",
    "Render no readable Ledger words",
    "adult-only fictional cast",
    "no child",
    "no real-person likeness",
    "render no letters",
    "Do not substitute generic speed-line texture",
)
BANNED_GENERATED_COPY = (
    "DRAFT LOST / OUTER DRAW ACTIVE",
    "SERVICE SHARED / IRON CLAIM EARNED",
    "DEFENDERS DECLARED",
    "THRESHOLD HELD",
    "HEARTH WARDEN—EARNED",
    "THORNPATH WAYFINDER—EARNED",
    "TWO HANDS, ONE THRESHOLD",
    "labeled for return",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(data: dict[str, Any], *, check_files: bool = True) -> list[str]:
    found: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            found.append(message)

    check(data.get("record_type") == "MultiChapterBuiltInImageGenPromptManifest", "record type")
    check(data.get("state") == "PREFLIGHT_READY_FOR_AUTHORIZED_BUILT_IN_EXECUTION", "state")
    check(data.get("mechanism") == "OPENAI_BUILT_IN_IMAGEGEN_ONLY", "mechanism")
    check(data.get("planning_structure") == "ComicPanelPlan", "planning structure")
    check(data.get("animation_shot_plan") is None and data.get("e_conte") is None, "cross-medium boundary")
    requests = data.get("requests", [])
    check(len(requests) == 16, "request count")
    expected_ids = []
    for path in PLANS.values():
        expected_ids.extend(row["panel_id"] for row in json.loads(path.read_text(encoding="utf-8"))["plans"])
    actual_ids = [panel_id for request in requests for panel_id in request.get("panel_ids", [])]
    check(actual_ids == expected_ids, "exact chronological panel coverage")
    check(len(actual_ids) == len(set(actual_ids)) == 80, "unique 80-panel coverage")
    check(all(len(request.get("panel_ids", [])) == 5 for request in requests), "five panels per request")
    check(len({request.get("sequence_id") for request in requests}) == 16, "unique sequences")
    for request in requests:
        request_id = request.get("request_id")
        prompt = request.get("prompt", "")
        check(hashlib.sha256(prompt.encode("utf-8")).hexdigest() == request.get("prompt_sha256"), f"prompt hash {request_id}")
        check(all(phrase in prompt for phrase in REQUIRED_PHRASES), f"prompt contract {request_id}")
        check(not any(phrase in prompt for phrase in BANNED_GENERATED_COPY), f"generated copy withheld {request_id}")
        check(all(panel_id in prompt for panel_id in request.get("panel_ids", [])), f"panel bindings {request_id}")
        references = request.get("reference_images", [])
        hashes = {reference.get("sha256") for reference in references}
        check(2 <= len(references) <= 3 and hashes <= ALLOWED_HASHES, f"reference boundary {request_id}")
        check(request.get("reference_count") == len(references), f"reference count {request_id}")
        if check_files:
            for reference in references:
                path = ROOT / reference.get("path", "")
                check(path.is_file() and sha256(path) == reference.get("sha256"), f"reference file {request_id}")
        check(request.get("execution_state") == "PREFLIGHTED_NOT_EXECUTED", f"execution state {request_id}")
        for key in (
            "output",
            "elapsed_seconds",
            "model",
            "endpoint",
            "provider_request_id",
            "usage",
            "monetary_cost_usd",
            "deterministic_seed",
        ):
            check(request.get(key) is None, f"null pre-execution {request_id} {key}")
    boundary = data.get("authorized_reference_boundary", {})
    check(boundary.get("only_these_exact_hashes") is True, "exact hash boundary")
    check(boundary.get("new_generated_outputs_may_be_reuploaded") is False, "no output reupload")
    check(boundary.get("bfl_uploads") == 0 and boundary.get("other_provider_uploads") == 0, "provider upload boundary")
    check(
        data.get("anti_duplication")
        == {
            "chapter_count": 2,
            "sequence_requests": 16,
            "panel_plan_coverage": 80,
            "default_candidates_per_panel": 1,
            "whole_chapter_alternate_style_arms": 0,
            "targeted_repair_cap_per_failed_panel": 2,
        },
        "anti-duplication contract",
    )
    summary = data.get("summary", {})
    check(summary.get("chapters") == 2 and summary.get("sequences") == 16 and summary.get("panel_plans") == 80, "summary coverage")
    check(summary.get("reference_uses") == sum(row.get("reference_count", 0) for row in requests), "reference uses")
    check(32 <= summary.get("reference_uses", 0) <= 48, "reference-use range")
    check(summary.get("provider_calls") == 0 and summary.get("outputs") == 0 and summary.get("paid_api_spend_usd") == 0, "zero execution summary")
    decisions = data.get("promotion_decisions", [])
    check(len(decisions) == 2, "promotion decisions")
    if check_files:
        for decision in decisions:
            path = ROOT / decision.get("path", "")
            check(path.is_file() and sha256(path) == decision.get("sha256"), f"promotion binding {decision.get('path')}")
            if path.is_file():
                payload = json.loads(path.read_text(encoding="utf-8"))
                check(payload.get("state") == "APPROVED_FOR_EXACT_PROMPT_PREFLIGHT_NOT_YET_EXECUTED", "promotion state")
                check(payload.get("approved_mechanism") == "OPENAI_BUILT_IN_IMAGEGEN_ONLY", "promotion mechanism")
                continuity = payload.get("visual_continuity_decisions", {})
                check("medium_chestnut_brown" in continuity.get("tamsin_hair", ""), "Tamsin continuity anchor")
                check("rigid_left_lower_leg_brace" in continuity.get("soren_injury", ""), "Soren injury continuity")
                check("never_firearm" in continuity.get("wardens_reach", ""), "Warden's Reach continuity")
                check("compact_recurved_bow" in continuity.get("sigrid_weapons", ""), "Sigrid weapon continuity")
                check(continuity.get("ledger_words") == "WITHHELD_FROM_GENERATED_PIXELS_FOR_LOCAL_LETTERING", "local Ledger copy")
    return found


def self_test(data: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.update(state="EXECUTED"),
        lambda value: value.update(mechanism="BFL"),
        lambda value: value.update(planning_structure="AnimationShotPlan"),
        lambda value: value.update(e_conte={}),
        lambda value: value["requests"].pop(),
        lambda value: value["requests"][1].update(sequence_id=value["requests"][0]["sequence_id"]),
        lambda value: value["requests"][0]["panel_ids"].pop(),
        lambda value: value["requests"][1]["panel_ids"].__setitem__(0, value["requests"][0]["panel_ids"][0]),
        lambda value: value["requests"][0].update(prompt="weak"),
        lambda value: value["requests"][0].update(prompt_sha256="0" * 64),
        lambda value: value["requests"][0].update(prompt=value["requests"][0]["prompt"].replace("one row only", "two rows")),
        lambda value: value["requests"][0].update(prompt=value["requests"][0]["prompt"] + " ROAD TENDED inscription"),
        lambda value: value["requests"][0]["reference_images"].append({"path": "private.png", "sha256": "1" * 64}),
        lambda value: value["requests"][0].update(reference_count=99),
        lambda value: value["requests"][0].update(execution_state="COMPLETE"),
        lambda value: value["requests"][0].update(output={}),
        lambda value: value["requests"][0].update(monetary_cost_usd=0),
        lambda value: value["authorized_reference_boundary"].update(new_generated_outputs_may_be_reuploaded=True),
        lambda value: value["authorized_reference_boundary"].update(bfl_uploads=1),
        lambda value: value["anti_duplication"].update(default_candidates_per_panel=4),
        lambda value: value["anti_duplication"].update(whole_chapter_alternate_style_arms=1),
        lambda value: value["anti_duplication"].update(targeted_repair_cap_per_failed_panel=8),
        lambda value: value["summary"].update(panel_plans=79),
        lambda value: value["summary"].update(reference_uses=99),
        lambda value: value["summary"].update(provider_calls=1),
        lambda value: value["summary"].update(paid_api_spend_usd=1),
        lambda value: value["promotion_decisions"].pop(),
    ]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(data)
        mutation(candidate)
        rejected += bool(errors(candidate, check_files=False))
    return rejected, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    found = errors(data)
    result: dict[str, Any] = {
        "status": "PASS" if not found else "FAIL",
        "errors": found,
        "requests": len(data.get("requests", [])),
        "panels": data.get("summary", {}).get("panel_plans"),
        "reference_uses": data.get("summary", {}).get("reference_uses"),
    }
    if args.self_test:
        rejected, total = self_test(data)
        result["self_test"] = f"{rejected}/{total}"
        if rejected != total:
            found.append(f"only {rejected}/{total} mutations rejected")
            result["status"] = "FAIL"
    print(json.dumps(result, sort_keys=True))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())

