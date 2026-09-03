"""Compile the measured three-block CH05 sequence-cadence review assembly."""
from __future__ import annotations

import hashlib
import json
from itertools import pairwise
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
SIX_ROUTE = ROOT / "docs/research/evidence/ch05-six-route-comparison-r1.json"
ASSEMBLIES = {
    "reduced_palette_text_control": ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-assembly-r1.json",
    "r6": ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json",
    "premium_cel": ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json",
}
TRIAGES = {
    "reduced_palette_text_control": ROOT / "docs/research/evidence/ch05-complete-chapter-reduced-palette-text-control-agent-triage-r1.json",
    "r6": ROOT / "docs/research/evidence/ch05-complete-chapter-agent-triage-r6.json",
    "premium_cel": ROOT / "docs/research/evidence/ch05-complete-chapter-premium-cel-agent-triage-r1.json",
}
OUTPUT = ROOT / "production/comic/run-manifests/ch05-sequence-cadence-review-assembly-r1.json"
OUTPUT_TRIAGE = ROOT / "docs/research/evidence/ch05-sequence-cadence-review-triage-r1.json"
ROUTE_BY_ORDER = {
    **{order: "reduced_palette_text_control" for order in range(1, 6)},
    **{order: "r6" for order in range(6, 40)},
    **{order: "premium_cel" for order in range(40, 51)},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def input_record(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def semantic_status(route: str, row: dict[str, Any]) -> tuple[str, str]:
    if route == "reduced_palette_text_control":
        return row["semantic_status"], row["semantic_note"]
    return row["status"], row["note"]


def main() -> int:
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    six_route = json.loads(SIX_ROUTE.read_text(encoding="utf-8"))
    sources = {route: json.loads(path.read_text(encoding="utf-8")) for route, path in ASSEMBLIES.items()}
    triages = {route: json.loads(path.read_text(encoding="utf-8")) for route, path in TRIAGES.items()}
    entries_by_route = {route: {row["order"]: row for row in value["entries"]} for route, value in sources.items()}
    triage_by_route = {route: {row["display_order"]: row for row in value["rows"]} for route, value in triages.items()}

    recommended = six_route["sequence_cadence_recommendation"]
    expected_blocks = [
        ("s01-opening-departure", [1, 5], "reduced_palette_text_control"),
        *[(row["sequence_id"], row["panel_range"], "r6") for row in recommended["sequences"][1:8]],
        *[(row["sequence_id"], row["panel_range"], "premium_cel") for row in recommended["sequences"][8:]],
    ]
    observed_blocks = [(row["sequence_id"], row["panel_range"], row["selected_route"]) for row in recommended["sequences"]]
    if observed_blocks != expected_blocks:
        raise ValueError("six-route sequence recommendation no longer matches the pinned three-block cadence")

    entries: list[dict[str, Any]] = []
    triage_rows: list[dict[str, Any]] = []
    route_sequence: list[str] = []
    for plan in plans:
        order = plan["display_order"]
        route = ROUTE_BY_ORDER[order]
        selected = entries_by_route[route][order]
        source_review = triage_by_route[route][order]
        status, note = semantic_status(route, source_review)
        if status not in {"PASS", "WARN"}:
            raise ValueError(f"selected cadence includes semantic FAIL at P{order:03d}")
        route_sequence.append(route)
        source_triage = {
            "path": TRIAGES[route].relative_to(ROOT).as_posix(),
            "sha256": sha256(TRIAGES[route]),
            "status": status,
            "note": note,
        }
        entries.append(
            {
                "order": order,
                "panel_id": plan["panel_id"],
                "candidate_id": selected["candidate_id"],
                "sequence_id": selected["sequence_id"],
                "source": dict(selected["source"]),
                "layout": dict(entries_by_route["r6"][order]["layout"]),
                "selection": {
                    "route": route,
                    "sequence_level_selection": True,
                    "source_triage": source_triage,
                    "rationale": "Use the measured single-route narrative block; preserve within-sequence visual continuity and the six-route semantic/identity objective.",
                    "owner_review_state": "PENDING",
                    "accepted": False,
                    "rights_cleared": False,
                    "commercially_cleared": False,
                    "exact_production_base": False,
                },
                "animation_shot_plan": None,
                "e_conte": None,
            }
        )
        checks = dict(source_review.get("checks", {}))
        triage_rows.append(
            {
                "display_order": order,
                "panel_id": plan["panel_id"],
                "plan_revision_id": plan["plan_revision_id"],
                "candidate_id": selected["candidate_id"],
                "candidate_sha256": selected["source"]["sha256"],
                "route": route,
                "status": status,
                "primary_issue_class": source_review.get("primary_issue_class") if status != "PASS" else None,
                "note": note,
                "checks": checks,
                "human_review_state": "PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "rights_cleared": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            }
        )

    statuses = [row["status"] for row in triage_rows]
    transitions = sum(left != right for left, right in pairwise(route_sequence))
    summary = {
        "panels": 50,
        "reduced_palette_text_control": route_sequence.count("reduced_palette_text_control"),
        "r6": route_sequence.count("r6"),
        "premium_cel": route_sequence.count("premium_cel"),
        "semantic_pass": statuses.count("PASS"),
        "semantic_warn": statuses.count("WARN"),
        "semantic_fail": statuses.count("FAIL"),
        "route_transitions": transitions,
        "owner_reviewed": 0,
        "accepted": 0,
    }
    if summary != {
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
    }:
        raise ValueError(f"unexpected selected-cadence summary: {summary}")

    inputs = [input_record(SIX_ROUTE), *[input_record(path) for path in ASSEMBLIES.values()], *[input_record(path) for path in TRIAGES.values()]]
    assembly = {
        "record_type": "ComicChapterProductionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-sequence-cadence-review-assembly-r1",
        "state": "REVIEW_ONLY_SEQUENCE_CADENCE_OWNER_PENDING",
        "medium": "comic",
        "chapter_complete": True,
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "comic_panel_plan_collection": sources["r6"]["comic_panel_plan_collection"],
        "canvas": sources["r6"]["canvas"],
        "inputs": inputs,
        "selection_policy": {
            "unit": "complete narrative sequence",
            "blocks": [
                {"panel_range": [1, 5], "route": "reduced_palette_text_control"},
                {"panel_range": [6, 39], "route": "r6"},
                {"panel_range": [40, 50], "route": "premium_cel"},
            ],
            "within_sequence_route_changes": 0,
            "targeted_repair_rule": "Repair only an explicit semantic FAIL in the same style; this review assembly has no selected semantic FAIL.",
        },
        "summary": summary,
        "entries": entries,
        "owner_disposition": {
            "accepted_sequence_assignments": None,
            "accepted_panel_ids": None,
            "commercial_rights_clearance": None,
            "exact_production_base": None,
        },
        "limitations": [
            "The cadence is a non-gating engineering recommendation assembled for full-chapter review.",
            "Three source semantic warnings remain visible at P003, P032, and P045.",
            "Cross-route palette, lighting, line-weight, and environment continuity require owner review at the two block boundaries.",
            "Provisional lettering does not establish canon dialogue.",
        ],
        "boundary": "Review-only assembly; no art acceptance, rights or commercial clearance, canon replacement, or exact production-base selection.",
    }
    write_json(OUTPUT, assembly)

    triage = {
        "record_type": "CH05SequenceCadenceReviewTriage",
        "schema_version": "1.0",
        "record_id": "ng-ch05-sequence-cadence-review-triage-r1",
        "state": "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [input_record(OUTPUT)],
        "summary": {
            "chapter_panels": 50,
            "pass": 47,
            "warn": 3,
            "fail": 0,
            "warning_panels": ["ng-ch05-sc01-p003", "ng-ch05-sc01-p032", "ng-ch05-sc01-p045"],
            "route_transitions": 2,
            "human_reviewed": 0,
            "accepted": 0,
        },
        "rows": triage_rows,
        "limitations": assembly["limitations"],
        "boundary": assembly["boundary"],
    }
    write_json(OUTPUT_TRIAGE, triage)
    print(json.dumps({"assembly": input_record(OUTPUT), "triage": input_record(OUTPUT_TRIAGE), "summary": summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
