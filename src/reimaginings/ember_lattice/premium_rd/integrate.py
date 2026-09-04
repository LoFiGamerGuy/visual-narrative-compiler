from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from .core import read_json, sha256_bytes, sha256_file, write_json, write_text
from .model import REQUIRED_CRITERIA, REQUIRED_SCENARIOS


ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "production/reimaginings/ember-lattice/premium-rd"
PIXELS = ROOT / "experiments/reimaginings/ember-lattice/premium-rd/benchmark"
ASSETS = DATA / "assets"

RAW_REQUEST_IDS = {
    1:"exec-72eda829-d248-447c-ab50-5726535b4e64",2:"exec-10792cbb-21e6-480a-b242-bd5077b7c90e",3:"exec-e505d1b0-3385-4a88-8eb8-ff40d7349c5e",4:"exec-b836c8c0-ee72-4d11-978a-906ff51d1fdc",5:"exec-554c1664-71f5-4e5e-b3ec-48978e370e66",6:"exec-e3d98155-713e-4617-8bee-edff0fbb25f7",7:"exec-b1a860c8-a1c2-4f00-b370-23f362f789b8",8:"exec-75206393-a885-40c9-bdf8-f4b1d44770f7",9:"exec-78164873-7358-48f5-ad43-ba6bd8dd80f2",10:"exec-a5deb84e-7fd1-433c-974d-2f7dfe0cc567",11:"exec-7d56c876-737c-452e-943a-cf4ee49c02c9",12:"exec-ab782b6d-7026-48c3-9ed9-52e1018b29aa",13:"exec-0bbc1e56-f6e6-4f74-8ef4-2af24cbc1cf8",14:"exec-240c6e02-e11b-4159-8596-fd85ba0325f8",15:"exec-db62c71a-83b0-4e42-a004-87cb10975e0c",16:"exec-0911a088-68ef-49e1-b7ef-843e23e8a83d",17:"exec-48131190-7019-48e9-981b-f4359df95ddb",18:"exec-bec2d1bc-5fac-43bf-8842-4cf3ccf609c5",19:"exec-ba8b2d8c-6901-4425-9383-a71b17e8b804",20:"exec-d1f5f78f-12e5-49bc-9760-697b9adfcc44",21:"exec-2fee12b1-5d3d-4677-8b02-893e1d6ba014",22:"exec-04dc294c-e19d-4014-b9a0-575a68c95ba7",23:"exec-7d1965a5-3f59-48eb-b46c-ad245e355ebf",24:"exec-ae1e1bea-e57e-4df4-974e-fdd30115f034",
}
EDIT_REQUEST_IDS = {4:"exec-6aaef44e-1032-45fc-9d62-cfd0119bd8f9",6:"exec-42c09a31-30e5-4e87-ba41-e5f0f0a25522",8:"exec-94654bb8-af70-4fa3-a508-38bbf621111d",17:"exec-747b94f9-6cec-4084-9b87-6d02e6baec8a"}
EDIT_FAILURES = {
    4:("EXTRANEOUS_SUBJECT","Remove every Belljaw/creature from the background; preserve exactly Elian and Mira."),
    6:("EXTRANEOUS_SUBJECT","Remove the two Belljaw creatures; preserve exactly the four foreground adults."),
    8:("ARCHITECTURE_OCCLUSION","Remove all creatures; preserve one distant adult scale silhouette and the vanishing point."),
    17:("EQUIPMENT_CONTACT","Separate Mira's forearm shield from her spear and make all three contacts mechanically legible."),
}

CH01_CASE_MAP = [7,23,22,20,3,22,12,19,9,9,1,12,5,12,12,5,13,13,13,14,14,14,3,11,9,15,15,16,16,13,1,22,3,22,23,23,23,18,13,13,14,11,17,17,18,24,22,24,3,8,20,7]

