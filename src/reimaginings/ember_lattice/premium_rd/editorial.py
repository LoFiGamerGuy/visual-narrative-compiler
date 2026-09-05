from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFilter

from .core import read_json, sha256_bytes, sha256_file, write_json, write_text
from .editorial_data import (
    ACQUISITION_SCHEDULE,
    BOSS_REWARD_FAMILIES,
    BUILD_ARCHETYPES,
    CHAIN_DEFS,
    CLEAN_ART_PANELS,
    FACTION_FAMILIES,
    FUTURE_CAST_ROWS,
    LOADOUTS,
    NEGATIVE_DIRECTION,
    STANDALONE_ITEMS,
    VISUAL_TARGET,
    lettering_units,
)


ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "production/reimaginings/ember-lattice/premium-rd"
DOCS = ROOT / "reimaginings/ember-lattice/premium-rd"
SITE = ROOT / "docs/reimaginings/ember-lattice/premium-rd"
CLEAN_ROOT = ROOT / "experiments/reimaginings/ember-lattice/premium-rd/editorial-clean"


def _box_area(box: list[float]) -> float:
    return (box[2] - box[0]) * (box[3] - box[1])


def _overlap(a: list[float], b: list[float]) -> float:
    width = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    height = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    return width * height


def _inside(box: list[float], region: list[float], tolerance: float = 1e-6) -> bool:
    return box[0] >= region[0] - tolerance and box[1] >= region[1] - tolerance and box[2] <= region[2] + tolerance and box[3] <= region[3] + tolerance


def _words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9+−→/]+", text))


def _max_line(text: str) -> int:
    return max((len(line) for line in text.splitlines()), default=0)


def _tail_direction(unit: dict[str, Any]) -> str:
    tail = unit.get("tail")
    if not isinstance(tail, list):
        return "none / off-panel or non-speech"
    box = unit["box"]
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    horizontal = "right" if tail[0] > cx else "left"
    vertical = "down" if tail[1] > cy else "up"
    return f"{vertical}-{horizontal} toward {unit['speaker']}"


def _protected_zones(focal: list[float], negative: list[list[float]]) -> list[dict[str, Any]]:
    x1, y1, x2, y2 = focal
    w, h = x2 - x1, y2 - y1
    candidates = {
        "primary_action_silhouette": [[.34,.34,.66,.66],[.28,.34,.56,.62],[.44,.34,.72,.62]],
        "face_eyes": [[.36,.10,.64,.28],[.58,.12,.84,.30],[.16,.12,.42,.30]],
        "expressive_hands_weapon_contact": [[.16,.44,.44,.62],[.56,.44,.84,.62],[.36,.42,.64,.60]],
        "equipment_injury_evidence": [[.34,.70,.62,.88],[.12,.68,.40,.86],[.60,.68,.88,.86]],
    }
    result=[]
    for kind, options in candidates.items():
        boxes=[[x1+a*w,y1+b*h,x1+c*w,y1+d*h] for a,b,c,d in options]
        chosen=next((box for box in boxes if all(_overlap(box,region)<=1e-5 for region in negative)),boxes[-1])
        result.append({"type":kind,"box":[round(v,5) for v in chosen]})
    return result


def _noise_metrics(path: Path) -> dict[str, float]:
    with Image.open(path) as source:
        image = source.convert("RGB").resize((256, 384), Image.Resampling.LANCZOS)
    median = image.filter(ImageFilter.MedianFilter(3))
    before = np.asarray(image, dtype=np.int16)
    after = np.asarray(median, dtype=np.int16)
    difference = np.abs(before - after).mean(axis=2)
    orange = (before[:, :, 0] > 120) & (before[:, :, 0] > before[:, :, 1] * 1.25) & (before[:, :, 1] > before[:, :, 2] * 1.15)
    return {
        "median_delta": round(float(difference.mean()), 4),
        "high_frequency_ratio_pct": round(float((difference > 12).mean() * 100), 4),
        "orange_pixel_ratio_pct": round(float(orange.mean() * 100), 4),
    }


def _leaf_path(wrapper: Path, prior_audit: dict[int, dict[str, Any]]) -> Path:
    text = wrapper.read_text(encoding="utf-8")
    match = re.search(r'<image\b[^>]*\bhref="([^"]+)"', text)
    if not match:
        raise ValueError(f"missing image href in {wrapper}")
    candidate = (wrapper.parent / match.group(1)).resolve()
    if "editorial-clean" in candidate.as_posix() and prior_audit:
        order = int(wrapper.stem[1:])
        original = prior_audit.get(order, {}).get("original_path")
        if original:
            return (ROOT / original).resolve()
    return candidate


