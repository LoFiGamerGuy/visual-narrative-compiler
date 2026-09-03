"""Build deterministic four-chapter visual-progression review artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from build_ch06_default_route_review import (
    fit_width,
    font,
    labeled_canvas,
    rel,
    sha256,
    stack,
)
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "experiments/review-packets/ch06-ch09-progression-review-r1"
MANIFEST = ROOT / "production/comic/run-manifests/ch06-ch09-progression-review-r1.json"
CHAPTERS = ("ch06", "ch07", "ch08", "ch09")
SAMPLE_ORDERS = (1, 6, 11, 16, 21, 26, 31, 36, 40)


def packet_path(chapter: str) -> Path:
    return ROOT / f"production/comic/run-manifests/{chapter}-default-house-route-review-packet-r1.json"


def artifact_path(chapter: str, kind: str) -> Path:
    return ROOT / f"experiments/review-packets/{chapter}-default-house-route-r1/{chapter}-{kind}-r1.png"


def chapter_banner(image: Image.Image, chapter: str, label: str) -> Image.Image:
    fitted = fit_width(image.convert("RGB"), 1200)
    canvas = Image.new("RGB", (1200, fitted.height + 42), "#11151b")
    ImageDraw.Draw(canvas).text((10, 9), f"{chapter.upper()} · {label}", fill="#e9edf2", font=font(18))
    canvas.paste(fitted, (0, 42))
    return canvas


def sample_row(chapter: str, packet: dict[str, Any]) -> Image.Image:
    candidates = packet["candidates"]
    chosen = [candidates[index - 1] for index in SAMPLE_ORDERS]
    cells: list[Image.Image] = []
    for order, candidate in zip(SAMPLE_ORDERS, chosen, strict=True):
        with Image.open(ROOT / candidate["path"]) as opened:
            cells.append(labeled_canvas(opened.convert("RGB"), f"P{order:03d}", 128, 26))
    height = max(cell.height for cell in cells)
    row = Image.new("RGB", (1200, height), "#11151b")
    for index, cell in enumerate(cells):
        row.paste(cell, (8 + index * 132, 0))
    return chapter_banner(row, chapter, "fixed-ordinal phone sampler")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    packets: dict[str, dict[str, Any]] = {}
    source_bindings = []
    triage_total = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for chapter in CHAPTERS:
        path = packet_path(chapter)
        packet = json.loads(path.read_text(encoding="utf-8"))
        if len(packet["candidates"]) != 40 or packet["summary"]["complete_chapter"] is not True:
            raise ValueError(f"{chapter} is not a complete 40-panel packet")
        packets[chapter] = packet
        source_bindings.append({"chapter": chapter.upper(), "path": rel(path), "sha256": sha256(path)})
        for state in triage_total:
            triage_total[state] += packet["summary"]["triage"][state]

    contact_rows = []
    sequence_rows = []
    for chapter in CHAPTERS:
        with Image.open(artifact_path(chapter, "contact-sheet")) as opened:
            contact_rows.append(chapter_banner(opened, chapter, "40-panel contact"))
        with Image.open(artifact_path(chapter, "sequence-contact-sheet")) as opened:
            sequence_rows.append(chapter_banner(opened, chapter, "eight chronological sequences"))

    contact_out = OUT_DIR / "ch06-ch09-progression-contact-sheet-r1.png"
    sequence_out = OUT_DIR / "ch06-ch09-sequence-progression-r1.png"
    sampler_out = OUT_DIR / "ch06-ch09-phone-progression-sampler-r1.png"
    stack(contact_rows, 1200, 14, "#11151b").save(contact_out, format="PNG", compress_level=9)
    stack(sequence_rows, 1200, 14, "#11151b").save(sequence_out, format="PNG", compress_level=9)

    sampler = stack([sample_row(chapter, packets[chapter]) for chapter in CHAPTERS], 1200, 12, "#11151b")
    sampler.save(sampler_out, format="PNG", compress_level=9)

    artifacts = []
    for kind, path in (
        ("four_chapter_contact_sheet", contact_out),
        ("four_chapter_sequence_progression", sequence_out),
        ("four_chapter_phone_sampler", sampler_out),
    ):
        with Image.open(path) as opened:
            dimensions = [opened.width, opened.height]
        artifacts.append({"type": kind, "path": rel(path), "sha256": sha256(path), "dimensions": dimensions})

    manifest = {
        "record_type": "ComicMultiChapterProgressionReview",
        "schema_version": "1.0",
        "record_id": "ng-ch06-ch09-progression-review-r1",
        "state": "OWNER_REVIEW_PENDING",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "chapters": [chapter.upper() for chapter in CHAPTERS],
        "source_packets": source_bindings,
        "summary": {
            "complete_chapters": 4,
            "panel_candidates": 160,
            "sequence_sources": 32,
            "triage": triage_total,
            "sampled_panels": len(CHAPTERS) * len(SAMPLE_ORDERS),
            "whole_chapter_alternate_arms": 0,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "artifacts": artifacts,
        "limitations": [
            "The sampler selects fixed ordinal panels for navigation; it is not a quality ranking.",
            "CH06 and CH07 retain their documented one and two blocking candidate failures respectively.",
            "All pixels remain ignored, non-reproducible, unaccepted, and commercially uncleared research evidence.",
        ],
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": 3, "chapters": 4, "panels": 160, "sampled": 36, "triage": triage_total}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
