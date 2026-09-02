"""Compile the deterministic assembly manifest from verified CH05 panel crops."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
SPLIT_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/panel-split-report.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_width(plan: dict[str, Any]) -> int:
    order = plan["display_order"]
    if order in {17, 30, 48, 50}:
        return 1040
    cast_count = len(plan.get("visible_adult_cast", []))
    motion = plan["comic_direction"]["motion_mode"]
    if motion == "directional_motion":
        return 960
    if motion == "practical_action":
        return 900
    if cast_count == 0:
        return 680
    if cast_count == 1:
        return 800
    return 880


def gutter_after(plan: dict[str, Any]) -> int:
    order = plan["display_order"]
    if order in {5, 14, 19, 24, 29, 34, 39, 44}:
        return 120
    if order in {17, 30, 48, 50}:
        return 96
    return 64 if len(plan.get("visible_adult_cast", [])) == 0 else 72


def main() -> int:
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    report = json.loads(SPLIT_REPORT.read_text(encoding="utf-8"))
    by_id = {row["panel_id"]: row for row in report["panels"]}
    if list(by_id) != [row["panel_id"] for row in plans]:
        raise ValueError("split report is not exact canonical CH05 order")
    entries = []
    for plan in plans:
        split = by_id[plan["panel_id"]]
        output = split["output"]
        entries.append({
            "order": plan["display_order"],
            "panel_id": plan["panel_id"],
            "candidate_id": f"chapter-r1-p{plan['display_order']:03d}",
            "sequence_id": split["sequence_id"],
            "source": {
                "path": output["path"],
                "sha256": output["sha256"],
                "width": output["width"],
                "height": output["height"],
            },
            "layout": {
                "target_width": target_width(plan),
                "alignment": "center",
                "gutter_after": gutter_after(plan),
            },
            "animation_shot_plan": None,
            "e_conte": None,
        })
    manifest = {
        "record_type": "ComicChapterProductionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-assembly-r1",
        "state": "COMPLETE_READING_DRAFT_READY_FOR_ASSEMBLY_UNACCEPTED",
        "medium": "comic",
        "chapter_complete": True,
        "animation_shot_plan": None,
        "e_conte": None,
        "comic_panel_plan_collection": {
            "path": PLAN.relative_to(ROOT).as_posix(),
            "sha256": sha256(PLAN),
        },
        "canvas": {
            "width": 1200,
            "side_margin": 80,
            "background": "#11151a",
            "top_gutter": 72,
            "phone_width": 390,
            "phone_viewport_height": 844,
        },
        "entries": entries,
        "boundary": "Complete local review assembly only; no candidate is accepted, commercially cleared, or selected as an exact production base.",
    }
    encoded = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(encoded, encoding="utf-8", newline="\n")
    print(json.dumps({"entries": len(entries), "output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