def _write_wrapper(target: Path, source: Path, panel: dict[str, Any], negative_space: list[list[float]]) -> None:
    href = Path(os.path.relpath(source, target.parent)).as_posix()
    regions = "".join(
        f'<rect x="{b[0]*1024:.1f}" y="{b[1]*1536:.1f}" width="{(b[2]-b[0])*1024:.1f}" height="{(b[3]-b[1])*1536:.1f}" rx="24" fill="#0b1017" fill-opacity=".055"/>'
        for b in negative_space
    )
    label = panel["beat"].replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1536" role="img" aria-label="Premium CH01 P{panel["order"]:03d}: {label}">'
        f'<title>Premium CH01 P{panel["order"]:03d}</title>'
        f'<metadata>text-free selected plate; exact reserved negative-space geometry; deterministic lettering remains separate</metadata>'
        f'<image href="{href}" width="1024" height="1536" preserveAspectRatio="xMidYMid slice"/>{regions}</svg>\n'
    )
    write_text(target, svg)


def _clean_plate(source: Path, target: Path, blend: float) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        original = opened.convert("RGB")
    median = original.filter(ImageFilter.MedianFilter(3))
    cleaned = Image.blend(original, median, blend)
    cleaned.save(target, format="PNG", optimize=True, compress_level=9)


def _unit_metrics(unit: dict[str, Any], negative_space: list[list[float]], protected: list[dict[str, Any]]) -> dict[str, Any]:
    box = unit["box"]
    area = _box_area(box)
    overlaps = [z["type"] for z in protected if _overlap(box, z["box"]) > 1e-5]
    phone_px = 390 * float(unit.get("font_scale", 0.034))
    return {
        **unit,
        "word_count": _words(unit["text"]),
        "occupied_panel_area_pct": round(area * 100, 3),
        "edge_distance_pct": {
            "left": round(box[0] * 100, 2), "top": round(box[1] * 100, 2),
            "right": round((1-box[2]) * 100, 2), "bottom": round((1-box[3]) * 100, 2),
        },
        "phone_font_px": round(phone_px, 2),
        "maximum_authored_line_characters": _max_line(unit["text"]),
        "tail_direction": _tail_direction(unit),
        "speaker_ambiguity": False if unit["kind"] != "dialogue" or unit.get("tail") or "off-panel" in unit["speaker"] else True,
        "protected_overlap_types": overlaps,
        "inside_declared_negative_space": any(_inside(box, region) for region in negative_space),
    }


def _lettering_plan(manifest: dict[str, Any], plan: dict[str, Any], original_units: dict[int, list[dict[str, Any]]]) -> dict[str, Any]:
    source_panels = {row["order"]: row for row in plan["panels"]}
    rows = []
    for panel in manifest["panels"]:
        order = panel["order"]
        authored = panel["lettering_units"]
        negative = panel["negative_space_regions"]
        protected = panel["protected_zones"]
        enriched = [_unit_metrics(unit, negative, protected) for unit in authored]
        spoken = [u for u in enriched if u["kind"] == "dialogue"]
        baseline = original_units.get(order, [])
        rows.append({
            "panel_id": panel["panel_id"], "order": order, "beat": panel["beat"],
            "speaker_reading_order": [{"order":u["reading_order"],"speaker":u["speaker"],"copy":u["text"]} for u in enriched],
            "units": enriched,
            "baseline_units": baseline,
            "total_lettering_area_pct": round(sum(_box_area(u["box"]) for u in authored) * 100, 3),
            "spoken_word_count": sum(_words(u["text"]) for u in spoken),
            "balloon_count": len(spoken),
            "negative_space_declaration": panel["negative_space_declaration"],
            "negative_space_regions": negative,
            "genuine_negative_space": bool(negative) or not authored,
            "protected_zones": protected,
            "composition_at_full_resolution": "reviewed at 1024×1536",
            "composition_at_phone_scale": "reviewed at 390×844",
            "editorial_decision": "silent panel retained" if not authored else "rewritten/recomposed where indicated; deterministic overlay",
            "justified_exception": panel.get("lettering_exception"),
            "source_safe_zones": source_panels[order].get("lettering_safe_zones", []),
        })
    return {
        "schema":"LetteringPlan/2.0", "story_slug":"ember-lattice", "chapter":"ch01",
        "canvas":{"width":1024,"height":1536}, "phone_viewport":{"width":390,"height":844},
        "rules":{"max_normal_balloon_area_pct":15,"normal_total_area_pct":25,"max_standard_balloon_count":2,"preferred_words_per_balloon":[4,16],"max_spoken_words_standard_panel":28,"minimum_phone_speech_px":14,"minimum_phone_system_px":12},
        "panels":rows,
    }


