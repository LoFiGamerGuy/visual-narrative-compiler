"""Compile the conservative review-only CH05 semantic-pass hybrid assembly."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
R6 = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json"
CLEAR = ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-assembly-r1.json"
PREMIUM = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json"
R6_TRIAGE = ROOT / "docs/research/evidence/ch05-complete-chapter-agent-triage-r6.json"
CLEAR_TRIAGE = ROOT / "docs/research/evidence/ch05-complete-chapter-clear-line-watercolor-agent-triage-r1.json"
PREMIUM_TRIAGE = ROOT / "docs/research/evidence/ch05-complete-chapter-premium-cel-agent-triage-r1.json"
TARGET_PROMPTS = ROOT / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-r1.json"
TARGET_TRIAGE = ROOT / "docs/research/evidence/ch05-targeted-repair-trio-agent-triage-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-semantic-pass-hybrid-assembly-r1.json"
HYBRID_TRIAGE = ROOT / "docs/research/evidence/ch05-semantic-pass-hybrid-triage-r1.json"

CLEAR_ORDERS = [2, 6, 10, 17, 19, 20, 29, 36, 44]
PREMIUM_ORDERS = [4, 22, 26, 30, 33, 41, 43, 46, 48, 49, 50]
TARGET_ORDERS = [1, 39]
TARGET_FILES = {
    1: "experiments/review-packets/ch05-premium-cel-targeted-repair-trio-r1/source-panels/P001-premium-cel-clean-graphic-hybrid-r1.png",
    32: "experiments/review-packets/ch05-premium-cel-targeted-repair-trio-r1/source-panels/P032-premium-cel-clean-graphic-hybrid-r1.png",
    39: "experiments/review-packets/ch05-premium-cel-targeted-repair-trio-r1/source-panels/P039-premium-cel-clean-graphic-hybrid-r1.png",
}
TARGET_STATUS = {1: "PASS", 32: "WARN", 39: "PASS"}
TARGET_NOTES = {
    1: "Cold farmhouse is physically behind and upslope; both adults show a clear backs-to-camera downhill-away vector with Sigrid leading.",
    32: "Prints are confined to the far dry bank, but their asymmetric toe/heel direction back toward Soren remains ambiguous; do not select.",
    39: "One uninterrupted map view simultaneously shows square farmhouse, circular mill, distinct torn-edge upstream diamond, and Soren's finger at the third mark.",
}
RATIONALES = {
    1: "Targeted repair closes the departure-vector failure while retaining the cold-house negative state.",
    2: "Clear-line selection strengthens the opening map-direction read with a measured PASS.",
    4: "Premium-cel selection strengthens the restrained wary eyeline exchange with a measured PASS.",
    6: "Clear-line selection preserves Sigrid-leading trail-marker action with a measured PASS.",
    10: "Clear-line selection gives the listening beat a readable mature expression and measured PASS.",
    17: "Clear-line selection provides the strongest measured mill-reveal silhouette and set read.",
    19: "Clear-line selection makes Sigrid's bridge-warning stop palm explicit with a measured PASS.",
    20: "Clear-line selection clearly stages Sigrid leading across wet stepping stones with a measured PASS.",
    22: "Premium-cel selection clearly shows Soren intercepting Sigrid's reach before contact with the cloth.",
    26: "Premium-cel selection isolates Sigrid's heat-test hand above the ember with a measured PASS.",
    29: "Clear-line selection visibly separates Sigrid's entry role from Soren's independent exterior watch.",
    30: "Premium-cel selection gives the mill interior a strong readable geography and measured PASS.",
    33: "Premium-cel selection clearly stages Sigrid foreground, Soren background, and the bell/drip freeze.",
    36: "Clear-line selection preserves exactly one plank and visibly connects both adults through the brace to the tin endpoint.",
    39: "Targeted repair simultaneously exposes all three map marks and places Soren's finger at the torn-edge third mark.",
    41: "Premium-cel selection shows the drum fully cold and out with no glow or smoke plume.",
    43: "Premium-cel selection leaves the open tin on the stone while Sigrid visibly retains the creek map.",
    44: "Clear-line selection gives the knife-to-twine contact a safe, readable causal endpoint.",
    46: "Premium-cel selection clearly places the retained map inside Sigrid's plaid wrap.",
    48: "Premium-cel selection strongly establishes the first new farmhouse smoke of the chapter.",
    49: "Premium-cel selection preserves Soren's alarm, map possession, and smoking-house context.",
    50: "Premium-cel selection provides the strongest grounded urgent return with Sigrid leading and Soren following.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def target_triage() -> dict[str, Any]:
    rows = []
    for order in (1, 32, 39):
        path = ROOT / TARGET_FILES[order]
        if not path.is_file():
            raise ValueError(f"targeted output missing: {path}")
        with Image.open(path) as image:
            width, height = image.size
            image.verify()
        rows.append(
            {
                "display_order": order,
                "panel_id": f"ng-ch05-sc01-p{order:03d}",
                "candidate_id": f"targeted-trio-r1-p{order:03d}",
                "source": {
                    "path": TARGET_FILES[order],
                    "sha256": sha256(path),
                    "width": width,
                    "height": height,
                },
                "status": TARGET_STATUS[order],
                "note": TARGET_NOTES[order],
                "review_basis": "manual_visual_semantic_gate_triage",
                "human_review_state": "PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            }
        )
    return {
        "record_type": "CH05TargetedRepairTrioAgentTriage",
        "schema_version": "1.0",
        "record_id": "ng-ch05-targeted-repair-trio-agent-triage-r1",
        "state": "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": TARGET_PROMPTS.relative_to(ROOT).as_posix(), "sha256": sha256(TARGET_PROMPTS)}],
        "summary": {"candidates": 3, "pass": 2, "warn": 1, "fail": 0, "selected_for_hybrid": 2},
        "rows": rows,
        "boundary": "Agent visual triage only; no owner acceptance, commercial clearance, or exact production-base status.",
    }


def main() -> int:
    targeted = target_triage()
    write_json(TARGET_TRIAGE, targeted)
    sources = {
        "r6": json.loads(R6.read_text(encoding="utf-8")),
        "clear_line": json.loads(CLEAR.read_text(encoding="utf-8")),
        "premium_cel": json.loads(PREMIUM.read_text(encoding="utf-8")),
    }
    triage_docs = {
        "r6": json.loads(R6_TRIAGE.read_text(encoding="utf-8")),
        "clear_line": json.loads(CLEAR_TRIAGE.read_text(encoding="utf-8")),
        "premium_cel": json.loads(PREMIUM_TRIAGE.read_text(encoding="utf-8")),
        "targeted": targeted,
    }
    entry_by_route = {
        route: {row["order"]: row for row in document["entries"]} for route, document in sources.items()
    }
    triage_by_route = {
        route: {row["display_order"]: row for row in document["rows"]} for route, document in triage_docs.items()
    }
    entries = []
    hybrid_rows = []
    route_sequence = []
    for order in range(1, 51):
        if order in TARGET_ORDERS:
            route = "targeted"
            source_row = triage_by_route[route][order]
            source = dict(source_row["source"])
            candidate_id = source_row["candidate_id"]
            sequence_id = "targeted-repair-trio-r1"
            source_triage = {
                "path": TARGET_TRIAGE.relative_to(ROOT).as_posix(),
                "sha256": None,
                "status": source_row["status"],
                "note": source_row["note"],
            }
        elif order in CLEAR_ORDERS:
            route = "clear_line"
            chosen = entry_by_route[route][order]
            source = dict(chosen["source"])
            candidate_id = chosen["candidate_id"]
            sequence_id = chosen.get("sequence_id")
            triage_row = triage_by_route[route][order]
            if triage_row["status"] != "PASS":
                raise ValueError(f"non-PASS clear-line replacement P{order:03d}")
            source_triage = {
                "path": CLEAR_TRIAGE.relative_to(ROOT).as_posix(),
                "sha256": sha256(CLEAR_TRIAGE),
                "status": triage_row["status"],
                "note": triage_row["note"],
            }
        elif order in PREMIUM_ORDERS:
            route = "premium_cel"
            chosen = entry_by_route[route][order]
            source = dict(chosen["source"])
            candidate_id = chosen["candidate_id"]
            sequence_id = chosen.get("sequence_id")
            triage_row = triage_by_route[route][order]
            if triage_row["status"] != "PASS":
                raise ValueError(f"non-PASS premium-cel replacement P{order:03d}")
            source_triage = {
                "path": PREMIUM_TRIAGE.relative_to(ROOT).as_posix(),
                "sha256": sha256(PREMIUM_TRIAGE),
                "status": triage_row["status"],
                "note": triage_row["note"],
            }
        else:
            route = "r6"
            chosen = entry_by_route[route][order]
            source = dict(chosen["source"])
            candidate_id = chosen["candidate_id"]
            sequence_id = chosen.get("sequence_id")
            triage_row = triage_by_route[route][order]
            source_triage = {
                "path": R6_TRIAGE.relative_to(ROOT).as_posix(),
                "sha256": sha256(R6_TRIAGE),
                "status": triage_row["status"],
                "note": triage_row["note"],
            }
        if source_triage["status"] not in ({"PASS", "WARN"} if order == 32 else {"PASS"}):
            raise ValueError(f"selection is not semantic-pass eligible: P{order:03d}")
        base = entry_by_route["r6"][order]
        entries.append(
            {
                "order": order,
                "panel_id": base["panel_id"],
                "candidate_id": candidate_id,
                "sequence_id": sequence_id,
                "source": source,
                "layout": dict(base["layout"]),
                "selection": {
                    "route": route,
                    "replaces_r6": route != "r6",
                    "source_triage": source_triage,
                    "rationale": RATIONALES.get(order, "Retain the r6 semantic-pass candidate; no measured replacement offers a required gate improvement."),
                    "owner_review_state": "PENDING",
                    "accepted": False,
                },
                "animation_shot_plan": None,
                "e_conte": None,
            }
        )
        hybrid_rows.append(
            {
                "display_order": order,
                "panel_id": base["panel_id"],
                "candidate_id": candidate_id,
                "candidate_sha256": source["sha256"],
                "selected_route": route,
                "status": "WARN" if order == 32 else "PASS",
                "primary_issue_class": "far_bank_footprint_orientation" if order == 32 else None,
                "note": source_triage["note"] if order == 32 else "Selected source is a measured semantic PASS in its source triage.",
                "checks": {"hair_and_wardrobe": "PASS", "cross_panel_canon": "WARN" if order == 32 else "PASS"},
                "human_review_state": "PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            }
        )
        route_sequence.append(route)

    write_json(TARGET_TRIAGE, targeted)
    target_hash = sha256(TARGET_TRIAGE)
    for entry in entries:
        if entry["selection"]["route"] == "targeted":
            entry["selection"]["source_triage"]["sha256"] = target_hash
    counts = {route: route_sequence.count(route) for route in ("r6", "clear_line", "premium_cel", "targeted")}
    transitions = sum(left != right for left, right in zip(route_sequence, route_sequence[1:]))
    manifest = {
        "record_type": "ComicChapterProductionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-semantic-pass-hybrid-assembly-r1",
        "state": "REVIEW_ONLY_SEMANTIC_PASS_HYBRID_OWNER_PENDING",
        "medium": "comic",
        "chapter_complete": True,
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "comic_panel_plan_collection": dict(sources["r6"]["comic_panel_plan_collection"]),
        "canvas": dict(sources["r6"]["canvas"]),
        "inputs": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
            for path in (R6, CLEAR, PREMIUM, R6_TRIAGE, CLEAR_TRIAGE, PREMIUM_TRIAGE, TARGET_TRIAGE)
        ],
        "selection_policy": {
            "base": "Start from the exact r6 ordered entries and retain its layout for all 50 plans.",
            "replacement_rule": "Replace only an explicitly listed candidate with measured PASS source triage and a panel-specific semantic rationale.",
            "warning_rule": "Retain r6 P032 as the sole WARN; targeted P032 remains diagnostic-only and unselected.",
            "explicit_replacements": {
                "targeted": TARGET_ORDERS,
                "clear_line": CLEAR_ORDERS,
                "premium_cel": PREMIUM_ORDERS,
            },
        },
        "summary": {
            "panels": 50,
            "r6_retained": counts["r6"],
            "clear_line_selected": counts["clear_line"],
            "premium_cel_selected": counts["premium_cel"],
            "targeted_selected": counts["targeted"],
            "replacements": 50 - counts["r6"],
            "semantic_pass": 49,
            "semantic_warn": 1,
            "semantic_fail": 0,
            "route_transitions": transitions,
            "owner_reviewed": 0,
            "accepted": 0,
        },
        "entries": entries,
        "style_transition_limitation": (
            f"The hybrid contains {transitions} adjacent route transitions across painterly r6, clear-line watercolor, premium-cel, and targeted hybrid sources. "
            "Semantic PASS selection does not prove chapter-wide palette, line-weight, lighting, character-scale, or texture continuity; transitions require owner review at full scroll and phone width."
        ),
        "cross_panel_gate_projection": {
            "cold_farmhouse_until_reversal": "PASS",
            "departure_vector": "PASS",
            "independent_entry_roles": "PASS",
            "impossible_far_bank_prints": "WARN_P032_ORIENTATION",
            "continuous_leverage_force_path": "PASS",
            "third_upstream_mark": "PASS",
            "drum_fully_out": "PASS",
            "map_possession": "PASS",
        },
        "boundary": "Review-only deterministic assembly; no art acceptance, rights conclusion, canon replacement, commercial clearance, or exact production-base decision.",
    }
    write_json(OUTPUT, manifest)
    hybrid_triage = {
        "record_type": "CH05CompleteChapterAgentTriage",
        "schema_version": "1.0",
        "record_id": "ng-ch05-semantic-pass-hybrid-triage-r1",
        "display_title": "CH05 SEMANTIC-PASS HYBRID R1 - AGENT TRIAGE",
        "state": "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT)}],
        "summary": {"chapter_panels": 50, "pass": 49, "warn": 1, "fail": 0, "hair_and_wardrobe_pass": 50, "human_reviewed": 0, "accepted": 0},
        "rows": hybrid_rows,
        "style_transition_limitation": manifest["style_transition_limitation"],
        "boundary": manifest["boundary"],
    }
    write_json(HYBRID_TRIAGE, hybrid_triage)
    print(json.dumps({**manifest["summary"], "manifest": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "triage_sha256": sha256(HYBRID_TRIAGE)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
