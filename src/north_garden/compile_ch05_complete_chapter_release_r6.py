"""Compile the hash-bound CH05 complete-chapter r6 review release."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/research/evidence/ch05-complete-chapter-release-r6.json"
PRODUCTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r6.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json"
TRIAGE = ROOT / "docs/research/evidence/ch05-complete-chapter-agent-triage-r6.json"
TRIAGE_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/triage-sheet-report.json"
BUILD_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/build-report.json"
LETTERING_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/lettered/lettering-build-report.json"
CONTINUITY_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/continuity-sheet-report.json"
STYLE = ROOT / "production/comic/style-direction/ch05-mill-signal-r14.json"
HANDOFF = ROOT / "docs/research/ch05-complete-chapter-review-handoff-r6.md"
ADR_0173 = ROOT / "docs/adr/ADR-0173-p043-open-tin-not-all-contents-and-map-remains-for-p046.md"
ADR_0174 = ROOT / "docs/adr/ADR-0174-freeze-ch05-r6-and-retain-p032-warn-after-diminishing-returns.md"
ADR_0175 = ROOT / "docs/adr/ADR-0175-freeze-ch05-r6-release-and-do-not-invent-missing-ch01-ch04-chapter-plans.md"
REPAIR_MANIFESTS = [
    ROOT / f"production/comic/run-manifests/ch05-complete-chapter-targeted-repairs-r{i}.json"
    for i in range(1, 6)
]

ARTIFACTS = [
    ("lettered_phone_scroll", ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/lettered/ch05-complete-chapter-lettered-phone-390px-r1.png"),
    ("lettered_full_scroll", ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/lettered/ch05-complete-chapter-lettered-r1.png"),
    ("contact_sheet", ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/ch05-complete-chapter-contact-sheet.png"),
    ("triage_sheet", ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/ch05-complete-chapter-triage-sheet.png"),
    ("continuity_sheet", ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/ch05-complete-chapter-continuity-sheet.png"),
    ("lettering_safe_zone_overlay", ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/ch05-complete-chapter-long-scroll-lettering-overlay.png"),
    ("clean_full_scroll", ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/ch05-complete-chapter-long-scroll.png"),
    ("clean_phone_scroll", ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/ch05-complete-chapter-phone-390px.png"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def binding(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def artifact(kind: str, path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
    return {
        "kind": kind,
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "width_px": width,
        "height_px": height,
        "bytes": path.stat().st_size,
        "repository_state": "IGNORED_LOCAL_REVIEW_ARTIFACT",
    }


def main() -> int:
    production = load(PRODUCTION)
    assembly = load(ASSEMBLY)
    triage = load(TRIAGE)
    style = load(STYLE)
    if len(production["panels"]) != 50 or len(assembly["entries"]) != 50:
        raise ValueError("release requires exactly 50 selected panel rows")
    if triage["summary"] | {} != triage["summary"]:
        raise ValueError("triage summary must be an object")
    if (triage["summary"]["pass"], triage["summary"]["warn"], triage["summary"]["fail"]) != (49, 1, 0):
        raise ValueError("release requires the frozen 49/1/0 r6 triage")

    executions: dict[str, dict[str, Any]] = {}
    for panel in production["panels"]:
        execution_id = panel.get("source_service_execution_id")
        if not execution_id:
            raise ValueError(f"missing service execution id: {panel['panel_id']}")
        executions.setdefault(
            execution_id,
            {"elapsed_seconds": panel["candidate"]["elapsed_seconds"], "reference_uses": len(panel["input_references"])},
        )
    generated_candidates = 50
    for path in REPAIR_MANIFESTS:
        repair = load(path)
        generated_candidates += len(repair.get("repairs", [])) + len(repair.get("diagnostic_candidates", []))

    source_files = [
        PRODUCTION, ASSEMBLY, TRIAGE, TRIAGE_REPORT, BUILD_REPORT, LETTERING_REPORT,
        CONTINUITY_REPORT, STYLE, HANDOFF, ADR_0173, ADR_0174, ADR_0175, *REPAIR_MANIFESTS,
    ]
    document = {
        "record_type": "CH05CompleteChapterReviewRelease",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-review-release-r6",
        "state": "FROZEN_REVIEW_CANDIDATE_UNACCEPTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "source_bindings": [binding(path) for path in source_files],
        "measured_summary": {
            "comic_panel_plans": 50,
            "selected_chapter_panels": len(production["panels"]),
            "built_in_raster_outputs": len(executions),
            "panel_level_candidates": generated_candidates,
            "authorized_reference_uses": sum(row["reference_uses"] for row in executions.values()),
            "unique_authorized_reference_hashes": len(production["provider_policy"]["uploaded_reference_hashes"]),
            "unique_execution_elapsed_sum_seconds": round(sum(row["elapsed_seconds"] for row in executions.values()), 3),
            "approximate_unique_client_generation_wall_seconds": 1200.7,
            "agent_triage": {"pass": 49, "warn": 1, "fail": 0, "gating": False},
            "remaining_warning_panel_ids": ["ng-ch05-sc01-p032"],
            "lettered_panels": load(LETTERING_REPORT)["summary"]["lettered_panels"],
            "human_reviewed": 0,
            "human_review_minutes": None,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
            "direct_paid_api_cloud_spend_usd": 0,
            "built_in_product_monetary_cost_usd": None,
        },
        "review_artifacts": [artifact(kind, path) for kind, path in ARTIFACTS],
        "strongest_route": style["selected_engineering_route"],
        "release_decision": {
            "selected_baseline": "r6",
            "status": "PROVISIONAL_ENGINEERING_RECOMMENDATION_PENDING_OWNER_REVIEW",
            "reason": "Complete coverage plus hash-isolated repairs improved seven previously weak panels while preserving every immediate non-target source hash.",
            "p032_disposition": "Retain the first selected P032, preserve the second attempt as diagnostic, and stop stochastic repetition pending owner review or deterministic repair research.",
        },
        "provider_disclosure": {
            "product": "openai_builtin_imagegen",
            "model": None,
            "endpoint": None,
            "provider_request_ids": None,
            "provider_usage": None,
            "provider_cost_usd": None,
            "seed": None,
            "direct_paid_provider_api_calls": 0,
            "external_uploads_beyond_authorized_hashes": 0,
        },
        "owner_review_state": {
            "human_reviewed": False,
            "human_review_minutes": None,
            "accepted_candidate_ids": [],
            "commercial_clearance": "NOT_EVALUATED",
            "exact_production_base_decision": "NOT_EVALUATED",
        },
        "limitations": [
            "Agent triage is non-gating and does not accept art.",
            "P032 toe-versus-heel direction remains a phone-width warning after two stochastic attempts.",
            "The 1,592.908-second sum of per-execution observations is not wall time because some calls overlapped; the reconciled approximate wall is 1,200.7 seconds.",
            "Built-in model, endpoint, request ID, usage, monetary cost, seed, and exact stochastic reproducibility are unavailable.",
            "Generated pixels remain ignored local evidence and are not committed or published.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), **document["measured_summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
