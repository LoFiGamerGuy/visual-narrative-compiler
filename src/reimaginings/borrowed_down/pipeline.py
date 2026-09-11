#!/usr/bin/env python3
"""Deterministic authoring, validation, raster assembly, and review pipeline for Borrowed Down."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
SLUG = "borrowed-down"
PROD = ROOT / "production" / "reimaginings" / SLUG
DOCS = ROOT / "docs" / "reimaginings" / SLUG
ART = ROOT / "experiments" / "reimaginings" / SLUG
SOURCE = PROD / "source"
CHAPTERS = [f"CH{i:02d}" for i in range(1, 11)]
CELLS = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]
ROLES = ["establish", "intent", "constraint", "action", "consequence"]

CHARACTERS = {
    "mae": "Mae Nox, fictional adult woman age 41, tall and broad-shouldered, dark brown skin, one blunt black wedge braid to shoulder blades, ochre work coat, teal rope harness, heavy split-toe boots, practical mature proportions",
    "dax": "Dax Pell, fictional adult man age 38, lean, copper-brown skin, silver-black asymmetrical curl crest leaning left, narrow moustache, coral half-cape, charcoal wrap trousers, yellow barometer gauntlet, practical mature proportions",
    "orra": "Orra Venn, fictional adult woman age 56, compact, shaved head, white triangular mantle over black load armor, brass plumb-staff, practical mature proportions",
    "tavi": "Tavi Rusk, fictional adult age 47, round powerful silhouette, indigo head wrap, sleeveless boiler apron over practical clothes, mature proportions",
    "eshe": "Eshe Pell, fictional adult woman age 44, copper-brown skin, horizontal black bob, long angular slate archive coat with yellow seam marks, mature proportions",
}

STYLE = (
    "pressure-print comic: bold woodcut-like dry-brush black edges, flat imperfect off-register "
    "oxidized teal, warning coral and acid-yellow risograph inks on warm fibrous paper; angular "
    "adult proportions, large readable hands, graphic negative-space force paths, simplified "
    "backgrounds except for functional machinery, one dominant value break per cell"
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def source_chapters() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(SOURCE.glob("ch*-sequences.json")):
        rows.extend(load(path)["chapters"])
    return sorted(rows, key=lambda x: x["id"])


def chapter_palette(chapter: str) -> str:
    n = int(chapter[2:])
    if n <= 2:
        return "soot black, oxidized teal, warning coral, warm paper"
    if n <= 4:
        return "deep teal and coral with acid yellow only for charged saltglass and clues"
    if n <= 6:
        return "coral-dominant danger, black structure, wider warm-paper silence"
    if n <= 8:
        return "indigo-teal drowned spaces, coral bodies, multiplying acid-yellow load lines"
    if n == 9:
        return "near-black civic interior, coral alarms, rare acid-yellow cords"
    return "soot black, teal, coral and acid yellow interlocked against bright dawn paper"


def panel_summary(seq: dict[str, Any], index: int) -> str:
    if index == 0:
        return f"Establish {seq['setting']}; show {', '.join(seq['cast'])}; make geography and current load direction obvious."
    if index == 1:
        return f"Intent: {seq['objective']}; show the responsible adult initiating a concrete step."
    if index == 2:
        return f"Constraint becomes physical and visible: {seq['constraint']}."
    if index == 3:
        return f"Causal action: {seq['action']}; show footing, contact, rope or mechanism tension, and force direction."
    return f"Consequence and remaining state: {seq['consequence']}; nothing resets between cells."


def compile_prompt(chapter: dict[str, Any], seq: dict[str, Any], accumulated: list[str]) -> str:
    visible = [CHARACTERS[c] for c in seq["cast"] if c in CHARACTERS]
    adult_groups = [c for c in seq["cast"] if c not in CHARACTERS and (c.startswith("fictional_adult") or "adult" in c.lower() or "guard" in c.lower() or "citizen" in c.lower() or "worker" in c.lower() or "rigger" in c.lower())]
    visible.extend(f"a group of fictional adults: {c}" for c in adult_groups)
    nonhuman = [c for c in seq["cast"] if c not in CHARACTERS and c not in adult_groups]
    panels = "\n".join(f"Cell {i + 1}: {panel_summary(seq, i)}" for i in range(5))
    lettering_clearance = "; ".join(
        f"cell {i + 1} reserve normalized rectangle {item['safe_zone']} as low-detail negative space"
        for i, item in enumerate(seq["lettering"])
    )
    return f"""Use case: illustration-story
