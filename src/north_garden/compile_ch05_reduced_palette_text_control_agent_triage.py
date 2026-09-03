"""Compile deterministic non-gating triage for the CH05 text-control arm."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
PROMPT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-prompt-manifest-r1.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-assembly-r1.json"
BUILD_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/build-report.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-complete-chapter-reduced-palette-text-control-agent-triage-r1.json"
SHEET = ROOT / "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/ch05-complete-chapter-reduced-palette-text-control-triage-sheet-r1.png"

SEMANTIC: dict[int, tuple[str, str | None, str]] = {
    1: ("PASS", None, "Both adults travel downhill with the cold, unlit farmhouse behind them; the chimney has no smoke."),
    2: ("PASS", None, "Sigrid checks a folded creek map and points at a circled location aligned with the drawn smoke indication."),
    3: ("WARN", "track_overlap", "Soren's boot is held back and several prints cross the trail, but fresh-over-old overlap is not unambiguous."),
    4: ("PASS", None, "The two mature adults stop in opposite thirds and exchange a clear wary look."),
    5: ("PASS", None, "A people-free runnel crosses the trail with a readable diagonal water direction."),
    6: ("PASS", None, "Sigrid steps first and points to the older marker while Soren waits behind her."),
    7: ("PASS", None, "The marker shows one simple mill-wheel glyph and no written name."),
    8: ("FAIL", "map_fold_state", "The creek sheet is exposed, but a farmhouse drawing remains plainly visible on the rear sheet; the requested hide-farmhouse fold is not achieved."),
    9: ("PASS", None, "Sigrid leads the narrow wet trail and Soren follows in the correct order."),
    10: ("PASS", None, "Sigrid's listening profile reads clearly against empty dark woods before water is shown."),
    11: ("PASS", None, "Soren's oatmeal sleeve and adult hand bind the role while soot-dark twine is pinched at a wet thorn."),
    12: ("WARN", "twine_direction", "The taut diagonal twine is unmistakable, but the empty wet ground gives no decisive downhill orientation."),
    13: ("PASS", None, "The adults descend beside the creek with Sigrid ahead and Soren following."),
    14: ("PASS", None, "The people-free ridge shoulder blocks the prior smoke line completely."),
    15: ("PASS", None, "Sigrid's wet thumb visibly obscures the creek line on the map."),
    16: ("PASS", None, "Both adults walk in one direction without facing each other while Soren gestures through the deduction."),
    17: ("PASS", None, "The abandoned mill, broken roof, wheel, creek, and unsafe bridge establish the destination."),
    18: ("PASS", None, "Smoke rises from the ridge behind the mill and is visibly separate from the mill roof."),
    19: ("PASS", None, "Sigrid's open stop hand arrests Soren before the open bridge route."),
    20: ("PASS", None, "The adults cross below the bridge on separated stones with clear weight transfer and splash."),
    21: ("PASS", None, "A newly tied red cloth strip hangs from a wet low branch against an unreadable background."),
    22: ("PASS", None, "Soren's oatmeal-sleeved hand intercepts Sigrid's plaid-sleeved reach before the cloth is touched."),
    23: ("PASS", None, "The pair circle through wet grass toward the collapsed loading opening."),
    24: ("PASS", None, "A narrow smoke thread reveals a metal drum hidden behind the stone opening."),
    25: ("PASS", None, "The overhead drum contains wet needles, pooled water, and one damp ember."),
    26: ("PASS", None, "Sigrid holds an open hand above the ember without contact; heat smoke rises beside the fingers."),
    27: ("PASS", None, "Soren tracks a second taut line from the exterior into the dark mill opening."),
    28: ("PASS", None, "The line is visibly tied to a small brass bell inside the doorway."),
    29: ("PASS", None, "Sigrid enters the wall breach while Soren independently watches the exterior in the opposite direction."),
    30: ("PASS", None, "Daylight bars, standing water, broken gears, and an empty interior establish the mill."),
    31: ("PASS", None, "Sigrid crouches beside dry prints that end cleanly at the near water edge."),
    32: ("WARN", "far_bank_orientation", "Prints begin on far dry ground, but heel-toe asymmetry does not reliably prove that they face back toward Soren."),
    33: ("PASS", None, "A drip hangs from the bell while Sigrid and Soren freeze at clearly different depths."),
    34: ("PASS", None, "Both adults remain still on opposite sides of the empty doorway and neither approaches the bell."),
    35: ("PASS", None, "The sealed tin remains isolated high on a daylight upper beam."),
    36: ("FAIL", "continuous_force_path", "Soren raises one diagonal plank toward the tin while Sigrid braces a separate lower plank; no single plank connects both grips to the tin."),
    37: ("PASS", None, "The opened tin is on stone beside dry matches, the creek map, and a blank card."),
    38: ("PASS", None, "The map clearly distinguishes the farmhouse square from the mill circle."),
    39: ("PASS", None, "A distinct triangle appears upstream on the torn extension where Soren's finger stops."),
    40: ("PASS", None, "Sigrid's calm mature profile and alert gaze carry the signal-not-campfire deduction."),
    41: ("PASS", None, "The rain-soaked drum is fully out with no ember, flame, glow, or smoke plume."),
    42: ("PASS", None, "The creek-side doorway, vibrating bell, and taut line establish the second ring's new direction."),
    43: ("PASS", None, "The tin remains open on the stone while Sigrid visibly retains the creek map during retreat."),
    44: ("WARN", "cut_contact", "The pocket knife and taut twine read, but the blade-contact point is narrow and becomes ambiguous at phone width."),
    45: ("PASS", None, "The empty creek and mill exterior hold after the cut with the distant bell still."),
    46: ("PASS", None, "Sigrid places the retained creek map inside her plaid wrap while the notebook remains in her bag."),
    47: ("PASS", None, "Both adults climb uphill toward the farmhouse under cleared sky with no chimney smoke."),
    48: ("PASS", None, "The distant farmhouse becomes the destination and displays the chapter's first chimney smoke."),
    49: ("PASS", None, "Soren looks back from the map toward the smoking farmhouse in a readable realization beat."),
    50: ("FAIL", "role_order", "Both adults run toward the house and Soren carries the map, but Soren is closer to the destination while Sigrid trails in the foreground."),
}

LETTERING: dict[int, tuple[str, str]] = {
    1: ("PASS", "Top-left sky clears the adults, farmhouse, chimney, and travel silhouette."),
    2: ("PASS", "Top-right negative space clears Sigrid, her hand, and the map."),
    3: ("PASS", "Top-left background clears the held boot and principal print chain."),
    4: ("FAIL", "Top-right zone covers Sigrid's hair, forehead, and upper face."),
    5: ("FAIL", "Top zone crosses the runnel, the only story object in the insert."),
    6: ("PASS", "Top-right sky clears faces, pointing hand, marker, and stepping silhouette."),
    7: ("WARN", "Top zone occupies highly textured marker stone but leaves the wheel glyph unobscured."),
    8: ("PASS", "Top-right negative space clears both hands and all map edges."),
    9: ("FAIL", "Top-left zone covers Soren's hair and upper head."),
    10: ("PASS", "Top-right woods remain clear of Sigrid's face and listening silhouette."),
    11: ("WARN", "Top-left zone grazes the active hand while leaving the fingertips, thorn, and twine readable under transparency."),
    12: ("FAIL", "Top zone crosses the taut twine, the panel's sole causal clue."),
    13: ("WARN", "Top-left zone uses busy water texture but clears both adult silhouettes."),
    14: ("PASS", "Top zone remains in open cloud and clears the smoke-occluding ridge edge."),
    15: ("FAIL", "Top-left zone lies on the map, a required story prop."),
    16: ("WARN", "Top-right zone grazes Soren's hair but leaves both faces, silhouettes, and gesture readable under transparency."),
    17: ("FAIL", "Top zone overlaps the mill's broken roofline, the reveal's defining shape."),
    18: ("FAIL", "Top zone covers the smoke column whose separation from the mill is the clue."),
    19: ("FAIL", "Top-left zone covers Sigrid's hair, forehead, and upper face."),
    20: ("PASS", "Top-right open water clears both adults, the bridge, and stepping stones."),
    21: ("WARN", "Top zone crosses the support branch and upper knot while the red cloth remains readable under transparency."),
    22: ("WARN", "Top-right zone overlaps Soren's sleeve but clears both important hands and the cloth."),
    23: ("PASS", "Top-left sky clears both adults and the collapsed loading opening."),
    24: ("FAIL", "Top zone covers the thin smoke thread that reveals the drum."),
    25: ("FAIL", "Top zone covers the drum rim, smoke wisp, and wet-needle clue field."),
    26: ("FAIL", "Top-right zone covers Sigrid's tied hair."),
    27: ("FAIL", "Top-left zone covers Soren's hair and upper face."),
    28: ("FAIL", "Top zone covers the bell hanger and taut-line attachment."),
    29: ("FAIL", "Top-left zone covers Soren's hair and upper face during the role split."),
    30: ("PASS", "Top zone uses high rafters and clears gears, water, doorway, and travel space."),
    31: ("FAIL", "Top-left zone covers Sigrid's tied hair and upper face."),
    32: ("FAIL", "Top-right zone covers Soren's hair and upper head."),
    33: ("FAIL", "Top-left zone covers the bell mount and drip mechanism."),
    34: ("FAIL", "Top-right zone covers Soren's head and upper torso."),
    35: ("PASS", "Top zone stays in daylight above the isolated tin."),
    36: ("FAIL", "Top-right zone covers the high tin and upper plank contact area."),
    37: ("FAIL", "Top zone covers the open tin rim and upper map area."),
    38: ("FAIL", "Top zone covers the map's upstream creek route."),
    39: ("FAIL", "Top-left zone covers Soren's hair and upper face."),
    40: ("PASS", "Top-right negative space clears Sigrid's face and deduction silhouette."),
    41: ("PASS", "Top zone remains above the drum and its no-smoke opening."),
    42: ("FAIL", "Top zone covers the upper bell and creek-side doorway relationship."),
    43: ("FAIL", "Top-left zone covers Soren's hair, face, and retreat silhouette."),
    44: ("PASS", "Top-right background clears both hands, blade, and twine contact."),
    45: ("PASS", "Top zone uses open sky and clears the mill, creek, and still bell."),
    46: ("PASS", "Top-right negative space clears Sigrid's face, hands, wrap, map, and notebook."),
    47: ("PASS", "Top-left sky clears both climbing adults and the farmhouse direction."),
    48: ("FAIL", "Top zone crosses the new farmhouse smoke column."),
    49: ("FAIL", "Top-left zone covers Soren's hair and forehead."),
    50: ("FAIL", "Top-right zone covers the urgent destination and smoke column."),
}

STYLE_PASS = {10, 11, 14, 21, 22, 25, 35, 40, 41, 44, 46, 48}
STYLE_WARN = {2, 4, 8, 16, 18, 26, 28}
PHONE_WARN = {3, 12, 25, 26, 32, 37, 44}
STRONGEST = [10, 14, 35, 40, 41, 46]
DETAIL_FIELDS = [
    "terrain, grass, rocks, architecture, and clothing", "map linework, plaid, hair, and skin", "mud, water, prints, grass, and coat", "faces, hair, plaid, coat, and layered clothing", "stones, mud, grass, and water", "figures, water, marker stone, vegetation, and clothing", "lichen, stone chips, and forest", "hands, map linework, paper folds, and sleeves", "forest canopy, bark, wet ground, and clothing", "localized face, hair, and plaid against simplified woods",
    "localized hand, thorn, and twine against one dark field", "wet terrain, stones, grass, and twine", "rocks, water, brush, and both wardrobes", "four broad landscape silhouettes and cloud field", "map contour, vegetation symbols, water, skin, and plaid", "two detailed figures against broad negative space", "mill timber, stone, terrain, water, and bridge", "simplified ridge/smoke masses with localized mill roof", "faces, clothing, bridge, creek, and terrain", "water, stones, bridge timber, and both figures",
    "localized wet branch and red cloth against fog", "localized hands, sleeves, cloth edge, and blank field", "figures, grass, rubble, water, and masonry", "stone blocks, timber, metal, smoke, and brush", "localized drum, wet needles, water, and ember", "localized face, hand, plaid, drum, and smoke", "face, coat, stone wall, timber, water, and twine", "bell, timber, masonry, and twine with moderate surface marks", "figures, rubble, masonry, water, and timber", "gears, rafters, masonry, water, and debris",
    "figure, prints, gears, timber, stone, and water", "figure, prints, gears, timber, stone, and water", "bell, drip, two figures, gears, timber, and water", "two figures, gears, timber, masonry, and water", "four broad beam/daylight masses with localized tin", "two adults, two planks, gears, beams, stone, and water", "tin, matches, map, card, rock, and surface texture", "map linework and paper texture across the full frame", "face, hair, hand, map, rock, and paper texture", "localized mature profile against one dark interior field",
    "localized wet drum and rain against simplified creek silhouettes", "stone blocks, door, creek, bell, twine, and motion marks", "two figures, stone, tin, map, gears, doorway, and creek", "localized hands, blade, and twine against softened creek", "mill timber, wheel, rock, creek, hillside, and bell", "localized face, hands, plaid, map, and notebook against negative space", "figures, cloth, slope, rocks, snow, sky, and mountains", "five broad landscape/house/smoke masses", "face, hair, coat, map, terrain, house, and smoke", "two figures, cloth, mud, rocks, house, trail, and smoke",
]
CHECK_KEYS = (
    "role_binding", "role_order", "visible_adult_count", "shared_set_and_blocking",
    "target_change_behavior", "causal_action_or_clue", "hair_and_wardrobe",
    "mature_fictional_adult", "lettering_clearance", "phone_readability",
    "cross_panel_canon", "strict_3_to_5_mass_style",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["DejaVuSans-Bold.ttf", "Arial Bold.ttf"] if bold else ["DejaVuSans.ttf", "Arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def worst(*statuses: str) -> str:
    rank = {"PASS": 0, "WARN": 1, "FAIL": 2}
    return max(statuses, key=rank.__getitem__)


def style_status(order: int) -> str:
    return "PASS" if order in STYLE_PASS else "WARN" if order in STYLE_WARN else "FAIL"


def wrap(draw: ImageDraw.ImageDraw, value: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in value.split():
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
            if len(lines) == 2:
                break
    if current and len(lines) < 2:
        lines.append(current)
    return lines


def continuity_note(order: int, cast: list[str]) -> str:
    partial = {
        3: "Soren is bound by the oatmeal coat and boot; hair is intentionally outside this low insert.",
        8: "Soren is bound by oatmeal sleeves and mature hands; hair is intentionally outside the map insert.",
        11: "Soren is bound by the oatmeal sleeve and mature hand; hair is outside the twine insert.",
        15: "Sigrid is bound by the plaid cuff and mature hand; hair is outside the map insert.",
        22: "Plaid and oatmeal sleeves bind the two mature adult roles; hair is outside the hand insert.",
        44: "Soren is bound by oatmeal sleeves and mature hands; hair is outside the cutting insert.",
    }
    if order in partial:
        return partial[order]
    if not cast:
        return "No person appears, matching the zero-cast ComicPanelPlan."
    if cast == ["SOREN"]:
        return "Soren retains swept wavy light-brown/dark-blond hair, stubble, mature proportions, and the pale oatmeal coat."
    if cast == ["SIGRID"]:
        return "Sigrid retains dark tied-back hair, mature proportions, and the dark blue-brown plaid wrap."
    return "Both mature fictional adults retain role-correct hair colors and approved oatmeal-coat/plaid-wrap wardrobes."


def build_sheet(entries: list[dict[str, Any]], rows: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    columns, tile_w, tile_h, gap, margin, header = 5, 300, 270, 14, 24, 126
    canvas = Image.new("RGB", (1604, header + math.ceil(50 / columns) * tile_h + 9 * gap), "#e7e3da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 15), "CH05 REDUCED-PALETTE TEXT CONTROL - AGENT TRIAGE", fill="#20252a", font=selected_font(24, True))
    draw.text((margin, 50), f"overall {summary['overall_pass']}/{summary['overall_warn']}/{summary['overall_fail']} | semantic {summary['semantic_pass']}/{summary['semantic_warn']}/{summary['semantic_fail']} | strict style {summary['style_pass']}/{summary['style_warn']}/{summary['style_fail']}", fill="#3b454d", font=selected_font(16))
    draw.text((margin, 77), "Tile status includes semantic + lettering + phone + strict 3-5-mass style. Green is not acceptance or clearance.", fill="#695848", font=selected_font(14))
    by_panel = {row["panel_id"]: row for row in rows}
    for index, entry in enumerate(entries):
        row = by_panel[entry["panel_id"]]
        source = ROOT / entry["source"]["path"]
        if not source.is_file() or sha256(source) != entry["source"]["sha256"]:
            raise ValueError(f"source mismatch: {entry['panel_id']}")
        with Image.open(source) as opened:
            panel = opened.convert("RGB")
        col, grid_row = index % columns, index // columns
        x, y = margin + col * (tile_w + gap), header + grid_row * (tile_h + gap)
        color = "#2d8a57" if row["status"] == "PASS" else "#c47a16" if row["status"] == "WARN" else "#b83b3b"
        draw.rectangle((x, y, x + tile_w, y + tile_h), fill="#faf8f2", outline=color, width=4)
        draw.text((x + 9, y + 7), f"{entry['order']:02d} P{entry['order']:03d} {row['status']}", fill=color, font=selected_font(15, True))
        framed = ImageOps.contain(panel, (tile_w - 18, 165), Image.Resampling.LANCZOS)
        canvas.paste(framed, (x + (tile_w - framed.width) // 2, y + 35 + (165 - framed.height) // 2))
        compact = f"S:{row['semantic_status'][0]} L:{row['lettering_status'][0]} P:{row['phone_status'][0]} T:{row['style_status'][0]}"
        draw.text((x + 9, y + 205), compact, fill="#343b41", font=selected_font(13, True))
        issue = (row["primary_issue_class"] or "no blocking issue").replace("_", " ")
        for line_no, line in enumerate(wrap(draw, issue, selected_font(12), tile_w - 18)):
            draw.text((x + 9, y + 229 + line_no * 15), line, fill="#343b41", font=selected_font(12))
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(SHEET, format="PNG", compress_level=6, optimize=False)
    return {"path": SHEET.relative_to(ROOT).as_posix(), "sha256": sha256(SHEET), "width": canvas.width, "height": canvas.height, "bytes": SHEET.stat().st_size, "tracked": False}


def main() -> int:
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    entries = sorted(assembly["entries"], key=lambda row: row["order"])
    build_report = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    if len(plans) != 50 or len(entries) != 50 or [p["panel_id"] for p in plans] != [e["panel_id"] for e in entries]:
        raise ValueError("assembly differs from canonical 50-panel ComicPanelPlan order")
    if set(SEMANTIC) != set(range(1, 51)) or set(LETTERING) != set(range(1, 51)) or len(DETAIL_FIELDS) != 50:
        raise ValueError("manual triage must cover exactly P001-P050")

    rows: list[dict[str, Any]] = []
    for plan, entry in zip(plans, entries, strict=True):
        order = plan["display_order"]
        semantic, semantic_issue, semantic_note = SEMANTIC[order]
        lettering, lettering_note = LETTERING[order]
        phone = "WARN" if order in PHONE_WARN else "PASS"
        style = style_status(order)
        overall = worst(semantic, lettering, phone, style)
        primary = semantic_issue if semantic != "PASS" else "lettering_safe_zone" if lettering != "PASS" else "phone_readability" if phone != "PASS" else "strict_style_density" if style != "PASS" else None
        checks = {key: "PASS" for key in CHECK_KEYS}
        checks["lettering_clearance"] = lettering
        checks["phone_readability"] = phone
        checks["strict_3_to_5_mass_style"] = style
        if order in {8, 36}:
            checks["target_change_behavior"] = "FAIL"
        if order == 50:
            checks["role_order"] = "FAIL"
        if order in {3, 12, 32, 44}:
            checks["causal_action_or_clue"] = "WARN"
        if order in {32, 36}:
            checks["cross_panel_canon"] = semantic
        style_prefix = {"PASS": "Visually satisfies", "WARN": "Borderline against", "FAIL": "Exceeds"}[style]
        rows.append({
            "display_order": order,
            "panel_id": plan["panel_id"],
            "plan_revision_id": plan["plan_revision_id"],
            "narrative_beat": plan["narrative_beat"],
            "candidate_id": entry["candidate_id"],
            "candidate_sha256": entry["source"]["sha256"],
            "native_dimensions": {"width": entry["source"]["width"], "height": entry["source"]["height"]},
            "status": overall,
            "status_scope": "worst of semantic/causal, lettering clearance, 390px phone readability, and strict 3-5-mass style",
            "semantic_status": semantic,
            "semantic_note": semantic_note,
            "lettering_status": lettering,
            "lettering_note": lettering_note,
            "phone_status": phone,
            "phone_note": "Required beat remains readable in the 390px viewport." if phone == "PASS" else "A fine causal clue remains visible but ambiguous at 390px width.",
            "style_status": style,
            "dominant_mass_assessment": "3-5" if style == "PASS" else "approximately 5-7" if style == "WARN" else "more than 5 and/or distributed texture",
            "style_note": f"{style_prefix} the strict 3-5 dominant-mass, localized-texture rubric: {DETAIL_FIELDS[order - 1]}.",
            "primary_issue_class": primary,
            "mature_identity_hair_wardrobe_note": continuity_note(order, plan["visible_adult_cast"]),
            "checks": checks,
            "human_review_state": "PENDING",
            "human_review_minutes": None,
            "accepted": False,
            "rights_cleared": False,
            "commercially_cleared": False,
            "exact_production_base": False,
        })

    counts = lambda field: {key.lower(): sum(row[field] == key for row in rows) for key in ("PASS", "WARN", "FAIL")}
    overall_counts, semantic_counts = counts("status"), counts("semantic_status")
    lettering_counts, phone_counts, style_counts = counts("lettering_status"), counts("phone_status"), counts("style_status")
    summary = {
        "chapter_panels": 50,
        **{f"overall_{key}": value for key, value in overall_counts.items()},
        **{f"semantic_{key}": value for key, value in semantic_counts.items()},
        **{f"lettering_{key}": value for key, value in lettering_counts.items()},
        **{f"phone_{key}": value for key, value in phone_counts.items()},
        **{f"style_{key}": value for key, value in style_counts.items()},
        "strict_style_compliance_rate": style_counts["pass"] / 50,
        "visible_adult_cast_panels": 32,
        "mature_identity_hair_wardrobe_pass": 32,
        "zero_cast_panels_without_people": 18,
        "strongest_shortlist": len(STRONGEST),
        "human_reviewed": 0,
        "accepted": 0,
    }
    sheet = build_sheet(entries, rows, summary)
    input_paths = (PLAN, PROMPT, EXECUTION, ASSEMBLY, BUILD_REPORT)
    document = {
        "record_type": "CH05CompleteChapterReducedPaletteTextControlAgentTriage",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-reduced-palette-text-control-agent-triage-r1",
        "state": "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in input_paths],
        "inspection_basis": {
            "native_pixels": "All 50 hash-bound crops inspected at native resolution.",
            "phone_scale": "All ten deterministic 390x844 viewport images, covering all 50 panels, inspected.",
            "lettering": "All 50 canonical safe-zone overlays inspected at native resolution; transparent overlap only avoids failure when face, silhouette, action, and story-object readability remain intact.",
            "style": "Manual visual count against the prompt's strict 3-5 dominant-mass and localized-texture rubric; this is not an automated color-cluster measurement.",
        },
        "inspection_artifacts": build_report["artifacts"],
        "summary": summary,
        "semantic_failures": [{"panel": order, "issue": SEMANTIC[order][1], "note": SEMANTIC[order][2]} for order in (8, 36, 50)],
        "semantic_warnings": [{"panel": order, "issue": SEMANTIC[order][1], "note": SEMANTIC[order][2]} for order in (3, 12, 32, 44)],
        "gate_transfer": {
            "cold_farmhouse_until_reversal": "PASS",
            "departure_vector": "PASS",
            "independent_entry_roles": "PASS",
            "near_bank_prints_stop": "PASS",
            "far_bank_prints_face_back": "WARN_ORIENTATION_AMBIGUOUS",
            "tin_high_on_beam": "PASS",
            "continuous_leverage_force_path": "FAIL_TWO_DISCONNECTED_PLANKS",
            "same_tin_open_beside_retained_map": "PASS",
            "third_upstream_mark_at_torn_edge": "PASS",
            "drum_fully_out": "PASS",
            "map_retained_during_retreat": "PASS",
            "same_map_hidden_under_wrap": "PASS",
            "first_new_farmhouse_smoke": "PASS",
            "stove_not_lit_before_departure": "PASS_VISUAL_REALIZATION",
        },
        "continuity_result": {
            "result": "PASS_32_OF_32_VISIBLE_CAST_PANELS",
            "SOREN": "swept wavy light-brown/dark-blond hair, mature stubbled face, pale oatmeal work coat",
            "SIGRID": "dark-brown/near-black tied-back hair, mature angular face, dark blue-brown plaid wrap",
            "note": "All 32 planned cast panels preserve mature fictional-adult presentation and role-correct wardrobe/hair; planned inserts bind identity through wardrobe. This is fictional-character continuity review, not biometric recognition.",
        },
        "style_hypothesis_result": {
            "result": "PARTIAL_STRICT_COMPLIANCE_12_OF_50",
            "pass_rate": 0.24,
            "pass_panels": sorted(STYLE_PASS),
            "warn_panels": sorted(STYLE_WARN),
            "finding": "Palette restraint and continuity are strong, but 31 panels exceed the strict mass/texture budget. The best compliance occurs in profiles, clue inserts, and broad landscapes with deliberate negative space.",
        },
        "strongest_shortlist": [{"display_order": order, "panel_id": rows[order - 1]["panel_id"], "candidate_id": rows[order - 1]["candidate_id"], "candidate_sha256": rows[order - 1]["candidate_sha256"], "status": "PASS"} for order in STRONGEST],
        "rows": rows,
        "triage_sheet": sheet,
        "recommendation": "Do not promote or accept the arm wholesale. Preserve P010, P014, P035, P040, P041, and P046 as the strongest all-axis review candidates. Correct P008, P036, and P050 with minimal targeted changes; relocate or gutter the 27 failed lettering zones; retain the reduced palette while enforcing broad background silhouettes and localized detail budgets on dense action/environment panels.",
        "limitations": [
            "This is rigorous but non-gating agent visual triage; owner review remains pending.",
            "Semantic, style, identity, lettering, and phone judgments are manual observations of generated pixels.",
            "Strict style mass bands are perceptual rubric classifications, not automated segmentation or unique-color counts.",
            "A PASS does not establish acceptance, rights, commercial clearance, or exact production-base status.",
            "No identical generation was repeated, so stochastic reproducibility remains unmeasured.",
        ],
        "boundary": "Review evidence only; no acceptance, rights clearance, commercial clearance, canon replacement, exact production-base selection, AnimationShotPlan, or E-Conte decision.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({**summary, "output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "sheet": sheet}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