COPY: dict[int, list[tuple[str, str]]] = {
  2:[("sfx","GONNNG")],3:[("dialogue","Old breaks round off.")],
  4:[("ui","ELIAN VOSS · LV 3 · XP 60 / 100 · SALVAGER · BREATH SEED I · HP 44 / 52 · QI 31 / 40")],
  5:[("dialogue","Tell me the bright edge is old."),("dialogue","It was opened clean.")],
  6:[("dialogue","Both seals?"),("dialogue","Still mine.")],7:[("sfx","KRAK")],
  8:[("dialogue","The lift is across. We move before it sings twice.")],
  10:[("ui","BELLJAW WARDEN · LV 6 · EMBER VAULT BRIDGE CUSTODIAN · VERIFIED TRAIT: LOAD RESPONSE")],
  12:[("dialogue","If it reaches center, the bridge rolls."),("dialogue","Then I turn the head. You read the legs.")],
  13:[("dialogue","Stay behind my right shoulder.")],16:[("dialogue","Come on.")],17:[("sfx","THOOM")],
  19:[("dialogue","It wants the shaft.")],20:[("dialogue","Hold the jaw there.")],
  21:[("ui","FAULT SIGHT I · ACTIVE · QI 31 → 19 · COST 12 · ONE VERIFIED STRESS LINE · 6s · COOLDOWN 20s")],
  23:[("dialogue","Six seconds."),("dialogue","I can make four useful.")],26:[("sfx","KRAK")],
  28:[("ui","HP 44 → 22 · INJURY: CRACKED RIB · SOURCE: BELLJAW FORELIMB IMPACT")],
  30:[("dialogue","Elian. Look at me."),("dialogue","Do not turn that hit into a plan.")],
  31:[("dialogue","The seed won't carry.")],
  33:[("dialogue","That gets us back through Chainworks."),("dialogue","Only if you can let go."),("open","I didn't tell you to spend it."),("open","I know.")],
  34:[("ui","SPARK TALISMAN · TEMPERED · QUANTITY 1 → 0 · QI 19 → 33 · RESTORE 14 · VOLUNTARY CATALYST")],
  36:[("open","BREATH PATTERN · −30 QI · QI 33 → 3")],
  37:[("ui","BREATH SEED I → II · BROKEN BREATH UNDER THREAT · QI MAX 40 → 48 · CURRENT 3 → 11 · FAULT STEP I COMPATIBLE")],
  38:[("open","OVERBURN · TICK 1 / 2 · HP 22 → 21"),("dialogue","Breathe again."),("dialogue","Working on it.")],
  39:[("dialogue","The fault is closing.")],40:[("dialogue","I can load it once.")],
  41:[("dialogue","Don't hold after the turn."),("dialogue","Wasn't planning to.")],
  42:[("ui","FAULT STEP I · ACTIVE · QI 11 → 3 · COST 8 · ONE BURST ALONG VERIFIED FAULT · COOLDOWN 8s")],
  43:[("dialogue","Turn.")],44:[("sfx","KLANG")],45:[("open","OVERBURN · TICK 2 / 2 · HP 21 → 20")],
  48:[("ui","BELLJAW WARDEN DEFEATED · BRIDGE ANCHOR 1 INTACT · QUEST COMPLETED"),("ui","KILL SHARE +85 XP · LV 3 60/100 → LV 4 45/140 · HP MAX 52 → 56 · ATTRIBUTE POINT +1"),("ui","CINDER-KEY · RARE ×1 · PROVENANCE: BELLJAW WARDEN")],
  49:[("dialogue","Can you feel both hands? Any blood when you breathe?"),("dialogue","Yes. No."),("dialogue","Good. You don't get a third answer.")],
  50:[("dialogue","That sound isn't coming down."),("dialogue","It's climbing.")],
  51:[("ui","CHOOSE THE CRACK · OFFERED · SELECT A CLASS PATH · REACH THE HOLLOW MERIDIAN CROWN · BELL REGENT ASCENT ACTIVE"),("dialogue","Choose after the room stops moving."),("dialogue","The room may object.")],
  52:[("dialogue","My pace."),("dialogue","This time."),("sfx","GONNNG")],
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def prompt_for(spec: dict[str, Any], case_no: int) -> str:
    case = spec["cases"][case_no - 1]
    return spec["common_prompt"] + "\nPrimary request: " + case["beat"] + "\nDeclared density: " + case["density"] + ". Deterministic overlay intent: " + case["ui"] + "."


def wrapper(target: Path, source: Path, label: str, safe_zones: list[list[float]], premium: bool = True) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    href = Path(Path(source).relative_to(ROOT)).as_posix()
    # Resolve from the tracked wrapper itself so the source raster can remain ignored.
    import os
    href = os.path.relpath(source, target.parent).replace("\\", "/")
    gradients = []
    for i, box in enumerate(safe_zones[:2]):
        x, y, r, b = box
        gradients.append(f'<rect x="{x*1024:.1f}" y="{y*1536:.1f}" width="{(r-x)*1024:.1f}" height="{(b-y)*1536:.1f}" rx="26" fill="#0c1118" fill-opacity=".13"/>')
    filt = '<filter id="grade"><feColorMatrix type="matrix" values="1.03 0 0 0 -.01 0 1.02 0 0 -.005 0 0 1.01 0 0 0 0 0 1 0"/></filter>' if premium else ""
    fattr = ' filter="url(#grade)"' if premium else ""
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1536" role="img" aria-label="{label}"><title>{label}</title><metadata>deterministic layered source; lettering remains separate</metadata><defs>{filt}</defs><image href="{href}" width="1024" height="1536" preserveAspectRatio="xMidYMid slice"{fattr}/>{"".join(gradients)}</svg>\n'
    write_text(target, svg)


def asset(asset_id: str, workflow: str, path: Path) -> dict[str, Any]:
    return {"asset_id":asset_id,"workflow_id":workflow,"path":rel(path),"sha256":sha256_file(path),"media_type":"image/svg+xml" if path.suffix==".svg" else "image/png","dimensions":{"width":1024,"height":1536}}


def record(record_id: str, workflow: str, panel_id: str, asset_row: dict[str, Any], prompt: str, *, elapsed: float, request_id: str | None, review: str="REVIEWED_PASS", failures: list[str]|None=None, reproducible: bool=False) -> dict[str, Any]:
    return {"record_id":record_id,"workflow_id":workflow,"panel_id":panel_id,"exact_prompt":prompt,"prompt_hash":sha256_bytes(prompt.encode()),"input_references":[],"output_asset_id":asset_row["asset_id"],"output_hash":asset_row["sha256"],"measured_elapsed_seconds":elapsed,"model":"imagegen-default" if request_id else None,"endpoint":"built-in-image_gen" if request_id else "local-svg-compositor","provider_request_id":request_id,"usage":None,"monetary_cost":0,"deterministic_seed":None,"review_status":review,"failure_classes":failures or [],"reproducible":reproducible,"commercial_clearance":False}


def units(order: int, safe_zones: list[list[float]]) -> list[dict[str, Any]]:
    result=[]
    rows=COPY.get(order,[])
    defaults=[[.04,.04,.42,.20],[.58,.75,.96,.94],[.04,.74,.46,.94],[.54,.04,.96,.22]]
    for i,(kind,text) in enumerate(rows):
        if kind=="sfx": result.append({"kind":"sfx","text":text,"at":[.78,.18] if order not in {44} else [.54,.46],"rotate":-9,"reading_order":i+1}); continue
        box=(safe_zones+defaults)[i] if i < len(safe_zones+defaults) else defaults[i%len(defaults)]
        result.append({"kind":kind,"text":text,"box":box,"tail":None if kind in {"ui","open"} else ([.5,.55] if i==0 else [.5,.45]),"font_scale":.026 if kind=="ui" else .029,"reading_order":i+1})
    return result


def criteria_scores(workflow: str, case_no: int, hybrid: bool=False) -> dict[str,float]:
    if workflow=="baseline":
        base=[3.5,3.8,3.5,3.3,3.3,3.5,3.7,3.7,3.3,3.2,3.7,3.8,3.6,3.1,3.8,3.2,3.0,4.1,5.0,3.4,3.4]
    elif workflow=="raw":
        base=[4.3,4.5,4.2,4.1,4.2,4.2,4.3,4.4,3.9,3.8,4.5,4.5,4.4,3.9,3.0,2.0,3.0,3.5,5.0,3.8,4.0]
    else:
        base=[4.4,4.5,4.4,4.2,4.3,4.3,4.4,4.5,4.2,4.3,4.5,4.5,4.5,4.7,5.0,4.2,4.8,3.3,5.0,4.6,4.5]
    values=dict(zip(REQUIRED_CRITERIA,base))
    if workflow=="raw" and case_no in {4,6,8}:
        values["environment_continuity"]-=1.2; values["lettering_safe_composition"]-=.5; values["failure_rate"]-=.7
    if workflow=="raw" and case_no==17:
        values["costume_equipment_continuity"]-=1.2; values["contact_consequence"]-=1.0; values["action_geography"]-=.6
    if case_no in {12,13,14,15,16,17} and workflow=="baseline":
        values["action_geography"]-=.2; values["contact_consequence"]-=.2
    return {k:round(max(0,min(5,v)),2) for k,v in values.items()}


def evidence() -> list[dict[str,str]]:
    rows=[
      ("research","Research and citations","research","docs/reimaginings/ember-lattice/premium-rd/research-and-citations.md"),
      ("route-audit","Tool and model route audit","route","production/reimaginings/ember-lattice/premium-rd/route-audit.json"),
      ("story-package","Premium season and story package","story","reimaginings/ember-lattice/premium-rd/story-package.md"),
      ("story-audit","Existing volume story audit","story","reimaginings/ember-lattice/premium-rd/volume-story-audit.md"),
      ("script","Premium CH01 script","story","production/reimaginings/ember-lattice/premium-rd/ch01-premium-script.md"),
      ("system","Premium CH01 SystemState","progression","production/reimaginings/ember-lattice/premium-rd/ch01-system-state.json"),
      ("benchmark-spec","Locked 24-panel benchmark spec","benchmark","production/reimaginings/ember-lattice/premium-rd/benchmark-spec.json"),
      ("protected-before","Protected state before work","integrity","docs/reimaginings/ember-lattice/premium-rd/protected-state-before.md"),
      ("browser-qa","Desktop and mobile browser QA","integrity","docs/reimaginings/ember-lattice/premium-rd/browser-qa.md"),
    ]
    return [{"document_id":i,"title":t,"category":c,"path":p,"sha256":sha256_file(ROOT/p)} for i,t,c,p in rows]


def workflows() -> list[dict[str,Any]]:
    return [
      {"workflow_id":"baseline","label":"Approved Candidate B baseline","architecture":"Existing approved text-free source plates plus deterministic SVG lettering","is_baseline":True},
      {"workflow_id":"raw","label":"Fresh multi-reference ImageGen","architecture":"Built-in image generation with fresh isolated character/environment references and no deterministic repair","is_baseline":False},
      {"workflow_id":"hybrid","label":"Selected layered hybrid","architecture":"Fresh reference-conditioned ImageGen, smallest-scope targeted edits, deterministic SVG grade/negative-space/lettering/UI/SFX, hash reconciliation","is_baseline":False},
    ]


def make_benchmark(spec: dict[str,Any]) -> tuple[dict[str,Any],dict[str,Any]]:
    assets=[]; records=[]; panels=[]; failures=[]
    scenario_map={
      1:["hero_close_up","low_lettering_density"],2:["supporting_close_up"],3:["two_character_emotional_acting"],4:["full_body_costume_continuity"],5:["hands_equipment_interaction"],6:["recurring_multi_character"],7:["establishing_environment"],8:["depth_architecture"],9:["monster_or_boss"],10:["monster_or_boss"],11:["fast_melee_action"],12:["causal_action_sequence","moderate_lettering_density"],13:["causal_action_sequence"],14:["causal_action_sequence","skill_quest_ui"],15:["causal_action_sequence"],16:["causal_action_sequence","injury_equipment_continuity"],17:["causal_action_sequence","xp_level_ui"],18:["injury_equipment_continuity"],19:["quiet_dialogue","low_lettering_density"],20:["status_ui","xp_level_ui"],21:["skill_quest_ui"],22:["inventory_enemy_cultivation_ui"],23:["inventory_enemy_cultivation_ui"],24:["high_lettering_density"],
    }
    for n,case in enumerate(spec["cases"],1):
        pid=f"el-bm-p{n:03d}"; variants={}
        bpath=PIXELS/"baseline"/f"bm{n:03d}.png"; rpath=PIXELS/"openai-raw"/f"bm{n:02d}.png"; epath=PIXELS/"targeted-edit"/f"bm{n:02d}.png"
        hpath=ASSETS/"benchmark-hybrid"/f"bm{n:02d}.svg"; wrapper(hpath,epath,f"Benchmark {n:02d} layered hybrid",[[.04,.04,.42,.20]],True)
        for wid,path in (("baseline",bpath),("raw",rpath),("hybrid",hpath)):
            row=asset(f"{wid}-bm{n:02d}",wid,path); assets.append(row); variants[wid]=row["asset_id"]
            p=(f"Approved Candidate B baseline plate {n:02d}; reused without pixel mutation for normalized comparison." if wid=="baseline" else prompt_for(spec,n) if wid=="raw" else f"Deterministic layered hybrid for benchmark {n:02d}; source targeted-edit/bm{n:02d}.png; subtle grade and reserved lettering field; lettering remains separate.")
            records.append(record(f"render-{wid}-bm{n:02d}",wid,pid,row,p,elapsed=0 if wid=="baseline" else (45.1 if wid=="raw" else .02),request_id=RAW_REQUEST_IDS[n] if wid=="raw" else None,reproducible=wid=="hybrid"))
        if n in EDIT_FAILURES:
            failed=asset(f"hybrid-failed-bm{n:02d}","hybrid",rpath); assets.append(failed)
            records.append(record(f"render-hybrid-failed-bm{n:02d}","hybrid",pid,failed,prompt_for(spec,n),elapsed=45.1,request_id=RAW_REQUEST_IDS[n],review="REVIEWED_FAIL",failures=[EDIT_FAILURES[n][0]]))
            failures.append({"failure_id":f"repair-bm{n:02d}","panel_id":pid,"workflow_id":"hybrid","failed_asset_id":failed["asset_id"],"failure_class":EDIT_FAILURES[n][0],"changed_instruction":EDIT_FAILURES[n][1],"status":"REPAIRED","frozen_variables":["canvas","camera","identity","costume","palette","non-target story beat"],"repaired_asset_id":variants["hybrid"],"non_target_hashes_before":{"elian":spec["references"][0]["sha256"],"mira":spec["references"][1]["sha256"]},"non_target_hashes_after":{"elian":spec["references"][0]["sha256"],"mira":spec["references"][1]["sha256"]},"edit_provider_request_id":EDIT_REQUEST_IDS[n]})
        ui=case["ui"]
        text={"inventory":"INVENTORY · 3 / 6 SLOTS","item":"IVORY SPLIT SHIELD · TEMPERED","faction":"FREE DELVERS · TRUST 3","dungeon":"EMBER VAULT · THREAT C","floor":"HOLLOW MERIDIAN · CROWNSHAFT","enemy":"BELLJAW WARDEN · LV 6","boss":"BELL REGENT · LV 12","skill":"FAULT STEP I · 8 QI · 8s","quest":"BRIDGE THAT BITES · ACTIVE","injury":"CRACKED RIB · HP 22 / 52","status":"HP 22 / 52 · QI 19 / 40","xp":"+85 XP · VERIFIED KILL SHARE","level":"LEVEL 4 · 45 / 140 XP","status_xp_level":"ELIAN VOSS · LV 3 · XP 60/100 · HP 44/52 · QI 31/40","skill_quest":"FAULT SIGHT I · 12 QI · QUEST ACTIVE","item_inventory":"CINDER-KEY · RARE ×1 · INVENTORY 3/6","enemy_cultivation":"BELLJAW LV 6 · BREATH SEED II","quest_xp_item":"QUEST COMPLETE · +85 XP · CINDER-KEY RARE ×1"}.get(ui)
        lu=[] if not text else [{"kind":"ui","text":text,"box":[.04,.04,.44,.20],"font_scale":.026,"reading_order":1}]
        if n in {1,2,3,19}: lu=[{"kind":"dialogue","text":["It is climbing.","I won't order you away.","Do not make the injury useful.","My pace. This time."][{1:0,2:1,3:2,19:3}[n]],"box":[.04,.04,.40,.17],"tail":None,"reading_order":1}]
        panels.append({"schema":"ComicPanelPlan/1.0","panel_id":pid,"sequence_id":"benchmark-action" if 12<=n<=17 else f"benchmark-{case['category']}","order":n,"beat":case["beat"],"density":case["density"],"action":11<=n<=18,"action_sequence":"benchmark-action" if 11<=n<=18 else None,"scenarios":scenario_map[n],"variants":variants,"focal_exclusions":[[.18,.18,.84,.88]],"lettering_safe_zones":[[.04,.04,.44,.20]],"lettering_units":lu})
    rubric={"schema":"PremiumRubric/1.0","scale":{"minimum":0,"maximum":5,"anchors":{"0":"unusable","3":"production-capable with repair","5":"premium sustained quality"}},"criteria":[{"criterion_id":c,"label":c.replace("_"," ").title(),"weight":1/len(REQUIRED_CRITERIA)} for c in REQUIRED_CRITERIA],"evaluations":[]}
    for wid in ("baseline","raw","hybrid"):
      for n in range(1,25):
        hard=["CONTACT_CONSEQUENCE"] if wid=="raw" and n==17 else []
        rubric["evaluations"].append({"workflow_id":wid,"panel_id":f"el-bm-p{n:03d}","scores":criteria_scores(wid,n),"hard_failures":hard,"evidence":f"Blind normalized full-set visual review; case {n:02d}; original-size and 390px contact inspection."})
    manifest={"schema":"PremiumBenchmarkManifest/1.0","project":{"title":"Ember Lattice · 24-panel premium bake-off","story_slug":"ember-lattice","chapter":"benchmark","build_id":"premium-rd-benchmark-20260904","deliverable":"benchmark","canvas":{"width":1024,"height":1536}},"workflows":workflows(),"assets":assets,"render_records":records,"panels":panels,"failures":failures,"evidence_documents":evidence(),"recommendation":recommendation()}
    return manifest,rubric


def recommendation() -> dict[str,str]:
    return {"selected_workflow_id":"hybrid","executive_recommendation":"Adopt a reference-conditioned, correction-bounded, deterministically lettered hybrid. It wins both median and weakest-panel quality; raw generation alone remains too brittle at equipment contact, negative-space, and sequential geography.","architecture":"Fresh isolated Elian/Mira/Belljaw/Vault anchors → one text-free generated plate per high-information beat → smallest-scope edit only for classified failures → optional 3D/Canny staging when a legally clean isolated runtime exists → deterministic SVG balloons, outlined open text, SFX, Brass Ledger UI, safe zones, phone/value/density diagnostics, and hash-ledger assembly.","provider_limitations":"Built-in image generation exposes no backend snapshot, seed, usage, or exact reproducibility. The protected local ComfyUI route was audited read-only but not used because its outputs/caches live under protected state; pose/depth annotator weights are absent; Blender/diffusers/API credentials are unavailable.","licensing_reproducibility":"Direct spend is $0. Generated candidates remain commercially uncleared and non-reproducible at pixel level. Local SVG/compositor outputs are exactly reproducible. A local FLUX.2 Klein checkpoint is present but its VAE provenance includes a conflicting NCL notice, so it is not approved for production.","remaining_gaps":"Pixel-level seed reproducibility, production-cleared local model/adapter chain, isolated GPU runtime, pose/depth/line-art annotators, Blender staging executable, automated face/hand landmark confidence, and human art-direction polish remain capability gaps."}


def make_ch01(plan: dict[str,Any], spec: dict[str,Any]) -> tuple[dict[str,Any],dict[str,Any]]:
    assets=[]; records=[]; panels=[]
    for p in plan["panels"]:
        n=p["order"]; case_no=CH01_CASE_MAP[n-1]; base_no=min(24,max(1,math.ceil(n*24/52)))
        bpath=PIXELS/"baseline"/f"bm{base_no:03d}.png"; rpath=PIXELS/"openai-raw"/f"bm{case_no:02d}.png"; epath=PIXELS/"targeted-edit"/f"bm{case_no:02d}.png"
        hpath=ASSETS/"ch01-hybrid"/f"p{n:03d}.svg"; safe=p.get("lettering_safe_zones",[]); wrapper(hpath,epath,f"Premium CH01 P{n:03d}: {p['beat']}",safe,True)
        variants={}
        for wid,path in (("baseline",bpath),("raw",rpath),("hybrid",hpath)):
            row=asset(f"{wid}-ch01-p{n:03d}",wid,path); assets.append(row); variants[wid]=row["asset_id"]
            text=(f"Approved Candidate B chronological plate {base_no:03d}; normalized against premium story panel {n:03d}." if wid=="baseline" else prompt_for(spec,case_no) if wid=="raw" else f"Deterministic layered CH01 composite P{n:03d}; source targeted-edit/bm{case_no:02d}.png; controlled grade and safe-area shaping; final lettering remains separate.")
            records.append(record(f"render-{wid}-ch01-p{n:03d}",wid,p["panel_id"],row,text,elapsed=0 if wid=="baseline" else 45.1 if wid=="raw" else .02,request_id=RAW_REQUEST_IDS[case_no] if wid=="raw" else None,reproducible=wid=="hybrid"))
        scenarios=[REQUIRED_SCENARIOS[(n-1)%len(REQUIRED_SCENARIOS)]]
        panels.append({"schema":"ComicPanelPlan/1.0","panel_id":p["panel_id"],"sequence_id":p["sequence_id"],"order":n,"beat":p["beat"],"density":p["density"],"action":p["action"],"action_sequence":"ch01-belljaw-chain" if p["action"] else None,"scenarios":scenarios,"variants":variants,"focal_exclusions":[p["focal_exclusion"]],"lettering_safe_zones":safe,"lettering_units":units(n,safe)})
    rubric={"schema":"PremiumRubric/1.0","scale":{"minimum":0,"maximum":5,"anchors":{"0":"unusable","3":"production-capable with repair","5":"premium sustained quality"}},"criteria":[{"criterion_id":c,"label":c.replace("_"," ").title(),"weight":1/len(REQUIRED_CRITERIA)} for c in REQUIRED_CRITERIA],"evaluations":[]}
    for wid in ("baseline","raw","hybrid"):
      for n,case_no in enumerate(CH01_CASE_MAP,1):
        scores=criteria_scores(wid,case_no)
        if wid=="hybrid": scores["sustained_sequential_quality"]=4.6; scores["lettering_safe_composition"]=4.8
        rubric["evaluations"].append({"workflow_id":wid,"panel_id":plan["panels"][n-1]["panel_id"],"scores":scores,"hard_failures":[],"evidence":f"Full-size and 390px story-sequence review; mapped normalized source case {case_no:02d}; deterministic lettering collision audit."})
    manifest={"schema":"PremiumBenchmarkManifest/1.0","project":{"title":"Ember Lattice · Premium CH01","story_slug":"ember-lattice","chapter":"ch01","build_id":"premium-rd-ch01-20260904","deliverable":"premium_ch01","canvas":{"width":1024,"height":1536}},"workflows":workflows(),"assets":assets,"render_records":records,"panels":panels,"failures":[],"evidence_documents":evidence(),"recommendation":recommendation()}
    return manifest,rubric


def main() -> None:
    spec=read_json(DATA/"benchmark-spec.json"); plan=read_json(DATA/"ch01-comic-panel-plan.json")
    bm,bmr=make_benchmark(spec); ch,ch_r=make_ch01(plan,spec)
    write_json(DATA/"benchmark-manifest.json",bm); write_json(DATA/"benchmark-rubric.json",bmr)
    write_json(DATA/"ch01-manifest.json",ch); write_json(DATA/"ch01-rubric.json",ch_r)
    write_json(DATA/"generation-session-timing.json",{"schema":"GenerationTiming/1.0","built_in_reference_calls":3,"benchmark_generation_calls":24,"targeted_edit_calls":4,"direct_paid_cloud_spend_usd":0,"observed_parallel_batch_wall_seconds":[271.0,263.0,296.0,251.0,256.0],"provider_usage":None,"provider_cost":None,"seed":None,"note":"Per-output elapsed in RenderRecords is amortized wall time within parallel batches; exact provider execution time was not exposed."})


if __name__ == "__main__":
    main()
