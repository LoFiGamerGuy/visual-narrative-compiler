"""Build the clean, lettered, phone, continuity, and triage hybrid review packet."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from build_ch05_complete_chapter_continuity_sheet import build as build_continuity
from build_ch05_complete_chapter_review import build as build_clean
from build_ch05_lettered_chapter_review import build as build_lettered


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-semantic-pass-hybrid-assembly-r1.json"
TRIAGE = ROOT / "docs/research/evidence/ch05-semantic-pass-hybrid-triage-r1.json"
LETTERING = ROOT / "production/comic/lettering/ch05-complete-chapter-lettering-proposal-r1.json"
PACKET = ROOT / "experiments/review-packets/ch05-semantic-pass-hybrid-r1"
CLEAN = PACKET / "clean"
LETTERED = PACKET / "lettered"
REVIEW = PACKET / "review"
INDEX = PACKET / "packet-index.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing packet artifact: {path}")
    result: dict[str, Any] = {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }
    if path.suffix.lower() == ".png":
        from PIL import Image

        with Image.open(path) as image:
            result.update({"width": image.width, "height": image.height})
    return result


def main() -> int:
    PACKET.mkdir(parents=True, exist_ok=True)
    clean_report = build_clean(ROOT, MANIFEST, CLEAN)
    build_report = CLEAN / "build-report.json"
    lettered_report = build_lettered(
        build_report,
        LETTERING,
        LETTERED,
        record_id="ng-ch05-semantic-pass-hybrid-lettering-build-r1",
        artifact_stem="ch05-semantic-pass-hybrid-lettered-r1",
    )
    continuity_path = REVIEW / "ch05-semantic-pass-hybrid-continuity-sheet-r1.png"
    build_continuity(MANIFEST, continuity_path)
    triage_path = REVIEW / "ch05-semantic-pass-hybrid-triage-sheet-r1.png"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "src/north_garden/build_ch05_complete_chapter_triage_sheet.py"),
            "--assembly",
            str(MANIFEST),
            "--triage",
            str(TRIAGE),
            "--output",
            str(triage_path),
        ],
        cwd=ROOT,
        check=True,
    )
    artifacts = {
        "clean_long_scroll": artifact(ROOT / clean_report["artifacts"]["long_scroll"]["path"]),
        "clean_contact_sheet": artifact(ROOT / clean_report["artifacts"]["contact_sheet"]["path"]),
        "lettering_safe_zone_scroll": artifact(ROOT / clean_report["artifacts"]["long_scroll_lettering_overlay"]["path"]),
        "lettering_safe_zone_contact_sheet": artifact(ROOT / clean_report["artifacts"]["contact_sheet_lettering_overlay"]["path"]),
        "clean_phone_scroll": artifact(ROOT / clean_report["artifacts"]["phone_long_scroll"]["path"]),
        "lettered_long_scroll": artifact(ROOT / lettered_report["artifacts"]["lettered_long_scroll"]["path"]),
        "lettered_phone_scroll": artifact(ROOT / lettered_report["artifacts"]["lettered_phone_scroll"]["path"]),
        "continuity_sheet": artifact(continuity_path),
        "triage_sheet": artifact(triage_path),
    }
    index = {
        "record_type": "CH05SemanticPassHybridReviewPacketIndex",
        "schema_version": "1.0",
        "record_id": "ng-ch05-semantic-pass-hybrid-review-packet-r1",
        "state": "REVIEW_PACKET_UNACCEPTED_OWNER_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [
            {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256(MANIFEST)},
            {"path": TRIAGE.relative_to(ROOT).as_posix(), "sha256": sha256(TRIAGE)},
            {"path": LETTERING.relative_to(ROOT).as_posix(), "sha256": sha256(LETTERING)},
        ],
        "summary": {
            "chapter_panels": 50,
            "semantic_pass": 49,
            "semantic_warn": 1,
            "semantic_fail": 0,
            "sole_warning_panel": "ng-ch05-sc01-p032",
            "artifact_categories": len(artifacts),
            "owner_reviewed": 0,
            "accepted": 0,
        },
        "artifacts": artifacts,
        "reports": {
            "clean_build": artifact(build_report),
            "lettering_build": artifact(LETTERED / "lettering-build-report.json"),
            "continuity_build": artifact(REVIEW / "continuity-sheet-report.json"),
            "triage_build": artifact(REVIEW / "triage-sheet-report.json"),
        },
        "limitations": [
            "Thirty-three adjacent route transitions require full-scroll and phone-width style continuity review.",
            "Lettering uses provisional review copy and does not establish canon dialogue.",
            "P032 remains a semantic warning and is deliberately not hidden by the aggregate packet.",
            "All pixels and reports remain beneath the ignored local experiments tree.",
        ],
        "boundary": "Review packet only; no acceptance, commercial clearance, rights conclusion, canon replacement, or exact production-base decision.",
    }
    INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"packet": INDEX.relative_to(ROOT).as_posix(), "sha256": sha256(INDEX), "artifacts": len(artifacts), "pass": 49, "warn": 1, "fail": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
