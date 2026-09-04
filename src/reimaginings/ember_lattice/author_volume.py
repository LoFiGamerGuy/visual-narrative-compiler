from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from volume_story_data import (
    ACTION_ORDERS,
    CHAPTER_BEATS,
    CHAPTER_TITLES,
    CHAPTER_ZONES,
    DIALOGUE,
    HIGH_ORDERS,
    MODERATE_ORDERS,
    SYSTEM_PANELS,
)


ROOT = Path(__file__).resolve().parents[3]
PROD = ROOT / "production" / "reimaginings" / "ember-lattice"
VOLUME = PROD / "volume"

STYLE_BLOCK = """Use case: illustration-story
Asset type: one finished source-art panel for a vertical-scroll action manhwa; no lettering baked into art
Style/medium: original clean modern action-anime/manhwa illustration matching the registered Candidate B anchor; crisp tapered charcoal contour; simplified mature adult anime facial geometry; controlled two-step cel shading; sparse dry-brush only at impact; not painterly fantasy
Color palette: charcoal, muted teal, aged ivory, restrained brass, exactly one localized ember-orange focal accent when the beat calls for magic or a fault
Composition: one moment only; strong readable silhouette; clear foreground/midground separation; phone-first value grouping; reserved low-detail negative space at the declared lettering edge; action vectors and contact readable without text
Adult cast contract: all humans are fictional adults with mature facial proportions, shoulders, hands, practical non-sexualized gear, and predominantly fair/light complexions as individually registered; preserve each distinct face, hair, build, costume, weapon, injury, and role silhouette
Density contract: honor the declared low/moderate/high panel density; low means one dominant subject or action over a flat, graded, blurred, silhouette, or simplified environment, not microtexture
Constraints: no text, letters, numbers, fake glyphs, caption, balloon, speech bubble, dialogue box, menu, status card, interface rectangle, watermark, signature, logo, title, border, panel grid, split-screen, inset, collage, multiple moments, child, teenager, sexualization, gore, copied character, named franchise style, or living-artist imitation
Avoid: generic painterly fantasy splash art; blue holographic UI; blanket particles; decorative filigree; muddy facial values; dark complexion drift; crowd clutter; unreadable weapon grip; effects hiding contact"""

CHARACTER_PROMPTS = {
    "Elian": "Elian Voss, fictional adult man age 27, fair/light peach-beige warm complexion, lean long-limbed mature build, diamond face, narrow green eyes, ash-blond short hair over charcoal underlayer and forked forelock, gray-green knee coat, ivory wrap shirt, charcoal trousers; current chapter equipment and injuries must remain exact",
    "Mira": "Mira Vale, fictional adult woman age 32, light peach freckled complexion, tall athletic mature build, broad heart face, steel-gray eyes, copper-red angular bob with shaved right temple, charcoal/teal brigandine, matte ivory split shield, current long spear form exact",
    "Orin": "Orin Pell, fictional adult man age 41, light neutral-olive beige complexion, broad compact mature build, square face, hazel eyes, dark hair graying at temples, short boxed beard, rust-red forge apron, brass-rimmed left monocle, current kiln-satchel state exact",
    "Sable": "Sable Renn, fictional adult woman age 35, fair cool complexion, wiry mature build, narrow face, amber eyes, black undercut swept left with one silver temple streak, black-plum Pathcutter coat, white diagonal shoulder guard, segmented straight saber, restrained charcoal-ember debt cord",
    "Delver": "rescued fictional adult delver age 38, light beige complexion, stocky mature build, shaved brown hair, plain ochre maintenance coat; clearly distinct from principal cast",
}

CHAPTER_CAST = {
    1: ["Elian", "Mira"], 2: ["Elian", "Mira"], 3: ["Elian", "Mira", "Orin"],
    4: ["Elian", "Mira", "Orin", "Sable"], 5: ["Elian", "Mira", "Orin"],
    6: ["Elian", "Mira", "Orin"], 7: ["Elian", "Mira", "Orin"],
    8: ["Elian", "Mira", "Orin", "Sable"], 9: ["Elian", "Mira", "Orin", "Sable"],
    10: ["Elian", "Mira", "Orin", "Sable"],
}