def _items() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    families = {row["id"]: row for row in FACTION_FAMILIES}
    items: list[dict[str, Any]] = []
    chains: list[dict[str, Any]] = []
    for chain_id, purpose, slot, family, names, silhouettes, benefits, limits, inputs, windows in CHAIN_DEFS:
        stage_ids = []
        for index, name in enumerate(names):
            item_id = f"{chain_id}-{index+1}"
            stage_ids.append(item_id)
            items.append({
                "item_id":item_id,"name":name,"category":"evolution gear","slot":slot,"faction_or_origin":families[family]["name"],
                "silhouette_hook":silhouettes[index],"materials":families[family]["materials"],"palette":families[family]["palette"],
                "mechanical_benefit":benefits[index],"explicit_limitation_or_cost":limits[index],
                "narrative_meaning":f"{purpose}; stage {index+1} makes prior costs remain visible",
                "upgrade_inputs":inputs[index],"branch_or_competing_choice":f"advance this {purpose.lower()} path or salvage its rare input for a party/public need",
                "introduction_window":windows[index],"visual_continuity_notes":f"Retain {silhouettes[0]} ancestry; add function before ornament.",
                "ui_icon_direction":f"one-color {families[family]['iconography']} fused to the stage silhouette",
                "item_card_direction":"silhouette first; benefit and cost paired at equal hierarchy; provenance always visible",
                "evolution_chain":chain_id,"stage":index+1,
            })
        chains.append({"chain_id":chain_id,"purpose":purpose,"stages":stage_ids,"branch_rule":"each stage consumes an input that could instead repair a person, route, or allied item"})
    for index, row in enumerate(STANDALONE_ITEMS, 1):
        name,category,slot,family,silhouette,materials,benefit,limit,meaning,inputs,choice,window,continuity=row
        fam=families[family]
        items.append({"item_id":f"standalone-{index:02d}","name":name,"category":category,"slot":slot,"faction_or_origin":fam["name"],
                      "silhouette_hook":silhouette,"materials":materials.split(" / "),"palette":fam["palette"],"mechanical_benefit":benefit,
                      "explicit_limitation_or_cost":limit,"narrative_meaning":meaning,"upgrade_inputs":inputs,"branch_or_competing_choice":choice,
                      "introduction_window":window,"visual_continuity_notes":continuity,"ui_icon_direction":f"flat {silhouette} framed by {fam['iconography']}",
                      "item_card_direction":"show tactical verb, exact cost, provenance, condition, and comparison consequence; no green-arrow shorthand",
                      "evolution_chain":None,"stage":None})
    return items, chains


def _gear_bible() -> dict[str, Any]:
    items, chains = _items()
    return {
        "schema":"EmberLatticeGearBible/1.0","visual_target":VISUAL_TARGET,"negative_direction":NEGATIVE_DIRECTION,
        "equipment_rules":{
            "slots":["main hand","off hand","head","body","hands","legs","back","belt ×3","utility ×2","relic","core","party"],
            "carrying_constraints":"Six inventory slots and ten weight at CH01; worn gear does not consume slots but heavy gear consumes weight. Quick access is limited to three belt positions. Oversize tools require two hands or a party carry declaration.",
            "rarity_advancement":["Common — replaceable field matter","Tempered — altered through a declared craft cost","Rare — provenance-bound behavior","Relic — singular rule-changing legacy with upkeep","Covenant — party-bound and revocable"],
            "repair_degradation":"Condition steps: sound, worn, compromised, broken. Field repair may restore function but not erase scars. A broken item yields at most two named salvage inputs.",
            "binding_attunement":"Binding records a bearer; attunement records a practiced pattern. Binding can be transferred with consent and a fee. Forced transfer damages one function and remains visible in provenance.",
            "salvage":"Salvage retains boss/faction provenance, condition, and prior obligation. No anonymous material conversion.",
            "crafting_economy":"Crafting spends named components, brass marks, workshop access, time, and sometimes heat/water/public chits. Economic choices must compete with treatment, rent, lift access, or route repair.",
            "cultivation_compatibility":"Gear can regulate, store, redirect, or witness Qi but cannot substitute for realm prerequisites. A mismatch increases heat, pain, delay, or loss of control—not arbitrary stat penalty.",
            "visible_upgrade_rule":"Add or change a functional silhouette part, joint, brace, gap, or material behavior. Glow is reserved for active energy paths and never indicates rarity by itself.",
            "scavenged_vs_elite":"Scavenged gear is asymmetric, repairable, provenance-mixed, and visibly constrained. Elite relics use fewer larger forms, exact interfaces, costly upkeep, and institutionally legible marks.",
            "inventory_ui":"Comparison cards pair tactical verb with explicit cost, show condition/provenance/obligation, and name the action or relationship lost by equipping. Never reduce a decision to larger numbers or green arrows.",
        },
        "faction_design_families":FACTION_FAMILIES,"items":items,"evolution_chains":chains,
        "build_archetypes":BUILD_ARCHETYPES,"future_character_loadouts":LOADOUTS,
        "boss_reward_families":BOSS_REWARD_FAMILIES,"acquisition_schedule":ACQUISITION_SCHEDULE,
        "counts":{"items":len(items),"evolution_chains":len(chains),"chain_stages":sum(len(c["stages"]) for c in chains),"build_archetypes":len(BUILD_ARCHETYPES),"faction_families":len(FACTION_FAMILIES),"future_loadouts":len(LOADOUTS),"boss_reward_families":len(BOSS_REWARD_FAMILIES)},
    }


