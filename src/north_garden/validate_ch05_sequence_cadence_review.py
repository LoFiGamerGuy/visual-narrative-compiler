"""Fail closed on the CH05 three-block sequence-cadence review packet."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Callable
from itertools import pairwise
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
SIX_ROUTE = ROOT / "docs/research/evidence/ch05-six-route-comparison-r1.json"
ASSEMBLIES = {
    "reduced_palette_text_control": ROOT
    / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-assembly-r1.json",
    "r6": ROOT
    / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json",
    "premium_cel": ROOT
    / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json",
}
TRIAGES = {
    "reduced_palette_text_control": ROOT
    / "docs/research/evidence/ch05-complete-chapter-reduced-palette-text-control-agent-triage-r1.json",
    "r6": ROOT / "docs/research/evidence/ch05-complete-chapter-agent-triage-r6.json",
    "premium_cel": ROOT
    / "docs/research/evidence/ch05-complete-chapter-premium-cel-agent-triage-r1.json",
}
ASSEMBLY = (
    ROOT
    / "production/comic/run-manifests/ch05-sequence-cadence-review-assembly-r1.json"
)
TRIAGE = ROOT / "docs/research/evidence/ch05-sequence-cadence-review-triage-r1.json"
LETTERING = (
    ROOT / "production/comic/lettering/ch05-complete-chapter-lettering-proposal-r1.json"
)
PACKET_INDEX = (
    ROOT
    / "experiments/review-packets/ch05-sequence-cadence-review-r1/packet-index.json"
)

EXPECTED_BLOCKS = [
    {"panel_range": [1, 5], "route": "reduced_palette_text_control"},
    {"panel_range": [6, 39], "route": "r6"},
    {"panel_range": [40, 50], "route": "premium_cel"},
]
EXPECTED_WARNINGS = [
    "ng-ch05-sc01-p003",
    "ng-ch05-sc01-p032",
    "ng-ch05-sc01-p045",
]
EXPECTED_ARTIFACTS = {
    "clean_long_scroll",
    "clean_contact_sheet",
    "lettering_safe_zone_scroll",
    "lettering_safe_zone_contact_sheet",
    "clean_phone_scroll",
    "lettered_long_scroll",
    "lettered_phone_scroll",
    "continuity_sheet",
    "boundary_continuity_sheet",
    "triage_sheet",
}
EXPECTED_REPORTS = {
    "clean_build",
    "lettering_build",
    "continuity_build",
    "triage_build",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_record(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def git_result(*args: str) -> int:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True
    ).returncode


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_route(order: int) -> str:
    if 1 <= order <= 5:
        return "reduced_palette_text_control"
    if 6 <= order <= 39:
        return "r6"
    if 40 <= order <= 50:
        return "premium_cel"
    raise ValueError(order)


def source_status(route: str, row: dict[str, Any]) -> tuple[str, str]:
    if route == "reduced_palette_text_control":
        return row["semantic_status"], row["semantic_note"]
    return row["status"], row["note"]


def validate_packet_file(
    item: dict[str, Any], label: str, errors: list[str], verify_files: bool
) -> None:
    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    relative = item.get("path", "")
    path = ROOT / relative
    check(
        isinstance(relative, str) and relative.startswith("experiments/"),
        f"{label}:path",
    )
    check(
        isinstance(item.get("sha256"), str)
        and len(item["sha256"]) == 64
        and item["sha256"] != "0" * 64,
        f"{label}:sha256 shape",
    )
    check(isinstance(item.get("bytes"), int) and item["bytes"] > 0, f"{label}:bytes")
    if isinstance(relative, str) and relative.lower().endswith(".png"):
        check(
            all(
                isinstance(item.get(field), int) and item[field] > 0
                for field in ("width", "height")
            ),
            f"{label}:dimensions shape",
        )
    if not verify_files:
        return
    check(path.is_file(), f"{label}:exists")
    if path.is_file():
        check(sha256(path) == item.get("sha256"), f"{label}:hash")
        check(path.stat().st_size == item.get("bytes"), f"{label}:byte binding")
        if path.suffix.lower() == ".png":
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    check(image.format == "PNG", f"{label}:format")
                    check(
                        [image.width, image.height]
                        == [item.get("width"), item.get("height")],
                        f"{label}:dimensions",
                    )
            except (OSError, SyntaxError) as error:
                errors.append(f"{label}:invalid PNG:{error}")
    check(git_result("check-ignore", "-q", relative) == 0, f"{label}:ignored")
    check(
        git_result("ls-files", "--error-unmatch", relative) != 0,
        f"{label}:must remain untracked",
    )


def validate(
    assembly: dict[str, Any],
    triage: dict[str, Any],
    packet: dict[str, Any],
    verify_files: bool = True,
) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    plans = sorted(load(PLAN)["plans"], key=lambda row: row["display_order"])
    sources = {route: load(path) for route, path in ASSEMBLIES.items()}
    source_triages = {route: load(path) for route, path in TRIAGES.items()}
    entries_by_route = {
        route: {row["order"]: row for row in value["entries"]}
        for route, value in sources.items()
    }
    triage_by_route = {
        route: {row["display_order"]: row for row in value["rows"]}
        for route, value in source_triages.items()
    }

    check(
        assembly.get("record_type") == "ComicChapterProductionManifest",
        "assembly record_type",
    )
    check(
        assembly.get("record_id") == "ng-ch05-sequence-cadence-review-assembly-r1",
        "assembly record_id",
    )
    check(
        assembly.get("state") == "REVIEW_ONLY_SEQUENCE_CADENCE_OWNER_PENDING",
        "assembly state",
    )
    check(assembly.get("chapter_complete") is True, "assembly chapter_complete")
    check(
        assembly.get("planning_structure") == "ComicPanelPlan"
        and assembly.get("animation_shot_plan") is None
        and assembly.get("e_conte") is None,
        "assembly planning boundary",
    )
    check(
        assembly.get("comic_panel_plan_collection") == input_record(PLAN),
        "panel-plan binding",
    )
    check(assembly.get("canvas") == sources["r6"]["canvas"], "R6 canvas")
    expected_inputs = [
        input_record(SIX_ROUTE),
        *[input_record(path) for path in ASSEMBLIES.values()],
        *[input_record(path) for path in TRIAGES.values()],
    ]
    check(assembly.get("inputs") == expected_inputs, "assembly input bindings")
    policy = assembly.get("selection_policy", {})
    check(policy.get("unit") == "complete narrative sequence", "selection unit")
    check(policy.get("blocks") == EXPECTED_BLOCKS, "exact route blocks")
    check(policy.get("within_sequence_route_changes") == 0, "within-sequence changes")
    check(
        "no selected semantic FAIL" in policy.get("targeted_repair_rule", ""),
        "repair rule",
    )

    expected_summary = {
        "panels": 50,
        "reduced_palette_text_control": 5,
        "r6": 34,
        "premium_cel": 11,
        "semantic_pass": 47,
        "semantic_warn": 3,
        "semantic_fail": 0,
        "route_transitions": 2,
        "owner_reviewed": 0,
        "accepted": 0,
    }
    check(assembly.get("summary") == expected_summary, "assembly summary")
    entries = assembly.get("entries", [])
    check(len(entries) == 50, "assembly entry count")
    route_sequence: list[str] = []
    statuses: list[str] = []
    for index, plan in enumerate(plans):
        if index >= len(entries):
            break
        order = index + 1
        route = expected_route(order)
        entry = entries[index]
        expected_source = entries_by_route[route][order]
        expected_triage = triage_by_route[route][order]
        status, note = source_status(route, expected_triage)
        route_sequence.append(entry.get("selection", {}).get("route"))
        statuses.append(status)
        prefix = f"assembly:P{order:03d}"
        check(entry.get("order") == order, f"{prefix}:order")
        check(entry.get("panel_id") == plan["panel_id"], f"{prefix}:panel")
        check(
            entry.get("candidate_id") == expected_source["candidate_id"],
            f"{prefix}:candidate",
        )
        check(
            entry.get("sequence_id") == expected_source["sequence_id"],
            f"{prefix}:sequence",
        )
        check(entry.get("source") == expected_source["source"], f"{prefix}:source")
        check(
            entry.get("layout") == entries_by_route["r6"][order]["layout"],
            f"{prefix}:R6 layout",
        )
        selection = entry.get("selection", {})
        check(selection.get("route") == route, f"{prefix}:route")
        check(
            selection.get("sequence_level_selection") is True,
            f"{prefix}:sequence selection",
        )
        check(
            selection.get("source_triage")
            == {
                "path": TRIAGES[route].relative_to(ROOT).as_posix(),
                "sha256": sha256(TRIAGES[route]),
                "status": status,
                "note": note,
            },
            f"{prefix}:source triage",
        )
        check(selection.get("owner_review_state") == "PENDING", f"{prefix}:owner state")
        for field in (
            "accepted",
            "rights_cleared",
            "commercially_cleared",
            "exact_production_base",
        ):
            check(selection.get(field) is False, f"{prefix}:{field}")
        check(
            entry.get("animation_shot_plan") is None and entry.get("e_conte") is None,
            f"{prefix}:planning boundary",
        )
        if verify_files:
            source_path = ROOT / entry.get("source", {}).get("path", "")
            check(source_path.is_file(), f"{prefix}:source exists")
            if source_path.is_file():
                check(
                    sha256(source_path) == entry["source"].get("sha256"),
                    f"{prefix}:source hash",
                )
                with Image.open(source_path) as image:
                    check(
                        [image.width, image.height]
                        == [
                            entry["source"].get("width"),
                            entry["source"].get("height"),
                        ],
                        f"{prefix}:source dimensions",
                    )
    check(
        statuses.count("PASS") == 47 and statuses.count("WARN") == 3,
        "source semantic counts",
    )
    check(statuses.count("FAIL") == 0, "source semantic failures")
    check(
        sum(left != right for left, right in pairwise(route_sequence)) == 2,
        "route transitions",
    )
    check(
        assembly.get("owner_disposition")
        == {
            "accepted_sequence_assignments": None,
            "accepted_panel_ids": None,
            "commercial_rights_clearance": None,
            "exact_production_base": None,
        },
        "owner disposition",
    )
    check(
        "no art acceptance" in assembly.get("boundary", ""),
        "assembly acceptance boundary",
    )

    check(
        triage.get("record_type") == "CH05SequenceCadenceReviewTriage",
        "triage record_type",
    )
    check(
        triage.get("record_id") == "ng-ch05-sequence-cadence-review-triage-r1",
        "triage record_id",
    )
    check(
        triage.get("state") == "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW",
        "triage state",
    )
    check(
        triage.get("planning_structure") == "ComicPanelPlan"
        and triage.get("animation_shot_plan") is None
        and triage.get("e_conte") is None,
        "triage planning boundary",
    )
    check(triage.get("inputs") == [input_record(ASSEMBLY)], "triage input binding")
    check(
        triage.get("summary")
        == {
            "chapter_panels": 50,
            "pass": 47,
            "warn": 3,
            "fail": 0,
            "warning_panels": EXPECTED_WARNINGS,
            "route_transitions": 2,
            "human_reviewed": 0,
            "accepted": 0,
        },
        "triage summary",
    )
    rows = triage.get("rows", [])
    check(len(rows) == 50, "triage row count")
    for index, entry in enumerate(entries):
        if index >= len(rows):
            break
        order = index + 1
        route = expected_route(order)
        source_row = triage_by_route[route][order]
        status, note = source_status(route, source_row)
        row = rows[index]
        prefix = f"triage:P{order:03d}"
        expected_primary = (
            source_row.get("primary_issue_class") if status != "PASS" else None
        )
        check(row.get("display_order") == order, f"{prefix}:order")
        check(row.get("panel_id") == plans[index]["panel_id"], f"{prefix}:panel")
        check(
            row.get("plan_revision_id") == plans[index]["plan_revision_id"],
            f"{prefix}:plan revision",
        )
        check(
            row.get("candidate_id") == entry.get("candidate_id"), f"{prefix}:candidate"
        )
        check(
            row.get("candidate_sha256") == entry.get("source", {}).get("sha256"),
            f"{prefix}:candidate hash",
        )
        check(row.get("route") == route, f"{prefix}:route")
        check(row.get("status") == status, f"{prefix}:status")
        check(
            row.get("primary_issue_class") == expected_primary,
            f"{prefix}:primary issue",
        )
        check(row.get("note") == note, f"{prefix}:note")
        check(row.get("checks") == source_row.get("checks", {}), f"{prefix}:checks")
        check(
            row.get("human_review_state") == "PENDING"
            and row.get("human_review_minutes") is None,
            f"{prefix}:review state",
        )
        for field in (
            "accepted",
            "rights_cleared",
            "commercially_cleared",
            "exact_production_base",
        ):
            check(row.get(field) is False, f"{prefix}:{field}")
    observed_warnings = [
        row.get("panel_id") for row in rows if row.get("status") == "WARN"
    ]
    check(observed_warnings == EXPECTED_WARNINGS, "exact warning panels")
    check(triage.get("boundary") == assembly.get("boundary"), "triage boundary")

    check(
        packet.get("record_type") == "CH05SequenceCadenceReviewPacketIndex",
        "packet record_type",
    )
    check(
        packet.get("record_id") == "ng-ch05-sequence-cadence-review-packet-r1",
        "packet record_id",
    )
    check(
        packet.get("state") == "REVIEW_PACKET_UNACCEPTED_OWNER_PENDING", "packet state"
    )
    check(
        packet.get("planning_structure") == "ComicPanelPlan"
        and packet.get("animation_shot_plan") is None
        and packet.get("e_conte") is None,
        "packet planning boundary",
    )
    check(
        packet.get("inputs")
        == [input_record(ASSEMBLY), input_record(TRIAGE), input_record(LETTERING)],
        "packet input bindings",
    )
    check(
        packet.get("summary")
        == {
            "chapter_panels": 50,
            "semantic_pass": 47,
            "semantic_warn": 3,
            "semantic_fail": 0,
            "warning_panels": EXPECTED_WARNINGS,
            "route_blocks": 3,
            "adjacent_route_transitions": 2,
            "artifact_categories": 10,
            "owner_reviewed": 0,
            "accepted": 0,
        },
        "packet summary",
    )
    artifacts = packet.get("artifacts", {})
    reports = packet.get("reports", {})
    check(set(artifacts) == EXPECTED_ARTIFACTS, "packet artifact set")
    check(set(reports) == EXPECTED_REPORTS, "packet report set")
    for label, item in artifacts.items():
        validate_packet_file(item, f"packet artifact:{label}", errors, verify_files)
    for label, item in reports.items():
        validate_packet_file(item, f"packet report:{label}", errors, verify_files)
    check(
        packet.get("review_order")
        == [
            "lettered_phone_scroll",
            "clean_phone_scroll",
            "continuity_sheet",
            "boundary_continuity_sheet",
            "triage_sheet",
            "lettering_safe_zone_contact_sheet",
            "clean_long_scroll",
        ],
        "packet review order",
    )
    check("no acceptance" in packet.get("boundary", ""), "packet acceptance boundary")
    if verify_files:
        relative_index = PACKET_INDEX.relative_to(ROOT).as_posix()
        check(
            git_result("check-ignore", "-q", relative_index) == 0,
            "packet index ignored",
        )
        check(
            git_result("ls-files", "--error-unmatch", relative_index) != 0,
            "packet index must remain untracked",
        )
    return errors


def self_test(
    assembly: dict[str, Any], triage: dict[str, Any], packet: dict[str, Any]
) -> tuple[int, int, list[int]]:
    Mutation = Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], None]
    mutations: list[Mutation] = [
        lambda a, _t, _p: a.__setitem__("state", "ACCEPTED"),
        lambda a, _t, _p: a.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda a, _t, _p: a.__setitem__("animation_shot_plan", {}),
        lambda a, _t, _p: a["canvas"].__setitem__("width", 999),
        lambda a, _t, _p: a["selection_policy"]["blocks"][0].__setitem__(
            "panel_range", [1, 6]
        ),
        lambda a, _t, _p: a["summary"].__setitem__("semantic_pass", 48),
        lambda a, _t, _p: a["entries"][5]["selection"].__setitem__(
            "route", "premium_cel"
        ),
        lambda a, _t, _p: a["entries"][0]["source"].__setitem__("sha256", "0" * 64),
        lambda a, _t, _p: a["entries"][0]["layout"].__setitem__("target_width", 1),
        lambda a, _t, _p: a["entries"][0]["selection"].__setitem__("accepted", True),
        lambda a, _t, _p: a["owner_disposition"].__setitem__(
            "accepted_panel_ids", ["P001"]
        ),
        lambda _a, t, _p: t.__setitem__("state", "GATING"),
        lambda _a, t, _p: t["summary"].__setitem__("warn", 2),
        lambda _a, t, _p: t["summary"].__setitem__("warning_panels", []),
        lambda _a, t, _p: t["rows"][2].__setitem__("status", "PASS"),
        lambda _a, t, _p: t["rows"][0].__setitem__("candidate_sha256", "0" * 64),
        lambda _a, t, _p: t["rows"][0].__setitem__("rights_cleared", True),
        lambda _a, _t, p: p.__setitem__("state", "ACCEPTED"),
        lambda _a, _t, p: p["summary"].__setitem__("adjacent_route_transitions", 1),
        lambda _a, _t, p: p["artifacts"]["lettered_phone_scroll"].__setitem__(
            "sha256", "0" * 64
        ),
        lambda _a, _t, p: p["artifacts"]["continuity_sheet"].__setitem__("width", 0),
        lambda _a, _t, p: p["reports"]["clean_build"].__setitem__("path", "wrong.json"),
        lambda _a, _t, p: p.__setitem__("boundary", "accepted"),
    ]
    caught = 0
    missed: list[int] = []
    for index, mutation in enumerate(mutations, 1):
        candidate_a = copy.deepcopy(assembly)
        candidate_t = copy.deepcopy(triage)
        candidate_p = copy.deepcopy(packet)
        mutation(candidate_a, candidate_t, candidate_p)
        if validate(candidate_a, candidate_t, candidate_p, verify_files=False):
            caught += 1
        else:
            missed.append(index)
    return caught, len(mutations), missed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    assembly = load(ASSEMBLY)
    triage = load(TRIAGE)
    packet = load(PACKET_INDEX)
    errors = validate(assembly, triage, packet)
    caught = total = 0
    missed: list[int] = []
    if args.self_test:
        caught, total, missed = self_test(assembly, triage, packet)
        if caught != total:
            errors.append(f"self-test:{caught}/{total}:missed={missed}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "panels_checked": len(assembly.get("entries", [])),
                "packet_files_checked": len(packet.get("artifacts", {}))
                + len(packet.get("reports", {})),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