MONSTER_PROMPTS = {
    1: "Belljaw Warden: invented ivory ceramic quadruped with a literal bell-shaped hinged jaw, black mechanical joints, broad forelimbs, one broken ankle seam; no dragon anatomy",
    2: "Cinder Mites: three invented palm-sized ivory beetle mechanisms with ember abdomens and chain-cutting mandibles; keep only three readable bodies",
    3: "Glassback Skitter: invented six-legged low creature with one transparent mineral wedge carapace, blunt head, pale resonant edge; no spider horror clutter",
    4: "Crownspike Bailiff: invented tall ivory-and-brass bipedal guardian, one vertical crown spike, migrating geometric chest sigil; faceless mechanical anatomy",
    6: "Mire Choir: exactly three invented reed-bodied amphibious constructs sharing one breath rhythm, teal ceramic bodies and ivory throat slits",
    7: "Collapse Hound: invented broad ivory ceramic quadruped with counterweight tail and load-bearing jaw, built to bite structural seams; not canine fur",
    8: "Brass Maw: invented squat ring-bodied cistern predator with exactly three hinged brass jaw arcs and one resonant central throat",
    9: "Crown Guards: at most three invented ivory cable guardians with simple hooked limbs and linked knee mechanisms",
    10: "Bell Regent: invented towering ivory bell torso on four long jointed mechanical legs, suspended crown yoke and hollow face aperture; climbs, never flies; stable monumental silhouette",
}

CAMERA_ACTION = [
    "side-on wide causal staging", "low three-quarter motion", "tight contact with plausible grip", "over-shoulder tactical read",
    "ground-level lateral tracking", "vertical follow-through", "medium consequence profile", "high-angle geography",
]
CAMERA_QUIET = [
    "vertical establishing wide", "clean medium two-shot", "expressive mature close-up", "controlled object insert",
    "calm negative-space wide", "over-shoulder decision view",
]

POS = {
    "tl": (0.04, 0.04), "tr": (0.58, 0.04), "tc": (0.30, 0.04),
    "bl": (0.04, 0.76), "br": (0.58, 0.76), "bc": (0.30, 0.76),
}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def density(chapter: int, order: int) -> str:
    if order in HIGH_ORDERS[chapter]:
        return "high"
    if order in MODERATE_ORDERS[chapter]:
        return "moderate"
    return "low"


def named_subjects(chapter: int, beat: str) -> list[str]:
    subjects = [name for name in CHARACTER_PROMPTS if name in beat]
    if any(token in beat.lower() for token in ("party", "group", "four adults", "three adults")):
        subjects.extend(CHAPTER_CAST[chapter])
    return list(dict.fromkeys(subjects))


def make_box(position: str, text: str, mode: str, line_count: int | None = None) -> list[float]:
    x, y = POS[position]
    if mode == "system":
        width = 0.39
        height = min(0.31, 0.075 + 0.037 * (line_count or 4))
    elif mode == "caption":
        width = 0.42
        height = min(0.15, 0.07 + 0.012 * math.ceil(len(text) / 40))
    else:
        width = 0.34 if mode in {"soft", "open", "distress"} else 0.39
        chars_per_line = 22 if width < 0.37 else 26
        lines = max(2, math.ceil(len(text) / chars_per_line))
        height = min(0.245, 0.055 + 0.031 * lines)
    if position.startswith("b"):
        y = 0.96 - height
    if position.endswith("r"):
        x = 0.96 - width
    if position.endswith("c"):
        x = (1 - width) / 2
    return [round(x, 4), round(y, 4), round(x + width, 4), round(y + height, 4)]


def tail_for(position: str) -> list[float]:
    return {
        "tl": [0.42, 0.36], "tr": [0.58, 0.36], "tc": [0.50, 0.36],
        "bl": [0.42, 0.66], "br": [0.58, 0.66], "bc": [0.50, 0.66],
    }[position]


def pick_system_position(dialogue_units: list[dict[str, Any]], order: int) -> str:
    occupied = {unit["position"] for unit in dialogue_units}
    preference = ["tr", "tl", "br", "bl"] if order % 2 == 0 else ["tl", "tr", "bl", "br"]
    return next((pos for pos in preference if pos not in occupied), preference[0])


