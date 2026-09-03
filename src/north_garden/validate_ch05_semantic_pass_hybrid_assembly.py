"""Validate the conservative CH05 semantic-pass hybrid assembly and triage."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-semantic-pass-hybrid-assembly-r1.json"
HYBRID_TRIAGE = ROOT / "docs/research/evidence/ch05-semantic-pass-hybrid-triage-r1.json"
TARGET_TRIAGE = ROOT / "docs/research/evidence/ch05-targeted-repair-trio-agent-triage-r1.json"
PACKET_INDEX = ROOT / "experiments/review-packets/ch05-semantic-pass-hybrid-r1/packet-index.json"
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
R6 = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json"
CLEAR = ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-assembly-r1.json"
PREMIUM = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json"
CLEAR_ORDERS = [2, 6, 10, 17, 19, 20, 29, 36, 44]
PREMIUM_ORDERS = [4, 22, 26, 30, 33, 41, 43, 46, 48, 49, 50]
TARGET_ORDERS = [1, 39]
EXPECTED_COUNTS = {"r6": 28, "clear_line": 9, "premium_cel": 11, "targeted": 2}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(document.get("record_type") == "ComicChapterProductionManifest", "record_type")
    check(document.get("record_id") == "ng-ch05-semantic-pass-hybrid-assembly-r1", "record_id")
    check(document.get("state") == "REVIEW_ONLY_SEMANTIC_PASS_HYBRID_OWNER_PENDING", "state")
    check(document.get("medium") == "comic" and document.get("chapter_complete") is True, "comic chapter")
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "planning boundary",
    )
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    source_docs = {
        "r6": json.loads(R6.read_text(encoding="utf-8")),
        "clear_line": json.loads(CLEAR.read_text(encoding="utf-8")),
        "premium_cel": json.loads(PREMIUM.read_text(encoding="utf-8")),
    }
    source_entries = {
        route: {row["order"]: row for row in source["entries"]} for route, source in source_docs.items()
    }
    rows = document.get("entries", [])
    check(
        len(rows) == 50
        and [row.get("order") for row in rows] == list(range(1, 51))
        and [row.get("panel_id") for row in rows] == [row["panel_id"] for row in plans],
        "exact ordered coverage",
    )
    routes = [row.get("selection", {}).get("route") for row in rows]
    check({route: routes.count(route) for route in EXPECTED_COUNTS} == EXPECTED_COUNTS, "derived route counts")
    check([row["order"] for row in rows if row.get("selection", {}).get("route") == "clear_line"] == CLEAR_ORDERS, "clear-line selection")
    check([row["order"] for row in rows if row.get("selection", {}).get("route") == "premium_cel"] == PREMIUM_ORDERS, "premium selection")
    check([row["order"] for row in rows if row.get("selection", {}).get("route") == "targeted"] == TARGET_ORDERS, "targeted selection")
    check(rows[31].get("selection", {}).get("route") == "r6", "P032 retains r6")
    check(all(row.get("layout") == source_entries["r6"][row["order"]]["layout"] for row in rows), "exact r6 layouts")
    check(document.get("canvas") == source_docs["r6"]["canvas"], "exact r6 canvas")
    check(document.get("comic_panel_plan_collection") == source_docs["r6"]["comic_panel_plan_collection"], "plan binding")

    for row in rows:
        order = row.get("order")
        route = row.get("selection", {}).get("route")
        selection = row.get("selection", {})
        check(isinstance(selection.get("rationale"), str) and len(selection["rationale"]) > 30, f"rationale P{order:03d}")
        check(selection.get("owner_review_state") == "PENDING" and selection.get("accepted") is False, f"selection boundary P{order:03d}")
        check(selection.get("source_triage", {}).get("status") in ({"PASS", "WARN"} if order == 32 else {"PASS"}), f"source triage P{order:03d}")
        check(row.get("animation_shot_plan") is None and row.get("e_conte") is None, f"entry planning boundary P{order:03d}")
        if route in source_entries:
            expected = source_entries[route][order]
            check(row.get("candidate_id") == expected["candidate_id"] and row.get("source") == expected["source"], f"source selection P{order:03d}")
        elif route == "targeted":
            check(row.get("candidate_id") == f"targeted-trio-r1-p{order:03d}", f"target candidate P{order:03d}")
        if verify_files:
            source = row.get("source", {})
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"source hash P{order:03d}")
            if path.is_file():
                with Image.open(path) as image:
                    check(image.size == (source.get("width"), source.get("height")), f"source dimensions P{order:03d}")

    expected_summary = {
        "panels": 50,
        "r6_retained": 28,
        "clear_line_selected": 9,
        "premium_cel_selected": 11,
        "targeted_selected": 2,
        "replacements": 22,
        "semantic_pass": 49,
        "semantic_warn": 1,
        "semantic_fail": 0,
        "route_transitions": 33,
        "owner_reviewed": 0,
        "accepted": 0,
    }
    check(document.get("summary") == expected_summary, "summary")
    check("33 adjacent route transitions" in document.get("style_transition_limitation", ""), "style-transition limitation")
    check(
        document.get("cross_panel_gate_projection", {}).get("impossible_far_bank_prints") == "WARN_P032_ORIENTATION"
        and sum(value == "PASS" for value in document.get("cross_panel_gate_projection", {}).values()) == 7,
        "cross-panel projection",
    )
    check(
        all(term in document.get("boundary", "") for term in ("Review-only", "no art acceptance", "commercial clearance", "exact production-base")),
        "rights/acceptance boundary",
    )
    policy = document.get("selection_policy", {})
    check(policy.get("explicit_replacements") == {"targeted": TARGET_ORDERS, "clear_line": CLEAR_ORDERS, "premium_cel": PREMIUM_ORDERS}, "selection policy")
    check("P032" in policy.get("warning_rule", "") and "unselected" in policy.get("warning_rule", ""), "P032 policy")

    triage = json.loads(HYBRID_TRIAGE.read_text(encoding="utf-8")) if HYBRID_TRIAGE.is_file() else {}
    triage_rows = triage.get("rows", [])
    check(triage.get("summary", {}).get("pass") == 49 and triage.get("summary", {}).get("warn") == 1 and triage.get("summary", {}).get("fail") == 0, "hybrid triage counts")
    check(len(triage_rows) == 50 and [row.get("status") for row in triage_rows].count("WARN") == 1 and triage_rows[31].get("status") == "WARN", "P032 sole warning")
    targeted = json.loads(TARGET_TRIAGE.read_text(encoding="utf-8")) if TARGET_TRIAGE.is_file() else {}
    check([row.get("status") for row in targeted.get("rows", [])] == ["PASS", "WARN", "PASS"], "targeted triage")
    if verify_files:
        for source in document.get("inputs", []):
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"input:{source.get('path')}")
        check(triage.get("inputs") == [{"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256(MANIFEST)}], "hybrid triage manifest binding")
        packet = json.loads(PACKET_INDEX.read_text(encoding="utf-8")) if PACKET_INDEX.is_file() else {}
        check(
            packet.get("record_type") == "CH05SemanticPassHybridReviewPacketIndex"
            and packet.get("planning_structure") == "ComicPanelPlan"
            and packet.get("animation_shot_plan") is None
            and packet.get("e_conte") is None,
            "packet identity/planning boundary",
        )
        check(
            packet.get("summary")
            == {
                "chapter_panels": 50,
                "semantic_pass": 49,
                "semantic_warn": 1,
                "semantic_fail": 0,
                "sole_warning_panel": "ng-ch05-sc01-p032",
                "artifact_categories": 9,
                "owner_reviewed": 0,
                "accepted": 0,
            },
            "packet summary",
        )
        check(
            set(packet.get("artifacts", {}))
            == {
                "clean_long_scroll",
                "clean_contact_sheet",
                "lettering_safe_zone_scroll",
                "lettering_safe_zone_contact_sheet",
                "clean_phone_scroll",
                "lettered_long_scroll",
                "lettered_phone_scroll",
                "continuity_sheet",
                "triage_sheet",
            },
            "packet artifact categories",
        )
        for group in (packet.get("artifacts", {}), packet.get("reports", {})):
            for name, item in group.items():
                path = ROOT / item.get("path", "")
                check(path.is_file() and sha256(path) == item.get("sha256") and path.stat().st_size == item.get("bytes"), f"packet artifact:{name}")
                check(subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode == 0, f"packet artifact ignored:{name}")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["entries"].pop(),
        lambda value: value["entries"][0].__setitem__("order", 2),
        lambda value: value["entries"][0]["selection"].__setitem__("route", "r6"),
        lambda value: value["entries"][31]["selection"].__setitem__("route", "targeted"),
        lambda value: value["entries"][1].__setitem__("source", value["entries"][0]["source"]),
        lambda value: value["entries"][1].__setitem__("layout", {}),
        lambda value: value["entries"][3]["selection"].__setitem__("rationale", "short"),
        lambda value: value["entries"][3]["selection"]["source_triage"].__setitem__("status", "FAIL"),
        lambda value: value["entries"][3]["selection"].__setitem__("accepted", True),
        lambda value: value["entries"][3].__setitem__("animation_shot_plan", {}),
        lambda value: value["summary"].__setitem__("r6_retained", 29),
        lambda value: value["summary"].__setitem__("semantic_fail", 1),
        lambda value: value.__setitem__("style_transition_limitation", "none"),
        lambda value: value["cross_panel_gate_projection"].__setitem__("impossible_far_bank_prints", "PASS"),
        lambda value: value["selection_policy"]["explicit_replacements"]["premium_cel"].pop(),
        lambda value: value["selection_policy"].__setitem__("warning_rule", "select P032"),
        lambda value: value.__setitem__("boundary", "accepted"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "summary": document.get("summary"), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
