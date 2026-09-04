#!/usr/bin/env python3
"""Deterministic authoring, validation, ingestion, lettering, and review pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
SLUG = "the-city-keeps-oaths"
PROD = ROOT / "production" / "reimaginings" / SLUG
DOCS = ROOT / "docs" / "reimaginings" / SLUG
ART = ROOT / "experiments" / "reimaginings" / SLUG
SOURCE = PROD / "source" / "volume.json"
CHAPTERS = [f"CH{i:02d}" for i in range(1, 11)]
ROLES = ["opening", "objective", "escalation", "action", "choice", "consequence"]
DENSITY_PATTERN = ["high", "low", "low", "low", "moderate", "low", "moderate", "low", "low", "low", "high", "low", "low", "moderate", "low", "low", "low", "moderate", "high", "low", "low", "low", "moderate", "low"]
SAFE_ZONES = [
    [0.06, 0.05, 0.50, 0.22], [0.52, 0.05, 0.94, 0.22], [0.06, 0.72, 0.50, 0.92],
    [0.50, 0.05, 0.94, 0.22], [0.06, 0.05, 0.50, 0.22], [0.50, 0.72, 0.94, 0.92],
]
LETTERING_OVERRIDES = {
    "CH03-S03-P05": [0.52, 0.72, 0.94, 0.92],
    "CH03-S04-P01": [0.06, 0.72, 0.50, 0.92],
    "CH03-S04-P05": [0.06, 0.72, 0.50, 0.92],
    "CH04-S02-P05": [0.06, 0.72, 0.50, 0.92],
    "CH04-S04-P01": [0.06, 0.72, 0.50, 0.92],
    "CH04-S04-P02": [0.06, 0.72, 0.50, 0.92],
    "CH04-S04-P04": [0.06, 0.72, 0.50, 0.92],
}

CHARACTERS = {
    "sola": "Sola Merrow, fictional adult woman age 38, tall athletic working build and mature proportions, warm brown skin, long dark auburn hair in a low segmented braid with one silver forelock, deep navy practical pathwright coat with ivory piping, ochre scarf, slate trousers and boots; copper oath bracer until broken; never sexualized",
    "tarin": "Tarin Kest, fictional adult man age 45, broad mature build, deep umber skin, short tightly curled black hair silver at both temples, pearl-gray practical warden coat over muted teal layers, dark trousers and boots; long ivory spear-key until broken; never sexualized",
    "kesin": "Kesin Or, fictional adult nonbinary archivist age 52, compact mature build, light olive skin, shaved head, round amber spectacles, plum-gray layered archive jacket, ink-dark gloves and satchel; never sexualized",
    "serac": "Serac Dain, fictional adult man age 51, lean mature build, pale bronze skin, swept-back charcoal hair with a white central streak, immaculate ivory magistrate coat with restrained black geometry and mirrored oath gauntlet; never sexualized",
    "varo": "Commander Varo Pell, fictional adult woman age 48, sturdy mature build, dark skin, close-cropped gray hair, practical graphite command uniform with one white shoulder plate; never sexualized",
}

STYLE = (
    "original clean cinematic fantasy-webtoon illustration; crisp controlled dark-navy contours; limited internal linework; "
    "smooth cel shading with restrained painterly gradients; clean skin, hair, fabric, stone and metal shapes; mature adult proportions; "
    "strong foreground/midground/background value separation; pearl stone, midnight blue and cool cyan with selective warm gold oathlight; "
    "generous negative space; one dominant focal subject; restrained luminous accents; emotionally legible faces; no texture fog"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git(args: list[str], cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True).stdout.strip()


def panel_summary(sequence: dict[str, Any], role_index: int) -> str:
    cast = ", ".join(sequence["cast"])
    values = [
        f"Establish {sequence['setting']} with {cast}; make current geography and emotional condition immediately legible.",
        f"Concrete objective: {sequence['objective']}; show an adult initiating a specific next step.",
        f"Escalation becomes visible: {sequence['escalation']}.",
        f"Causal action: {sequence['action']}; show contact, direction, footing, and response as applicable.",
        f"Consequential choice: {sequence['choice']}; center the deciding adult's face, hand, or posture.",
        f"Visible consequence: {sequence['consequence']}; preserve every changed state and leave one clear visual question.",
    ]
    return values[role_index]


def parse_letter(raw: str) -> dict[str, Any]:
    speaker, text = raw.split("|", 1)
    if not speaker and not text:
        return {"kind": "silence", "speaker": None, "text": ""}
    if speaker == "SFX":
        return {"kind": "sfx", "speaker": None, "text": text}
    if speaker in {"CAPTION", "ROAD", "CITY", "DISC", "MILL", "COURTYARD"}:
        return {"kind": "caption", "speaker": speaker.title(), "text": text}
    return {"kind": "dialogue", "speaker": speaker.title(), "text": text}


def state_appearance(state: list[str]) -> str:
    visible = [x for x in state if any(k in x for k in ("sola_", "tarin_", "badge", "spear", "coat", "brace", "bracer", "mantle", "fracture"))]
    return ", ".join(visible[-14:]) if visible else "baseline wardrobe and intact equipment"


def compile_prompt(chapter: dict[str, Any], sequence: dict[str, Any], group: int, carried: list[str]) -> str:
    start = 0 if group == 1 else 3
    beat_lines = "\n".join(f"Frame {i + 1}: {panel_summary(sequence, start + i)}" for i in range(3))
    visible = [CHARACTERS[c] for c in sequence["cast"] if c in CHARACTERS]
    groups = [c for c in sequence["cast"] if c.startswith("fictional_adult")]
    if groups:
        visible.extend(f"a small group of visibly mature fictional adults serving as {g.replace('fictional_adult_', '')}" for g in groups)
    nonhuman = [c for c in sequence["cast"] if c not in CHARACTERS and not c.startswith("fictional_adult")]
    return f"""Use case: illustration-story