def references_for(chapter: int, subjects: list[str], beat: str) -> list[str]:
    refs = ["ref-style-b"]
    if "Elian" in subjects:
        refs.append("ref-elian-v1")
    if "Mira" in subjects:
        refs.append("ref-mira-equipment-v1")
    if any(name in subjects for name in ("Orin", "Sable", "Delver")):
        refs.append("ref-volume-adults-v1")
    monster_present = any(word in beat for word in ("Belljaw", "Mite", "Glassback", "Bailiff", "Choir", "Hound", "Maw", "Guard", "Regent"))
    if monster_present:
        monster_ref = "ref-belljaw-v1" if chapter == 1 else ("ref-minor-bosses-v1" if chapter <= 7 else "ref-major-bosses-v1")
        refs.append(monster_ref)
    zone_ref = "ref-vault-effects-v1" if chapter <= 2 else "ref-volume-zones-v1"
    refs = list(dict.fromkeys(refs))
    # Four references keeps conditioning strong without turning the registry into a universal face blender.
    # On crowded action beats, creature anatomy outranks the environment sheet; cast contracts remain in prose.
    if monster_present and len(refs) > 4:
        refs = refs[:3] + [monster_ref]
    elif len(refs) < 4:
        refs.append(zone_ref)
    return refs[:4]


def prompt_for(chapter: int, order: int, beat: str, plan_density: str, action: bool, units: list[dict[str, Any]]) -> str:
    subjects = named_subjects(chapter, beat)
    subject_contract = "\n".join(f"Subject contract: {CHARACTER_PROMPTS[name]}" for name in subjects)
    monster = MONSTER_PROMPTS.get(chapter, "") if any(word in beat for word in ("Belljaw", "Mite", "Glassback", "Bailiff", "Choir", "Hound", "Maw", "Guard", "Regent")) else ""
    reserved = sorted({unit["position"] for unit in units if unit["kind"] != "sfx"})
    reservation = ", ".join(reserved) if reserved else "no large reserved copy area; preserve clean margins"
    camera = (CAMERA_ACTION if action else CAMERA_QUIET)[(order + chapter) % (len(CAMERA_ACTION) if action else len(CAMERA_QUIET))]
    return (
        f"Scene/backdrop: {CHAPTER_ZONES[chapter]}.\n"
        f"Primary request: CH{chapter:02d} panel {order:03d}, one exact story moment — {beat}\n"
        f"Composition/framing: {camera}; declared density {plan_density}; reserve simplified negative space at {reservation}; keep the narrative focal action away from those edges.\n"
        f"{subject_contract}\n"
        + (f"Creature contract: {monster}.\n" if monster else "")
        + STYLE_BLOCK
    )


