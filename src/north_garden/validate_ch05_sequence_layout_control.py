"""Validate deterministic and semantic contracts for P033-P038 layout controls."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageColor


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "src/north_garden/build_ch05_sequence_layout_control.py"
MANIFEST = ROOT / "production/comic/layout-controls/ch05-p033-p038-deterministic-r1.json"
RESULT = ROOT / "experiments/results/ch05-p033-p038-sequence-layout-control-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    completed = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip())
    return json.loads(RESULT.read_text(encoding="utf-8"))


def output_hashes(record: dict) -> dict:
    return {
        **{
            item["panel_id"]: {
                "image": item["image"]["sha256"],
                "story_occupancy_mask": item["story_occupancy_mask"]["sha256"],
            }
            for item in record["panels"]
        },
        "contact_sheet": record["contact_sheet"]["sha256"],
    }


def main() -> int:
    failures = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    try:
        first, second = build(), build()
    except RuntimeError as error:
        print(f"failure: builder failed: {error}")
        return 1

    first_hashes, second_hashes = output_hashes(first), output_hashes(second)
    if first_hashes != second_hashes:
        failures.append("two consecutive builds produced different hashes")
    if first_hashes != manifest["expected_output_sha256"]:
        failures.append("built output hashes do not match the reviewed manifest")
    for relative, expected in manifest["source_hashes"].items():
        if sha256(ROOT / relative) != expected:
            failures.append(f"source hash mismatch: {relative}")

    rows = {item["panel_id"]: item for item in first["panels"]}
    if [item["display_order"] for item in first["panels"]] != list(range(33, 39)):
        failures.append("panel order is not contiguous P033-P038")
    for panel_id, expected in manifest["expected_role_proxy_counts"].items():
        if rows[panel_id]["role_proxy_count"] != expected:
            failures.append(f"role proxy count mismatch: {panel_id}")
    if first["summary"]["safe_zone_overlap_pixels"] != 0:
        failures.append("story occupancy overlaps a lettering safe zone")

    color_tokens = first["continuity_color_tokens"]
    for chain in manifest["continuity_token_chains"]:
        target_rgb = np.array(ImageColor.getrgb(color_tokens[chain["color_token"]]))
        for panel_id in chain["panel_ids"]:
            with Image.open(ROOT / rows[panel_id]["image"]["path"]).convert("RGB") as image:
                pixels = np.asarray(image)
            count = int(np.all(pixels == target_rgb, axis=2).sum())
            if count < 50:
                failures.append(f"continuity color token absent: {chain['id']}:{panel_id}")

    for item in first["panels"]:
        if item["human_minutes"] is not None or item["accepted"]:
            failures.append(f"review/acceptance incorrectly promoted: {item['panel_id']}")
    summary = first["summary"]
    if any(summary[field] != 0 for field in ("provider_requests", "external_uploads", "accepted_panels")):
        failures.append("execution or acceptance count is nonzero")
    if summary["external_cost_usd"] != "0.000000" or summary["human_minutes"] is not None:
        failures.append("cost/minute boundary violated")
    if first.get("medium") != "comic" or first.get("animation_shot_plan") is not None:
        failures.append("ComicPanelPlan/AnimationShotPlan boundary violated")

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (6/6 hash-stable controls, 0 safe-zone pixels, 3 continuity-token chains)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
