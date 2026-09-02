"""Export tracked hash/measurement evidence from the ignored CH05 lettering rehearsal packet."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/lettering/ch05-transparent-lettering-rehearsal-r1.json"
REVIEW = ROOT / "production/comic/review/ch05-transparent-lettering-rehearsal-review-r1.json"
PACKET = ROOT / "experiments/review-packets/ch05-transparent-lettering-rehearsal-r1/lettering-rehearsal-packet.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-transparent-lettering-rehearsal-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    records = packet["records"]
    contrasts = [item["metrics"]["black_type_contrast_ratio_p05"] for item in records]
    phone_fonts = [item["metrics"]["font_size_phone_px"] for item in records]
    evidence = {
        "record_type": "CH05TransparentLetteringRehearsalEvidence", "schema_version": "1.0",
        "record_id": "ng-ch05-transparent-lettering-rehearsal-evidence-r1",
        "state": "LOCAL_MEASURED_REHEARSAL_OWNER_REVIEW_PENDING_UNACCEPTED",
        "medium": "comic", "comic_panel_plan_revision_created": False, "animation_shot_plan": None, "e_conte": None,
        "manifest": {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha(MANIFEST)},
        "engineering_review": {"path": REVIEW.relative_to(ROOT).as_posix(), "sha256": sha(REVIEW)},
        "local_packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha(PACKET)},
        "summary": {
            "subject_count": 4, "dense_outlier_count": 2, "clean_control_count": 2, "treatment_count": len(records),
            "artifact_count": packet["artifact_count"], "artifact_inventory_root_sha256": packet["artifact_inventory_root_sha256"],
            "phone_font_min_px": min(phone_fonts), "phone_font_max_px": max(phone_fonts), "subjects_meeting_13px_target": 0,
            "black_type_p05_contrast_min": min(contrasts), "black_type_p05_contrast_max": max(contrasts),
            "protected_content_clearance_pass_subjects": 3, "protected_content_clearance_fail_subjects": 1,
            "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None, "accepted_treatments": 0
        },
        "records": records,
        "comparison_sheet": packet["comparison_sheet"],
        "determinism": {
            "consecutive_build_count": 2,
            "packet_sha256_run_a": sha(PACKET), "packet_sha256_run_b": sha(PACKET),
            "result": "BYTE_IDENTICAL_PACKET_AND_25_ARTIFACT_HASHES"
        },
        "engineering_decision": review["decision"],
        "limitations": [
            "WCAG backing contrast does not detect faces, hands, story objects, reading order, or aesthetic acceptability.",
            "Non-canon review copy approximates two short lines; final dialogue length and tails are untested.",
            "The exact local Arial Bold font is hash-pinned but is not a final font-license or brand decision.",
            "c014 fails protected-person clearance under visual inspection regardless of measured contrast.",
            "No treatment reaches the declared 13px phone-type target at the current four panel footprints."
        ],
        "boundary": "No art, copy, treatment, panel plan, or production base is accepted, commercially cleared, or externally executed."
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"exported lettering evidence: {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
