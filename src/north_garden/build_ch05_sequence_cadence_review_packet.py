"""Build the complete CH05 three-block sequence-cadence review packet."""
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
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-sequence-cadence-review-assembly-r1.json"
TRIAGE = ROOT / "docs/research/evidence/ch05-sequence-cadence-review-triage-r1.json"
LETTERING = ROOT / "production/comic/lettering/ch05-complete-chapter-lettering-proposal-r1.json"
PACKET = ROOT / "experiments/review-packets/ch05-sequence-cadence-review-r1"
CLEAN = PACKET / "clean"
LETTERED = PACKET / "lettered"
REVIEW = PACKET / "review"
INDEX = PACKET / "packet-index.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for name in (["DejaVuSans-Bold.ttf", "Arial Bold.ttf"] if bold else ["DejaVuSans.ttf", "Arial.ttf"]):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


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


def build_boundary_sheet(path: Path) -> None:
    """Expose the only two route boundaries as adjacent full-panel pairs."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = {row["order"]: row for row in manifest["entries"]}
    canvas = Image.new("RGB", (1200, 1040), "#f2efe8")
    draw = ImageDraw.Draw(canvas)
    title_font = font(31, True)
    label_font = font(20)
    draw.text((42, 28), "CH05 SEQUENCE-CADENCE ROUTE BOUNDARIES", fill="#17202a", font=title_font)
    pairs = [
        (5, 6, "Boundary 1 - reduced-palette text control -> R6"),
        (39, 40, "Boundary 2 - R6 -> premium cel"),
    ]
    for row_index, (left_order, right_order, caption) in enumerate(pairs):
        top = 92 + row_index * 466
        draw.text((42, top), caption, fill="#17202a", font=label_font)
        for column, order in enumerate((left_order, right_order)):
            entry = entries[order]
            with Image.open(ROOT / entry["source"]["path"]) as opened:
                panel = ImageOps.contain(opened.convert("RGB"), (520, 350), Image.Resampling.LANCZOS)
            x = 42 + column * 568 + (520 - panel.width) // 2
            y = top + 48 + (350 - panel.height) // 2
            canvas.paste(panel, (x, y))
            label = f"P{order:03d} | {entry['selection']['route']}"
            draw.text((42 + column * 568, top + 406), label, fill="#17202a", font=label_font)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def main() -> int:
    PACKET.mkdir(parents=True, exist_ok=True)
    clean_report = build_clean(ROOT, MANIFEST, CLEAN)
    build_report = CLEAN / "build-report.json"
    lettered_report = build_lettered(
        build_report,
        LETTERING,
        LETTERED,
        record_id="ng-ch05-sequence-cadence-lettering-build-r1",
        artifact_stem="ch05-sequence-cadence-lettered-r1",
    )
    continuity_path = REVIEW / "ch05-sequence-cadence-continuity-sheet-r1.png"
    build_continuity(MANIFEST, continuity_path)
    boundary_path = REVIEW / "ch05-sequence-cadence-boundary-continuity-sheet-r1.png"
    build_boundary_sheet(boundary_path)
    triage_path = REVIEW / "ch05-sequence-cadence-triage-sheet-r1.png"
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
        "boundary_continuity_sheet": artifact(boundary_path),
        "triage_sheet": artifact(triage_path),
    }
    index = {
        "record_type": "CH05SequenceCadenceReviewPacketIndex",
        "schema_version": "1.0",
        "record_id": "ng-ch05-sequence-cadence-review-packet-r1",
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
            "semantic_pass": 47,
            "semantic_warn": 3,
            "semantic_fail": 0,
            "warning_panels": ["ng-ch05-sc01-p003", "ng-ch05-sc01-p032", "ng-ch05-sc01-p045"],
            "route_blocks": 3,
            "adjacent_route_transitions": 2,
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
        "review_order": [
            "lettered_phone_scroll",
            "clean_phone_scroll",
            "continuity_sheet",
            "boundary_continuity_sheet",
            "triage_sheet",
            "lettering_safe_zone_contact_sheet",
            "clean_long_scroll",
        ],
        "limitations": [
            "The three-block cadence is a non-gating engineering recommendation, not owner acceptance.",
            "P003, P032, and P045 retain explicit semantic warnings.",
            "The two route boundaries require visual review for palette, lighting, line-weight, and environment continuity.",
            "Lettering uses provisional review copy and does not establish canon dialogue.",
            "All generated pixels and build reports remain beneath the ignored local experiments tree.",
        ],
        "boundary": "Review packet only; no acceptance, rights or commercial clearance, canon replacement, or exact production-base decision.",
    }
    INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"packet": INDEX.relative_to(ROOT).as_posix(), "sha256": sha256(INDEX), "artifacts": len(artifacts), "pass": 47, "warn": 3, "fail": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