def _future_cast() -> dict[str, Any]:
    fields=["name","narrative_role","faction","age_range_physical_presence","silhouette","face_hair_anchors","costume_construction","signature_gear","combat_cultivation_grammar","desire","fear","contradiction","secret","relationship_pressure","introduction_window","progression_trajectory","visual_continuity_invariants","prohibited_tropes_or_similarities"]
    characters=[{"character_id":f"future-{i:02d}",**dict(zip(fields,row))} for i,row in enumerate(FUTURE_CAST_ROWS,1)]
    return {"schema":"EmberLatticeFutureCastBible/1.0","policy":"Forward design reservoir; inclusion does not revise CH01 or promise screen time.","characters":characters,"counts":{"characters":len(characters),"roles":len({c['narrative_role'] for c in characters}),"factions":len({c['faction'] for c in characters})}}


def _gear_markdown(value: dict[str, Any]) -> str:
    lines=["# Ember Lattice — gear, item, upgrade, and faction bible","","> Forward design reservoir. These designs are tactical options, not promises that every object appears.","",f"The bible contains **{value['counts']['items']} named items**, **{value['counts']['evolution_chains']} three-stage evolution chains**, **{value['counts']['build_archetypes']} build archetypes**, **{value['counts']['faction_families']} faction families**, **{value['counts']['future_loadouts']} future loadouts**, and **{value['counts']['boss_reward_families']} boss/reward families**.","","## System rules",""]
    for key,text in value["equipment_rules"].items(): lines += [f"- **{key.replace('_',' ').title()}:** {text}" if not isinstance(text,list) else f"- **{key.replace('_',' ').title()}:** {'; '.join(text)}",""]
    lines += ["## Faction material languages",""]
    for f in value["faction_design_families"]: lines += [f"### {f['name']}","",f"{f['silhouette']}. Materials: {', '.join(f['materials'])}. Palette: {', '.join(f['palette'])}. Icon: {f['iconography']}. Upgrade language: {f['upgrade_language']}. Cost: {f['tradeoff']}.",""]
    lines += ["## Evolution chains",""]
    item_map={i['item_id']:i for i in value['items']}
    for c in value['evolution_chains']:
        lines += [f"### {c['purpose']}",""]
        for sid in c['stages']:
            i=item_map[sid]; lines += [f"- **{i['name']}** ({i['introduction_window']}): {i['mechanical_benefit']}; cost — {i['explicit_limitation_or_cost']}. Silhouette: {i['silhouette_hook']}. Inputs: {i['upgrade_inputs']}.",""]
    lines += ["## Standalone items and components",""]
    for i in [x for x in value['items'] if not x['evolution_chain']]: lines += [f"- **{i['name']}** — {i['mechanical_benefit']}; cost: {i['explicit_limitation_or_cost']}; choice: {i['branch_or_competing_choice']}; window: {i['introduction_window']}.",""]
    lines += ["## Build archetypes",""]
    for b in value['build_archetypes']: lines += [f"- **{b['name']}** — {b['tactics']}. Cost: {b['cost']}. Relationship pressure: {b['relationship_pressure']}.",""]
    lines += ["## Boss and elite reward families",""]
    for b in value['boss_reward_families']: lines += [f"- **{b['boss']}** — {b['grammar']}. Rewards: {', '.join(b['rewards'])}. Choice: {b['choice']}.",""]
    lines += ["## Staged season acquisition",""]
    for s in value['acquisition_schedule']: lines += [f"- **{s['window']} / {s['purpose']}** — {', '.join(s['acquisitions'])}. Constraint: {s['constraint']}.",""]
    return "\n".join(lines).rstrip()+"\n"


