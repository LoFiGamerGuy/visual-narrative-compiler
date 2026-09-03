"""Fail closed on the stage-aware CH12-CH13 built-in ImageGen preflight."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from typing import Any

from compile_ch12_ch13_default_prompt_manifest import (
    ADR,
    DECISIONS,
    MARKDOWN,
    OUTPUT,
    PLANS,
    REFERENCES,
    ROOT,
    build_outputs,
    sha256,
)

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
    "Stage-aware continuity:",
    "clearly fictional adult",
    "never black or bright blond",
    "never blond or loose red curls",
    "medium chestnut-brown hair in one practical braid",
    "never blond, clean-shaven, or Soren-like",
    "padded rigid quarry brace",
    "CROWNROOT is an enormous non-human botanical and architectural root-cistern guardian",
    "never a human figure, human corpse, exposed body, humanoid monster, gore creature",
    "HOLLOW STAG is a full-grown non-human ecological guardian",
    "MIREBACK is a full-grown quadrupedal peat-root-and-slate creature",
    "Render no readable Ledger words",
    "adult-only fictional cast",
    "no child",
    "no real-person likeness",
    "render no letters",
    "Do not substitute generic speed-line texture",
    "premature or reset garment damage",
    "premature or reversed key fusion",
)
BANNED_GENERATED_COPY = (
    "TWO HANDS mark",
    "TWO HANDS, ONE THRESHOLD",
    "SINGLE KEEPER REQUIRED",
    "BOUNDARYWRIGHT WARDEN",
    "THORNPATH MARSHAL",
    "Crownroot speaks Hearth Warden",
    "they write separate authority, veto, halt, disclosure, and restart rules",
)
STAGE_TOKENS = {
    "ng-ch12-s01-hidden-section": "do not preview later damage or fusion",
    "ng-ch12-s02-ash-cut": "do not preview later damage or fusion",
    "ng-ch12-s03-false-cairn": "do not preview later damage or fusion",
    "ng-ch12-s04-separate-paths": "do not preview later damage or fusion",
    "ng-ch12-s05-sacrificed-cloth": "Panels 1-3 keep Soren's oatmeal shoulder intact",
    "ng-ch12-s06-truth-at-camp": "Panels 1-2 keep Sigrid's plaid cape intact",
    "ng-ch12-s07-negotiated-return": "the brass key remains separate from Warden's Reach",
    "ng-ch12-s08-gate-consent": "Panels 1-3 keep the brass key separate",
    "ng-ch13-s01-summer-under-winter": "the brass boundary key permanently fused into Warden's Reach",
    "ng-ch13-s02-moving-glass": "the brass boundary key permanently fused into Warden's Reach",
    "ng-ch13-s03-crownroot-demand": "the brass boundary key permanently fused into Warden's Reach",
    "ng-ch13-s04-soil-water-load": "the brass boundary key permanently fused into Warden's Reach",
    "ng-ch13-s05-seven-node-circle": "the brass boundary key permanently fused into Warden's Reach",
    "ng-ch13-s06-boundary-heart": "the brass boundary key permanently fused into Warden's Reach",
    "ng-ch13-s07-co-keeper-choice": "the brass boundary key permanently fused into Warden's Reach",
    "ng-ch13-s08-wider-branches": "the brass boundary key permanently fused into Warden's Reach",
}


def load_outputs() -> dict[str, Any]:
    return {
        "decisions": {
            chapter: json.loads(path.read_text(encoding="utf-8")) for chapter, path in DECISIONS.items()
        },
        "manifest": json.loads(OUTPUT.read_text(encoding="utf-8")),
        "markdown": MARKDOWN.read_text(encoding="utf-8"),
        "adr": ADR.read_text(encoding="utf-8"),
    }


def expected_outputs() -> dict[str, Any]:
    decisions, manifest, markdown, adr = build_outputs()
    return {"decisions": decisions, "manifest": manifest, "markdown": markdown, "adr": adr}


def validate(package: dict[str, Any], *, check_files: bool = True) -> list[str]:
    found: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            found.append(message)

    expected = expected_outputs()
    check(package == expected, "compiled outputs are stale, mutated, or nondeterministic")
    data = package.get("manifest", {})
    check(data.get("record_type") == "MultiChapterBuiltInImageGenPromptManifest", "record type")
    check(data.get("state") == "PREFLIGHT_READY_FOR_AUTHORIZED_BUILT_IN_EXECUTION", "state")
    check(data.get("mechanism") == "OPENAI_BUILT_IN_IMAGEGEN_ONLY", "mechanism")
    check(data.get("planning_structure") == "ComicPanelPlan", "planning structure")
    check(data.get("animation_shot_plan") is None and data.get("e_conte") is None, "cross-medium boundary")
    requests = data.get("requests", [])
    check(len(requests) == 16, "request count")
    check([request.get("chapter") for request in requests].count("CH12") == 8, "CH12 request count")
    check([request.get("chapter") for request in requests].count("CH13") == 8, "CH13 request count")
    expected_ids: list[str] = []
    for path in PLANS.values():
        document = json.loads(path.read_text(encoding="utf-8"))
        check(document.get("planning_structure") == "ComicPanelPlan", f"source planning structure {path.name}")
        check(document.get("animation_shot_plan") is None and document.get("e_conte") is None, f"source medium boundary {path.name}")
        expected_ids.extend(row["panel_id"] for row in document["plans"])
    actual_ids = [panel_id for request in requests for panel_id in request.get("panel_ids", [])]
    check(actual_ids == expected_ids, "exact chronological panel coverage")
    check(len(actual_ids) == len(set(actual_ids)) == 80, "unique 80-panel coverage")
    check(all(len(request.get("panel_ids", [])) == 5 for request in requests), "five panels per request")
    check(len({request.get("sequence_id") for request in requests}) == 16, "unique sequences")
    for request in requests:
        request_id = request.get("request_id", "")
        prompt = request.get("prompt", "")
        check(request_id == request.get("sequence_id"), f"request/sequence binding {request_id}")
        check(hashlib.sha256(prompt.encode("utf-8")).hexdigest() == request.get("prompt_sha256"), f"prompt hash {request_id}")
        check(all(phrase in prompt for phrase in REQUIRED_PHRASES), f"prompt contract {request_id}")
        check(not any(phrase in prompt for phrase in BANNED_GENERATED_COPY), f"generated copy withheld {request_id}")
        check(all(panel_id in prompt for panel_id in request.get("panel_ids", [])), f"panel bindings {request_id}")
        check(STAGE_TOKENS.get(request_id, "missing-stage-token") in prompt, f"stage continuity {request_id}")
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
            "output", "elapsed_seconds", "model", "endpoint", "provider_request_id", "usage",
            "monetary_cost_usd", "deterministic_seed",
        ):
            check(request.get(key) is None, f"null pre-execution {request_id} {key}")
    boundary = data.get("authorized_reference_boundary", {})
    check(boundary.get("images") == REFERENCES, "manifest reference declaration")
    check(boundary.get("only_these_exact_hashes") is True, "exact hash boundary")
    check(boundary.get("new_generated_outputs_may_be_reuploaded") is False, "no output reupload")
    check(boundary.get("bfl_uploads") == 0 and boundary.get("other_provider_uploads") == 0, "provider upload boundary")
    check(data.get("anti_duplication") == {
        "chapter_count": 2,
        "sequence_requests": 16,
        "panel_plan_coverage": 80,
        "default_candidates_per_panel": 1,
        "whole_chapter_alternate_style_arms": 0,
        "targeted_repair_cap_per_failed_panel": 2,
    }, "anti-duplication contract")
    summary = data.get("summary", {})
    check(summary.get("chapters") == 2 and summary.get("sequences") == 16, "summary chapter/sequence coverage")
    check(summary.get("panel_plans") == 80 and summary.get("reference_uses") == 44, "summary panel/reference coverage")
    check(summary.get("reference_uses") == sum(row.get("reference_count", 0) for row in requests), "reference-use sum")
    check(summary.get("provider_calls") == 0 and summary.get("outputs") == 0 and summary.get("paid_api_spend_usd") == 0, "zero execution summary")
    decisions = package.get("decisions", {})
    check(set(decisions) == {"CH12", "CH13"}, "decision chapter set")
    for chapter, payload in decisions.items():
        check(payload.get("state") == "APPROVED_FOR_EXACT_PROMPT_PREFLIGHT_NOT_YET_EXECUTED", f"promotion state {chapter}")
        check(payload.get("approved_mechanism") == "OPENAI_BUILT_IN_IMAGEGEN_ONLY", f"promotion mechanism {chapter}")
        check(payload.get("planning_structure") == "ComicPanelPlan", f"decision planning {chapter}")
        check(payload.get("animation_shot_plan") is None and payload.get("e_conte") is None, f"decision medium boundary {chapter}")
        check(set(payload.get("approved_reference_hashes", [])) == ALLOWED_HASHES, f"decision reference hashes {chapter}")
        check(payload.get("adr") == "ADR-0212", f"decision ADR {chapter}")
        continuity = payload.get("visual_continuity_decisions", {})
        check("CH12_P024" in continuity.get("stage_aware_garments", ""), f"shoulder transition {chapter}")
        check("CH12_P028" in continuity.get("stage_aware_garments", ""), f"plaid transition {chapter}")
        check("CH12_P039" in continuity.get("stage_aware_key", ""), f"key transition {chapter}")
        check("never_blond_or_soren_like" in continuity.get("halvor_identity", ""), f"Halvor identity {chapter}")
        check("nonhuman_botanical_architectural" in continuity.get("crownroot", ""), f"Crownroot identity {chapter}")
        check(continuity.get("ledger_words") == "WITHHELD_FROM_GENERATED_PIXELS_FOR_LOCAL_LETTERING", f"local lettering {chapter}")
        source = payload.get("source_plan", {})
        source_path = ROOT / source.get("path", "")
        check(source.get("panel_count") == 40, f"source count {chapter}")
        if check_files:
            check(source_path.is_file() and sha256(source_path) == source.get("sha256"), f"source hash {chapter}")
    bindings = data.get("promotion_decisions", [])
    check(len(bindings) == 2, "promotion decision bindings")
    if check_files:
        for binding in bindings:
            path = ROOT / binding.get("path", "")
            check(path.is_file() and sha256(path) == binding.get("sha256"), f"promotion file {binding.get('path')}")
    markdown = package.get("markdown", "")
    adr = package.get("adr", "")
    for token in ("Sixteen", "80", "44", "Sequence-specific", "Crownroot", "paid API/cloud spend remain zero"):
        check(token in markdown, f"preflight note token {token}")
    for token in ("ADR-0212", "chronological execution only", "CH12 P024", "P028", "P039", "New outputs remain ineligible for re-upload"):
        check(token in adr, f"ADR token {token}")
    return found


def self_test(package: dict[str, Any]) -> tuple[int, int]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("state", lambda p: p["manifest"].update(state="EXECUTED")),
        ("mechanism", lambda p: p["manifest"].update(mechanism="BFL")),
        ("planning", lambda p: p["manifest"].update(planning_structure="AnimationShotPlan")),
        ("econte", lambda p: p["manifest"].update(e_conte={})),
        ("request", lambda p: p["manifest"]["requests"].pop()),
        ("sequence", lambda p: p["manifest"]["requests"][1].update(sequence_id=p["manifest"]["requests"][0]["sequence_id"])),
        ("panel_missing", lambda p: p["manifest"]["requests"][0]["panel_ids"].pop()),
        ("panel_duplicate", lambda p: p["manifest"]["requests"][1]["panel_ids"].__setitem__(0, p["manifest"]["requests"][0]["panel_ids"][0])),
        ("prompt", lambda p: p["manifest"]["requests"][0].update(prompt="weak")),
        ("prompt_hash", lambda p: p["manifest"]["requests"][0].update(prompt_sha256="0" * 64)),
        ("stage", lambda p: p["manifest"]["requests"][4].update(prompt=p["manifest"]["requests"][4]["prompt"].replace("Panels 1-3 keep Soren's oatmeal shoulder intact", "ignore state"))),
        ("copy", lambda p: p["manifest"]["requests"][3].update(prompt=p["manifest"]["requests"][3]["prompt"] + " TWO HANDS, ONE THRESHOLD")),
        ("reference", lambda p: p["manifest"]["requests"][0]["reference_images"].append({"path": "private.png", "sha256": "1" * 64})),
        ("reference_count", lambda p: p["manifest"]["requests"][0].update(reference_count=99)),
        ("execution", lambda p: p["manifest"]["requests"][0].update(execution_state="COMPLETE")),
        ("output", lambda p: p["manifest"]["requests"][0].update(output={})),
        ("cost", lambda p: p["manifest"]["requests"][0].update(monetary_cost_usd=0)),
        ("reupload", lambda p: p["manifest"]["authorized_reference_boundary"].update(new_generated_outputs_may_be_reuploaded=True)),
        ("bfl", lambda p: p["manifest"]["authorized_reference_boundary"].update(bfl_uploads=1)),
        ("candidates", lambda p: p["manifest"]["anti_duplication"].update(default_candidates_per_panel=4)),
        ("alternates", lambda p: p["manifest"]["anti_duplication"].update(whole_chapter_alternate_style_arms=1)),
        ("repairs", lambda p: p["manifest"]["anti_duplication"].update(targeted_repair_cap_per_failed_panel=8)),
        ("panels", lambda p: p["manifest"]["summary"].update(panel_plans=79)),
        ("uses", lambda p: p["manifest"]["summary"].update(reference_uses=45)),
        ("calls", lambda p: p["manifest"]["summary"].update(provider_calls=1)),
        ("spend", lambda p: p["manifest"]["summary"].update(paid_api_spend_usd=1)),
        ("decision_missing", lambda p: p["decisions"].pop("CH13")),
        ("decision_provider", lambda p: p["decisions"]["CH12"].update(approved_mechanism="OTHER")),
        ("decision_ref", lambda p: p["decisions"]["CH13"]["approved_reference_hashes"].append("1" * 64)),
        ("halvor", lambda p: p["decisions"]["CH12"]["visual_continuity_decisions"].update(halvor_identity="blond")),
        ("crownroot", lambda p: p["decisions"]["CH13"]["visual_continuity_decisions"].update(crownroot="human")),
        ("markdown", lambda p: p.update(markdown=p["markdown"].replace("44", "45"))),
        ("adr", lambda p: p.update(adr=p["adr"].replace("ADR-0212", "ADR-0000"))),
    ]
    caught = 0
    for name, mutation in mutations:
        candidate = copy.deepcopy(package)
        mutation(candidate)
        if validate(candidate, check_files=False):
            caught += 1
        else:
            raise ValueError(f"mutation was not rejected: {name}")
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    package = load_outputs()
    found = validate(package)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(package)
    result = {
        "status": "PASS" if not found else "FAIL",
        "errors": found,
        "requests": len(package.get("manifest", {}).get("requests", [])),
        "panels": package.get("manifest", {}).get("summary", {}).get("panel_plans"),
        "reference_uses": package.get("manifest", {}).get("summary", {}).get("reference_uses"),
        "self_test": f"{caught}/{total}" if args.self_test else None,
    }
    print(json.dumps(result, sort_keys=True))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