Asset type: five selected comic panels in one deterministic sequence sheet for {chapter['id']} {seq['id']}
Primary request: Create a text-free 3-by-2 comic grid. The first five cells are the chronological story sequence below. The sixth cell is a quiet environment-only aftermath motif, never a duplicate character panel.
Scene/backdrop: {seq['setting']} in Veyr, a gravity-rationed city built beside a continent-high vertical ocean.
Characters: {'; '.join(visible) if visible else 'fictional adults with mature proportions as required by the scene'}.
Non-human subjects: {', '.join(nonhuman) if nonhuman else 'none'}.
Style/medium: {STYLE}.
Color palette: {chapter_palette(chapter['id'])}.
Composition/framing: exact clean 3-column by 2-row grid with strong black gutters; one readable moment per cell; varied camera distance; phone-readable silhouettes; the first five cells must read left-to-right top row then left-to-right bottom row.
Chronological cells:
{panels}
Irreversible state already in force: {', '.join(accumulated) if accumulated else 'none'}.
New state that must visibly persist after this sequence: {', '.join(seq['irreversible_state'])}.
Lettering clearance: {lettering_clearance}.
Constraints: all humans are explicitly fictional adults with unambiguously mature proportions and practical non-sexualized clothing; exact named-character hair, silhouette, wardrobe damage, injuries and equipment persist; coherent anatomy; readable hands; visible physical cause and effect; no spontaneous healing; no extra people unless the cell explicitly calls for a fictional-adult crowd; no glamor posing.
Avoid: any text, letters, numbers, labels, captions, speech balloons, sound-effect text, logos, signatures, watermarks, floating UI, children, child-coded features, young-looking adults, sexual content, gratuitous gore, real-person likeness, third-party characters, named-artist imitation, glossy 3D, soft clear-line watercolor."""


def compile_all() -> dict[str, Any]:
    chapters = source_chapters()
    contract = load(PROD / "continuity-contract.json")
    if [c["id"] for c in chapters] != CHAPTERS:
        raise ValueError("source chapters must be exactly CH01-CH10")
    accumulated: list[str] = []
    all_panels = 0
    all_sequences = 0
    continuity_nodes: list[dict[str, Any]] = []
    for chapter in chapters:
        cid = chapter["id"]
        out = PROD / "chapters" / cid.lower()
        plans: list[dict[str, Any]] = []
        prompts: list[dict[str, Any]] = []
        letters: list[dict[str, Any]] = []
        before = list(accumulated)
        for sidx, seq in enumerate(chapter["sequences"], 1):
            prompt = compile_prompt(chapter, seq, accumulated)
            prompts.append({
                "sequence_id": seq["id"], "target_panel_ids": [f"{seq['id']}-P{i:02d}" for i in range(1, 6)],
                "prompt": prompt, "prompt_sha256": sha_text(prompt),
                "reference_roles": ["pressure_print_style_anchor", "mae_dax_character_anchor"],
            })
            for pidx in range(5):
                pid = f"{seq['id']}-P{pidx + 1:02d}"
                x, y = CELLS[pidx]
                lettering = seq["lettering"][pidx]
                plan = {
                    "record_type": "ComicPanelPlan", "schema_version": "BorrowedDownComicPanelPlan/1.0",
                    "panel_id": pid, "chapter": cid, "sequence": seq["id"], "order": sidx * 5 - 4 + pidx,
                    "panel_role": ROLES[pidx], "density": ["T3", "T1", "T2", "T2", "T1"][pidx],
                    "summary": panel_summary(seq, pidx), "cast": seq["cast"],
                    "force_before": seq["constraint"] if pidx >= 2 else "chapter and sequence opening state",
                    "force_action": seq["action"] if pidx == 3 else panel_summary(seq, pidx),
                    "force_after": seq["consequence"] if pidx == 4 else "advances within contiguous sequence",
                    "irreversible_state": seq["irreversible_state"] if pidx == 4 else [],
                    "safe_zones": [lettering["safe_zone"]],
                    "lettering": {**lettering, "speaker_metadata_review_only": True, "tail_endpoint": [0.5, 0.56] if lettering["speaker"] else None},
                    "sequence_sheet": {"grid": [3, 2], "cell": [x, y], "crop_normalized": [x / 3, y / 2, (x + 1) / 3, (y + 1) / 2]},
                    "animation_shot_plan": None, "e_conte": None,
                }
                plans.append(plan)
                letters.append({"panel_id": pid, **plan["lettering"], "safe_zone": lettering["safe_zone"]})
            accumulated.extend(x for x in seq["irreversible_state"] if x not in accumulated)
            continuity_nodes.append({"sequence": seq["id"], "requires": list(before), "adds": seq["irreversible_state"], "consequence": seq["consequence"]})
            before = list(accumulated)
        dump(out / "comic-panel-plans.json", {"chapter": cid, "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None, "panels": plans})
        dump(out / "prompt-manifest.json", {"chapter": cid, "prompts": prompts})
        dump(out / "lettering-copy.json", {"chapter": cid, "entries": letters})
        dump(out / "story-state.json", {"chapter": cid, "opening_condition": chapter["opening_condition"], "objective": chapter["objective"], "state_before": before[: max(0, len(before) - sum(len(s["irreversible_state"]) for s in chapter["sequences"]))], "state_after": list(accumulated), "closing_turn": chapter["closing_turn"]})
        dump(out / "chapter-manifest.json", {"chapter": cid, "title": chapter["title"], "sequence_count": 6, "panel_count": 30, "selected_panel_target": 30, "short_chapter_rationale": "Six five-panel causal sequences prioritize complete chronological breadth and phone readability.", "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None})
        all_panels += len(plans)
        all_sequences += len(prompts)
    dump(PROD / "continuity-graph.json", {"record_type": "CrossChapterContinuityGraph", "nodes": continuity_nodes, "terminal_state": accumulated})
    summary = {"chapters": len(chapters), "sequences": all_sequences, "selected_panels": all_panels, "lettering_entries": all_panels, "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None}
    dump(PROD / "volume-manifest.json", summary)
    return summary


def validate_all(write_report: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    panel_ids: set[str] = set()
    total_panels = total_sequences = total_letters = 0
    for cid in CHAPTERS:
        out = PROD / "chapters" / cid.lower()
        try:
            plans = load(out / "comic-panel-plans.json")
            prompts = load(out / "prompt-manifest.json")
            letters = load(out / "lettering-copy.json")
            manifest = load(out / "chapter-manifest.json")
        except Exception as exc:
            errors.append(f"{cid}: missing or invalid compiled records: {exc}")
            continue
        if plans.get("animation_shot_plan") is not None or plans.get("e_conte") is not None:
            errors.append(f"{cid}: forbidden animation planning structure")
        if len(plans["panels"]) != 30 or len(prompts["prompts"]) != 6 or len(letters["entries"]) != 30:
            errors.append(f"{cid}: expected 30 panels, 6 prompts, 30 letters")
        for p in plans["panels"]:
            if p["panel_id"] in panel_ids:
                errors.append(f"duplicate panel id {p['panel_id']}")
            panel_ids.add(p["panel_id"])
            for z in p["safe_zones"]:
                if len(z) != 4 or not (0 <= z[0] < z[2] <= 1 and 0 <= z[1] < z[3] <= 1):
                    errors.append(f"{p['panel_id']}: bad [left,top,right,bottom] safe zone {z}")
            if p["lettering"]["kind"] == "silence" and p["lettering"]["text"]:
                errors.append(f"{p['panel_id']}: silence contains text")
            if p["lettering"]["kind"] != "silence" and len(p["lettering"]["text"].split()) > 24:
                errors.append(f"{p['panel_id']}: lettering exceeds 24 words")
        for prompt in prompts["prompts"]:
            if sha_text(prompt["prompt"]) != prompt["prompt_sha256"]:
                errors.append(f"{prompt['sequence_id']}: prompt hash mismatch")
            low = prompt["prompt"].lower()
            for forbidden in ["real person likeness", "final dialogue in pixels"]:
                if forbidden in low:
                    warnings.append(f"{prompt['sequence_id']}: inspect phrase {forbidden}")
        total_panels += len(plans["panels"])
        total_sequences += len(prompts["prompts"])
        total_letters += len(letters["entries"])
        if manifest["planning_structure"] != "ComicPanelPlan":
            errors.append(f"{cid}: wrong planning structure")
    if total_panels != 300 or total_sequences != 60 or total_letters != 300:
        errors.append(f"volume counts {total_panels}/{total_sequences}/{total_letters}, expected 300/60/300")
    result = {"status": "PASS" if not errors else "FAIL", "chapters": 10, "sequences": total_sequences, "panels": total_panels, "lettering_entries": total_letters, "errors": errors, "warnings": warnings}
    if write_report:
        dump(PROD / "validation-report.json", result)
    if errors:
        raise ValueError(json.dumps(result, indent=2))
    return result


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "arialbd.ttf" if bold else "arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= width or not line:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def extract_sequence(chapter: str, sequence: str, source: Path, elapsed: float, review: str) -> dict[str, Any]:
    chapter = chapter.upper()
    prompts = load(PROD / "chapters" / chapter.lower() / "prompt-manifest.json")["prompts"]
    prompt = next(p for p in prompts if p["sequence_id"] == sequence)
    image = Image.open(source).convert("RGB")
    w, h = image.size
    out_dir = ART / "chapters" / chapter.lower()
    seq_dir = out_dir / "sequence-sheets"
    panel_dir = out_dir / "panels"
    seq_dir.mkdir(parents=True, exist_ok=True)
    panel_dir.mkdir(parents=True, exist_ok=True)
    target_sheet = seq_dir / f"{sequence.lower()}.png"
    if source.resolve() != target_sheet.resolve():
        shutil.copy2(source, target_sheet)
    candidates = []
    crop_records = []
    for index, (cx, cy) in enumerate(CELLS, 1):
        left = round(cx * w / 3) + 8
        top = round(cy * h / 2) + 8
        right = round((cx + 1) * w / 3) - 8
        bottom = round((cy + 1) * h / 2) - 8
        crop = image.crop((left, top, right, bottom))
        pid = f"{sequence}-P{index:02d}"
        path = panel_dir / f"{pid.lower()}.png"
        crop.save(path, optimize=False, compress_level=9)
        candidates.append({"panel_id": pid, "file": path.relative_to(ROOT).as_posix(), "sha256": sha_file(path)})
        crop_records.append({"panel_id": pid, "crop_coordinates": [left, top, right, bottom], "crop_method": "deterministic 3x2 equal-cell crop with 8px inward trim"})
    record = {
        "record_type": "RenderRecord", "schema_version": "BorrowedDownRenderRecord/1.0",
        "product": "OpenAI built-in ImageGen in Codex", "tool": "image_gen", "target_chapter": chapter,
        "sequence": sequence, "target_panel_ids": prompt["target_panel_ids"], "exact_prompt": prompt["prompt"],
        "prompt_sha256": prompt["prompt_sha256"], "input_references": reference_inputs(),
        "output_file": target_sheet.relative_to(ROOT).as_posix(), "output_sha256": sha_file(target_sheet),
        "dimensions": [w, h], "elapsed_seconds": elapsed,
        "model": None, "model_snapshot": None, "endpoint": None, "provider_request_id": None,
        "usage": None, "monetary_cost_usd": None, "deterministic_seed": None,
        "crop_method": "3x2 equal cells, first five selected", "crop_coordinates": crop_records,
        "candidate_files": candidates, "agent_review_status": review,
        "failure_classes": [] if review == "PASS" else ["manual_visual_review_required"],
        "human_review_state": "owner_review_pending", "human_review_minutes": None,
        "acceptance_state": "unaccepted", "commercial_clearance_state": "commercially_uncleared",
        "exact_production_base_state": "not_an_exact_production_base", "reproducibility_state": "non_reproducible_unless_proven",
    }
    dump(PROD / "render-records" / chapter.lower() / f"{sequence.lower()}.json", record)
    return record


def reference_inputs() -> list[dict[str, Any]]:
    registry_path = PROD / "reference-registry.json"
    if not registry_path.exists():
        return []
    return [{"id": x["id"], "file": x["file"], "sha256": x["sha256"]} for x in load(registry_path)["references"] if x.get("active")]


def letter_panel(image: Image.Image, entry: dict[str, Any], width: int = 960) -> Image.Image:
    art = ImageOps.contain(image.convert("RGB"), (width, width), method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, art.height + 132), (244, 226, 184))
    canvas.paste(art, ((width - art.width) // 2, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, art.height, width, art.height + 132), fill=(244, 226, 184))
    draw.line((0, art.height, width, art.height), fill=(17, 18, 17), width=5)
    if entry["kind"] == "silence":
        draw.line((width // 2 - 28, art.height + 65, width // 2 + 28, art.height + 65), fill=(197, 72, 64), width=4)
        return canvas
    label = entry["speaker"].upper() if entry.get("speaker") else entry["kind"].upper()
    lf = font(19, True)
    tf = font(30 if entry["kind"] != "sfx" else 40, True)
    draw.text((28, art.height + 16), label, font=lf, fill=(197, 72, 64))
    lines = wrap(draw, entry["text"], tf, width - 230)
    y = art.height + 42
    for line in lines[:2]:
        draw.text((28, y), line, font=tf, fill=(17, 18, 17))
        y += 38
    return canvas


def assemble_chapter(chapter: str) -> dict[str, Any]:
    chapter = chapter.upper()
    plans = load(PROD / "chapters" / chapter.lower() / "comic-panel-plans.json")["panels"]
    letters = {x["panel_id"]: x for x in load(PROD / "chapters" / chapter.lower() / "lettering-copy.json")["entries"]}
    title = load(PROD / "chapters" / chapter.lower() / "chapter-manifest.json")["title"]
    base = ART / "chapters" / chapter.lower()
    panel_dir = base / "panels"
    missing = [p["panel_id"] for p in plans if not (panel_dir / f"{p['panel_id'].lower()}.png").exists()]
    if missing:
        raise FileNotFoundError(f"{chapter}: missing {len(missing)} panels: {missing[:5]}")
    review = base / "review"
    lettered = base / "lettered-panels"
    review.mkdir(parents=True, exist_ok=True)
    lettered.mkdir(parents=True, exist_ok=True)
    clean_images: list[Image.Image] = []
    lettered_images: list[Image.Image] = []
    safe_images: list[Image.Image] = []
    for p in plans:
        im = Image.open(panel_dir / f"{p['panel_id'].lower()}.png").convert("RGB")
        clean_images.append(im.copy())
        lp = letter_panel(im, letters[p["panel_id"]])
        lp_path = lettered / f"{p['panel_id'].lower()}.png"
        lp.save(lp_path, compress_level=9)
        lettered_images.append(lp)
        overlay = im.copy()
        d = ImageDraw.Draw(overlay, "RGBA")
        for z in p["safe_zones"]:
            x1, y1, x2, y2 = int(z[0]*im.width), int(z[1]*im.height), int(z[2]*im.width), int(z[3]*im.height)
            d.rectangle((x1,y1,x2,y2), fill=(230,210,45,50), outline=(230,210,45,255), width=4)
        safe_images.append(overlay)
    header_h = 180
    total_h = header_h + sum(x.height + 20 for x in lettered_images)
    scroll = Image.new("RGB", (960, total_h), (17, 18, 17))
    d = ImageDraw.Draw(scroll)
    d.text((32, 24), "BORROWED DOWN", font=font(34, True), fill=(244,226,184))
    d.text((32, 72), f"{chapter} — {title}", font=font(44, True), fill=(63,143,151))
    d.text((32, 132), "Owner-review draft • generated art unaccepted and commercially uncleared", font=font(20), fill=(197,72,64))
    y = header_h
    for im in lettered_images:
        scroll.paste(im, (0, y)); y += im.height + 20
    scroll_path = base / f"{chapter.lower()}-reading-draft.png"
    scroll.save(scroll_path, compress_level=9)
    phone = scroll.resize((390, round(scroll.height * 390 / 960)), Image.Resampling.LANCZOS)
    phone_path = base / f"{chapter.lower()}-phone-preview.png"
    phone.save(phone_path, compress_level=9)
    contact = make_contact(clean_images, 5, 6, 240, title=f"{chapter} CLEAN CONTACT — 30 PANELS")
    contact_path = review / f"{chapter.lower()}-contact-sheet.png"; contact.save(contact_path, compress_level=9)
    safe = make_contact(safe_images, 5, 6, 240, title=f"{chapter} SAFE ZONES [L,T,R,B]")
    safe_path = review / f"{chapter.lower()}-safe-zone-review.png"; safe.save(safe_path, compress_level=9)
    compact = make_contact(lettered_images, 5, 6, 240, title=f"{chapter} COMPACT LETTERED REVIEW")
    compact_path = review / f"{chapter.lower()}-compact-lettered-review.png"; compact.save(compact_path, compress_level=9)
    artifacts = [scroll_path, phone_path, contact_path, safe_path, compact_path]
    result = {"chapter": chapter, "panels": 30, "sequences": 6, "artifacts": [{"file": p.relative_to(ROOT).as_posix(), "sha256": sha_file(p), "dimensions": list(Image.open(p).size)} for p in artifacts]}
    dump(PROD / "reviews" / f"{chapter.lower()}-assembly.json", result)
    return result


def make_contact(images: list[Image.Image], cols: int, rows: int, cell: int, title: str) -> Image.Image:
    gap, top = 12, 72
    out = Image.new("RGB", (cols * cell + (cols + 1) * gap, top + rows * cell + (rows + 1) * gap), (17, 18, 17))
    d = ImageDraw.Draw(out); d.text((gap, 16), title, font=font(30, True), fill=(244,226,184))
    for i, image in enumerate(images):
        thumb = ImageOps.fit(image.convert("RGB"), (cell, cell), method=Image.Resampling.LANCZOS)
        x = gap + (i % cols) * (cell + gap); y = top + gap + (i // cols) * (cell + gap)
        out.paste(thumb, (x, y))
        d.rectangle((x, y, x + cell - 1, y + cell - 1), outline=(63,143,151), width=2)
    return out


def volume_hub() -> dict[str, Any]:
    rows = []
    for cid in CHAPTERS:
        assembly_path = PROD / "reviews" / f"{cid.lower()}-assembly.json"
        if not assembly_path.exists():
            raise FileNotFoundError(assembly_path)
        rows.append(load(assembly_path))
    index = ART / "START-HERE.html"
    source = {c["id"]: c for c in source_chapters()}
    cards = []
    for row in rows:
        cid = row["chapter"]; base = f"chapters/{cid.lower()}"; chapter = source[cid]
        sequence_links = " · ".join(f"<a href='{base}/sequence-sheets/{cid.lower()}-s{i:02d}.png'>S{i:02d}</a>" for i in range(1,7))
        cards.append(f"<article><h2>{cid}: {chapter['title']}</h2><p><b>Objective:</b> {chapter['objective']}<br><b>Closing turn:</b> {chapter['closing_turn']}</p><p><a href='{base}/{cid.lower()}-reading-draft.png'>Reading draft</a> · <a href='{base}/{cid.lower()}-phone-preview.png'>Phone preview</a> · <a href='{base}/review/{cid.lower()}-compact-lettered-review.png'>Compact lettered review</a> · <a href='{base}/review/{cid.lower()}-contact-sheet.png'>Contact sheet</a> · <a href='{base}/review/{cid.lower()}-safe-zone-review.png'>Safe-zone review</a></p><p>Sequence sheets: {sequence_links}</p></article>")
    html = """<!doctype html><meta charset='utf-8'><title>Borrowed Down — Volume I</title><style>body{font:18px system-ui;background:#111;color:#f4e2b8;max-width:980px;margin:auto;padding:32px;line-height:1.5}a{color:#55bbc5}article{border-top:2px solid #c54840;padding:12px}small{color:#aaa}.callout{background:#1d2929;padding:16px;border-left:6px solid #e2cf37}</style><h1>Borrowed Down</h1><p class='callout'>Beside a vertical ocean, two adult workers discover that their city’s gravity is a debt someone else has been forced to carry.</p><p><b>Visual direction:</b> pressure-print woodcut × three-ink risograph.</p><p><a href='references/mae-dax-character-anchor.png'>Principal character sheet</a> · <a href='style-probes/pressure-print.png'>Selected visual anchor</a> · <a href='../../../reimaginings/borrowed-down/story-bible.md'>Story/progression bible</a> · <a href='../../../reimaginings/borrowed-down/visual-bible.md'>Visual bible</a> · <a href='ten-chapter-progression.html'>Ten-chapter progression hub</a> · <a href='strongest-panels.html'>Strongest panels</a> · <a href='targeted-repair-decisions.html'>Targeted-repair decisions</a></p><p><small>All generated candidates are owner-review-pending, unaccepted, commercially uncleared, and non-reproducible unless proven otherwise. Direct paid/cloud spend: $0. Built-in product usage/cost fields unavailable.</small></p>""" + "".join(cards)
    index.parent.mkdir(parents=True, exist_ok=True); index.write_text(html, encoding="utf-8")
    progression = ART / "ten-chapter-progression.html"
    progression.write_text(html.replace("<h1>Borrowed Down</h1>", "<h1>Borrowed Down — Ten-Chapter Progression Hub</h1>"), encoding="utf-8")
    strongest_dir = ART / "strongest"; strongest_dir.mkdir(parents=True, exist_ok=True)
    strongest_links = []
    for cid in CHAPTERS:
        for sid, pid in [(4,4),(6,5)]:
            src = ART / "chapters" / cid.lower() / "panels" / f"{cid.lower()}-s{sid:02d}-p{pid:02d}.png"
            dst = strongest_dir / f"{cid.lower()}-s{sid:02d}-p{pid:02d}.png"
            shutil.copy2(src, dst)
            strongest_links.append(f"<figure><img src='strongest/{dst.name}' style='max-width:440px'><figcaption>{cid} S{sid:02d} P{pid:02d}</figcaption></figure>")
    strongest = ART / "strongest-panels.html"
    strongest.write_text("<!doctype html><meta charset='utf-8'><style>body{background:#111;color:#f4e2b8;font:18px system-ui}figure{display:inline-block}img{border:3px solid #55bbc5}</style><h1>Borrowed Down — strongest causal and turning panels</h1>"+"".join(strongest_links), encoding="utf-8")
    repair = ART / "targeted-repair-decisions.html"
    repair.write_text("<!doctype html><meta charset='utf-8'><style>body{background:#111;color:#f4e2b8;font:18px system-ui;max-width:900px;margin:auto;line-height:1.5}a{color:#55bbc5}li{margin:.7em}</style><h1>Targeted repair decisions</h1><p>No chapter-wide rerender was permitted. Story-readable WARN sequences remain preserved as diagnostic evidence. Only story-blocking or continuity-blocking units were repaired; every non-target selected-panel hash had to remain exact.</p><ol><li><b>CH08-S01 — spent-knot continuity:</b> replaced the full five-panel sequence so Tavi visibly returns Dax's gauntlet and the spent breath cord is used only as an inert drain pull. <a href='../../../production/reimaginings/borrowed-down/repairs/ch08-s01-r2/comparison.json'>Hash comparison</a>.</li><li><b>CH10-S04-P05 — keelback anatomy:</b> replaced only the bottom-middle selected panel, removing the toothed reptilian predator anatomy in favor of the established smooth crescent-bodied adult keelback. The other 299 selected panels remained byte-identical. <a href='../../../production/reimaginings/borrowed-down/repairs/ch10-s04-p05-r2/comparison.json'>Hash comparison</a>.</li></ol><p>Both failed originals remain archived under diagnostics. Replacements remain owner-review-pending, unaccepted, commercially uncleared, and non-reproducible unless proven otherwise.</p>", encoding="utf-8")
    result = {"chapters": 10, "panels": 300, "start_page": index.relative_to(ROOT).as_posix(), "progression_hub": progression.relative_to(ROOT).as_posix(), "sha256": {"start_page": sha_file(index), "progression_hub": sha_file(progression)}}
    dump(PROD / "reviews" / "volume-review-index.json", result)
    return result


def reconcile() -> dict[str, Any]:
    errors: list[str] = []
    sequence_records: list[dict[str, Any]] = []
    for cid in CHAPTERS:
        for i in range(1,7):
            path = PROD / "render-records" / cid.lower() / f"{cid.lower()}-s{i:02d}.json"
            if not path.exists():
                errors.append(f"missing {path.relative_to(ROOT)}")
                continue
            record = load(path); sequence_records.append(record)
            if sha_text(record["exact_prompt"]) != record["prompt_sha256"]:
                errors.append(f"{record['sequence']}: prompt hash mismatch")
            out = ROOT / record["output_file"]
            if not out.exists() or sha_file(out) != record["output_sha256"]:
                errors.append(f"{record['sequence']}: output hash mismatch or absent")
            for candidate in record["candidate_files"]:
                cp = ROOT / candidate["file"]
                if not cp.exists() or sha_file(cp) != candidate["sha256"]:
                    errors.append(f"{candidate['panel_id']}: crop hash mismatch or absent")
            for key in ["model","model_snapshot","endpoint","provider_request_id","usage","monetary_cost_usd","deterministic_seed"]:
                if record[key] is not None:
                    errors.append(f"{record['sequence']}: unavailable field {key} is not null")
            if record["acceptance_state"] != "unaccepted" or record["commercial_clearance_state"] != "commercially_uncleared":
                errors.append(f"{record['sequence']}: premature promotion")
    registry = load(PROD / "reference-registry.json")
    for ref in registry["references"]:
        path = ROOT / ref["file"]
        if not path.exists() or sha_file(path) != ref["sha256"]:
            errors.append(f"reference {ref['id']}: hash mismatch or absent")
    repair_records: list[dict[str, Any]] = []
    ch10_repair_path = PROD / "render-records" / "repairs" / "ch10-s04-p05-r2.json"
    if ch10_repair_path.exists():
        repair = load(ch10_repair_path); repair_records.append(repair)
        if sha_text(repair["exact_prompt"]) != repair["prompt_sha256"]:
            errors.append("CH10-S04-P05-r2: prompt hash mismatch")
        out = ROOT / repair["output_file"]
        if not out.exists() or sha_file(out) != repair["output_sha256"]:
            errors.append("CH10-S04-P05-r2: edited output hash mismatch or absent")
        for candidate in repair["candidate_files"]:
            cp = ROOT / candidate["file"]
            if not cp.exists() or sha_file(cp) != candidate["sha256"]:
                errors.append("CH10-S04-P05-r2: repaired panel hash mismatch or absent")
        composite = repair["canonical_composite_sheet"]
        composite_path = ROOT / composite["file"]
        if not composite_path.exists() or sha_file(composite_path) != composite["sha256"]:
            errors.append("CH10-S04-P05-r2: canonical composite hash mismatch or absent")
        for key in ["model","model_snapshot","endpoint","provider_request_id","usage","monetary_cost_usd","deterministic_seed"]:
            if repair[key] is not None:
                errors.append(f"CH10-S04-P05-r2: unavailable field {key} is not null")
    active_statuses = []
    for record in sequence_records:
        if record["sequence"] == "CH10-S04" and repair_records:
            active_statuses.append(repair_records[0]["agent_review_status"])
        else:
            active_statuses.append(record["agent_review_status"])
    statuses = {x: sum(status == x for status in active_statuses) for x in ["PASS","WARN","FAIL"]}
    ref_counts: dict[str,int] = {}
    for record in sequence_records:
        for ref in record["input_references"]:
            ref_counts[ref["id"]] = ref_counts.get(ref["id"],0)+1
    for record in repair_records:
        for ref in record["input_references"]:
            ref_counts[ref["id"]] = ref_counts.get(ref["id"],0)+1
    style_records = load(PROD / "style-probe-render-records.json")["records"]
    character_record = load(PROD / "render-records" / "references" / "mae-dax-character-anchor.json")
    sequence_seconds = sum(r["elapsed_seconds"] for r in sequence_records)
    diagnostic_records = []
    ch08_r1 = PROD / "diagnostics" / "ch08-s01-r1-spent-knot-fail" / "ch08-s01-r1-render-record.json"
    if ch08_r1.exists(): diagnostic_records.append(load(ch08_r1))
    repair_seconds = sum(r["elapsed_seconds"] for r in repair_records)
    diagnostic_seconds = sum(r["elapsed_seconds"] for r in diagnostic_records)
    total_seconds = sequence_seconds + repair_seconds + diagnostic_seconds + sum(r["elapsed_seconds"] for r in style_records) + character_record["elapsed_seconds"]
    tracked_pixels = subprocess.check_output(["git","ls-files","experiments"],cwd=ROOT,text=True).splitlines()
    if tracked_pixels:
        errors.append(f"generated pixels tracked: {tracked_pixels[:3]}")
    result = {
        "status":"PASS" if not errors else "FAIL", "errors":errors, "chapters":10,
        "active_sequences":len(sequence_records), "sequence_generation_requests":len(sequence_records)+len(repair_records)+len(diagnostic_records), "style_generation_requests":len(style_records),
        "reference_generation_requests":1, "total_generation_requests":len(sequence_records)+len(repair_records)+len(diagnostic_records)+len(style_records)+1,
        "selected_panels":sum(len(r["candidate_files"]) for r in sequence_records),
        "sequence_statuses":statuses, "preserved_diagnostic_failures":len(diagnostic_records)+(1 if repair_records else 0), "reference_use_counts":ref_counts,
        "sequence_elapsed_seconds_sum":round(sequence_seconds+repair_seconds+diagnostic_seconds,3), "all_generation_elapsed_seconds_sum":round(total_seconds,3),
        "direct_paid_cloud_spend_usd":0, "provider_cost_metadata":"unavailable/null",
        "provider_model_metadata":"unavailable/null", "deterministic_seed":"unavailable/null",
        "tracked_generated_pixels":len(tracked_pixels), "owner_review_state":"pending",
        "commercial_clearance":"uncleared", "reproducibility":"not established"
    }
    dump(PROD / "output-reconciliation.json", result)
    dump(PROD / "cost-and-timing-summary.json", {k:v for k,v in result.items() if "seconds" in k or "spend" in k or "provider" in k or k in ["total_generation_requests"]})
    if errors:
        raise ValueError(json.dumps(result,indent=2))
    return result


def owner_start() -> dict[str, Any]:
    reconciliation = load(PROD / "output-reconciliation.json")
    integrity = load(PROD / "integrity-report.json") if (PROD / "integrity-report.json").exists() else {}
    source = source_chapters()
    abs_art = ART.as_posix()
    lines = ["# Borrowed Down — owner start", "", "Beside a vertical ocean, two adult workers discover that their city’s gravity is a debt someone else has been forced to carry.", "", "## Start here", "", f"- [Interactive ten-chapter review hub]({abs_art}/START-HERE.html)", f"- [Ten-chapter progression hub]({abs_art}/ten-chapter-progression.html)", f"- [Principal fictional-adult character sheet]({abs_art}/references/mae-dax-character-anchor.png)", f"- [Strongest panels]({abs_art}/strongest-panels.html)", f"- [Targeted-repair decisions]({abs_art}/targeted-repair-decisions.html)", "- [Story and progression bible](../../../reimaginings/borrowed-down/story-bible.md)", "- [Visual/production bible](../../../reimaginings/borrowed-down/visual-bible.md)", "- [Premise and style ADR](adr/ADR-R001-premise-and-style-selection.md)", "", "## Chapters", ""]
    for chapter in source:
        cid=chapter["id"]; base=f"{abs_art}/chapters/{cid.lower()}"
        lines += [f"- **{cid}: {chapter['title']}** — [reading draft]({base}/{cid.lower()}-reading-draft.png), [phone preview]({base}/{cid.lower()}-phone-preview.png), [compact lettered review]({base}/review/{cid.lower()}-compact-lettered-review.png), [contact sheet]({base}/review/{cid.lower()}-contact-sheet.png), [safe zones]({base}/review/{cid.lower()}-safe-zone-review.png)"]
    lines += ["", "## Production evidence", "", f"- Chapters / active sequences / selected panels: 10 / {reconciliation['active_sequences']} / {reconciliation['selected_panels']}", f"- Active sequence PASS / WARN / FAIL: {reconciliation['sequence_statuses']['PASS']} / {reconciliation['sequence_statuses']['WARN']} / {reconciliation['sequence_statuses']['FAIL']}", f"- Preserved failed diagnostics: {reconciliation['preserved_diagnostic_failures']}", f"- Generation requests including repairs, style, and reference work: {reconciliation['total_generation_requests']}", f"- Summed measured generation latency: {reconciliation['all_generation_elapsed_seconds_sum']} seconds (overlapping agent calls are summed, not wall-clock duration)", f"- Active/reference input uses recorded: {reconciliation['reference_use_counts']}", "- Direct paid/cloud spend: $0; built-in ImageGen cost/usage metadata unavailable and recorded as null.", "- Generated candidates remain owner-review-pending, unaccepted, commercially uncleared, and non-reproducible unless proven otherwise.", f"- Isolated branch: `{integrity.get('isolated_branch','pending final audit')}`", f"- Protected refs unchanged: `{integrity.get('protected_refs_unchanged','pending final audit')}`", "", "## Remaining owner decisions", "", "1. Visual acceptance per sequence and principal reference sheet.", "2. Commercial/license review; no clearance is inferred.", "3. Whether retained WARN sequences merit future targeted repair after complete-volume reading."]
    path=DOCS / "START_HERE.md"; path.write_text("\n".join(lines)+"\n",encoding="utf-8")
    return {"file":path.relative_to(ROOT).as_posix(),"sha256":sha_file(path)}


def prepare_ch08_s01_repair() -> dict[str, Any]:
    chapter, sequence = "CH08", "CH08-S01"
    diag_prod = PROD / "diagnostics" / "ch08-s01-r1-spent-knot-fail"
    diag_art = ART / "diagnostics" / "ch08-s01-r1-spent-knot-fail"
    diag_prod.mkdir(parents=True, exist_ok=True); diag_art.mkdir(parents=True, exist_ok=True)
    plans_path = PROD / "chapters" / "ch08" / "comic-panel-plans.json"
    prompts_path = PROD / "chapters" / "ch08" / "prompt-manifest.json"
    state_path = PROD / "chapters" / "ch08" / "story-state.json"
    record_path = PROD / "render-records" / "ch08" / "ch08-s01.json"
    for src in [plans_path, prompts_path, state_path, record_path]:
        if src.exists(): shutil.copy2(src, diag_prod / src.name)
    old_record = load(record_path)
    old_record["agent_review_status"] = "FAIL"
    old_record["failure_classes"] = ["irreversible_state_violation_reused_spent_breath_knot"]
    dump(diag_prod / "ch08-s01-r1-render-record.json", old_record)
    old_sheet = ART / "chapters" / "ch08" / "sequence-sheets" / "ch08-s01.png"
    if old_sheet.exists(): shutil.copy2(old_sheet, diag_art / "ch08-s01-r1.png")
    for i in range(1,6):
        old_panel = ART / "chapters" / "ch08" / "panels" / f"ch08-s01-p{i:02d}.png"
        if old_panel.exists(): shutil.copy2(old_panel, diag_art / old_panel.name)
    snapshot = []
    for cid in CHAPTERS:
        for path in sorted((ART / "chapters" / cid.lower() / "panels").glob("*.png")):
            if not path.name.startswith("ch08-s01-"):
                snapshot.append({"file":path.relative_to(ROOT).as_posix(),"sha256":sha_file(path)})
    dump(diag_prod / "non-target-panel-hashes-before.json", {"count":len(snapshot),"files":snapshot})
    source = next(c for c in source_chapters() if c["id"] == chapter)
    seq = source["sequences"][0]
    accumulated = load(PROD / "chapters" / "ch07" / "story-state.json")["state_after"]
    prompt = compile_prompt(source, seq, accumulated)
    prompt = prompt.replace(CHARACTERS["dax"], "Dax Pell, fictional adult man age 38, lean, copper-brown skin, silver-black asymmetrical curl crest leaning left, narrow moustache, torn short coral collar wrap with its long cape tail permanently absent, charcoal wrap trousers, two yellow witness cords, yellow barometer gauntlet just returned by Tavi, practical mature proportions")
    prompt_manifest = load(prompts_path)
    target = next(x for x in prompt_manifest["prompts"] if x["sequence_id"] == sequence)
    target["prompt"] = prompt; target["prompt_sha256"] = sha_text(prompt)
    dump(prompts_path, prompt_manifest)
    dump(PROD / "repairs" / "ch08-s01-r2" / "prompt-record.json", target)
    plans = load(plans_path)
    for pidx, plan in enumerate([p for p in plans["panels"] if p["sequence"] == sequence]):
        plan["summary"] = panel_summary(seq, pidx)
        plan["force_before"] = seq["constraint"] if pidx >= 2 else "chapter and sequence opening state"
        plan["force_action"] = seq["action"] if pidx == 3 else panel_summary(seq, pidx)
        plan["force_after"] = seq["consequence"] if pidx == 4 else "advances within contiguous sequence"
        plan["irreversible_state"] = seq["irreversible_state"] if pidx == 4 else []
    dump(plans_path, plans)
    state = load(state_path)
    state["state_after"] = ["Dax's spent breath-knot remains unusable and its snapped cord is discarded." if x == "Dax's breath-knot is spent and frayed." else x for x in state["state_after"]]
    dump(state_path, state)
    return {"repair":"CH08-S01-r2","prompt_sha256":sha_text(prompt),"diagnostic_record":str((diag_prod / "ch08-s01-r1-render-record.json").relative_to(ROOT)),"non_target_snapshot_count":len(snapshot)}


def verify_ch08_s01_repair() -> dict[str, Any]:
    before = load(PROD / "diagnostics" / "ch08-s01-r1-spent-knot-fail" / "non-target-panel-hashes-before.json")
    changed = []
    for item in before["files"]:
        path = ROOT / item["file"]
        if not path.exists() or sha_file(path) != item["sha256"]:
            changed.append(item["file"])
    old_record = load(PROD / "diagnostics" / "ch08-s01-r1-spent-knot-fail" / "ch08-s01-r1-render-record.json")
    new_record = load(PROD / "render-records" / "ch08" / "ch08-s01.json")
    result = {"status":"PASS" if not changed else "FAIL","repair":"CH08-S01-r2","preserved_non_target_hashes":before["count"]-len(changed),"expected_non_target_hashes":before["count"],"changed_non_targets":changed,"old_output_sha256":old_record["output_sha256"],"new_output_sha256":new_record["output_sha256"],"old_failure_class":old_record["failure_classes"]}
    dump(PROD / "repairs" / "ch08-s01-r2" / "comparison.json", result)
    if changed: raise ValueError(json.dumps(result,indent=2))
    return result


def prepare_ch10_s04_p05_repair() -> dict[str, Any]:
    sequence = "CH10-S04"
    diag_prod = PROD / "diagnostics" / "ch10-s04-r1-creature-fail"
    diag_art = ART / "diagnostics" / "ch10-s04-r1-creature-fail"
    repair_prod = PROD / "repairs" / "ch10-s04-p05-r2"
    diag_prod.mkdir(parents=True, exist_ok=True); diag_art.mkdir(parents=True, exist_ok=True); repair_prod.mkdir(parents=True, exist_ok=True)
    record_path = PROD / "render-records" / "ch10" / "ch10-s04.json"
    old_record = load(record_path)
    old_record["agent_review_status"] = "FAIL"
    old_record["failure_classes"] = ["keelback_anatomy_violation_toothed_reptilian_predator"]
    sheet = ART / "chapters" / "ch10" / "sequence-sheets" / "ch10-s04.png"
    archived_sheet = diag_art / "ch10-s04-r1.png"
    shutil.copy2(sheet, archived_sheet)
    archived_candidates = []
    for candidate in old_record["candidate_files"]:
        src = ROOT / candidate["file"]
        dst = diag_art / src.name
        shutil.copy2(src, dst)
        archived_candidates.append({**candidate, "file": dst.relative_to(ROOT).as_posix()})
    old_record["output_file"] = archived_sheet.relative_to(ROOT).as_posix()
    old_record["candidate_files"] = archived_candidates
    dump(diag_prod / "ch10-s04-r1-render-record.json", old_record)
    dump(record_path, old_record)
    snapshot = []
    for cid in CHAPTERS:
        for path in sorted((ART / "chapters" / cid.lower() / "panels").glob("*.png")):
            if path.name != "ch10-s04-p05.png":
                snapshot.append({"file":path.relative_to(ROOT).as_posix(),"sha256":sha_file(path)})
    dump(diag_prod / "non-target-panel-hashes-before.json", {"count":len(snapshot),"files":snapshot})
    registry_path = PROD / "reference-registry.json"
    registry = load(registry_path)
    registry["references"] = [x for x in registry["references"] if x["id"] != "ch10_s04_r1_edit_target"]
    registry["references"].append({
        "id":"ch10_s04_r1_edit_target", "file":archived_sheet.relative_to(ROOT).as_posix(), "sha256":sha_file(archived_sheet),
        "depicts":"fictional adults and an invented creature in a six-cell pressure-print comic sequence; bottom-middle cell contains the anatomy error targeted for repair",
        "inspection":"locally inspected at original resolution by agent on 2026-09-03; exact bottom-middle repair target verified",
        "eligibility":"eligible only as the edit target for Borrowed Down CH10-S04-P05 through OpenAI built-in ImageGen",
        "real_person_likeness":False, "children":False, "private_data":False, "third_party_art":False, "active":False,
        "owner_review_state":"pending", "commercial_clearance":"uncleared"
    })
    dump(registry_path, registry)
    prompt = """Edit only the bottom-middle cell (cell 5) of this existing 3-by-2 comic sequence sheet. Replace the toothed reptilian dragon-like creature with the established fictional adult keelback mother: a whale-sized black crescent body, broad smooth pressure-shaped silhouette, oxidized-teal coral rib vents, small navigation fins, and a chain visibly parting as she pulls free. She has no visible teeth, no reptilian snout, no predatory eyes, no jaws, and no hostile pose. Preserve the causal beat: synchronized release transfers stored fall into the voluntary rope web while the central anchor begins tearing apart. Preserve cells 1, 2, 3, 4, and 6 as closely as possible; preserve the exact grid, black gutters, pressure-print woodcut and three-ink risograph style, warm fibrous paper, adult characters, machinery, palette, and text-free layout. All people are fictional adults with mature proportions and practical non-sexualized clothing. Do not add text, letters, numbers, captions, logos, signatures, watermarks, children, real-person likenesses, gore, or third-party characters. The first reference is the exact edit target and composition source. The second reference is only the canonical appearance anchor for fictional adults Mae Nox and Dax Pell; do not copy its layout."""
    prompt_record = {
        "repair":"CH10-S04-P05-r2", "exact_prompt":prompt, "prompt_sha256":sha_text(prompt),
        "input_references":[
            {"id":"ch10_s04_r1_edit_target","file":archived_sheet.relative_to(ROOT).as_posix(),"sha256":sha_file(archived_sheet)},
            {"id":"mae_dax_character_anchor","file":"experiments/reimaginings/borrowed-down/references/mae-dax-character-anchor.png","sha256":sha_file(ART / "references" / "mae-dax-character-anchor.png")}
        ],
        "scope":"bottom-middle cell only; canonical selection replacement limited to CH10-S04-P05"
    }
    dump(repair_prod / "prompt-record.json", prompt_record)
    return {"repair":"CH10-S04-P05-r2","prompt_sha256":prompt_record["prompt_sha256"],"edit_target":archived_sheet.relative_to(ROOT).as_posix(),"non_target_snapshot_count":len(snapshot),"exact_prompt":prompt}


def apply_ch10_s04_p05_repair(source: Path, elapsed: float) -> dict[str, Any]:
    repair_prod = PROD / "repairs" / "ch10-s04-p05-r2"
    diag_art = ART / "diagnostics" / "ch10-s04-r1-creature-fail"
    repair_art = ART / "repairs" / "ch10-s04-p05-r2"
    repair_art.mkdir(parents=True, exist_ok=True)
    edited = repair_art / "ch10-s04-r2-imagegen-edit.png"
    shutil.copy2(source, edited)
    old_sheet = Image.open(diag_art / "ch10-s04-r1.png").convert("RGB")
    edit_image = Image.open(edited).convert("RGB")
    if edit_image.size != old_sheet.size:
        edit_image = edit_image.resize(old_sheet.size, Image.Resampling.LANCZOS)
    w, h = old_sheet.size; cell_w, cell_h = w // 3, h // 2
    full_box = (cell_w, cell_h, cell_w * 2, cell_h * 2)
    crop_box = (cell_w + 8, cell_h + 8, cell_w * 2 - 8, cell_h * 2 - 8)
    canonical_sheet = old_sheet.copy(); canonical_sheet.paste(edit_image.crop(full_box), (cell_w, cell_h))
    sheet_path = ART / "chapters" / "ch10" / "sequence-sheets" / "ch10-s04.png"
    canonical_sheet.save(sheet_path, compress_level=9)
    panel_path = ART / "chapters" / "ch10" / "panels" / "ch10-s04-p05.png"
    edit_image.crop(crop_box).save(panel_path, compress_level=9)
    prompt_record = load(repair_prod / "prompt-record.json")
    record = {
        "record_type":"TargetedPanelRepairRenderRecord", "schema_version":"BorrowedDownRenderRecord/1.0",
        "product":"OpenAI built-in ImageGen in Codex", "tool":"image_gen", "target_chapter":"CH10", "sequence":"CH10-S04", "target_panel_ids":["CH10-S04-P05"],
        "exact_prompt":prompt_record["exact_prompt"], "prompt_sha256":prompt_record["prompt_sha256"], "input_references":prompt_record["input_references"],
        "output_file":edited.relative_to(ROOT).as_posix(), "output_sha256":sha_file(edited), "dimensions":list(Image.open(edited).size), "elapsed_seconds":elapsed,
        "model":None, "model_snapshot":None, "endpoint":None, "provider_request_id":None, "usage":None, "monetary_cost_usd":None, "deterministic_seed":None,
        "crop_method":"bottom-middle equal cell from ImageGen edit, 8px inward trim; only repaired selected panel promoted",
        "crop_coordinates":[{"panel_id":"CH10-S04-P05","crop_coordinates":list(crop_box),"crop_method":"bottom-middle cell with 8px inward trim"}],
        "candidate_files":[{"panel_id":"CH10-S04-P05","file":panel_path.relative_to(ROOT).as_posix(),"sha256":sha_file(panel_path)}],
        "canonical_composite_sheet":{"file":sheet_path.relative_to(ROOT).as_posix(),"sha256":sha_file(sheet_path),"preserved_cells":[1,2,3,4,6]},
        "agent_review_status":"PASS", "failure_classes":[], "human_review_state":"owner_review_pending", "human_review_minutes":None,
        "acceptance_state":"unaccepted", "commercial_clearance_state":"commercially_uncleared", "exact_production_base_state":"not_an_exact_production_base", "reproducibility_state":"non_reproducible_unless_proven"
    }
    render_path = PROD / "render-records" / "repairs" / "ch10-s04-p05-r2.json"
    dump(render_path, record)
    return {"repair":"CH10-S04-P05-r2","render_record":render_path.relative_to(ROOT).as_posix(),"repaired_panel_sha256":sha_file(panel_path),"canonical_sheet_sha256":sha_file(sheet_path)}


def verify_ch10_s04_p05_repair() -> dict[str, Any]:
    diag_prod = PROD / "diagnostics" / "ch10-s04-r1-creature-fail"
    before = load(diag_prod / "non-target-panel-hashes-before.json")
    changed = []
    for item in before["files"]:
        path = ROOT / item["file"]
        if not path.exists() or sha_file(path) != item["sha256"]:
            changed.append(item["file"])
    old_record = load(diag_prod / "ch10-s04-r1-render-record.json")
    repair = load(PROD / "render-records" / "repairs" / "ch10-s04-p05-r2.json")
    old_panel = next(x for x in old_record["candidate_files"] if x["panel_id"] == "CH10-S04-P05")
    new_panel = repair["candidate_files"][0]
    result = {"status":"PASS" if not changed and old_panel["sha256"] != new_panel["sha256"] else "FAIL", "repair":"CH10-S04-P05-r2", "preserved_non_target_hashes":before["count"]-len(changed), "expected_non_target_hashes":before["count"], "changed_non_targets":changed, "old_target_sha256":old_panel["sha256"], "new_target_sha256":new_panel["sha256"], "old_failure_class":old_record["failure_classes"]}
    dump(PROD / "repairs" / "ch10-s04-p05-r2" / "comparison.json", result)
    if result["status"] != "PASS": raise ValueError(json.dumps(result,indent=2))
    return result


def git_integrity() -> dict[str, Any]:
    def run(args: list[str], cwd: Path) -> str:
        return subprocess.check_output(args, cwd=cwd, text=True).strip()
    original = Path(r"C:\AgentWorkspaces\anime-pipeline")
    result = {
        "isolated_worktree": str(ROOT), "isolated_branch": run(["git","branch","--show-current"], ROOT),
        "isolated_head": run(["git","rev-parse","HEAD"], ROOT),
        "original_worktree": str(original), "original_branch": run(["git","branch","--show-current"], original),
        "original_head": run(["git","rev-parse","HEAD"], original),
        "main": run(["git","rev-parse","main"], original), "origin_main": run(["git","rev-parse","origin/main"], original),
        "protected_baseline": "40e7940016ea3c3966752b61f55a931f91a13ac7",
        "original_status_porcelain": run(["git","status","--porcelain"], original).splitlines(),
    }
    result["protected_refs_unchanged"] = result["original_head"] == result["main"] == result["origin_main"] == result["protected_baseline"]
    dump(PROD / "integrity-report.json", result)
    return result


def set_review(chapter: str, status: str, sequences: list[str], failure: str | None) -> dict[str, Any]:
    chapter = chapter.upper()
    targets = sequences or [f"{chapter}-S{i:02d}" for i in range(1, 7)]
    changed = []
    for sequence in targets:
        path = PROD / "render-records" / chapter.lower() / f"{sequence.lower()}.json"
        record = load(path)
        record["agent_review_status"] = status
        record["failure_classes"] = [] if status == "PASS" else [failure or "manual_visual_review_required"]
        dump(path, record)
        changed.append(sequence)
    return {"chapter": chapter, "status": status, "sequences": changed, "failure_class": failure}


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("compile")
    sub.add_parser("validate")
    ingest = sub.add_parser("ingest")
    ingest.add_argument("--chapter", required=True); ingest.add_argument("--sequence", required=True); ingest.add_argument("--source", type=Path, required=True); ingest.add_argument("--elapsed", type=float, required=True); ingest.add_argument("--review", choices=["PASS","WARN","FAIL"], default="WARN")
    assemble = sub.add_parser("assemble"); assemble.add_argument("--chapter", required=True)
    review = sub.add_parser("review"); review.add_argument("--chapter", required=True); review.add_argument("--status", required=True, choices=["PASS","WARN","FAIL"]); review.add_argument("--sequence", action="append", default=[]); review.add_argument("--failure")
    sub.add_parser("hub"); sub.add_parser("integrity"); sub.add_parser("reconcile"); sub.add_parser("owner-start")
    sub.add_parser("prepare-ch08-s01-repair"); sub.add_parser("verify-ch08-s01-repair")
    sub.add_parser("prepare-ch10-s04-p05-repair")
    repair = sub.add_parser("apply-ch10-s04-p05-repair"); repair.add_argument("--source", type=Path, required=True); repair.add_argument("--elapsed", type=float, required=True)
    sub.add_parser("verify-ch10-s04-p05-repair")
    args = parser.parse_args()
    if args.command == "compile": result = compile_all()
    elif args.command == "validate": result = validate_all()
    elif args.command == "ingest": result = extract_sequence(args.chapter, args.sequence, args.source, args.elapsed, args.review)
    elif args.command == "assemble": result = assemble_chapter(args.chapter)
    elif args.command == "review": result = set_review(args.chapter, args.status, args.sequence, args.failure)
    elif args.command == "hub": result = volume_hub()
    elif args.command == "integrity": result = git_integrity()
    elif args.command == "reconcile": result = reconcile()
    elif args.command == "owner-start": result = owner_start()
    elif args.command == "prepare-ch08-s01-repair": result = prepare_ch08_s01_repair()
    elif args.command == "verify-ch08-s01-repair": result = verify_ch08_s01_repair()
    elif args.command == "prepare-ch10-s04-p05-repair": result = prepare_ch10_s04_p05_repair()
    elif args.command == "apply-ch10-s04-p05-repair": result = apply_ch10_s04_p05_repair(args.source, args.elapsed)
    else: result = verify_ch10_s04_p05_repair()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
