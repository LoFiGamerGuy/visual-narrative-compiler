"""Compile a conditional CH05 panel-scale/cadence policy from measured layout evidence."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
PLANS=ROOT/"production/comic/ch05-sc01-panel-plans-v1.json"
COVERAGE=ROOT/"production/comic/coverage/ch05-remaining-panel-priority-r1.json"
SELECTED=ROOT/"production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json"
DENSITY=ROOT/"docs/research/evidence/ch05-continuity-style-density-r1.json"
LETTERING=ROOT/"docs/research/evidence/ch05-lettering-width-copy-sensitivity-r1.json"
BANDS=ROOT/"docs/research/evidence/ch05-outside-art-lettering-band-r1.json"
OUTPUT=ROOT/"production/comic/layout/ch05-panel-scale-cadence-policy-r1.json"
CHART=ROOT/"experiments/review-packets/ch05-panel-scale-cadence-policy-r1/ch05-panel-scale-cadence-map-r1.png"
EVIDENCE=ROOT/"docs/research/evidence/ch05-panel-scale-cadence-policy-r1.json"
FONT=Path("C:/Windows/Fonts/arialbd.ttf")

RULES={
 "WIDE_DIRECTIONAL_ANCHOR":{"min":1040,"max":1200,"function":"dual-cast travel/action/reveal anchor","copy":"silent or minimal; use 1200 for tested two-line in-art copy"},
 "WIDE_ENVIRONMENTAL_MOTION":{"min":880,"max":1120,"function":"water/smoke/path motion without people","copy":"normally silent; outside-art caption only after plan revision"},
 "TALL_OR_WIDE_DUAL_CAUSAL":{"min":700,"max":1040,"function":"two-person practical action with literal leverage/hand geometry","copy":"keep action silent; do not trade causal geometry for a balloon"},
 "MEDIUM_SINGLE_CAUSAL":{"min":700,"max":960,"function":"one-adult hand/object causal action","copy":"keep action silent or move approved caption outside art"},
 "MEDIUM_TWO_SHOT":{"min":880,"max":1040,"function":"dual reaction/observation/blocked movement","copy":"if attributed speech is required, test 1200 or revise plan semantics"},
 "MEDIUM_CHARACTER_CLUE":{"min":720,"max":960,"function":"single-adult observation/deduction/continuity","copy":"tested two-line in-art copy requires 1200; otherwise outside-art caption is only a plan-revision option"},
 "SMALL_OBJECT_INSERT":{"min":520,"max":720,"function":"silent clue/object/environment insert","copy":"no dialogue; do not shrink lettering into the art"},
 "SMALL_SENSORY_INSERT":{"min":560,"max":760,"function":"quiet smoke/water/bell/absence beat","copy":"prefer silence; caption band requires plan revision"},
 "MEDIUM_SENSORY_REACTION":{"min":760,"max":1040,"function":"dual sensory/reaction beat","copy":"speech needs literal speaker semantics and 1200 test footprint"},
}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def row_root(rows:list[dict])->str:return hashlib.sha256("\n".join(json.dumps(r,sort_keys=True,separators=(",",":")) for r in rows).encode()).hexdigest()
def select_rule(motion:str,cast:list[str])->str:
 n=len(cast)
 if motion=="practical_action":return "TALL_OR_WIDE_DUAL_CAUSAL" if n==2 else "MEDIUM_SINGLE_CAUSAL"
 if motion=="directional_motion":return "WIDE_DIRECTIONAL_ANCHOR" if n else "WIDE_ENVIRONMENTAL_MOTION"
 if motion=="held_sensory_event":return "SMALL_SENSORY_INSERT" if n==0 else "MEDIUM_CHARACTER_CLUE" if n==1 else "MEDIUM_SENSORY_REACTION"
 if n==0:return "SMALL_OBJECT_INSERT"
 if n==1:return "MEDIUM_CHARACTER_CLUE"
 return "MEDIUM_TWO_SHOT"
def chart(rows:list[dict])->None:
 w,row_h,top=1500,29,115;h=top+len(rows)*row_h+50;im=Image.new("RGB",(w,h),(235,238,242));d=ImageDraw.Draw(im);title=ImageFont.truetype(str(FONT),26);body=ImageFont.truetype(str(FONT),14);small=ImageFont.truetype(str(FONT),12)
 d.text((24,15),"CH05 conditional panel-scale cadence · all 50 ComicPanelPlans",font=title,fill=(20,27,36));d.text((24,55),"Bars show provisional width ranges, not accepted layout. Copy gates can force 1200px or an explicit outside-art plan revision.",font=body,fill=(60,69,81));d.text((24,82),"520",font=small,fill=(60,70,80));d.text((1320,82),"1200 source px",font=small,fill=(60,70,80))
 colors={"selected":(56,137,104),"A":(63,116,186),"B":(207,145,49),"C":(127,135,147)}
 for i,r in enumerate(rows):
  y=top+i*row_h;state_label="SEL" if r["coverage_state"]=="selected" else r["coverage_state"]
  d.text((22,y+5),f"P{r['display_order']:03d}",font=small,fill=(32,39,48));d.text((67,y+5),state_label,font=small,fill=colors[r["coverage_state"]]);d.text((102,y+5),r["scale_role"].replace("_"," ")[:33],font=small,fill=(55,64,75))
  x1=525+round((r["width_range_px"][0]-520)/680*780);x2=525+round((r["width_range_px"][1]-520)/680*780);d.rounded_rectangle((x1,y+6,x2,y+21),radius=5,fill=colors[r["coverage_state"]]);d.text((1315,y+5),f"{r['width_range_px'][0]}–{r['width_range_px'][1]}",font=small,fill=(35,43,52))
 CHART.parent.mkdir(parents=True,exist_ok=True);im.save(CHART,optimize=False)
def main()->int:
 plans=json.loads(PLANS.read_text(encoding="utf-8"));coverage=json.loads(COVERAGE.read_text(encoding="utf-8"));selected=json.loads(SELECTED.read_text(encoding="utf-8"));density=json.loads(DENSITY.read_text(encoding="utf-8"));lettering=json.loads(LETTERING.read_text(encoding="utf-8"));bands=json.loads(BANDS.read_text(encoding="utf-8"))
 coverage_by={r["panel_id"]:r for r in coverage["rows"]};selected_by={r["panel_id"]:r for r in selected["rows"]};rows=[]
 for p in plans["plans"]:
  c=coverage_by[p["panel_id"]];rule_id=select_rule(c["motion_mode"],p["visible_adult_cast"]);rule=RULES[rule_id];actual=selected_by.get(p["panel_id"])
  explicit_dialogue=" says " in (" "+p["narrative_beat"].lower()+" ")
  rows.append({"display_order":p["display_order"],"panel_id":p["panel_id"],"plan_revision_id":p["plan_revision_id"],"coverage_state":c["coverage_state"],"narrative_function":c["narrative_function"],"motion_mode":c["motion_mode"],"visible_adult_cast":p["visible_adult_cast"],"scale_role":rule_id,"width_range_px":[rule["min"],rule["max"]],"function":rule["function"],"copy_policy":rule["copy"],"explicit_dialogue_detected":explicit_dialogue,"final_copy_bound":False,"current_selected_width_px":actual["layout"]["target_width"] if actual else None,"current_selected_candidate_id":actual["candidate_id"] if actual else None,"layout_accepted":False,"comic_panel_plan_revision_created":False})
 chart(rows)
 role_counts=Counter(r["scale_role"] for r in rows)
 policy={"record_type":"ComicPanelScaleCadencePolicy","schema_version":"1.0","record_id":"ng-ch05-panel-scale-cadence-policy-r1","state":"CONDITIONAL_RECOMMENDATION_OWNER_PENDING","medium":"comic","comic_panel_plan_collection":{"path":PLANS.relative_to(ROOT).as_posix(),"sha256":sha(PLANS)},"rules":RULES,"rule_count":len(RULES),"rows":rows,"row_root_sha256":row_root(rows),"summary":{"plan_count":50,"selected_evidence_count":14,"minimum_width_px":min(r["width_range_px"][0] for r in rows),"maximum_width_px":max(r["width_range_px"][1] for r in rows),"explicit_dialogue_plan_count":sum(r["explicit_dialogue_detected"] for r in rows),"final_copy_bound_count":0,"layout_accepted_count":0,"comic_panel_plan_revisions":0},"role_counts":dict(sorted(role_counts.items())),
 "measured_constraints":{"selected_widths_px":sorted({r["layout"]["target_width"] for r in selected["rows"]}),"selected_width_min_px":min(r["layout"]["target_width"] for r in selected["rows"]),"selected_width_max_px":max(r["layout"]["target_width"] for r in selected["rows"]),"tested_two_line_in_art_minimum_px":{"c005":1200,"c013":1200,"h001":1200},"tested_one_line_h001_minimum_px":1120,"target_phone_type_px":lettering["summary"]["target_phone_font_px"],"outside_art_band_phone_type_px":bands["summary"]["font_size_phone_px"],"outside_art_height_increase_percent":bands["summary"]["scroll_height_increase_percent"],"c005_edge_occupancy":next(x["metrics"]["edge_occupancy_ge_32"] for x in density["selected_records"] if x["candidate_id"]=="c005")},
 "lettering_gate":"Opacity cannot compensate for undersized phone type or semantic overlap. In-art copy uses exact copy-length testing; outside-art bands require caption/direct-text semantics and a ComicPanelPlan revision.","animation_shot_plan":None,"e_conte":None,"boundary":"Policy is a fail-closed recommendation matrix, not a layout acceptance, plan revision, final-copy assignment, or generation authority."}
 OUTPUT.parent.mkdir(parents=True,exist_ok=True)
 with OUTPUT.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(policy,indent=2)+"\n")
 evidence={"record_type":"CH05PanelScaleCadencePolicyEvidence","schema_version":"1.0","record_id":"ng-ch05-panel-scale-cadence-policy-evidence-r1","state":"FIFTY_PLAN_CONDITIONAL_SCALE_MATRIX_READY","policy":{"path":OUTPUT.relative_to(ROOT).as_posix(),"sha256":sha(OUTPUT),"row_root_sha256":policy["row_root_sha256"]},"inputs":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)} for p in (PLANS,COVERAGE,SELECTED,DENSITY,LETTERING,BANDS)],"summary":policy["summary"]|{"rule_count":len(RULES),"provider_calls":0,"uploads":0,"external_cost_usd":0,"human_review_minutes":None},"role_counts":policy["role_counts"],"measured_constraints":policy["measured_constraints"],"chart":{"path":CHART.relative_to(ROOT).as_posix(),"sha256":sha(CHART),"bytes":CHART.stat().st_size},"limitations":["Width bands are conditional recommendations, not optimized or accepted per-panel layouts.","Only three existing subjects have exact lettering-width sweeps; 1200px is not a universal typography law.","Final copy, speaker binding, tail geometry, and owner cadence decisions remain absent.","Density statistics cannot assess storytelling or identity."],"activity":{"plans_revised":0,"layouts_accepted":0,"copy_bound":0,"provider_calls":0,"uploads":0,"external_cost_usd":0},"boundary":policy["boundary"]}
 with EVIDENCE.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(evidence,indent=2)+"\n")
 print(f"CH05 scale/cadence policy: 50 plans / {len(RULES)} conditional roles / widths 520–1200 / dialogue plans {policy['summary']['explicit_dialogue_plan_count']}")
 print(f"selected evidence widths {policy['measured_constraints']['selected_widths_px']}; 0 plan revisions/layout acceptances/copy/provider/upload/$0")
 return 0
if __name__=="__main__":raise SystemExit(main())
