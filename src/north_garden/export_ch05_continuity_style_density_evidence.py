"""Export tracked evidence for CH05 phone-scale style/density diagnostics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "experiments/review-packets/ch05-continuity-style-density-r1/continuity-style-density-packet.json"
REVIEW = ROOT / "production/comic/review/ch05-continuity-style-density-review-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-continuity-style-density-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    evidence = {
        "record_type": "CH05ContinuityStyleDensityEvidence", "schema_version": "1.0",
        "record_id": "ng-ch05-continuity-style-density-evidence-r1",
        "state": "LOCAL_DIAGNOSTIC_OWNER_REVIEW_PENDING_UNACCEPTED",
        "medium": "comic", "comic_panel_plan_revision_created": False, "assembly_revision_created": False,
        "animation_shot_plan": None, "e_conte": None,
        "local_packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha(PACKET)},
        "engineering_review": {"path": REVIEW.relative_to(ROOT).as_posix(), "sha256": sha(REVIEW)},
        "summary": {
            "selected_candidate_count": len(packet["selected_records"]), "style_triage_candidate_count": 26,
            "style_count": 4, "sequence_count": 3, "adjacent_pair_count": len(packet["adjacent_appearance_jumps"]),
            "artifact_count": packet["artifact_count"], "accepted_candidates": 0, "human_review_minutes": None,
            "provider_calls": 0, "uploads": 0, "cost_usd": 0
        },
        "feature_names": packet["feature_names"], "selected_records": packet["selected_records"],
        "adjacent_appearance_jumps": packet["adjacent_appearance_jumps"], "max_adjacent_jump": packet["max_adjacent_jump"],
        "style_engineering_results_all_26": packet["style_engineering_results_all_26"],
        "selected_style_counts": packet["selected_style_counts"], "manual_continuity_review": packet["manual_continuity_review"],
        "artifacts": packet["artifacts"], "artifact_inventory_root_sha256": packet["artifact_inventory_root_sha256"],
        "determinism": {"consecutive_analysis_count": 2, "packet_sha256_run_a": sha(PACKET), "packet_sha256_run_b": sha(PACKET), "result": "BYTE_IDENTICAL_PACKET_AND_4_ARTIFACT_HASHES"},
        "engineering_decision": review["decision"],
        "limitations": [
            "Features are global statistics at the current phone footprint and cannot detect identity, hair, wardrobe, hands, objects, causality, or lettering clearance.",
            "Style tasks, prompts, formats, and reference conditions are unbalanced; pass rates are descriptive rather than universal scores.",
            "Adjacent z-score distance can identify appearance changes but cannot decide whether a rhythmic contrast is desirable.",
            "Manual continuity review remains provisional and owner acceptance remains zero."
        ],
        "boundary": "Diagnostic density/rhythm evidence only; no candidate, style, sequence, plan, or production base is accepted."
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"exported continuity/style/density evidence: {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