def main() -> None:
    existing_requests: dict[str, dict[str, Any]] = {}
    existing_path = VOLUME / "generation-requests.json"
    if existing_path.exists():
        existing_requests = {row["request_id"]: row for row in json.loads(existing_path.read_text(encoding="utf-8"))["requests"]}
    master_chapters: list[dict[str, Any]] = []
    all_requests: list[dict[str, Any]] = []
    density_total = {"low": 0, "moderate": 0, "high": 0}
    action_total = 0
    dialogue_metrics = []
    for chapter in range(1, 11):
        chapter_id = f"ch{chapter:02d}"
        chapter_dir = VOLUME / "chapters" / chapter_id
        dialogue_by_panel: dict[int, list[dict[str, Any]]] = {}
        for unit_order, row in enumerate(DIALOGUE[chapter], start=1):
            panel_order, speaker, mode, position, text = row
            dialogue_by_panel.setdefault(panel_order, []).append({
                "unit_id": f"el-{chapter_id}-p{panel_order:03d}-d{unit_order:02d}",
                "kind": "caption" if mode == "caption" else "dialogue",
                "mode": mode,
                "speaker": speaker,
                "position": position,
                "text": text,
                "box": make_box(position, text, mode),
                "tail": None if mode in {"caption", "open"} else tail_for(position),
                "reading_order": unit_order,
            })

        panels = []
        lettering: dict[str, list[dict[str, Any]]] = {}
        chapter_requests = []
        for order, beat in enumerate(CHAPTER_BEATS[chapter], start=1):
            panel_id = f"el-{chapter_id}-s01-p{order:03d}"
            plan_density = density(chapter, order)
            is_action = order in ACTION_ORDERS[chapter]
            units = list(dialogue_by_panel.get(order, []))
            if order in SYSTEM_PANELS[chapter]:
                kind, lines = SYSTEM_PANELS[chapter][order]
                pos = pick_system_position(units, order)
                units.append({
                    "unit_id": f"{panel_id}-ui",
                    "kind": kind,
                    "mode": "ledger-v2",
                    "speaker": "Brass Ledger",
                    "position": pos,
                    "lines": lines,
                    "box": make_box(pos, " ".join(lines), "system", len(lines)),
                    "tail": None,
                    "reading_order": 90,
                })
            if is_action and order % 4 == 0:
                units.append({
                    "unit_id": f"{panel_id}-sfx",
                    "kind": "sfx", "mode": "outlined", "speaker": None,
                    "position": "bc", "text": ["KRAK", "THOOM", "KLANG", "SHNK"][(chapter + order) % 4],
                    "at": [0.52, 0.61], "rotate": -8 if order % 2 else 8, "reading_order": 80,
                })
            subjects = named_subjects(chapter, beat)
            refs = references_for(chapter, subjects, beat)
            panels.append({
                "schema": "ComicPanelPlan/1.0",
                "panel_id": panel_id,
                "chapter": chapter_id,
                "sequence_id": f"el-{chapter_id}-s01",
                "order": order,
                "density": plan_density,
                "action": is_action,
                "beat": beat,
                "camera": (CAMERA_ACTION if is_action else CAMERA_QUIET)[(order + chapter) % (len(CAMERA_ACTION) if is_action else len(CAMERA_QUIET))],
                "subjects": subjects,
                "zone": CHAPTER_ZONES[chapter],
                "focal_exclusion": [0.24, 0.23, 0.76, 0.77],
                "lettering_exclusions": [unit["box"] for unit in units if "box" in unit],
                "references": refs,
            })
            lettering[panel_id] = units
            density_total[plan_density] += 1
            action_total += int(is_action)

            if chapter == 1 and order <= 16:
                source_path = f"experiments/reimaginings/ember-lattice/pilot/source/p{order:03d}.png"
                source_reuse = "owner-approved Phase A pilot source art"
            else:
                source_path = f"experiments/reimaginings/ember-lattice/volume/{chapter_id}/source/p{order:03d}.png"
                source_reuse = None
                exact_prompt = prompt_for(chapter, order, beat, plan_density, is_action, units)
                request = {
                    "schema": "GenerationRequest/1.0",
                    "request_id": f"volume-{chapter_id}-p{order:03d}-r1",
                    "chapter": chapter_id,
                    "panel_id": panel_id,
                    "exact_prompt": exact_prompt,
                    "prompt_hash": sha_text(exact_prompt),
                    "reference_ids": refs,
                    "output_path": source_path,
                    "measured_elapsed_seconds": None,
                    "model": None, "endpoint": None, "provider_request_id": None,
                    "usage": None, "monetary_cost": None, "seed": None,
                    "review_status": "NOT_GENERATED",
                    "failure_classes": [],
                    "owner_approval": "PENDING",
                    "commercial_clearance": False,
                    "production_base": False,
                    "reproducible": False,
                }
                existing = existing_requests.get(request["request_id"])
                if existing and existing.get("prompt_hash") == request["prompt_hash"] and existing.get("output_path") == request["output_path"]:
                    for key in ("measured_elapsed_seconds", "model", "endpoint", "provider_request_id", "usage", "monetary_cost", "seed", "review_status", "failure_classes", "sha256", "dimensions", "visual_review"):
                        if key in existing:
                            request[key] = existing[key]
                chapter_requests.append(request)
                all_requests.append(request)
            panels[-1]["source_path"] = source_path
            panels[-1]["source_reuse"] = source_reuse

        spoken_words = sum(len(row[4].split()) for row in DIALOGUE[chapter])
        system_moments = len(SYSTEM_PANELS[chapter])
        density_counts = {name: sum(p["density"] == name for p in panels) for name in density_total}
        dialogue_metrics.append({
            "chapter": chapter_id, "spoken_internal_words": spoken_words,
            "dialogue_units": len(DIALOGUE[chapter]), "meaningful_system_moments": system_moments,
            "density": density_counts, "action_panels": sum(p["action"] for p in panels),
        })
        plan_collection = {
            "schema": "ComicPanelPlanCollection/1.0", "story_slug": "ember-lattice",
            "chapter": chapter_id, "title": CHAPTER_TITLES[chapter],
            "animation_shot_plan": None, "e_conte": None,
            "canvas": {"nominal_width": 1024, "nominal_height": 1536, "phone_width": 390},
            "panels": panels,
        }
        write_json(chapter_dir / "comic-panel-plans.json", plan_collection)
        write_json(chapter_dir / "lettering-copy.json", {"schema":"LetteringCopyCollection/2.0","chapter":chapter_id,"panel_units":lettering})
        write_json(chapter_dir / "prompt-manifest.json", {"schema":"PromptManifest/1.0","chapter":chapter_id,"requests":chapter_requests})
        master_chapters.append({
            "chapter": chapter_id, "title": CHAPTER_TITLES[chapter], "zone": CHAPTER_ZONES[chapter],
            "opening_condition": CHAPTER_BEATS[chapter][0], "closing_turn": CHAPTER_BEATS[chapter][-1],
            "panel_count": 24, "action_panels": sum(p["action"] for p in panels),
            "density": density_counts, "dialogue_words": spoken_words, "system_moments": system_moments,
        })

    total_panels = sum(row["panel_count"] for row in master_chapters)
    summary = {
        "schema": "VolumeMaster/1.0", "story_slug": "ember-lattice",
        "owner_approval_record": "production/reimaginings/ember-lattice/owner-approval.json",
        "phase_b_authorized": True, "chapters": master_chapters,
        "totals": {
            "chapters": 10, "panels": total_panels, "action_panels": action_total,
            "action_percentage": round(action_total / total_panels * 100, 3),
            "density": density_total,
            "density_percentages": {k: round(v / total_panels * 100, 3) for k, v in density_total.items()},
            "new_generation_requests": len(all_requests), "approved_pilot_sources_reused": 16,
            "direct_paid_cloud_spend_usd": 0,
        },
        "planning_schema": "ComicPanelPlan only",
        "animation_shot_plan": None, "e_conte": None,
    }
    errors = []
    if len(master_chapters) != 10 or total_panels != 240:
        errors.append("Volume must contain exactly ten 24-panel chapters")
    if not 35 <= summary["totals"]["action_percentage"] <= 45:
        errors.append("Action percentage outside 35–45%")
    if density_total != {"low":159,"moderate":60,"high":21}:
        errors.append(f"Density contract changed: {density_total}")
    for row in dialogue_metrics:
        if not 300 <= row["spoken_internal_words"] <= 520:
            errors.append(f'{row["chapter"]} dialogue word target failed: {row["spoken_internal_words"]}')
        if row["meaningful_system_moments"] < 4:
            errors.append(f'{row["chapter"]} has fewer than four meaningful system moments')
    if errors:
        raise SystemExit("Volume authoring failed:\n- " + "\n- ".join(errors))
    write_json(VOLUME / "volume-master.json", summary)
    write_json(VOLUME / "dialogue-and-density-metrics.json", {
        "schema":"VolumeAuthoringMetrics/1.0", "chapters":dialogue_metrics,
        "totals": {
            "spoken_internal_words": sum(row["spoken_internal_words"] for row in dialogue_metrics),
            "dialogue_units": sum(row["dialogue_units"] for row in dialogue_metrics),
            "meaningful_system_moments": sum(row["meaningful_system_moments"] for row in dialogue_metrics),
        },
    })
    write_json(VOLUME / "generation-requests.json", {"schema":"GenerationRequestCollection/1.0","requests":all_requests})
    write_json(VOLUME / "action-choreography.json", {
        "schema":"VolumeActionChoreography/1.0",
        "chapters":[{"chapter":f"ch{ch:02d}","action_panel_orders":sorted(ACTION_ORDERS[ch]),"causal_requirement":"geography → intention → initiation → contact/interruption → consequence → response → adaptation → payoff/state"} for ch in range(1,11)]
    })
    print(json.dumps(summary["totals"], indent=2))


if __name__ == "__main__":
    main()
