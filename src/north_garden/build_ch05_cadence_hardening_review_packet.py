"""Build deterministic local review artifacts for the CH05 cadence-hardening batch."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_ch05_overnight_review_packet as packet_tools


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "experiments/review-packets/ch05-cadence-hardening-r1"
REGISTRY = RUN_ROOT / "candidate-registry.json"
PLAN = ROOT / "production/comic/overnight/ch05-cadence-hardening-plan-r1.json"
PANELS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
BASE_REGISTRY = ROOT / "experiments/review-packets/ch05-overnight-production-r1/candidate-registry.json"
OUT = RUN_ROOT / "review"
PACKET = OUT / "review-packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    panels = json.loads(PANELS.read_text(encoding="utf-8"))
    baseline = json.loads(BASE_REGISTRY.read_text(encoding="utf-8"))
    entries = registry["entries"]
    if len(entries) != plan["generation_target"]["planned_candidates"]:
        raise SystemExit("hardening registry incomplete")
    panel_by_id = {item["panel_id"]: item for item in panels["plans"]}
    OUT.mkdir(parents=True, exist_ok=True)
    packet_tools.OUT = OUT
    derivatives = packet_tools.save_individual_derivatives(entries, panel_by_id)
    artifacts: dict[str, object] = {}
    artifacts["hardening_candidates"] = packet_tools.artifact(
        OUT / "contact-sheet-hardening-candidates.png",
        packet_tools.build_grid("CH05 CADENCE HARDENING - SIX CANDIDATES", "Five clean engineering results and one preserved duplicate-plank diagnostic", entries, columns=3, cell=(620, 720), render_mode="clean", plans=panel_by_id),
    )
    artifacts["lettering_overlays"] = packet_tools.artifact(
        OUT / "contact-sheet-hardening-lettering-overlays.png",
        packet_tools.build_grid("CH05 HARDENING - LETTERING SAFE ZONES", "Cyan is the exact ComicPanelPlan zone; compare h002/h003/h004 with their source failures", entries, columns=3, cell=(620, 720), render_mode="overlay", plans=panel_by_id),
    )
    artifacts["phone_previews"] = packet_tools.artifact(
        OUT / "contact-sheet-hardening-phone-previews.png",
        packet_tools.build_grid("CH05 HARDENING - PHONE PREVIEWS", "Each candidate is reduced through a 390x844 phone viewport", entries, columns=3, cell=(520, 930), render_mode="phone", plans=panel_by_id),
    )
    old = {item["candidate_id"]: item for item in baseline["entries"]}
    new = {item["candidate_id"]: item for item in entries}
    combined = {**old, **new}
    artifacts["p050_style_completion"] = packet_tools.artifact(
        OUT / "comparison-p050-style-completion.png",
        packet_tools.build_grid("CH05 P050 - THREE-STYLE WIDE ACTION", "Same ComicPanelPlan: clear-line watercolor / limited ink / cel-painted", [combined[cid] for cid in ["c017", "c018", "h001"]], columns=3, cell=(620, 720), render_mode="clean", plans=panel_by_id),
    )
    artifacts["targeted_repair_pairs"] = packet_tools.artifact(
        OUT / "comparison-targeted-repair-pairs.png",
        packet_tools.build_grid("CH05 TARGETED REPAIRS - OLD / NEW", "Each row: source failure on the left, minimal composition correction on the right", [combined[cid] for cid in ["c003", "h002", "c007", "h003", "c009", "h004"]], columns=2, cell=(760, 760), render_mode="clean", plans=panel_by_id),
    )
    artifacts["p036_causal_correction"] = packet_tools.artifact(
        OUT / "comparison-p036-causal-correction.png",
        packet_tools.build_grid("CH05 P036 - CAUSAL SEMANTIC CORRECTION", "c011 incomplete connection / h005 duplicate-plank lever / h006 single-plank reach and brace", [combined[cid] for cid in ["c011", "h005", "h006"]], columns=3, cell=(620, 760), render_mode="clean", plans=panel_by_id),
    )
    record = {
        "record_type": "CH05CadenceHardeningReviewPacket",
        "schema_version": "1.0",
        "record_id": "ng-ch05-cadence-hardening-review-packet-r1",
        "state": "READY_FOR_OWNER_REVIEW_UNACCEPTED",
        "plan": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "candidate_registry": {"path": REGISTRY.relative_to(ROOT).as_posix(), "sha256": sha256(REGISTRY)},
        "candidate_count": len(entries),
        "distinct_panel_plans": len({item["panel_id"] for item in entries}),
        "total_elapsed_seconds": registry["total_elapsed_seconds"],
        "disclosed_spend_usd": None,
        "artifacts": artifacts,
        "candidate_derivatives": derivatives,
        "provider_metadata_limitations": ["model unavailable", "endpoint unavailable", "provider request ID unavailable", "usage unavailable", "cost unavailable", "deterministic seed unavailable"],
        "boundary": "Ignored local research pixels; no acceptance, commercial clearance, exact-base promotion, or expanded upload authority."
    }
    PACKET.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"built hardening packet: {PACKET.relative_to(ROOT)} {sha256(PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