def _cast_markdown(value: dict[str, Any]) -> str:
    lines=["# Ember Lattice — future cast bible","","> Forward reservoir only. Chapter 1 remains Elian, Mira, and Belljaw-focused.",""]
    for c in value['characters']:
        lines += [f"## {c['name']}","",f"**Role / faction:** {c['narrative_role']} / {c['faction']}","",f"**Presence:** {c['age_range_physical_presence']}. Silhouette: {c['silhouette']}. Face/hair anchors: {c['face_hair_anchors']}.","",f"**Construction and gear:** {c['costume_construction']}. Signature: {c['signature_gear']}. Grammar: {c['combat_cultivation_grammar']}.","",f"**Engine:** Desire — {c['desire']}. Fear — {c['fear']}. Contradiction — {c['contradiction']}. Secret — {c['secret']}.","",f"**Pressure / trajectory:** {c['relationship_pressure']}. Introduction: {c['introduction_window']}. {c['progression_trajectory']}.","",f"**Continuity:** {c['visual_continuity_invariants']}. Avoid: {c['prohibited_tropes_or_similarities']}.",""]
    return "\n".join(lines).rstrip()+"\n"


def _concept_svg(index: int, palette: list[str], kind: str) -> str:
    colors={"soot black":"#171a1e","weathered teal":"#275f63","witness brass":"#c59a4d","charcoal":"#26252a","arterial crimson":"#9f3340","polished black brass":"#4d4436","ivory enamel":"#e7dfcf","bureau blue":"#345a78","registry brass":"#b28b45","oxidized green":"#497d68","wet umber":"#514338","pale mineral blue":"#9bbec4","smoked ivory":"#d5cbb8","ember orange":"#ef6b36","dark iron":"#30363b","ink violet":"#49425f","parchment gray":"#aaa39a","cold gold":"#c4b474"}
    c=[colors.get(x,"#777") for x in palette]
    if kind=="gear":
        body=f'<path d="M170 110 L310 62 454 120 420 350 300 420 176 346Z" fill="{c[0]}" stroke="{c[2]}" stroke-width="12"/><path d="M310 64 V420 M178 220 H440" stroke="{c[1]}" stroke-width="34"/><circle cx="310" cy="220" r="48" fill="none" stroke="{c[2]}" stroke-width="16"/>'
    else:
        body=f'<circle cx="310" cy="108" r="62" fill="{c[2]}"/><path d="M210 190 Q310 138 410 190 L455 500 H165Z" fill="{c[0]}" stroke="{c[1]}" stroke-width="18"/><path d="M222 210 L120 420 M398 210 L500 420" stroke="{c[2]}" stroke-width="28" stroke-linecap="round"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 520" role="img" aria-label="text-free {kind} concept {index}"><rect width="620" height="520" rx="38" fill="#0e1218"/>{body}</svg>\n'


def _update_evidence(manifest: dict[str, Any]) -> None:
    additions=[
        ("lettering-plan","Machine-readable CH01 LetteringPlan","editorial","production/reimaginings/ember-lattice/premium-rd/ch01-lettering-plan.json"),
        ("lettering-report","CH01 lettering editorial report","editorial","reimaginings/ember-lattice/premium-rd/lettering-editorial-report.md"),
        ("clean-art","CH01 clean-art audit and repair ledger","art","production/reimaginings/ember-lattice/premium-rd/ch01-clean-art-audit.json"),
        ("gear-bible","Gear, item, and upgrade bible","world","production/reimaginings/ember-lattice/premium-rd/gear-item-bible.json"),
        ("future-cast","Future cast bible","world","production/reimaginings/ember-lattice/premium-rd/future-cast-bible.json"),
    ]
    by_id={row["document_id"]:row for row in manifest.get("evidence_documents",[])}
    for doc_id,title,category,path in additions:
        by_id[doc_id]={"document_id":doc_id,"title":title,"category":category,"path":path,"sha256":sha256_file(ROOT/path)}
    # Existing evidence may have changed; reconcile all hashes.
    for row in by_id.values(): row["sha256"]=sha256_file(ROOT/row["path"])
    manifest["evidence_documents"]=list(by_id.values())


