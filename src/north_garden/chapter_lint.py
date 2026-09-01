"""Deterministic, non-gating lint for an edition-selected comic sequence.

This deliberately reports unavailable checks rather than inventing results.  It is
the first chapter-level QA gate, not a VLM substitute and not a publication gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EDITION = ROOT / "production/editions/north-garden-research-edition-001.json"
DEFAULT_OUTPUT = ROOT / "experiments/results/chapter_lint_ch01_research_edition_001.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phash(path: Path) -> str:
    """Return a compact DCT perceptual hash without non-standard dependencies."""
    with Image.open(path) as source:
        image = source.convert("L").resize((32, 32), Image.Resampling.LANCZOS)
    pixels = list(image.get_flattened_data())
    values = [[float(pixels[y * 32 + x]) for x in range(32)] for y in range(32)]
    coeffs: list[float] = []
    for v in range(8):
        for u in range(8):
            if u == 0 and v == 0:
                continue
            total = 0.0
            for y in range(32):
                for x in range(32):
                    total += values[y][x] * math.cos((2 * x + 1) * u * math.pi / 64) * math.cos((2 * y + 1) * v * math.pi / 64)
            coeffs.append(total)
    median = sorted(coeffs)[len(coeffs) // 2]
    return "".join("1" if value > median else "0" for value in coeffs)


def hamming(left: str, right: str) -> int:
    return sum(a != b for a, b in zip(left, right, strict=True))


def lint(edition_path: Path) -> dict[str, object]:
    edition = json.loads(edition_path.read_text(encoding="utf-8"))
    plans_path = ROOT / edition["comic_plan_collection"]
    plans = json.loads(plans_path.read_text(encoding="utf-8"))["plans"]
    display_order = {plan["panel_id"]: plan["display_order"] for plan in plans}
    if "selected_revisions" in edition:
        selected = edition["selected_revisions"]
    else:
        collection_path = ROOT / edition["panel_revision_collection"]
        collection = json.loads(collection_path.read_text(encoding="utf-8"))
        by_revision_id = {item["panel_revision_id"]: item for item in collection["revisions"]}
        selected = [
            {
                "panel_id": by_revision_id[revision_id]["panel_id"],
                "accepted_asset": by_revision_id[revision_id]["asset_path"],
                "sha256": by_revision_id[revision_id]["sha256"],
                "panel_revision_id": revision_id,
            }
            for revision_id in edition["selected_panel_revision_ids"]
        ]
    panel_ids = [item["panel_id"] for item in selected]
    checks: list[dict[str, object]] = []
    checks.append({
        "id": "panel_ids_unique_and_known",
        "status": "pass" if len(panel_ids) == len(set(panel_ids)) and set(panel_ids) <= set(display_order) else "fail",
        "observed_panel_ids": panel_ids,
    })
    order = [display_order[item] for item in panel_ids]
    checks.append({"id": "reading_order_strictly_increasing", "status": "pass" if order == sorted(order) and len(order) == len(set(order)) else "fail", "display_order": order})
    candidates: list[dict[str, object]] = []
    for revision in selected:
        path = ROOT / revision["accepted_asset"]
        actual_sha = sha256(path) if path.exists() else "MISSING"
        candidates.append({
            "panel_id": revision["panel_id"],
            "path": revision["accepted_asset"],
            "sha256": actual_sha,
            "phash_dct_63": phash(path) if path.exists() else None,
        })
    checks.append({
        "id": "selected_asset_hashes", "status": "pass" if all(item["sha256"] == revision["sha256"] for item, revision in zip(candidates, selected, strict=True)) else "fail",
        "candidates": [{"panel_id": item["panel_id"], "sha256": item["sha256"]} for item in candidates],
    })
    pairs: list[dict[str, object]] = []
    for index, left in enumerate(candidates):
        for right in candidates[index + 1:]:
            distance = hamming(str(left["phash_dct_63"]), str(right["phash_dct_63"]))
            pairs.append({"left_panel_id": left["panel_id"], "right_panel_id": right["panel_id"], "hamming_distance": distance, "near_duplicate": distance <= 6})
    probable_duplicates = [pair for pair in pairs if pair["near_duplicate"]]
    checks.append({
        "id": "duplicate_panel_phash",
        "status": "pass" if not probable_duplicates else "advisory",
        "threshold": 6,
        "threshold_state": "UNCALIBRATED_ADVISORY_ONLY",
        "reason": "A single approved archival sequence cannot calibrate a duplicate threshold. Human review is required for any near pair.",
        "pairs": pairs,
    })
    checks.append({
        "id": "balloon_geometry_and_reading_order",
        "status": "not_assessable",
        "reason": "The accepted CH01 art archive has no balloon/lettering geometry manifest. Do not infer balloon checks from raster art.",
    })
    return {
        "record_type": "ChapterLintRecord",
        "schema_version": "1.0",
        "edition_id": edition["edition_id"],
        "edition_path": str(edition_path.relative_to(ROOT)).replace("\\", "/"),
        "comic_plan_collection": edition["comic_plan_collection"],
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "summary": {
            "pass": sum(item["status"] == "pass" for item in checks),
            "fail": sum(item["status"] == "fail" for item in checks),
            "not_assessable": sum(item["status"] == "not_assessable" for item in checks),
            "advisory": sum(item["status"] == "advisory" for item in checks),
            "gating": False,
            "limitation": "A passing lint result does not establish narrative quality, character identity, set continuity, or production acceptance.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edition", type=Path, default=DEFAULT_EDITION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    edition_path = args.edition.resolve()
    output_path = args.output.resolve()
    record = lint(edition_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"{record['summary']['fail']} failures, {record['summary']['advisory']} advisories, {record['summary']['not_assessable']} not-assessable checks; wrote {output_path}")
    return 0 if record["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