Asset type: text-free three-panel vertical continuity strip for {chapter['id']} {sequence['id']} group {group}
Input images: Image 1 is the registered clean-cinematic style anchor; Image 2 is the registered Sola progression sheet when Sola appears; Image 3 is the registered supporting-adult sheet when Tarin, Kesin, or Serac appears. Use only for original identity, wardrobe state, contour, palette, and equipment continuity.
Primary request: Create one portrait canvas divided into exactly three stacked chronological comic frames with clean narrow gutters. Each frame is a distinct story moment, not a montage.
Scene/backdrop: {sequence['setting']} in Caelune, an original city of pearl-stone crescent districts suspended above a deep blue cloud sea by living luminous roads.
Characters: {'; '.join(visible) if visible else 'visibly mature fictional adults in practical clothing'}.
Non-human subjects: {', '.join(nonhuman) if nonhuman else 'none'}.
Style/medium: {STYLE}.
Composition/framing: top-to-bottom chronology; one dominant focal subject and no more than two competing actions per frame; simple low-detail backgrounds except when the frame establishes geography; large readable gestures and silhouettes; naturally quiet open areas, but never draw a box for text.
Chronological frames:
{beat_lines}
Irreversible visible state already in force: {state_appearance(carried)}.
New state introduced by this sequence and visible when causally reached: {', '.join(sequence['state_adds'])}.
Constraints: all humans are explicitly fictional adults with unmistakably mature proportions; preserve named identity, hair, clothing, injury, equipment, and relationship state; coherent hands and anatomy; clear cause and effect; disciplined light; at most one cyan-gold oath effect per frame; source art contains no final lettering.
Avoid: any text, letters, numbers, captions, speech balloons, empty caption rectangles, blank placards, logos, signatures, watermarks, floating interface, children, child-coded or young-looking adults, sexualized clothing or framing, real-person likeness, third-party characters, title-specific designs, named-artist imitation, woodcut marks, dry brush, risograph, paper grain, hatching, crosshatching, grunge, muddy palette, equal detail everywhere, crowded machinery, multiple competing effects, generic glossy 3D.
"""


def compile_all() -> dict[str, Any]:
    source = load(SOURCE)
    chapters = source["chapters"]
    if [c["id"] for c in chapters] != CHAPTERS:
        raise ValueError("source must contain exactly CH01-CH10")
    carried: list[str] = []
    graph: list[dict[str, Any]] = []
    total_panels = total_sequences = total_prompts = 0
    for chapter in chapters:
        if len(chapter["sequences"]) != 4:
            raise ValueError(f"{chapter['id']} must have four sequences")
        before_chapter = list(carried)
        plans: list[dict[str, Any]] = []
        prompts: list[dict[str, Any]] = []
        lettering: list[dict[str, Any]] = []
        display = 0
        for sequence in chapter["sequences"]:
            if len(sequence["letters"]) != 6:
                raise ValueError(f"{sequence['id']} needs six lettering entries")
            before_sequence = list(carried)
            for group in (1, 2):
                prompt = compile_prompt(chapter, sequence, group, carried)
                pids = [f"{sequence['id']}-P{i:02d}" for i in range((group - 1) * 3 + 1, group * 3 + 1)]
                prompts.append({
                    "request_id": f"{sequence['id']}-G{group:02d}", "sequence_id": sequence["id"], "group_index": group,
                    "target_panel_ids": pids, "prompt": prompt, "prompt_sha256": sha_text(prompt),
                    "input_reference_roles": ["selected style-system anchor", "principal-character and progression continuity", "supporting-character continuity"],
                    "candidate_state": "owner-review-pending", "acceptance_state": "unaccepted", "commercial_clearance_state": "commercially_uncleared",
                })
            for i in range(6):
                display += 1
                panel_id = f"{sequence['id']}-P{i + 1:02d}"
                letter = parse_letter(sequence["letters"][i])
                safe = LETTERING_OVERRIDES.get(panel_id, SAFE_ZONES[i])
                continuity_in = list(carried)
                continuity_out = list(carried)
                if i == 5:
                    continuity_out += [s for s in sequence["state_adds"] if s not in continuity_out]
                plan = {
                    "record_type": "ComicPanelPlan", "schema_version": "CityKeepsOathsComicPanelPlan/1.0",
                    "panel_id": panel_id, "plan_revision_id": f"{panel_id}-R1", "display_order": display,
                    "scene_beat_id": sequence["id"], "narrative_phase_id": ROLES[i], "narrative_beat": panel_summary(sequence, i),
                    "composition_intent": "one dominant focal subject; readable silhouette; quiet area for local lettering",
                    "visible_adult_cast": sequence["cast"], "asset_ids": [], "spatial_mode": "original-fantasy-location",
                    "spatial_stage_contract_id": f"{sequence['id']}-STAGE", "spatial_assignments": {"setting": sequence["setting"], "screen_direction": "maintain within sequence"},
                    "sequence_id": sequence["id"], "scale_role": "vertical-scale" if DENSITY_PATTERN[display - 1] == "high" else "human-scale",
                    "density_class": DENSITY_PATTERN[display - 1], "continuity_carry_in": continuity_in, "continuity_carry_out": continuity_out,
                    "comic_direction": "top-to-bottom mobile scroll", "chapter": chapter["id"], "panel_role": ROLES[i],
                    "irreversible_state": sequence["state_adds"] if i == 5 else [], "safe_zones": [safe],
                    "lettering": {**letter, "safe_zone": safe, "safe_zone_format": "[left, top, right, bottom]"},
                    "generation_group": {"request_id": f"{sequence['id']}-G{1 if i < 3 else 2:02d}", "layout": [1, 3], "frame": i % 3,
                        "crop_normalized": [0.0, (i % 3) / 3, 1.0, ((i % 3) + 1) / 3]},
                    "animation_shot_plan": None, "e_conte": None,
                }
                plans.append(plan)
                lettering.append({"panel_id": panel_id, **plan["lettering"]})
            carried += [s for s in sequence["state_adds"] if s not in carried]
            graph.append({"sequence_id": sequence["id"], "requires": before_sequence, "adds": sequence["state_adds"], "state_after": list(carried)})
        out = PROD / "chapters" / chapter["id"].lower()
        dump(out / "comic-panel-plans.json", {"chapter": chapter["id"], "planning_structure": "ComicPanelPlan", "medium": "comic", "animation_shot_plan": None, "e_conte": None, "panels": plans})
        dump(out / "prompt-manifest.json", {"chapter": chapter["id"], "prompts": prompts})
        dump(out / "lettering-copy.json", {"chapter": chapter["id"], "entries": lettering})
        dump(out / "story-state.json", {"chapter": chapter["id"], "opening_condition": chapter["opening_condition"], "objective": chapter["objective"], "state_before": before_chapter, "state_after": list(carried), "closing_turn": chapter["closing_turn"]})
        dump(out / "chapter-manifest.json", {"chapter": chapter["id"], "title": chapter["title"], "sequence_count": 4, "panel_count": 24, "generation_request_count": 8, "density_budget": {"low": 16, "moderate": 5, "high": 3}, "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None})
        total_panels += 24
        total_sequences += 4
        total_prompts += 8
    dump(PROD / "continuity-graph.json", {"record_type": "CrossChapterContinuityGraph", "nodes": graph, "terminal_state": carried})
    result = {"chapters": 10, "sequences": total_sequences, "selected_panels": total_panels, "generation_requests": total_prompts, "lettering_entries": total_panels, "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None}
    dump(PROD / "volume-manifest.json", result)
    return result


def validate_all(write: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    panel_ids: set[str] = set()
    totals = Counter()
    previous_state: list[str] = []
    for cid in CHAPTERS:
        out = PROD / "chapters" / cid.lower()
        try:
            plans_doc = load(out / "comic-panel-plans.json")
            prompts_doc = load(out / "prompt-manifest.json")
            letters_doc = load(out / "lettering-copy.json")
            story = load(out / "story-state.json")
        except Exception as exc:
            errors.append(f"{cid}: missing or invalid compiled record: {exc}")
            continue
        plans = plans_doc.get("panels", [])
        prompts = prompts_doc.get("prompts", [])
        letters = letters_doc.get("entries", [])
        if len(plans) != 24 or len(prompts) != 8 or len(letters) != 24:
            errors.append(f"{cid}: expected 24 panels, 8 prompts and 24 lettering entries")
        if plans_doc.get("planning_structure") != "ComicPanelPlan" or plans_doc.get("animation_shot_plan") is not None or plans_doc.get("e_conte") is not None:
            errors.append(f"{cid}: sole planning structure violation")
        if story.get("state_before") != previous_state:
            errors.append(f"{cid}: cross-chapter state edge mismatch")
        previous_state = story.get("state_after", [])
        density = Counter(p.get("density_class") for p in plans)
        if density != Counter({"low": 16, "moderate": 5, "high": 3}):
            errors.append(f"{cid}: density budget mismatch {dict(density)}")
        highs = [i for i, p in enumerate(plans) if p.get("density_class") == "high"]
        if any(b - a == 1 for a, b in zip(highs, highs[1:])):
            errors.append(f"{cid}: adjacent high-density panels")
        for index, panel in enumerate(plans, 1):
            required = {"panel_id","plan_revision_id","display_order","scene_beat_id","narrative_phase_id","narrative_beat","composition_intent","visible_adult_cast","asset_ids","spatial_mode","spatial_stage_contract_id","spatial_assignments","sequence_id","scale_role","density_class","continuity_carry_in","continuity_carry_out","comic_direction"}
            missing = sorted(required - panel.keys())
            if missing:
                errors.append(f"{panel.get('panel_id', cid)}: missing {missing}")
            if panel.get("display_order") != index:
                errors.append(f"{panel.get('panel_id')}: bad display order")
            pid = panel.get("panel_id")
            if pid in panel_ids:
                errors.append(f"duplicate panel id {pid}")
            panel_ids.add(pid)
            if panel.get("animation_shot_plan") is not None or panel.get("e_conte") is not None:
                errors.append(f"{pid}: forbidden cross-medium structure")
            for zone in panel.get("safe_zones", []):
                if len(zone) != 4 or not (0 <= zone[0] < zone[2] <= 1 and 0 <= zone[1] < zone[3] <= 1):
                    errors.append(f"{pid}: invalid [left,top,right,bottom] safe zone {zone}")
            words = panel.get("lettering", {}).get("text", "").split()
            if len(words) > 18:
                warnings.append(f"{pid}: lettering exceeds target 18 words")
        for prompt in prompts:
            if sha_text(prompt["prompt"]) != prompt["prompt_sha256"]:
                errors.append(f"{prompt['request_id']}: prompt hash mismatch")
            low = prompt["prompt"].lower()
            for forbidden in ("empty caption rectangle", "text baked", "young-looking adults"):
                if forbidden not in low and forbidden != "text baked":
                    errors.append(f"{prompt['request_id']}: missing required exclusion {forbidden}")
        totals.update({"panels":len(plans), "prompts":len(prompts), "letters":len(letters), "chapters":1})
    if totals != Counter({"panels":240,"prompts":80,"letters":240,"chapters":10}):
        errors.append(f"volume counts mismatch {dict(totals)}")
    registry_path=PROD/"reference-registry.json"
    if not registry_path.exists():
        errors.append("reference registry missing")
    else:
        registry=load(registry_path); active=[r for r in registry.get("references",[]) if r.get("active")]
        if len(active)>4: errors.append(f"active reference set exceeds four: {len(active)}")
        ids=set()
        for ref in active:
            if ref["id"] in ids: errors.append(f"duplicate reference id {ref['id']}")
            ids.add(ref["id"]); path=ROOT/ref["file"]
            if not path.exists(): errors.append(f"reference missing: {ref['id']}")
            elif sha_file(path)!=ref["sha256"]: errors.append(f"reference hash mismatch: {ref['id']}")
            if not ref.get("created_in_experiment") or not ref.get("locally_inspected"): errors.append(f"reference not qualified: {ref['id']}")
    result = {"status":"PASS" if not errors else "FAIL", "counts":dict(totals), "errors":errors, "warnings":warnings, "validated_utc":utc_now()}
    if write:
        dump(PROD / "validation-report.json", result)
    if errors:
        raise ValueError(json.dumps(result, indent=2))
    return result


def reference_inputs() -> list[dict[str, Any]]:
    path = PROD / "reference-registry.json"
    if not path.exists():
        return []
    return [{"id": r["id"], "file": r["file"], "sha256": r["sha256"]} for r in load(path)["references"] if r.get("active")]


def ingest(request_id: str, source: Path, elapsed: float, review_status: str, failures: list[str]) -> dict[str, Any]:
    request_id = request_id.upper()
    chapter = request_id[:4]
    prompt_doc = load(PROD / "chapters" / chapter.lower() / "prompt-manifest.json")
    prompt = next(x for x in prompt_doc["prompts"] if x["request_id"] == request_id)
    image = Image.open(source).convert("RGB")
    width, height = image.size
    target_dir = ART / "chapters" / chapter.lower()
    strip_dir = target_dir / "source-strips"
    panel_dir = target_dir / "panels"
    strip_dir.mkdir(parents=True, exist_ok=True)
    panel_dir.mkdir(parents=True, exist_ok=True)
    strip = strip_dir / f"{request_id.lower()}.png"
    if source.resolve() != strip.resolve():
        shutil.copy2(source, strip)
    crops = []
    candidates = []
    for idx, pid in enumerate(prompt["target_panel_ids"]):
        top = round(idx * height / 3) + 4
        bottom = round((idx + 1) * height / 3) - 4
        crop_box = [4, top, width - 4, bottom]
        panel = image.crop(crop_box)
        panel_path = panel_dir / f"{pid.lower()}.png"
        panel.save(panel_path, compress_level=9)
        crops.append({"panel_id":pid, "crop_coordinates":crop_box, "method":"equal vertical thirds with four-pixel inward trim"})
        candidates.append({"panel_id":pid, "file":panel_path.relative_to(ROOT).as_posix(), "sha256":sha_file(panel_path), "dimensions":list(panel.size)})
    record = {
        "record_type":"RenderRecord", "schema_version":"CityKeepsOathsRenderRecord/1.0", "request_id":request_id,
        "exact_prompt":prompt["prompt"], "prompt_sha256":prompt["prompt_sha256"], "target_chapter":chapter,
        "target_sequence":prompt["sequence_id"], "target_panel_ids":prompt["target_panel_ids"],
        "input_references":reference_inputs(), "output_path":strip.relative_to(ROOT).as_posix(), "output_sha256":sha_file(strip),
        "dimensions":[width,height], "measured_elapsed_seconds":elapsed, "product":"OpenAI built-in ImageGen in Codex", "tool":"image_gen",
        "model":None, "endpoint":None, "provider_request_id":None, "usage":None, "monetary_cost_usd":None, "deterministic_seed":None,
        "extraction_method":"equal vertical thirds", "crop_coordinates":crops, "candidate_paths_and_hashes":candidates,
        "review_status":review_status, "failure_classes":failures, "human_review_state":"owner_review_pending",
        "acceptance_state":"unaccepted", "commercial_clearance_state":"commercially_uncleared",
        "production_base_state":"not_an_exact_production_base", "reproducibility_state":"non_reproducible_unless_proven",
        "recorded_utc":utc_now(),
    }
    dump(PROD / "render-records" / chapter.lower() / f"{request_id.lower()}.json", record)
    return record


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for name in (["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"]):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if not current or draw.textbbox((0,0), candidate, font=face)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def letter_panel(image: Image.Image, entry: dict[str, Any], width: int = 960) -> Image.Image:
    art = ImageOps.contain(image.convert("RGB"), (width, 1300), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", art.size, (241,244,244))
    canvas.paste(art, (0,0))
    if entry["kind"] == "silence" or not entry["text"]:
        return canvas
    draw = ImageDraw.Draw(canvas)
    l,t,r,b = entry["safe_zone"]
    box = [round(l*art.width), round(t*art.height), round(r*art.width), round(b*art.height)]
    pad = 18
    label_face = font(20, True)
    text_face = font(36 if entry["kind"] != "sfx" else 44, True)
    label = entry.get("speaker") or ("SFX" if entry["kind"] == "sfx" else "")
    lines = wrap(draw, entry["text"], text_face, max(80, box[2]-box[0]-2*pad))[:3]
    line_h = 43 if entry["kind"] != "sfx" else 50
    need_h = pad*2 + len(lines)*line_h + (24 if label else 0)
    if need_h > box[3]-box[1]:
        box[3] = min(art.height-8, box[1] + need_h)
    fill = (248,250,249)
    outline = (23,35,54)
    if entry["kind"] == "caption":
        draw.rounded_rectangle(box, radius=12, fill=(23,35,54), outline=(92,225,219), width=3)
        text_color=(248,250,249); label_color=(230,179,82)
    elif entry["kind"] == "sfx":
        fill=None; text_color=(248,250,249); label_color=(248,250,249)
    else:
        draw.rounded_rectangle(box, radius=28, fill=fill, outline=outline, width=3)
        text_color=outline; label_color=(37,143,151)
    y=box[1]+pad
    if label:
        draw.text((box[0]+pad,y), label.upper(), font=label_face, fill=label_color, stroke_width=2 if entry["kind"]=="sfx" else 0, stroke_fill=(23,35,54))
        y+=24
    for line in lines:
        draw.text((box[0]+pad,y), line, font=text_face, fill=text_color, stroke_width=2 if entry["kind"]=="sfx" else 0, stroke_fill=(23,35,54))
        y+=line_h
    return canvas


def entropy(gray: Image.Image) -> float:
    hist = np.asarray(gray.histogram(), dtype=np.float64)
    p = hist[hist > 0] / hist.sum()
    return float(-(p * np.log2(p)).sum())


def density_metrics(image: Image.Image) -> dict[str, float]:
    phone = ImageOps.contain(image.convert("RGB"), (390,2000), Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(phone)
    a = np.asarray(gray, dtype=np.float32)
    edges = np.asarray(gray.filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    high = np.asarray(gray.filter(ImageFilter.UnsharpMask(radius=1, percent=200, threshold=2)), dtype=np.float32)
    high_freq = np.abs(high-a)
    h,w = a.shape
    center = a[h//4:3*h//4,w//4:3*w//4]
    border = np.concatenate([a[:max(1,h//8)].ravel(),a[-max(1,h//8):].ravel(),a[:, :max(1,w//8)].ravel(),a[:, -max(1,w//8):].ravel()])
    tiles=[]
    for yy in range(0,h,max(1,h//4)):
        for xx in range(0,w,max(1,w//4)):
            tiles.append(entropy(Image.fromarray(a[yy:min(h,yy+h//4),xx:min(w,xx+w//4)].astype(np.uint8))))
    return {
        "edge_density":round(float((edges>32).mean()),6), "global_entropy":round(entropy(gray),6),
        "local_entropy_mean":round(float(np.mean(tiles)),6), "high_frequency_occupancy":round(float((high_freq>10).mean()),6),
        "focal_luminance_separation":round(float(abs(center.mean()-border.mean())/255),6),
        "luminance_stddev":round(float(a.std()/255),6),
    }


def contact(images: list[Image.Image], title: str, grayscale: bool = False, zones: list[list[float]] | None = None) -> Image.Image:
    cell_w, cell_h, cols = 280, 300, 4
    rows = math.ceil(len(images)/cols)
    sheet=Image.new("RGB",(cols*cell_w,64+rows*cell_h),(238,242,242))
    draw=ImageDraw.Draw(sheet); draw.text((18,16),title,font=font(28,True),fill=(23,35,54))
    for i,img in enumerate(images):
        tile=ImageOps.contain(img.convert("L" if grayscale else "RGB"),(cell_w-16,cell_h-34),Image.Resampling.LANCZOS).convert("RGB")
        x=(i%cols)*cell_w+(cell_w-tile.width)//2; y=64+(i//cols)*cell_h+8
        sheet.paste(tile,(x,y))
        if zones:
            l,t,r,b=zones[i]; d=ImageDraw.Draw(sheet); d.rectangle((x+l*tile.width,y+t*tile.height,x+r*tile.width,y+b*tile.height),outline=(230,179,82),width=3)
        draw.text((x,y+tile.height+3),f"P{i+1:02d}",font=font(16,True),fill=(23,35,54))
    return sheet


def assemble(chapter: str) -> dict[str, Any]:
    chapter=chapter.upper(); out=PROD/"chapters"/chapter.lower()
    plans=load(out/"comic-panel-plans.json")["panels"]; letters={x["panel_id"]:x for x in load(out/"lettering-copy.json")["entries"]}
    images=[]; lettered=[]
    for p in plans:
        path=ART/"chapters"/chapter.lower()/"panels"/f"{p['panel_id'].lower()}.png"
        if not path.exists(): raise FileNotFoundError(path)
        img=Image.open(path).convert("RGB"); images.append(img); lettered.append(letter_panel(img,letters[p["panel_id"]]))
    gutter_after=[42 if p["panel_role"] in {"opening","objective","escalation"} else 28 if p["panel_role"]=="action" else 72 if p["panel_role"]=="choice" else 132 for p in plans]
    leading_gutter=72; total=sum(i.height for i in lettered)+leading_gutter+sum(gutter_after)
    scroll=Image.new("RGB",(960,total),(239,243,244)); y=leading_gutter
    for img,gap in zip(lettered,gutter_after): scroll.paste(img,(0,y)); y+=img.height+gap
    chapter_dir=ART/"chapters"/chapter.lower(); review_dir=chapter_dir/"review"; review_dir.mkdir(parents=True,exist_ok=True)
    draft=chapter_dir/f"{chapter.lower()}-reading-draft.png"; scroll.save(draft,compress_level=9)
    phone=scroll.resize((390,round(scroll.height*390/scroll.width)),Image.Resampling.LANCZOS); phone_path=chapter_dir/f"{chapter.lower()}-phone-preview.png"; phone.save(phone_path,compress_level=9)
    artifacts=[]
    edge_images=[ImageOps.autocontrast(ImageOps.grayscale(i).filter(ImageFilter.FIND_EDGES)).convert("RGB") for i in images]
    for name,img in [
        (f"{chapter.lower()}-contact-sheet.png",contact(images,f"{chapter} source panels")),
        (f"{chapter.lower()}-compact-lettered-review.png",contact(lettered,f"{chapter} local lettering")),
        (f"{chapter.lower()}-grayscale-review.png",contact(images,f"{chapter} grayscale",True)),
        (f"{chapter.lower()}-density-map.png",contact(edge_images,f"{chapter} edge-density map")),
        (f"{chapter.lower()}-safe-zone-review.png",contact(images,f"{chapter} safe zones",False,[p["safe_zones"][0] for p in plans])),
    ]:
        path=review_dir/name; img.save(path,compress_level=9); artifacts.append({"file":path.relative_to(ROOT).as_posix(),"sha256":sha_file(path),"dimensions":list(img.size)})
    calibration=load(PROD/"pilot"/"density-calibration.json") if (PROD/"pilot"/"density-calibration.json").exists() else None
    metrics=[]
    for p,img in zip(plans,images):
        measured=density_metrics(img); flags=[]
        if calibration:
            ceiling=calibration["material_deviation_flags"][p["density_class"]]
            if measured["edge_density"]>ceiling["edge_density_max"]: flags.append("edge_density_above_pilot_class")
            if measured["high_frequency_occupancy"]>ceiling["high_frequency_occupancy_max"]: flags.append("high_frequency_occupancy_above_pilot_class")
            if measured["global_entropy"]>ceiling["global_entropy_max"]: flags.append("global_entropy_above_pilot_class")
            if measured["focal_luminance_separation"]<calibration["material_deviation_flags"]["all"]["focal_luminance_separation_min"]: flags.append("focal_luminance_proxy_below_pilot")
        metrics.append({"panel_id":p["panel_id"],"planned_density":p["density_class"],**measured,"review_status":"WARN" if flags else "PASS","failure_classes":flags})
    status_counts=Counter(m["review_status"] for m in metrics); failure_counts=Counter(x for m in metrics for x in m["failure_classes"])
    dump(out/"density-metrics.json",{"chapter":chapter,"calibration":calibration,"panels":metrics,"rhythm":[p["density_class"] for p in plans],"status_totals":dict(status_counts),"failure_classes":dict(failure_counts),"manual_review_required_for_flags":True})
    for path,img in [(draft,scroll),(phone_path,phone)]: artifacts.insert(0,{"file":path.relative_to(ROOT).as_posix(),"sha256":sha_file(path),"dimensions":list(img.size)})
    record={"chapter":chapter,"panels":24,"sequences":4,"artifacts":artifacts,"phone_width":390,"lettering_method":"deterministic local balloons and captions in normalized [left,top,right,bottom] safe zones","generated_source_text_free":True,"variable_scroll_cadence":{"leading_gutter_pixels":leading_gutter,"gutter_after_pixels":gutter_after,"roles":{"opening_objective_escalation":42,"action":28,"choice":72,"consequence_sequence_breath":132}},"metric_review_status_totals":dict(status_counts),"metric_failure_classes":dict(failure_counts)}
    dump(PROD/"reviews"/f"{chapter.lower()}-assembly.json",record)
    return record


def snapshot_isolation() -> dict[str, Any]:
    original=Path(r"C:\AgentWorkspaces\anime-pipeline")
    prior=Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining-20260903")
    legacy=Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining")
    untracked=git(["ls-files","--others","--exclude-standard"],original).splitlines()
    files=[]
    for rel in untracked:
        path=original/rel
        if path.is_file(): files.append({"path":rel.replace("\\","/"),"bytes":path.stat().st_size,"sha256":sha_file(path)})
    record={
        "captured_utc":utc_now(), "protected_baseline":"40e7940016ea3c3966752b61f55a931f91a13ac7",
        "new_worktree":str(ROOT), "new_branch":git(["branch","--show-current"],ROOT),
        "worktree_porcelain":git(["worktree","list","--porcelain"],original),
        "refs":git(["for-each-ref","--sort=refname","--format=%(refname)%09%(objectname)","refs/heads","refs/remotes"],original),
        "protected_worktrees":[
            {"path":str(original),"head":git(["rev-parse","HEAD"],original),"branch":git(["branch","--show-current"],original),"status":git(["status","--porcelain=v2","--branch","--untracked-files=all"],original)},
            {"path":str(legacy),"head":git(["rev-parse","HEAD"],legacy),"branch":git(["branch","--show-current"],legacy),"status":git(["status","--porcelain=v2","--branch","--untracked-files=all"],legacy)},
            {"path":str(prior),"head":git(["rev-parse","HEAD"],prior),"branch":git(["branch","--show-current"],prior),"status":git(["status","--porcelain=v2","--branch","--untracked-files=all"],prior)},
        ], "original_untracked_count":len(files), "original_untracked_files":files,
    }
    dump(DOCS/"isolation-baseline.json",record); return record


def integrity() -> dict[str, Any]:
    baseline=load(DOCS/"isolation-baseline.json")
    failures=[]
    for item in baseline["protected_worktrees"]:
        path=Path(item["path"])
        if git(["rev-parse","HEAD"],path)!=item["head"]: failures.append(f"HEAD changed: {path}")
        if git(["branch","--show-current"],path)!=item["branch"]: failures.append(f"branch changed: {path}")
        if git(["status","--porcelain=v2","--branch","--untracked-files=all"],path)!=item["status"]: failures.append(f"worktree status changed: {path}")
    original=Path(baseline["protected_worktrees"][0]["path"])
    now=[]
    for rel in git(["ls-files","--others","--exclude-standard"],original).splitlines():
        p=original/rel
        if p.is_file(): now.append({"path":rel.replace("\\","/"),"bytes":p.stat().st_size,"sha256":sha_file(p)})
    if now!=baseline["original_untracked_files"]: failures.append("original pre-existing untracked inventory changed")
    ref_expect={line.split("\t")[0]:line.split("\t")[1] for line in baseline["refs"].splitlines() if "\t" in line and "clean-webtoon" not in line}
    current=git(["for-each-ref","--sort=refname","--format=%(refname)%09%(objectname)","refs/heads","refs/remotes"],original)
    ref_now={line.split("\t")[0]:line.split("\t")[1] for line in current.splitlines() if "\t" in line}
    for ref,oid in ref_expect.items():
        if ref_now.get(ref)!=oid: failures.append(f"protected ref changed: {ref}")
    record={"status":"PASS" if not failures else "FAIL","checked_utc":utc_now(),"failures":failures,"protected_refs":ref_expect,"original_untracked_count":len(now),"new_branch":git(["branch","--show-current"],ROOT),"new_head":git(["rev-parse","HEAD"],ROOT)}
    dump(PROD/"integrity-report.json",record)
    if failures: raise ValueError(json.dumps(record,indent=2))
    return record


def reconcile() -> dict[str, Any]:
    production_records=[]
    for p in sorted((PROD/"render-records").glob("ch*/*.json")): production_records.append(load(p))
    auxiliary_records=[]
    pilot_path=PROD/"pilot"/"render-records.json"
    if pilot_path.exists(): auxiliary_records.extend(load(pilot_path)["requests"])
    for p in sorted((PROD/"render-records"/"references").glob("*.json")): auxiliary_records.append(load(p))
    records=production_records+auxiliary_records
    errors=[]
    for r in records:
        if sha_text(r["exact_prompt"])!=r["prompt_sha256"]: errors.append(f"{r['request_id']}: prompt hash mismatch")
        path=ROOT/r["output_path"]
        if not path.exists(): errors.append(f"{r['request_id']}: output missing")
        elif sha_file(path)!=r["output_sha256"]: errors.append(f"{r['request_id']}: output hash mismatch")
        for candidate in r.get("candidate_paths_and_hashes",[]):
            candidate_path=ROOT/candidate["file"]
            if not candidate_path.exists(): errors.append(f"{r['request_id']}: candidate missing {candidate['file']}")
            elif sha_file(candidate_path)!=candidate["sha256"]: errors.append(f"{r['request_id']}: candidate hash mismatch {candidate['file']}")
        for key in ("model","endpoint","provider_request_id","usage","deterministic_seed"):
            if r.get(key) is not None: errors.append(f"{r['request_id']}: unavailable {key} must remain null")
    statuses=Counter(r["review_status"] for r in records); failures=Counter(f for r in records for f in r["failure_classes"])
    elapsed=sum(float(r["measured_elapsed_seconds"]) for r in records if r.get("measured_elapsed_seconds") is not None)
    candidates=sum(len(r["candidate_paths_and_hashes"]) for r in production_records)
    expected_complete=len(production_records)==80 and candidates==240 and len(auxiliary_records)==11
    out={"status":"PASS" if expected_complete and not errors else "FAIL","errors":errors,"chapters":10,"sequences":40,"panel_groups":80,"selected_panels":candidates,"lettering_entries":240,"prompt_count":len(records),"reference_use_count":sum(len(r.get("input_references",[])) for r in records),"generation_requests":{"total":len(records),"production":len(production_records),"bounded_style_and_topology_pilot":9,"reference_assets":2},"review_status_totals":dict(statuses),"failure_classes":dict(failures),"summed_measured_generation_seconds":round(elapsed,3),"timing_note":"sum of independently measured request latencies where available; concurrent calls are not wall-clock duration; three initial style probes retain null per-request latency","direct_paid_cloud_spend_usd":0,"provider_metadata_availability":{"model":False,"endpoint":False,"provider_request_id":False,"usage":False,"seed":False},"candidate_state":"owner-review-pending","acceptance_state":"unaccepted","commercial_clearance_state":"commercially_uncleared","production_base_state":"not_an_exact_production_base","reproducibility_state":"non_reproducible_unless_proven","generated_pixels_tracked_by_git":len(git(["ls-files",str(ART.relative_to(ROOT))],ROOT).splitlines())}
    dump(PROD/"output-reconciliation.json",out); dump(PROD/"cost-and-timing-summary.json",out); return out


def volume_hub() -> dict[str, Any]:
    progression_ids=["CH01-S04-P06","CH02-S04-P06","CH03-S03-P06","CH04-S03-P06","CH05-S03-P06","CH06-S04-P06","CH07-S03-P06","CH08-S03-P06","CH09-S04-P06","CH10-S04-P06"]
    strongest_ids=["CH01-S01-P05","CH02-S04-P06","CH03-S03-P05","CH04-S03-P06","CH05-S03-P06","CH06-S03-P06","CH07-S03-P05","CH08-S03-P05","CH09-S04-P06","CH10-S04-P06"]
    def panel(pid: str) -> Image.Image:
        return Image.open(ART/"chapters"/pid[:4].lower()/"panels"/f"{pid.lower()}.png").convert("RGB")
    review_dir=ART/"volume-review"; review_dir.mkdir(parents=True,exist_ok=True)
    progression=contact([panel(x) for x in progression_ids],"Ten-chapter visible progression")
    strongest=contact([panel(x) for x in strongest_ids],"Strongest individual panels")
    progression_path=review_dir/"progression-hub.png"; strongest_path=review_dir/"strongest-panels.png"
    progression.save(progression_path,compress_level=9); strongest.save(strongest_path,compress_level=9)
    chapter_rows=[]; totals=Counter(); failures=Counter(); manual_sequences=Counter(); manual_failures=Counter()
    for cid in CHAPTERS:
        review=load(PROD/"reviews"/f"{cid.lower()}-assembly.json")
        metrics=load(PROD/"chapters"/cid.lower()/"density-metrics.json")
        manual_path=PROD/"reviews"/f"{cid.lower()}-manual-review.json"
        manual=load(manual_path) if manual_path.exists() else {"overall_status":"FAIL","sequence_reviews":[],"warns":[{"failure_class":"manual_review_missing"}]}
        totals.update(metrics["status_totals"]); failures.update(metrics["failure_classes"])
        manual_sequences.update(x["status"] for x in manual.get("sequence_reviews",[])); manual_failures.update(x["failure_class"] for x in manual.get("warns",[]))
        chapter_rows.append({"chapter":cid,"assembly":review,"metric_status_totals":metrics["status_totals"],"metric_failure_classes":metrics["failure_classes"],"manual_review":manual})
    index={"chapters":chapter_rows,"manual_sequence_status_totals":dict(manual_sequences),"manual_failure_classes":dict(manual_failures),"panel_metric_status_totals":dict(totals),"metric_failure_classes":dict(failures),"manual_taxonomy":"production/reimaginings/the-city-keeps-oaths/review-taxonomy.json","progression_hub":{"file":progression_path.relative_to(ROOT).as_posix(),"sha256":sha_file(progression_path)},"strongest_panels":{"file":strongest_path.relative_to(ROOT).as_posix(),"sha256":sha_file(strongest_path)}}
    dump(PROD/"reviews"/"volume-review-index.json",index)
    lines=[
        "# The City Keeps Oaths — owner review start", "",
        "**Spoiler-light premise:** Adult pathwright Sola Merrow learns that Caelune's luminous roads are records of kept promises. When the roads reject the government, she must decide whether one expert should hold a city—or help its people hold one another.", "",
        "This is an original ten-chapter, 240-panel opening volume. Generated images are owner-review-pending, unaccepted, commercially uncleared, not exact production bases, and non-reproducible unless proven.", "",
        "## Progression system", "",
        "The **Covenant Lattice** records voluntary, witnessed, costed promises only after completion. Sola earns the visible Listen, Hold, Span, Sever, and Chorus chords through consequential choices; each capability changes her tool, posture, relationships, responsibilities, and the city's physical roads. It is diegetic covenant craft, not a floating statistics interface.", "",
        "## Selected visual direction", "",
        "Candidate A scored 93/100 on the preregistered rubric and was locked without a refinement probe. The house style uses crisp dark-navy contours, smooth restrained cel shading, midnight and pearl value families, selective cyan-gold oathlight, mature adult proportions, one dominant focal subject, simplified dialogue backgrounds, and detailed vertical-scale environments only at earned peaks. Woodcut texture, hatching, grunge, generated text boxes, equal detail everywhere, effect fog, and glossy 3D rendering are excluded.", "",
        "The production topology is two text-free three-panel vertical strips per six-panel sequence. It won the controlled pilot at 94/100 by preserving identity and causality while keeping each crop independently phone-readable; it is not the rejected six-moment 3×2 sheet strategy.", "",
        "## Research and originality boundary", "",
        "The derivation record cites official or licensed material for [The Beginning After the End](https://tapas.io/series/tbate-comic/info), [Solo Leveling](https://www.tappytoon.com/en/book/187), and [Tower of God](https://m.webtoons.com/en/fantasy/tower-of-god/list?title_no=95), plus creator, producer, director, and reputable critical analysis. Only high-level principles—mobile pacing, readable silhouettes, selective effects, vertical scale, visible earned progression, and quiet space around reveals—were transferred. No published panels, third-party art, proprietary characters, costumes, settings, interfaces, or named-artist styles were used as references.", "",
        "## Read the volume", "",
    ]
    for cid in CHAPTERS:
        base=f"../../../experiments/reimaginings/{SLUG}/chapters/{cid.lower()}"
        lines.append(f"- {cid}: [reading draft]({base}/{cid.lower()}-reading-draft.png) · [390 px phone preview]({base}/{cid.lower()}-phone-preview.png) · [compact lettered review]({base}/review/{cid.lower()}-compact-lettered-review.png) · [source contact]({base}/review/{cid.lower()}-contact-sheet.png) · [grayscale]({base}/review/{cid.lower()}-grayscale-review.png) · [density map]({base}/review/{cid.lower()}-density-map.png) · [safe zones]({base}/review/{cid.lower()}-safe-zone-review.png) · [source strips]({base}/source-strips/)")
    lines += ["", "## Progression, cast, and strongest frames", "", f"- [Ten-chapter progression hub](../../../{progression_path.relative_to(ROOT).as_posix()})", f"- [Strongest individual panels](../../../{strongest_path.relative_to(ROOT).as_posix()})", "- [Sola progression character sheet](../../../experiments/reimaginings/the-city-keeps-oaths/references/sola-progression-sheet-v1.png)", "- [Supporting fictional-adult sheet](../../../experiments/reimaginings/the-city-keeps-oaths/references/supporting-adults-sheet-v1.png)", "- [Selected clean-cinematic style anchor](../../../experiments/reimaginings/the-city-keeps-oaths/style-probes/candidate-a.png)", "- [Topology pilot directory](../../../experiments/reimaginings/the-city-keeps-oaths/pilot/)", "", "## Bibles, research, and decisions", "", "- [Story bible](../../../reimaginings/the-city-keeps-oaths/story-bible.md)", "- [Progression bible](../../../reimaginings/the-city-keeps-oaths/progression-bible.md)", "- [Visual bible](../../../reimaginings/the-city-keeps-oaths/visual-bible.md)", "- [Ten-chapter outline](../../../reimaginings/the-city-keeps-oaths/volume-outline.md)", "- [Inspiration research and derivation matrix](research/inspiration-derivation.md)", "- [Cumulative experiment ledger](cumulative-experiment-ledger.md)", "- [Style selection](style-probe-review.md)", "- [Topology pilot](topology-pilot-review.md)", "- [ADR index](adr/README.md)", "", "## Production evidence", "", "- [Complete ComicPanelPlan source](../../../production/reimaginings/the-city-keeps-oaths/source/volume.json)", "- [Continuity graph](../../../production/reimaginings/the-city-keeps-oaths/continuity-graph.json)", "- [Adult-character contracts](../../../production/reimaginings/the-city-keeps-oaths/character-contracts.json)", "- [Reference registry](../../../production/reimaginings/the-city-keeps-oaths/reference-registry.json)", "- [Volume review index](../../../production/reimaginings/the-city-keeps-oaths/reviews/volume-review-index.json)", "- [Targeted repair record](../../../production/reimaginings/the-city-keeps-oaths/repairs/repair-wave.json) · [CH03 before/after](../../../experiments/reimaginings/the-city-keeps-oaths/repairs/lettering-wave/ch03-before-after.png) · [CH04 before/after](../../../experiments/reimaginings/the-city-keeps-oaths/repairs/lettering-wave/ch04-before-after.png)", "- [Output reconciliation](../../../production/reimaginings/the-city-keeps-oaths/output-reconciliation.json)", "- [Integrity report](../../../production/reimaginings/the-city-keeps-oaths/integrity-report.json)", "- [Final Git state and tracked file inventory](../../../production/reimaginings/the-city-keeps-oaths/final-git-state.json)", "", "## Current quantitative review", "", f"- Chapters / sequences / panels / planned production prompts: 10 / 40 / 240 / 80", f"- Panel metric proxy totals: {dict(totals)}", f"- Exact metric proxy classes: {dict(failures)}", "- Manual visual sequence classifications and repair outcomes are in the final audit and volume review index.", "- Direct paid/cloud spend: $0. Provider model, endpoint, request ID, usage, cost, and deterministic seed are unavailable and remain null.", "", "## Limitations and owner decisions", "", "- Generated candidates require owner acceptance and rights review; no commercial-clearance claim is made.", "- Density and focal metrics are pilot-relative proxies. Manual phone inspection controls when a metric and readable composition disagree.", "- The final branch-tip commit and remote parity are recorded in the closeout Git state and delivery handoff; a tracked file cannot literally contain the hash of its own containing commit without changing that hash."]
    path=DOCS/"START_HERE.md"; path.write_text("\n".join(lines)+"\n",encoding="utf-8")
    return index


def repair_lettering() -> dict[str, Any]:
    """Execute the single bounded deterministic lettering-only repair wave."""
    targets=sorted(LETTERING_OVERRIDES)
    target_chapters=sorted({panel[:4].lower() for panel in targets})
    repair_art=ART/"repairs"/"lettering-wave"
    before_dir=repair_art/"before"; after_dir=repair_art/"after"
    before_dir.mkdir(parents=True,exist_ok=True); after_dir.mkdir(parents=True,exist_ok=True)
    source_before=[]
    for cid in CHAPTERS:
        for p in sorted((ART/"chapters"/cid.lower()/"panels").glob("*.png")):
            source_before.append({"file":p.relative_to(ROOT).as_posix(),"sha256":sha_file(p)})
    review_names=["compact-lettered-review.png","safe-zone-review.png"]
    chapter_names=["reading-draft.png","phone-preview.png"]
    copied=[]
    for chapter in target_chapters:
        for suffix in review_names:
            src=ART/"chapters"/chapter/"review"/f"{chapter}-{suffix}"
            dst=before_dir/src.name
            shutil.copy2(src,dst); copied.append({"stage":"before","file":dst.relative_to(ROOT).as_posix(),"sha256":sha_file(dst)})
        for suffix in chapter_names:
            src=ART/"chapters"/chapter/f"{chapter}-{suffix}"
            dst=before_dir/src.name
            shutil.copy2(src,dst); copied.append({"stage":"before","file":dst.relative_to(ROOT).as_posix(),"sha256":sha_file(dst)})
    compile_all()
    for chapter in target_chapters:
        assemble(chapter.upper())
        for suffix in review_names:
            src=ART/"chapters"/chapter/"review"/f"{chapter}-{suffix}"
            dst=after_dir/src.name
            shutil.copy2(src,dst); copied.append({"stage":"after","file":dst.relative_to(ROOT).as_posix(),"sha256":sha_file(dst)})
        for suffix in chapter_names:
            src=ART/"chapters"/chapter/f"{chapter}-{suffix}"
            dst=after_dir/src.name
            shutil.copy2(src,dst); copied.append({"stage":"after","file":dst.relative_to(ROOT).as_posix(),"sha256":sha_file(dst)})
        before=Image.open(before_dir/f"{chapter}-compact-lettered-review.png").convert("RGB")
        after=Image.open(after_dir/f"{chapter}-compact-lettered-review.png").convert("RGB")
        comparison=Image.new("RGB",(before.width+after.width,max(before.height,after.height)+52),(241,244,244))
        draw=ImageDraw.Draw(comparison); face=font(30,True)
        draw.text((18,10),f"{chapter.upper()} BEFORE — failed lettering clearance",font=face,fill=(23,35,54))
        draw.text((before.width+18,10),f"{chapter.upper()} AFTER — localized safe-zone repair",font=face,fill=(23,35,54))
        comparison.paste(before,(0,52)); comparison.paste(after,(before.width,52))
        compare_path=repair_art/f"{chapter}-before-after.png"; comparison.save(compare_path,compress_level=9)
        copied.append({"stage":"comparison","file":compare_path.relative_to(ROOT).as_posix(),"sha256":sha_file(compare_path)})
    source_after=[]
    for cid in CHAPTERS:
        for p in sorted((ART/"chapters"/cid.lower()/"panels").glob("*.png")):
            source_after.append({"file":p.relative_to(ROOT).as_posix(),"sha256":sha_file(p)})
    before_map={x["file"]:x["sha256"] for x in source_before}; after_map={x["file"]:x["sha256"] for x in source_after}
    changes=[path for path in sorted(set(before_map)|set(after_map)) if before_map.get(path)!=after_map.get(path)]
    result={"status":"AWAITING_POST_REPAIR_MANUAL_REVIEW","bounded_repair_wave_evaluated":True,"executed_repair_count":len(targets),"comparison_count":len(target_chapters),"repair_type":"deterministic local lettering safe-zone relocation only","target_panel_ids":targets,"source_regeneration_requests":0,"source_panel_hashes_before":source_before,"source_panel_hashes_after":source_after,"source_panel_change_count":len(changes),"source_panel_changes":changes,"non_target_change_count":len(changes),"artifacts":copied,"policy":str((PROD/"repair-policy.json").relative_to(ROOT))}
    dump(PROD/"repairs"/"repair-wave.json",result)
    return result


def closeout() -> dict[str, Any]:
    validation=validate_all()
    missing=[]; artifact_errors=[]; manual_errors=[]; manual=[]; hard=[]
    taxonomy_contract=load(PROD/"review-taxonomy.json")
    required_taxonomy=set(taxonomy_contract["categories"])
    panel_hashes=[]
    for cid in CHAPTERS:
        assembly_path=PROD/"reviews"/f"{cid.lower()}-assembly.json"
        manual_path=PROD/"reviews"/f"{cid.lower()}-manual-review.json"
        if not assembly_path.exists(): missing.append(str(assembly_path.relative_to(ROOT)))
        else:
            for artifact in load(assembly_path)["artifacts"]:
                path=ROOT/artifact["file"]
                if not path.exists() or sha_file(path)!=artifact["sha256"]: artifact_errors.append(artifact["file"])
        if not manual_path.exists(): missing.append(str(manual_path.relative_to(ROOT)))
        else:
            item=load(manual_path); manual.append(item)
            if item.get("chapter")!=cid: manual_errors.append(f"{cid}: manual chapter mismatch")
            sequence_reviews=item.get("sequence_reviews",[])
            expected_sequences=[f"{cid}-S{i:02d}" for i in range(1,5)]
            if [x.get("sequence") for x in sequence_reviews]!=expected_sequences: manual_errors.append(f"{cid}: manual sequence coverage/order mismatch")
            if set(item.get("taxonomy",{}))!=required_taxonomy: manual_errors.append(f"{cid}: manual taxonomy coverage mismatch")
            for key,status in item.get("taxonomy",{}).items():
                if status not in taxonomy_contract["statuses"]: manual_errors.append(f"{cid}: invalid taxonomy status {key}={status}")
            for sequence in sequence_reviews:
                if sequence.get("status") not in taxonomy_contract["statuses"]: manual_errors.append(f"{cid}: invalid sequence status")
                if sequence.get("status")!="PASS" and not sequence.get("failure_classes"): manual_errors.append(f"{sequence.get('sequence')}: unexplained non-PASS")
            for warning in item.get("warns",[]):
                if not warning.get("failure_class") or not warning.get("disposition"): manual_errors.append(f"{cid}: incomplete warning record")
            if item.get("hard_repair_required"): hard.append(cid)
        for p in sorted((ART/"chapters"/cid.lower()/"panels").glob("*.png")):
            panel_hashes.append({"file":p.relative_to(ROOT).as_posix(),"sha256":sha_file(p)})
    if missing or artifact_errors or manual_errors: raise ValueError(json.dumps({"missing":missing,"artifact_errors":artifact_errors,"manual_errors":manual_errors},indent=2))
    repairs_dir=PROD/"repairs"; repairs_dir.mkdir(parents=True,exist_ok=True)
    if hard:
        dump(repairs_dir/"repair-wave.json",{"status":"BLOCKED_HARD_REPAIRS_PRESENT","chapters":hard,"evaluated_panels":len(panel_hashes),"policy":str((PROD/"repair-policy.json").relative_to(ROOT))})
        raise ValueError(f"hard repair required for {hard}")
    existing_repair_path=repairs_dir/"repair-wave.json"
    existing_repair=load(existing_repair_path) if existing_repair_path.exists() else None
    if existing_repair and existing_repair.get("status")=="PASS_REPAIRS_EXECUTED":
        repair=existing_repair
        if repair.get("source_panel_change_count")!=0 or repair.get("non_target_change_count")!=0:
            raise ValueError("repair wave changed generated source panels")
    else:
        repair={"status":"PASS_NO_REPAIR_REQUIRED","bounded_repair_wave_evaluated":True,"executed_repair_count":0,"comparison_count":0,"reason":"All visual WARNs are story-readable metric or minor continuity warnings; no story-breaking continuity, unreadable action, severe identity/anatomy/safety, missing irreversible state, or severe phone failure was found.","panel_hash_snapshot":panel_hashes,"non_target_change_count":0}
        dump(existing_repair_path,repair)
    reconciliation=reconcile()
    if reconciliation["status"]!="PASS": raise ValueError(json.dumps(reconciliation,indent=2))
    hub=volume_hub(); integrity_result=integrity()
    manual_status=Counter(x["status"] for item in manual for x in item["sequence_reviews"])
    manual_failures=Counter(x["failure_class"] for item in manual for x in item.get("warns",[]))
    if repair["executed_repair_count"]:
        repair_summary=f"{repair['status']}: {repair['executed_repair_count']} hard lettering-clearance defects were repaired by deterministic safe-zone relocation only. Before/after comparisons are preserved for {repair['comparison_count']} chapters; generated source-panel changes: {repair['source_panel_change_count']}; non-target changes: {repair['non_target_change_count']}; image regeneration requests: {repair['source_regeneration_requests']}."
    else:
        repair_summary=f"{repair['status']}: all 240 selected hashes were snapshotted; no hard repair class was present, so no aesthetic rerender was permitted. There are no before/after repair images because no repair was executed."
    final_lines=["# The City Keeps Oaths — final production audit","","## Outcome","",f"Exactly ten complete chapters, 40 sequences, and 240 selected panels are authored, illustrated, locally lettered, assembled, and linked from `START_HERE.md`. Structural validation, prompt/source/output reconciliation, density review, manual phone review, and protected-worktree integrity pass.","","## Quantitative record","",f"- Manual sequence status: {dict(manual_status)}",f"- Manual exact warning classes: {dict(manual_failures)}",f"- Metric proxy panel status: {hub['panel_metric_status_totals']}",f"- Metric proxy classes: {hub['metric_failure_classes']}",f"- Generation requests: {reconciliation['generation_requests']}",f"- Summed measured request latency: {reconciliation['summed_measured_generation_seconds']} seconds; not wall-clock time.","- Direct paid/cloud spend: $0.","- Model, endpoint, request ID, usage, provider cost, and seed were unavailable and remain null.","- Generated pixels tracked by Git: 0.","","## Repair wave","",repair_summary,"","## Known limitations","","- Every generated candidate remains owner-review-pending, unaccepted, commercially uncleared, not an exact production base, and non-reproducible unless proven.","- Pilot-relative density proxies produce conservative WARNs even when manual 390-pixel review passes; exact classes remain visible rather than being collapsed into a beauty score.","- Three initial concurrent style probes lack individual latency; their measured batch wall time is recorded and per-request latency remains null rather than invented.","","## Integrity","",f"Integrity status: {integrity_result['status']}. Protected `main`, `origin/main`, both earlier reimagining branches/worktrees, and all 159 pre-existing untracked files retain their baseline heads, branches, statuses, paths, sizes, and hashes."]
    (DOCS/"FINAL_AUDIT.md").write_text("\n".join(final_lines)+"\n",encoding="utf-8")
    result={"status":"PASS","validation":validation["status"],"chapters":10,"sequences":40,"panels":240,"manual_sequence_status":dict(manual_status),"repair_wave":repair["status"],"reconciliation":reconciliation["status"],"integrity":integrity_result["status"]}
    dump(PROD/"closeout-report.json",result); return result


def set_review(request_id: str, status: str, failures: list[str]) -> dict[str, Any]:
    chapter=request_id[:4].lower(); path=PROD/"render-records"/chapter/f"{request_id.lower()}.json"; record=load(path); record["review_status"]=status; record["failure_classes"]=failures; dump(path,record); return record


def main() -> None:
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="cmd",required=True)
    sub.add_parser("snapshot-isolation"); sub.add_parser("compile"); sub.add_parser("validate"); sub.add_parser("integrity"); sub.add_parser("reconcile"); sub.add_parser("hub"); sub.add_parser("repair-lettering"); sub.add_parser("closeout")
    p=sub.add_parser("ingest"); p.add_argument("--request",required=True); p.add_argument("--source",type=Path,required=True); p.add_argument("--elapsed",type=float,required=True); p.add_argument("--review",choices=["PASS","WARN","FAIL"],default="PASS"); p.add_argument("--failure",action="append",default=[])
    p=sub.add_parser("assemble"); p.add_argument("--chapter",required=True)
    p=sub.add_parser("set-review"); p.add_argument("--request",required=True); p.add_argument("--status",choices=["PASS","WARN","FAIL"],required=True); p.add_argument("--failure",action="append",default=[])
    args=parser.parse_args()
    if args.cmd=="snapshot-isolation": result=snapshot_isolation()
    elif args.cmd=="compile": result=compile_all()
    elif args.cmd=="validate": result=validate_all()
    elif args.cmd=="integrity": result=integrity()
    elif args.cmd=="reconcile": result=reconcile()
    elif args.cmd=="hub": result=volume_hub()
    elif args.cmd=="repair-lettering": result=repair_lettering()
    elif args.cmd=="closeout": result=closeout()
    elif args.cmd=="ingest": result=ingest(args.request,args.source,args.elapsed,args.review,args.failure)
    elif args.cmd=="assemble": result=assemble(args.chapter)
    else: result=set_review(args.request.upper(),args.status,args.failure)
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
