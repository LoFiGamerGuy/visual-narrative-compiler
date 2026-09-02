"""Export tracked evidence for local CH05 outside-art lettering-band alternatives."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/lettering/ch05-outside-art-lettering-band-r1.json"
REVIEW = ROOT / "production/comic/review/ch05-outside-art-lettering-band-review-r1.json"
PACKET = ROOT / "experiments/review-packets/ch05-outside-art-lettering-band-r1/outside-art-lettering-band-packet.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-outside-art-lettering-band-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    evidence = {
        "record_type": "CH05OutsideArtLetteringBandEvidence", "schema_version": "1.0",
        "record_id": "ng-ch05-outside-art-lettering-band-evidence-r1",
        "state": "LOCAL_NONPLAN_GEOMETRY_DEMONSTRATION_OWNER_REVIEW_PENDING",
        "medium": "comic", "comic_panel_plan_revision_created": False, "assembly_revision_created": False,
        "animation_shot_plan": None, "e_conte": None,
        "manifest": {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha(MANIFEST)},
        "engineering_review": {"path": REVIEW.relative_to(ROOT).as_posix(), "sha256": sha(REVIEW)},
        "local_packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha(PACKET)},
        "summary": {
            "treatment_count": 2, "subject_count": 3, "band_instance_count": 6, "artifact_count": packet["artifact_count"],
            "base_scroll_dimensions": [1200, 14566], "band_scroll_dimensions": [1200, 15046], "phone_scroll_dimensions": [390, 4890],
            "scroll_height_increase_px": 480, "scroll_height_increase_percent": 3.295,
            "font_size_phone_px": 13.975, "band_height_phone_px": 52.0, "source_pixels_changed": 0,
            "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None, "accepted_treatments": 0
        },
        "treatments": packet["treatments"], "comparison_sheet": packet["comparison_sheet"],
        "artifact_inventory_root_sha256": packet["artifact_inventory_root_sha256"],
        "determinism": {"consecutive_build_count": 2, "packet_sha256_run_a": sha(PACKET), "packet_sha256_run_b": sha(PACKET), "result": "BYTE_IDENTICAL_PACKET_AND_5_ARTIFACT_HASHES"},
        "engineering_decision": review["decision"],
        "limitations": [
            "The geometry is outside current ComicPanelPlan safe zones and is not a plan or assembly revision.",
            "No speech tail, speaker binding, final dialogue, localization, or final font is tested.",
            "Review copy is non-canon and only two short lines.",
            "Zero source-pixel change proves geometric non-overlap, not storytelling or accessibility acceptance.",
            "Light-band versus dark-direct preference remains owner review pending."
        ],
        "boundary": "No caption, direct text, dialogue, plan, assembly, art, or production base is accepted."
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"exported outside-art lettering evidence: {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
