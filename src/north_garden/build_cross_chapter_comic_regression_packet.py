"""Build a deterministic CH01-CH05 ComicPanelPlan visual-regression packet."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "experiments/review-packets/cross-chapter-comic-regression-r1"
REPORT = ROOT / "docs/research/evidence/cross-chapter-comic-regression-r1.json"
def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


TITLE_FONT = font(24)
CHAPTER_FONT = font(17)
LABEL_FONT = font(13)
PLAN_SOURCES = {
    "CH01": "production/comic/ch01-sc01-panel-plans-v2.json",
    "CH02": "production/comic/ch02-sc01-panel-plans-v1.json",
    "CH03": "production/comic/ch03-sc01-panel-plans-v1.json",
    "CH04": "production/comic/ch04-sc01-panel-plans-v1.json",
    "CH05": "production/comic/ch05-sc01-panel-plans-v1.json",
}
REVISION_SOURCES = {
    "CH01": "production/comic/panel-revisions/ch01-sc01-initial-import-r1.json",
    "CH02": "production/comic/panel-revisions/ch02-sc01-historical-import-r1.json",
    "CH03": "production/comic/panel-revisions/ch03-sc01-imagegen-r1.json",
    "CH04": "production/comic/panel-revisions/ch04-sc01-imagegen-r1.json",
}
ASSEMBLY = "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json"
CH05_ANCHORS = [
    "ng-ch05-sc01-p001", "ng-ch05-sc01-p009", "ng-ch05-sc01-p017", "ng-ch05-sc01-p020",
    "ng-ch05-sc01-p029", "ng-ch05-sc01-p036", "ng-ch05-sc01-p039", "ng-ch05-sc01-p043",
    "ng-ch05-sc01-p049", "ng-ch05-sc01-p050",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def source_binding(relative: str) -> dict[str, str]:
    return {"path": relative, "sha256": sha256(ROOT / relative)}


def adult_cast(plan: dict[str, Any]) -> list[str]:
    explicit = plan.get("visible_adult_cast")
    if isinstance(explicit, list):
        return explicit
    characters = plan.get("hard_assertion_manifest", {}).get("characters")
    if isinstance(characters, list):
        return characters
    assets = plan.get("asset_ids", [])
    inferred = []
    if any("identity-soren" in asset for asset in assets):
        inferred.append("SOREN")
    if any("identity-sigrid" in asset for asset in assets):
        inferred.append("SIGRID")
    return inferred


def contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "#121820")
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def rows() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for chapter in ("CH01", "CH02", "CH03", "CH04"):
        plans = {row["panel_id"]: row for row in load(PLAN_SOURCES[chapter])["plans"]}
        revisions = load(REVISION_SOURCES[chapter])["revisions"]
        for revision in revisions:
            panel_id = revision["panel_id"]
            plan = plans.get(panel_id)
            if not plan:
                raise ValueError(f"revision lacks ComicPanelPlan: {panel_id}")
            path = ROOT / revision["asset_path"]
            if not path.is_file() or sha256(path) != revision["sha256"]:
                raise ValueError(f"source asset mismatch: {revision['asset_path']}")
            result.append({
                "chapter": chapter, "panel_id": panel_id, "display_order": plan["display_order"],
                "plan_revision_id": plan["plan_revision_id"], "candidate_id": revision["panel_revision_id"],
                "source": {"path": revision["asset_path"], "sha256": revision["sha256"]},
                "source_acceptance_state": revision["acceptance_state"],
                "visible_adult_cast": adult_cast(plan),
            })
    plans = {row["panel_id"]: row for row in load(PLAN_SOURCES["CH05"])["plans"]}
    assembly = {row["panel_id"]: row for row in load(ASSEMBLY)["entries"]}
    for panel_id in CH05_ANCHORS:
        plan, entry = plans[panel_id], assembly[panel_id]
        path = ROOT / entry["source"]["path"]
        if sha256(path) != entry["source"]["sha256"]:
            raise ValueError(f"CH05 source mismatch: {panel_id}")
        result.append({
            "chapter": "CH05", "panel_id": panel_id, "display_order": plan["display_order"],
            "plan_revision_id": plan["plan_revision_id"], "candidate_id": entry["candidate_id"],
            "source": {"path": entry["source"]["path"], "sha256": entry["source"]["sha256"]},
            "source_acceptance_state": "PENDING_OWNER_REVIEW_UNACCEPTED",
            "visible_adult_cast": adult_cast(plan),
        })
    return result


def build_contact_sheet(entries: list[dict[str, Any]], path: Path) -> None:
    width, margin, header, row_height = 1800, 40, 80, 238
    cell_width, thumb_size = 170, (154, 166)
    chapters = ["CH01", "CH02", "CH03", "CH04", "CH05"]
    canvas = Image.new("RGB", (width, header + row_height * len(chapters) + 30), "#0b0f14")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 20), "NORTH GARDEN · CH01–CH05 COMICPANELPLAN VISUAL REGRESSION", fill="#e8edf2", font=TITLE_FONT)
    draw.text((margin, 52), "Green = historical internal research selection · amber = pending owner review", fill="#aeb9c5", font=LABEL_FONT)
    for row_index, chapter in enumerate(chapters):
        y = header + row_index * row_height
        draw.rectangle((0, y, width, y + row_height - 4), fill="#101720" if row_index % 2 == 0 else "#0d141c")
        subset = [entry for entry in entries if entry["chapter"] == chapter]
        draw.text((margin, y + 10), f"{chapter} · {len(subset)} current scene/anchor panels", fill="#8fd3ff", font=CHAPTER_FONT)
        for column, entry in enumerate(subset):
            x = margin + column * cell_width
            with Image.open(ROOT / entry["source"]["path"]) as image:
                thumb = contain(image, thumb_size)
            canvas.paste(thumb, (x, y + 38))
            status_color = "#70d6a5" if entry["source_acceptance_state"] == "INTERNAL_RESEARCH_ACCEPTED" else "#ffd166"
            label = entry["panel_id"].split("-")[-1].upper()
            draw.text((x, y + 208), f"{label} · {','.join(entry['visible_adult_cast']) or 'OBJECT/SET'}", fill=status_color, font=LABEL_FONT)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False, compress_level=9)


def build_phone_scroll(entries: list[dict[str, Any]], path: Path) -> None:
    width, panel_width, margin = 390, 350, 20
    blocks: list[tuple[dict[str, Any], Image.Image]] = []
    total = 58
    previous = None
    for entry in entries:
        with Image.open(ROOT / entry["source"]["path"]) as image:
            frame = image.convert("RGB")
            frame.thumbnail((panel_width, 700), Image.Resampling.LANCZOS)
        chapter_gap = 52 if entry["chapter"] != previous else 0
        total += chapter_gap + 34 + frame.height + 16
        blocks.append((entry, frame))
        previous = entry["chapter"]
    canvas = Image.new("RGB", (width, total), "#0b0f14")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 16), "CH01–CH05 continuity · phone-width", fill="#e8edf2", font=CHAPTER_FONT)
    y, previous = 56, None
    for entry, frame in blocks:
        if entry["chapter"] != previous:
            draw.rectangle((0, y, width, y + 40), fill="#182635")
            draw.text((margin, y + 12), f"{entry['chapter']} · {'full chapter anchors' if entry['chapter'] == 'CH05' else 'scene fragment'}", fill="#8fd3ff", font=CHAPTER_FONT)
            y += 52
        draw.text((margin, y + 7), f"{entry['panel_id']} · {','.join(entry['visible_adult_cast']) or 'object/set'}", fill="#c9d2dc", font=LABEL_FONT)
        y += 34
        canvas.paste(frame, ((width - frame.width) // 2, y))
        y += frame.height + 16
        previous = entry["chapter"]
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False, compress_level=9)


def artifact(kind: str, path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
    return {"kind": kind, "path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "width_px": width, "height_px": height, "bytes": path.stat().st_size}


def main() -> int:
    entries = rows()
    contact = OUTPUT_DIR / "cross-chapter-comic-regression-contact-sheet.png"
    phone = OUTPUT_DIR / "cross-chapter-comic-regression-phone-scroll.png"
    build_contact_sheet(entries, contact)
    build_phone_scroll(entries, phone)
    sources = [source_binding(value) for value in PLAN_SOURCES.values()]
    sources += [source_binding(value) for value in REVISION_SOURCES.values()]
    sources.append(source_binding(ASSEMBLY))
    document = {
        "record_type": "CrossChapterComicPanelPlanRegressionPacket",
        "schema_version": "1.0",
        "record_id": "ng-cross-chapter-comic-regression-r1",
        "state": "LOCAL_REVIEW_AID_MIXED_ACCEPTANCE_STATES",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "source_bindings": sources,
        "summary": {"chapters": 5, "scene_fragment_chapters": 4, "full_chapter_anchor_sets": 1, "panels": len(entries), "ch01_ch04_panels": 13, "ch05_anchors": 10, "historical_internal_research_selected": 7, "pending_owner_review": 16},
        "panels": entries,
        "artifacts": [artifact("chapter_row_contact_sheet", contact), artifact("phone_width_progression", phone)],
        "review_questions": [
            "Do Soren and Sigrid remain recognizable as the same fictional adults across chapter and renderer eras?",
            "Where do hair value, hair shape, face age, or role binding drift?",
            "Which wardrobe elements should become a stable kit before armor or weapon progression is introduced?",
            "Does CH05's clear-line watercolor/cel hybrid improve phone readability over the earlier evidence?",
            "Which earlier accepted scene qualities should survive future full-chapter style changes?",
        ],
        "boundary": {"new_generation": 0, "provider_calls": 0, "uploads": 0, "source_acceptance_states_modified": 0, "canon_or_panel_plans_created": 0, "commercial_clearance_decisions": 0},
        "limitations": [
            "CH01-CH04 are scene fragments, not complete chapters.",
            "The contact sheet compares mixed renderer eras and mixed review states; it is diagnostic, not a fairness-controlled renderer benchmark.",
            "Visual comparison is non-biometric and must not be represented as identity inference.",
            "CH05 anchors are selected for story/continuity coverage and do not replace review of the complete 50-panel scroll.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"report": REPORT.relative_to(ROOT).as_posix(), "sha256": sha256(REPORT), "panels": len(entries), "artifacts": document["artifacts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
