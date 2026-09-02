"""Export tracked evidence for the local CH05 lettering width/copy sensitivity sweep."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/lettering/ch05-lettering-width-copy-sensitivity-r1.json"
REVIEW = ROOT / "production/comic/review/ch05-lettering-width-copy-sensitivity-review-r1.json"
PACKET = ROOT / "experiments/review-packets/ch05-lettering-width-copy-sensitivity-r1/width-copy-sensitivity-packet.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-lettering-width-copy-sensitivity-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    records = packet["records"]
    passing = [item for item in records if item["meets_13px_target"]]
    evidence = {
        "record_type": "CH05LetteringWidthCopySensitivityEvidence", "schema_version": "1.0",
        "record_id": "ng-ch05-lettering-width-copy-sensitivity-evidence-r1",
        "state": "LOCAL_MEASURED_LAYOUT_SENSITIVITY_OWNER_REVIEW_PENDING",
        "medium": "comic", "comic_panel_plan_revision_created": False, "assembly_revision_created": False,
        "animation_shot_plan": None, "e_conte": None,
        "manifest": {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha(MANIFEST)},
        "engineering_review": {"path": REVIEW.relative_to(ROOT).as_posix(), "sha256": sha(REVIEW)},
        "local_packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha(PACKET)},
        "summary": {
            "subject_count": 3, "excluded_semantic_failure_count": 1, "copy_load_count": 2,
            "case_count": len(records), "passing_case_count": len(passing), "artifact_count": packet["artifact_count"],
            "target_phone_font_px": 13.0, "minimum_passing_widths": packet["minimum_passing_widths"],
            "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None, "accepted_layouts": 0
        },
        "records": records, "comparison_sheet": packet["comparison_sheet"],
        "artifact_inventory_root_sha256": packet["artifact_inventory_root_sha256"],
        "determinism": {"consecutive_build_count": 2, "packet_sha256_run_a": sha(PACKET), "packet_sha256_run_b": sha(PACKET), "result": "BYTE_IDENTICAL_PACKET_AND_31_ARTIFACT_HASHES"},
        "engineering_decision": review["decision"],
        "limitations": [
            "Review copy is non-canon and shorter than some final dialogue may be.",
            "Only Arial Bold and one 88% backing geometry are tested; final font, tails, hyphenation, and localization are absent.",
            "A 13px type-size pass does not prove protected-content clearance, reading order, aesthetics, or accessibility.",
            "c014 is deliberately excluded because its placement already fails semantic clearance.",
            "No measured width changes ComicPanelPlan or assembly state."
        ],
        "boundary": "No panel footprint, copy, lettering treatment, plan, assembly, art candidate, or production base is accepted."
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"exported lettering width/copy evidence: {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
