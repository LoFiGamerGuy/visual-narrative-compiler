"""Compile deterministic non-gating triage for the full CH05 flat-gouache arm."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-assembly-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-complete-chapter-flat-graphic-gouache-agent-triage-r1.json"
SHEET = ROOT / "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/review/ch05-complete-chapter-flat-graphic-gouache-triage-sheet-r1.png"

SEMANTIC: dict[int, tuple[str, str | None, str]] = {
    1: ("FAIL", "departure_and_reversal", "Both adults move uphill toward the farmhouse, and its chimney already emits smoke; this fails both downhill-away departure geography and the cold-house opening."),
    2: ("PASS", None, "Sigrid, the map, her circled/fingered location, and the external smoke direction are all visible in one over-shoulder frame."),
    3: ("WARN", "track_overlap", "Soren's held-back boot and multiple prints read, but fresh-over-old overlap is subtle at phone width."),
    4: ("PASS", None, "Soren and Sigrid exchange a readable look from opposite sides of the frame."),
    5: ("PASS", None, "A shallow rain-fed runnel crosses the trail with no people present."),
    6: ("PASS", None, "Sigrid steps first and points toward the older wheel-marked stone while Soren waits behind."),
    7: ("PASS", None, "The marker carries one clear mill-wheel glyph and no name."),
    8: ("WARN", "map_fold_state", "Soren's hands visibly fold the map, but the single image cannot prove that the farmhouse section becomes hidden while the creek remains exposed."),
    9: ("FAIL", "role_order", "Soren is farther ahead on the narrow trail while Sigrid follows; the plan requires Sigrid to lead."),
    10: ("PASS", None, "Sigrid's listening profile is held against dark, empty woods before the water is shown."),
    11: ("PASS", None, "A hand pinches soot-dark twine where it catches on a wet thorn."),
    12: ("WARN", "twine_direction", "The taut diagonal twine is clear, but the empty ground provides no reliable downhill direction cue."),
    13: ("PASS", None, "The pair descend beside the creek with Sigrid leading and Soren following."),
    14: ("PASS", None, "The ridge shoulder occludes the previously tracked smoke in a people-free landscape beat."),
    15: ("PASS", None, "Sigrid's wet thumb visibly obscures the creek line on the map."),
    16: ("PASS", None, "Both adults continue walking without facing each other while Soren gestures through his deduction."),
    17: ("PASS", None, "The abandoned mill, broken roofline, creek, and bridge establish the destination clearly."),
    18: ("PASS", None, "The smoke column rises on the ridge behind the mill rather than from the mill chimney."),
    19: ("PASS", None, "Sigrid's stop hand blocks the open bridge route while Soren visibly holds back."),
    20: ("PASS", None, "The adults cross below the bridge on separated stepping stones with readable weight shifts."),
    21: ("PASS", None, "A newly tied red cloth strip hangs and moves from the wet lower branch."),
    22: ("PASS", None, "Soren's stopping hand intercepts Sigrid's reaching hand before either touches the red cloth."),
    23: ("PASS", None, "Both adults circle toward the mill's collapsed loading opening through wet grass."),
    24: ("PASS", None, "A thin smoke thread reveals the metal drum behind the stone wall."),
    25: ("PASS", None, "The overhead drum view shows wet needles, pooled moisture, and one damp ember."),
    26: ("PASS", None, "Sigrid holds her open hand above the ember without disturbing it; the smoke/heat line separates her fingers."),
    27: ("PASS", None, "Soren tracks a second taut twine line through a dark opening in the mill wall."),
    28: ("PASS", None, "The taut line is visibly tied to the small brass bell inside the doorway."),
    29: ("PASS", None, "Sigrid enters through the wall opening while Soren independently watches the exterior; their gaze directions differ."),
    30: ("PASS", None, "Daylight bars, standing water, and broken gears establish the empty mill interior."),
    31: ("PASS", None, "Sigrid crouches beside dry footprints that stop cleanly at the near water edge."),
    32: ("WARN", "far_bank_footprint_orientation", "Prints begin on far dry ground, but their heel-toe asymmetry and orientation back toward Soren remain ambiguous at native and phone scale."),
    33: ("WARN", "different_depths", "The drip, ringing bell, and two frozen adults read, but the intended difference in their depths is modest rather than unmistakable."),
    34: ("PASS", None, "Both adults remain stationary on opposite sides of the empty doorway and neither approaches the bell."),
    35: ("PASS", None, "The sealed tin remains isolated high on an upper beam in daylight."),
    36: ("PASS", None, "One continuous plank connects Sigrid's brace to Soren's grip and the high tin contact, producing a readable leverage path."),
    37: ("PASS", None, "The same opened tin is presented with dry matches, creek map, and blank note card on the stone."),
    38: ("PASS", None, "The map clearly distinguishes a square farmhouse mark from a circular mill mark."),
    39: ("WARN", "third_upstream_mark_identity", "Three symbols are visible at once, including a second circle on a torn extension upstream, but the repeated-circle design and detached-looking fragment weaken certainty that it is the distinct third mark at the same torn edge."),
    40: ("PASS", None, "Sigrid's calm profile and alert gaze support the signal-not-campfire deduction beat."),
    41: ("PASS", None, "The rain-soaked drum is fully out with no ember, flame, glow, or smoke plume."),
    42: ("PASS", None, "The creek-side doorway, taut line, and vibrating bell establish the second ring's new direction."),
    43: ("FAIL", "map_possession", "The open tin and creek map remain together on the stone as both adults retreat; no retained map is visible on Sigrid, breaking the P037-P043-P046 possession chain."),
    44: ("PASS", None, "Soren's pocket knife contacts and severs the taut twine with both hands safely clear of the cutting edge."),
    45: ("PASS", None, "The empty creek and mill hold in silence after the cut with no renewed bell motion."),
    46: ("PASS", None, "Sigrid visibly tucks the retained creek map inside her plaid wrap."),
    47: ("PASS", None, "Both adults climb uphill toward the farmhouse under a cleared sky with no chimney smoke visible; lit windows do not alter the explicit no-smoke beat."),
    48: ("PASS", None, "The farmhouse becomes the distant destination and its chimney shows the chapter's first new smoke after the failed opening is discounted."),
    49: ("PASS", None, "Soren looks back from the map toward the smoking farmhouse, clearly staging his realization that the stove was not lit."),
    50: ("PASS", None, "Sigrid leads the uphill run toward the house while Soren follows carrying the map; footfalls and cloth provide causal motion."),
}

LETTERING: dict[int, tuple[str, str]] = {
    1: ("PASS", "Top-left zone stays in open sky and preserves both adults, the farmhouse, and travel silhouette."),
    2: ("FAIL", "Top-right zone covers the smoke column used for the map-direction comparison."),
    3: ("WARN", "Top-left zone overlaps Soren's coat hem but leaves the boot and principal print chain readable under transparency."),
    4: ("FAIL", "Top-right zone covers Sigrid's hair, forehead, and upper face."),
    5: ("FAIL", "Top zone sits directly over the runnel, the only story object in the insert."),
    6: ("PASS", "Top-right sky remains clear of faces, pointing hand, marker, and movement silhouettes."),
    7: ("FAIL", "Top zone covers the upper arc and spokes of the mill-wheel glyph."),
    8: ("FAIL", "Top-right zone covers Soren's right hand and the folded map edge."),
    9: ("PASS", "Top-left zone remains in dark foliage above the adult silhouettes."),
    10: ("PASS", "Top-right zone occupies empty woods away from Sigrid's face and listening silhouette."),
    11: ("WARN", "Top-left zone covers the oatmeal sleeve but leaves fingers, thorn, and twine contact visible under transparency."),
    12: ("FAIL", "Top zone crosses the taut twine, the panel's sole causal clue."),
    13: ("FAIL", "Top-left zone covers Soren's head and shoulder and interrupts his following silhouette."),
    14: ("PASS", "Top zone remains open sky over the smoke-occluding ridge."),
    15: ("FAIL", "Top-left zone covers the creek map, a required story prop."),
    16: ("WARN", "Top-right zone grazes Sigrid's hairline but leaves her eyes, expression, body silhouette, and Soren's gesture clear under transparency."),
    17: ("FAIL", "Top zone covers the mill's broken roofline, the reveal's defining shape."),
    18: ("FAIL", "Top zone covers the smoke column whose separation from the mill chimney is the entire clue."),
    19: ("FAIL", "Top-left zone covers Sigrid's hair, forehead, and upper face."),
    20: ("PASS", "Top-right zone sits on unused far-bank ground, clear of both adults and stepping stones."),
    21: ("WARN", "Top zone overlaps the supporting branch but leaves the red cloth knot and hanging silhouette readable under transparency."),
    22: ("PASS", "Top-right zone is empty sky and preserves both important hands and the cloth marker."),
    23: ("PASS", "Top-left zone stays in sky and distant smoke, clear of the adults and collapsed loading opening central to this beat."),
    24: ("FAIL", "Top zone covers the thin drum-smoke thread that reveals the hidden source."),
    25: ("FAIL", "Top zone covers the damp smoke wisp and wet-needle field inside the drum."),
    26: ("WARN", "Top-right zone overlaps Sigrid's tied hair but leaves her face, heat-testing hand, smoke, and drum rim readable under transparency."),
    27: ("FAIL", "Top-left zone covers Soren's hair and forehead, weakening both face and hair-continuity review."),
    28: ("PASS", "Top zone remains above the bell and taut line without covering either clue."),
    29: ("FAIL", "Top-left zone covers Soren's hair and upper face during the required exterior-watch role split."),
    30: ("PASS", "Top zone uses high rafters and preserves the broken gears, water, and navigable interior."),
    31: ("FAIL", "Top-left zone covers Sigrid's tied hair and upper face."),
    32: ("PASS", "Top-right zone occupies background machinery, clear of Soren and the far-bank footprint chain."),
    33: ("FAIL", "Top-left zone covers Sigrid's hair, forehead, and upper face."),
    34: ("FAIL", "Top-right zone covers Soren's head and upper torso, weakening the held two-person blocking."),
    35: ("PASS", "Top zone remains above the isolated tin and leaves the high-beam relationship readable."),
    36: ("PASS", "Top-right zone stays in open daylight and clears both adults, their grips, the plank, and tin contact."),
    37: ("FAIL", "Top zone covers the open tin rim and upper map area in the object spread."),
    38: ("FAIL", "Top zone covers the map's upstream creek path, an important deduction object."),
    39: ("FAIL", "Top-left zone covers Soren's hair and upper face in the clue close-up."),
    40: ("PASS", "Top-right zone remains empty sky away from Sigrid's face and deduction silhouette."),
    41: ("PASS", "Top zone stays above the closed drum body; only the nonessential handle edge approaches the zone."),
    42: ("WARN", "Top zone crosses the creek view through the doorway but leaves the bell and taut line readable under transparency."),
    43: ("FAIL", "Top-left zone covers Soren's hair and upper head during the retreat."),
    44: ("FAIL", "Top-right zone crosses the taut twine immediately beyond the knife contact point."),
    45: ("PASS", "Top zone uses empty sky and preserves the mill, creek, and still bell."),
    46: ("PASS", "Top-right zone is open sky and clears Sigrid's face, hands, wrap, and retained map."),
    47: ("PASS", "Top-left zone is open sky away from both climbing adults and the farmhouse."),
    48: ("PASS", "Top zone is open sky left of the farmhouse and new smoke column."),
    49: ("FAIL", "Top-left zone covers Soren's hair and forehead in the realization close-up."),
    50: ("FAIL", "Top-right zone covers Sigrid's face and overlaps the urgent destination/smoke area."),
}

DENSITY_VIOLATIONS = [
    "terrain and cloth", "map and cloth", "mud, prints, and coat", "faces, hair, cloth, and terrain", "pebble terrain and water",
    "clothing and terrain", "stone and moss", "map and coat", "forest and cloth", "face, hair, and forest",
    "skin, thorn, and coat", "terrain and twine", "terrain, cloth, and water", "terrain and mountain", "map and skin",
    "faces, cloth, and terrain", "mill timber, stone, and terrain", "forest, mill, and smoke", "cloth, bridge, and terrain", "water, terrain, and cloth",
    "bark, fabric, and grass", "hands, fabric, and bark", "cloth, building, stone, and grass", "stone, grass, and rust", "needles, rust, and water",
    "face, skin, cloth, and wood", "face, coat, and wood", "brass, wood, and twine", "cloth, wood, stone, and terrain", "wood, stone, water, and gears",
    "cloth, stone, water, and prints", "coat, stone, water, and prints", "faces, cloth, wood, water, and bell", "cloth, wood, stone, and water", "wood, stone, and tin",
    "timber, cloth, and water", "rock, map, matches, and tin", "map contour and paper", "map, paper, skin, and cloth", "face, hair, cloth, and landscape",
    "rain, metal, and grass", "wood, brass, and water", "cloth, wood, stone, and props", "skin, metal, twine, and water", "mill, timber, rock, water, and grass",
    "hair, cloth, map, and landscape", "terrain, cloth, and architecture", "terrain, architecture, trees, and smoke", "face, hair, coat, map, and terrain", "cloth, mud, terrain, and architecture",
]

PHONE_WARN = {3, 12, 18, 24, 27, 32, 33}
STRONGEST_ORDERS = [6, 10, 14, 20, 22, 23, 28, 30, 35, 36, 40, 41, 45, 46, 47, 48]
CHECK_KEYS = (
    "role_binding", "role_order", "visible_adult_count", "shared_set_and_blocking",
    "target_change_behavior", "causal_action_or_clue", "hair_and_wardrobe",
    "lettering_clearance", "phone_readability", "cross_panel_canon",
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


def wrap(draw: ImageDraw.ImageDraw, value: str, chosen: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in value.split():
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=chosen)[2] <= width:
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


def worst(*statuses: str) -> str:
    rank = {"PASS": 0, "WARN": 1, "FAIL": 2}
    return max(statuses, key=rank.__getitem__)


def hair_observation(order: int, cast: list[str]) -> str:
    if not cast:
        return "No adult is visible as planned; this insert does not exercise hair or wardrobe continuity."
    partial = {
        3: "Soren is identified by the pale oatmeal coat and boot; hair is intentionally outside this low insert.",
        8: "Soren is identified by both oatmeal-coated sleeves and adult hands; hair is intentionally outside this hand/map insert.",
        11: "Soren is identified by the oatmeal sleeve and adult hand; hair is intentionally outside this hand/twine insert.",
        15: "Sigrid is identified by the plaid-wrap cuff and adult hand; hair is intentionally outside this map insert.",
        22: "Sigrid's plaid sleeve and Soren's oatmeal sleeve bind the two adult hands correctly; hair is outside the insert.",
        44: "Soren is identified by oatmeal sleeves and adult hands; hair is intentionally outside this knife/twine insert.",
    }
    if order in partial:
        return partial[order]
    if cast == ["SOREN"]:
        return "Soren retains light-brown/dark-blond hair and the pale oatmeal work coat; no role-color or wardrobe swap is visible."
    if cast == ["SIGRID"]:
        return "Sigrid retains dark-brown/near-black tied hair and the dark blue-brown plaid wrap; no role-color or wardrobe swap is visible."
    return "Soren retains light-brown/dark-blond hair with the pale oatmeal coat, and Sigrid retains dark tied hair with the dark plaid wrap; roles do not swap."


def build_sheet(entries: list[dict[str, Any]], rows: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    by_panel = {row["panel_id"]: row for row in rows}
    columns, tile_w, tile_h, gap, margin, header = 5, 300, 254, 14, 24, 112
    grid_rows = math.ceil(len(entries) / columns)
    canvas = Image.new("RGB", (1604, header + margin + grid_rows * tile_h + (grid_rows - 1) * gap), "#e7e3da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 16), "CH05 FLAT-GRAPHIC GOUACHE R1 - AGENT TRIAGE", fill="#20252a", font=selected_font(26, True))
    draw.text((margin, 54), f"{summary['pass']} PASS | {summary['warn']} WARN | {summary['fail']} FAIL | lettering {summary['lettering_pass']}/{summary['lettering_warn']}/{summary['lettering_fail']} | owner review pending", fill="#3b454d", font=selected_font(17))
    draw.text((margin, 80), "Narrative + lettering status; strict density fails 50/50 separately. Green is not acceptance or clearance.", fill="#695848", font=selected_font(14))
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
        draw.text((x + 10, y + 8), f"{entry['order']:02d}  {entry['panel_id'].split('-')[-1].upper()}  {row['status']}", fill=color, font=selected_font(16, True))
        framed = ImageOps.contain(panel, (tile_w - 18, 165), Image.Resampling.LANCZOS)
        canvas.paste(framed, (x + (tile_w - framed.width) // 2, y + 38 + (165 - framed.height) // 2))
        label = (row["primary_issue_class"] or "no blocking issue").replace("_", " ")
        for line_no, line in enumerate(wrap(draw, label, selected_font(13), tile_w - 20)):
            draw.text((x + 10, y + 212 + line_no * 16), line, fill="#343b41", font=selected_font(13))
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(SHEET, format="PNG", compress_level=6, optimize=False)
    return {"path": SHEET.relative_to(ROOT).as_posix(), "sha256": sha256(SHEET), "width": canvas.width, "height": canvas.height, "bytes": SHEET.stat().st_size, "tracked": False}


def main() -> int:
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    entries = sorted(assembly["entries"], key=lambda row: row["order"])
    if len(plans) != 50 or len(entries) != 50 or [p["panel_id"] for p in plans] != [e["panel_id"] for e in entries]:
        raise ValueError("assembly differs from canonical 50-panel ComicPanelPlan order")
    if set(SEMANTIC) != set(range(1, 51)) or set(LETTERING) != set(range(1, 51)) or len(DENSITY_VIOLATIONS) != 50:
        raise ValueError("triage dictionaries must cover exactly P001-P050")

    rows: list[dict[str, Any]] = []
    for plan, entry in zip(plans, entries, strict=True):
        order = plan["display_order"]
        semantic_status, semantic_issue, semantic_note = SEMANTIC[order]
        lettering_status, lettering_note = LETTERING[order]
        phone_status = "WARN" if order in PHONE_WARN else "PASS"
        status = worst(semantic_status, lettering_status, phone_status)
        primary_issue = semantic_issue if semantic_status != "PASS" else "lettering_safe_zone" if lettering_status != "PASS" else "phone_readability" if phone_status != "PASS" else None
        checks = {key: "PASS" for key in CHECK_KEYS}
        checks["lettering_clearance"] = lettering_status
        checks["phone_readability"] = phone_status
        if order == 9:
            checks["role_order"] = "FAIL"
        if order == 8:
            checks["target_change_behavior"] = "WARN"
        if order in {3, 12, 33}:
            checks["causal_action_or_clue"] = semantic_status
        if order in {1, 32, 39, 43}:
            checks["cross_panel_canon"] = semantic_status
        rows.append({
            "display_order": order,
            "panel_id": plan["panel_id"],
            "plan_revision_id": plan["plan_revision_id"],
            "candidate_id": entry["candidate_id"],
            "candidate_sha256": entry["source"]["sha256"],
            "native_dimensions": {"width": entry["source"]["width"], "height": entry["source"]["height"]},
            "status": status,
            "status_scope": "semantic/causal, canonical lettering clearance, and 390px phone readability; strict style-density is reported independently",
            "semantic_status": semantic_status,
            "primary_issue_class": primary_issue,
            "note": f"{semantic_note} Lettering: {lettering_note}",
            "semantic_note": semantic_note,
            "hair_and_wardrobe_observation": hair_observation(order, plan["visible_adult_cast"]),
            "lettering_clearance_note": lettering_note,
            "phone_readability_note": "The required beat remains legible in the 390px review viewport." if phone_status == "PASS" else "The required fine-scale clue or depth distinction remains visible but ambiguous in the 390px review viewport.",
            "style_density_compliance": "FAIL_STRICT",
            "style_density_note": f"The frame exceeds the requested 4-6 broad-mass, minimal-local-texture limit through dense {DENSITY_VIOLATIONS[order - 1]} rendering; it reads as detailed painterly clear-line art rather than low-density flat gouache.",
            "checks": checks,
            "human_review_state": "PENDING",
            "human_review_minutes": None,
            "accepted": False,
            "commercially_cleared": False,
            "exact_production_base": False,
        })

    overall = {key: sum(row["status"] == key for row in rows) for key in ("PASS", "WARN", "FAIL")}
    semantic_counts = {key: sum(row["semantic_status"] == key for row in rows) for key in ("PASS", "WARN", "FAIL")}
    lettering_counts = {key: sum(row["checks"]["lettering_clearance"] == key for row in rows) for key in ("PASS", "WARN", "FAIL")}
    summary = {
        "chapter_panels": 50,
        "pass": overall["PASS"], "warn": overall["WARN"], "fail": overall["FAIL"],
        "semantic_pass": semantic_counts["PASS"], "semantic_warn": semantic_counts["WARN"], "semantic_fail": semantic_counts["FAIL"],
        "lettering_pass": lettering_counts["PASS"], "lettering_warn": lettering_counts["WARN"], "lettering_fail": lettering_counts["FAIL"],
        "phone_pass": 50 - len(PHONE_WARN), "phone_warn": len(PHONE_WARN), "phone_fail": 0,
        "style_density_pass": 0, "style_density_warn": 0, "style_density_fail_strict": 50,
        "hair_and_wardrobe_pass": 50,
        "role_correct_hair_and_wardrobe_pass": 50,
        "cross_panel_gates_pass": 3, "cross_panel_gates_warn": 2, "cross_panel_gates_fail": 3,
        "strongest_shortlist": len(STRONGEST_ORDERS), "human_reviewed": 0, "accepted": 0,
    }
    sheet = build_sheet(entries, rows, summary)
    strongest = [{"display_order": order, "panel_id": rows[order - 1]["panel_id"], "candidate_id": rows[order - 1]["candidate_id"], "candidate_sha256": rows[order - 1]["candidate_sha256"], "status": "PASS"} for order in STRONGEST_ORDERS]
    document = {
        "record_type": "CH05CompleteChapterAgentTriage",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-flat-graphic-gouache-agent-triage-r1",
        "display_title": "CH05 FLAT-GRAPHIC GOUACHE R1 - AGENT TRIAGE",
        "state": "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in (PLAN, ASSEMBLY)],
        "inspection_basis": {
            "native_pixels": "All 50 hash-bound split crops inspected at native detail.",
            "phone_scale": "All 50 panels inspected in deterministic 390px-wide viewport packets.",
            "lettering": "All 50 canonical safe-zone overlays inspected; clearance statuses assume the full proposed rectangle and separately note where transparency may preserve readability.",
        },
        "summary": summary,
        "role_continuity": {
            "result": "PASS_50_OF_50_WITH_PLANNED_PARTIAL_INSERTS",
            "SOREN": "light-brown/dark-blond hair and pale oatmeal work coat",
            "SIGRID": "dark-brown/near-black tied hair and dark blue-brown plaid wrap",
            "note": "No role-color swap or wardrobe loss was observed. Hair is not visible in planned hand/boot inserts; those rows bind role through approved wardrobe. This is manual fictional-character continuity review, not biometric recognition.",
        },
        "gate_transfer": {
            "cold_farmhouse_until_reversal": "FAIL_P001_PREMATURE_SMOKE",
            "departure_vector": "FAIL_P001_UPHILL_TOWARD_HOUSE",
            "independent_entry_roles": "PASS",
            "impossible_far_bank_prints": "WARN_ORIENTATION_AMBIGUOUS",
            "continuous_leverage_force_path": "PASS",
            "third_upstream_mark": "WARN_DISTINCT_IDENTITY_AND_TORN_EDGE_AMBIGUOUS",
            "drum_fully_out": "PASS",
            "map_possession": "FAIL_P043_MAP_LEFT_WITH_TIN",
        },
        "style_hypothesis_result": {
            "result": "FAIL_STRICT_DENSITY_0_OF_50",
            "requested_test": "flat graphic gouache with 4-6 broad value masses and minimal texture localized only at active clue/contact",
            "observed": "All 50 panels retain dense surface modeling across terrain, cloth, hair, wood, stone, water, maps, or metal. The arm is visually coherent but functions as detailed painterly clear-line art rather than the requested lower-density style.",
            "production_value": "Narrative staging, adult-role continuity, action clarity, and cadence remain useful evidence even though the style-density hypothesis fails.",
        },
        "strongest_shortlist": strongest,
        "rows": rows,
        "triage_sheet": sheet,
        "recommendation": "Do not promote the arm wholesale or call it flat/low-density. Preserve the 16 full-status passes as chapter-sequence evidence; repair P001, P009, and P043 semantics first, then relocate canonical lettering zones or recompose the 25 collisions. Retest the low-density hypothesis with explicit texture-budget controls rather than reusing this style label.",
        "limitations": [
            "Agent triage is non-gating and owner review remains pending.",
            "Hair, wardrobe, role, action, style, lettering, and canon judgments are manual visual observations.",
            "Lettering clearance evaluates the complete canonical safe-zone rectangle; a smaller or more transparent final balloon may reduce some WARN cases but does not cure face, hand, or story-object FAIL collisions.",
            "Prompt compliance and a PASS label do not establish acceptance, rights, commercial clearance, or exact production-base status.",
            "Built-in product model, endpoint, request ID, seed, usage, and monetary cost are unavailable.",
            "No identical request was repeated; stochastic reproducibility remains unmeasured.",
        ],
        "boundary": "Review evidence only; no acceptance, commercial clearance, canon replacement, exact production-base selection, AnimationShotPlan, or E-Conte decision.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({**summary, "output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "sheet": sheet}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