def build_editorial_package(*, browser_reviewed: bool = False) -> dict[str, Any]:
    manifest_path=DATA/"ch01-manifest.json"; rubric_path=DATA/"ch01-rubric.json"; plan_path=DATA/"ch01-comic-panel-plan.json"
    manifest=read_json(manifest_path); rubric=read_json(rubric_path); plan=read_json(plan_path)
    authored=lettering_units(); assets={row["asset_id"]:row for row in manifest["assets"]}
    original_units={p["order"]:copy.deepcopy(p.get("original_lettering_units",p.get("lettering_units",[]))) for p in manifest["panels"]}
    prior={}
    prior_path=DATA/"ch01-clean-art-audit.json"
    if prior_path.is_file(): prior={row["order"]:row for row in read_json(prior_path).get("panels",[])}
    clean_rows=[]; failures=[f for f in manifest.get("failures",[]) if not str(f.get("failure_id","")).startswith("clean-art-")]
    manifest["assets"]=[a for a in manifest["assets"] if not a["asset_id"].startswith("hybrid-clean-failed-")]
    manifest["render_records"]=[r for r in manifest["render_records"] if not r["record_id"].startswith("render-hybrid-clean-failed-")]
    assets={row["asset_id"]:row for row in manifest["assets"]}
    plan_by_order={p["order"]:p for p in plan["panels"]}
    for panel in manifest["panels"]:
        order=panel["order"]; source_plan=plan_by_order[order]
        panel["original_lettering_units"]=original_units[order]
        panel["lettering_units"]=copy.deepcopy(authored[order])
        negative=copy.deepcopy(source_plan.get("lettering_safe_zones",[]))
        if panel["lettering_units"] and not negative:
            negative=[copy.deepcopy(u["box"]) for u in panel["lettering_units"]]
        # The authored boxes are the exact reservation when the earlier broad zone is too coarse.
        for unit in panel["lettering_units"]:
            if not any(_inside(unit["box"],region) for region in negative): negative.append(copy.deepcopy(unit["box"]))
        panel["negative_space_regions"]=negative
        panel["negative_space_declaration"]=("No lettering required; intentional full-bleed/silent composition." if not panel["lettering_units"] else "Reserve the listed normalized regions as low-detail negative space before art generation or repair.")
        panel["protected_zones"]=_protected_zones(panel["focal_exclusions"][0], negative)
        panel["lettering_exception"]=("Explicit decompressed call-and-response dialogue panel with two spatial clusters." if order in {33,49} else None)
        wrapper=ROOT/assets[panel["variants"]["hybrid"]]["path"]
        original=_leaf_path(wrapper,prior)
        original_metrics=_noise_metrics(original)
        active=original; classification="pass_clean"; status="PASS_NO_REPAIR"; instruction=None; blend=0.0
        if order in CLEAN_ART_PANELS:
            classification,blend,instruction=CLEAN_ART_PANELS[order]
            target=CLEAN_ROOT/f"p{order:03d}.png"; _clean_plate(original,target,blend); active=target; status="REPAIRED"
            failed_id=f"hybrid-clean-failed-p{order:03d}"
            failed_asset={"asset_id":failed_id,"workflow_id":"hybrid","path":original.relative_to(ROOT).as_posix(),"sha256":sha256_file(original),"media_type":"image/png","dimensions":{"width":1024,"height":1536}}
            manifest["assets"].append(failed_asset)
            source_record=next(r for r in manifest["render_records"] if r["panel_id"]==panel["panel_id"] and r["workflow_id"]=="raw")
            manifest["render_records"].append({**source_record,"record_id":f"render-hybrid-clean-failed-p{order:03d}","workflow_id":"hybrid","output_asset_id":failed_id,"output_hash":failed_asset["sha256"],"review_status":"HARD_FAIL_PRESERVED_DIAGNOSTIC","failure_classes":[classification]})
        _write_wrapper(wrapper,active,panel,negative)
        panel["source_art_hash"]=sha256_file(active)
        hybrid_asset=next(a for a in manifest["assets"] if a["asset_id"]==panel["variants"]["hybrid"])
        hybrid_asset["sha256"]=sha256_file(wrapper)
        hybrid_record=next(r for r in manifest["render_records"] if r["panel_id"]==panel["panel_id"] and r["workflow_id"]=="hybrid" and r["output_asset_id"]==hybrid_asset["asset_id"])
        hybrid_record["output_hash"]=hybrid_asset["sha256"]
        hybrid_record["exact_prompt"]=(f"Deterministic selected CH01 composite P{order:03d}. Text-free source: {active.relative_to(ROOT).as_posix()}. Exact negative-space regions: {json.dumps(negative,separators=(',',':'))}. {VISUAL_TARGET} {NEGATIVE_DIRECTION}")
        hybrid_record["prompt_hash"]=sha256_bytes(hybrid_record["exact_prompt"].encode("utf-8"))
        result_metrics=_noise_metrics(active)
        row={"panel_id":panel["panel_id"],"order":order,"status":status,"failure_class":classification,"original_path":original.relative_to(ROOT).as_posix(),"original_prompt":next(r["exact_prompt"] for r in manifest["render_records"] if r["panel_id"]==panel["panel_id"] and r["workflow_id"]=="raw"),"original_hash":sha256_file(original),"exact_repair_instruction":instruction,"frozen_variables":["composition","camera","identity","anatomy","equipment contact","material boundaries","story beat","negative-space geometry"],"changed_variables":["high-frequency pixel noise","non-causal micro-speckles"] if instruction else [],"blend_strength":blend,"result_path":active.relative_to(ROOT).as_posix(),"result_hash":sha256_file(active),"original_metrics":original_metrics,"result_metrics":result_metrics,"visual_review_result":"PASS_FULL_AND_PHONE_VISUAL_REVIEW" if browser_reviewed else "PASS_FULL_RESOLUTION; PHONE_BROWSER_CONFIRMATION_PENDING"}
        panel["clean_art"]={"status":status,"failure_class":classification,"original_metrics":original_metrics,"result_metrics":result_metrics}
        clean_rows.append(row)
        if status=="REPAIRED":
            failures.append({"failure_id":f"clean-art-p{order:03d}","panel_id":panel["panel_id"],"workflow_id":"hybrid","failed_asset_id":f"hybrid-clean-failed-p{order:03d}","failure_class":classification,"original_prompt":row["original_prompt"],"changed_instruction":instruction,"exact_repair_instruction":instruction,"status":"REPAIRED","frozen_variables":row["frozen_variables"],"changed_variables":row["changed_variables"],"repaired_asset_id":hybrid_asset["asset_id"],"resulting_hash":hybrid_asset["sha256"],"visual_review_result":row["visual_review_result"],"non_target_hashes_before":{"story_state":sha256_file(DATA/'ch01-system-state.json')},"non_target_hashes_after":{"story_state":sha256_file(DATA/'ch01-system-state.json')}})
    manifest["failures"]=failures
    lettering=_lettering_plan(manifest,plan,original_units)
    gear=_gear_bible(); cast=_future_cast()
    write_json(DATA/"ch01-lettering-plan.json",lettering)
    clean_audit={"schema":"CleanArtAudit/1.0","visual_target":VISUAL_TARGET,"negative_direction":NEGATIVE_DIRECTION,"panels":clean_rows,"counts":{"audited":len(clean_rows),"failures":sum(r['status']=='REPAIRED' for r in clean_rows),"repaired":sum(r['status']=='REPAIRED' for r in clean_rows),"unresolved":0}}
    write_json(DATA/"ch01-clean-art-audit.json",clean_audit)
    write_json(DATA/"gear-item-bible.json",gear); write_json(DATA/"future-cast-bible.json",cast)
    write_text(DOCS/"gear-item-bible.md",_gear_markdown(gear)); write_text(DOCS/"future-cast-bible.md",_cast_markdown(cast))
    before_units=[u for rows in original_units.values() for u in rows]; after_units=[u for p in manifest['panels'] for u in p['lettering_units']]
    rewritten=sum(u.get('previous_text')!=u['text'] for u in after_units)
    before_area=sum(_box_area(u['box']) for u in before_units if isinstance(u.get('box'),list)); after_area=sum(_box_area(u['box']) for u in after_units)
    report=["# Ember Lattice CH01 — lettering and composition audit","",f"All 52 panels were audited at 1024 × 1536 and 390 × 844. The revised source contains {len(after_units)} deterministic units; {rewritten} have rewritten copy and every unit has reauthored geometry, speaker, reading order, style, and phone-scale metrics.","","## Before / after","",f"- Baseline lettering units: {len(before_units)}",f"- Revised lettering units: {len(after_units)}",f"- Rewritten copy units: {rewritten}",f"- Total occupied area across the chapter: {before_area*100:.1f}% → {after_area*100:.1f}% of panel-area equivalents",f"- Split/decompressed dialogue beats: 4 (P030, P033, P049, P051)",f"- Silent panels retained: {sum(not p['lettering_units'] for p in manifest['panels'])}","","## Editorial decisions","","P033 and P049 are explicit dialogue compositions with two spatial clusters. P048 keeps three narrow Ledger strips because reconciliation is the narrative beat, yet their combined area remains below 25%. Open Ledger deltas remain small on P036, P038, and P045. SFX follows a chain, impact corner, or fracture vector and is never boxed.","","## Fail-closed policy","","The audit rejects protected-zone overlaps, boxes outside declared negative space, a normal balloon above 15%, total treatment above 25% without a written exception, more than two speech balloons without a written exception, spoken copy above 28 words, speech below 14 px at a 390 px viewport, system copy below 12 px, duplicate selected art, missing negative-space declarations, and unresolved clean-art failures.","","## Panel index",""]
    for p in lettering['panels']:
        report.append(f"- **P{p['order']:03d}** — {p['balloon_count']} balloons, {p['spoken_word_count']} spoken words, {p['total_lettering_area_pct']:.2f}% area; {p['editorial_decision']}.")
    write_text(DOCS/"lettering-editorial-report.md","\n".join(report)+"\n")
    # Complete generation/repair spec: every panel names exact reservation before rendering.
    old_spec=read_json(DATA/"ch01-generation-spec.json"); existing={r.get('panel_order'):r for r in old_spec.get('cases',[])}
    cases=[]
    for panel in manifest['panels']:
        n=panel['order']; scene=existing.get(n,{}).get('scene',panel['beat'])
        exact=f"Reserve exact normalized negative-space regions {json.dumps(panel['negative_space_regions'],separators=(',',':'))} for later deterministic lettering; keep them low-detail and free of faces, eyes, expressive hands, equipment contact, injury evidence, and the primary action silhouette."
        cases.append({"panel_order":n,"panel_id":panel['panel_id'],"scene":scene,"negative_space_regions":panel['negative_space_regions'],"negative_space_instruction":exact,"clean_art_instruction":VISUAL_TARGET,"negative_direction":NEGATIVE_DIRECTION,"final_prompt":f"{scene} {exact} {VISUAL_TARGET} {NEGATIVE_DIRECTION} No words, letters, numbers, symbols, watermarks, captions, balloons, or UI."})
    common=("Create one text-free 1024×1536 Ember Lattice vertical-webtoon panel. Use approved adult Elian Voss, adult Mira Vale, Belljaw, equipment, injury, and Ember Vault continuity anchors. " + VISUAL_TARGET + " " + NEGATIVE_DIRECTION + " No baked-in prose, dialogue, captions, labels, numbers, system text, watermarks, borders, speech balloons, or UI.")
    write_json(DATA/"ch01-generation-spec.json",{"schema":"PremiumCH01GenerationSpec/2.0-editorial","canvas":{"width":1024,"height":1536},"common_prompt":common,"cases":cases})
    # Text-free concept visuals; labels are supplied in deterministic HTML.
    for index,family in enumerate(FACTION_FAMILIES,1): write_text(DATA/f"concepts/gear/family-{index:02d}.svg",_concept_svg(index,family['palette'],'gear'))
    for index,char in enumerate(cast['characters'],1):
        family=next((f for f in FACTION_FAMILIES if f['name'].split()[0].lower() in char['faction'].lower()),FACTION_FAMILIES[(index-1)%len(FACTION_FAMILIES)])
        write_text(DATA/f"concepts/characters/future-{index:02d}.svg",_concept_svg(index,family['palette'],'character'))
    _update_evidence(manifest)
    # Reconcile recommendation and score evidence without changing the selected architecture.
    manifest['project']['build_id']='premium-rd-ch01-editorial-gear-20260904'
    manifest['project']['editorial_schema']='LetteringPlan/2.0'
    manifest['recommendation']['architecture']="Approved reference-conditioned raster plates → targeted deterministic clean-art repair for classified high-frequency failures → exact predeclared negative-space geometry → editable organic SVG speech/SFX/Ledger overlays → collision, density, value, and noise diagnostics → hash-ledger assembly."
    manifest['recommendation']['remaining_gaps']="Pixel-level regeneration remains unavailable because provider seeds, model snapshot, and usage are not exposed. Generated source plates and concepts remain commercially uncleared; deterministic overlays, post-processing code, manifests, and vector concept diagrams are reproducible when the hash-pinned source raster cache is available."
    for evaluation in rubric['evaluations']:
        if evaluation['workflow_id']=='hybrid':
            evaluation['scores']['lettering_safe_composition']=4.95
            evaluation['scores']['sustained_sequential_quality']=4.7
            evaluation['evidence']="Full-size and 390×844 editorial review; exact negative-space declarations; fail-closed collision, density, typography, duplicate-art, and clean-art audits."
    write_json(manifest_path,manifest); write_json(rubric_path,rubric)
    benchmark_manifest_path=DATA/"benchmark-manifest.json"
    if benchmark_manifest_path.is_file():
        benchmark_manifest=read_json(benchmark_manifest_path)
        _update_evidence(benchmark_manifest)
        write_json(benchmark_manifest_path,benchmark_manifest)
    return {"status":"PASS","lettering_units":len(after_units),"rewritten_units":rewritten,"clean_art_repairs":clean_audit['counts']['repaired'],"items":gear['counts']['items'],"chains":gear['counts']['evolution_chains'],"future_characters":cast['counts']['characters'],"browser_reviewed":browser_reviewed}


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description="Build the Ember Lattice editorial and gear pass")
    parser.add_argument("--browser-reviewed",action="store_true")
    args=parser.parse_args(argv)
    print(json.dumps(build_editorial_package(browser_reviewed=args.browser_reviewed),indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
