"""Compile CH05 failure/repair evidence and the smallest next high-information experiment."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
INITIAL=ROOT/"docs/research/evidence/ch05-overnight-production-r1.json";HARD=ROOT/"docs/research/evidence/ch05-cadence-hardening-r1.json"
DENSITY=ROOT/"docs/research/evidence/ch05-continuity-style-density-r1.json";LETTERING=ROOT/"docs/research/evidence/ch05-transparent-lettering-rehearsal-r1.json"
COVERAGE=ROOT/"production/comic/coverage/ch05-remaining-panel-priority-r1.json";EFFORT=ROOT/"docs/research/evidence/ch05-tier-a-effort-scenarios-r1.json"
OUTPUT=ROOT/"production/comic/review/ch05-failure-class-repair-matrix-r1.json";CHART=ROOT/"experiments/review-packets/ch05-failure-class-repair-matrix-r1/ch05-targeted-repair-paths-r1.png";EVIDENCE=ROOT/"docs/research/evidence/ch05-failure-class-repair-matrix-r1.json"
FONT=Path("C:/Windows/Fonts/arialbd.ttf")
REPAIR_LINKS=[
 ("c001","c019","remove identity reference; literal downhill departure and role order","TARGET_FIXED_RELATED_PHONE_WARN_REMAINS"),
 ("c003","h002","place Soren lower-right; specify two crossing print chains","ALL_DIMENSIONS_PASS"),
 ("c007","h003","reserve entire top-left as flat sky; broad flat shapes","ALL_DIMENSIONS_PASS"),
 ("c009","h004","stage both adults in right two-thirds; top-left empty sky","ALL_DIMENSIONS_PASS"),
 ("c011","h005","retain lever terminology but demand complete floor-to-tin span","TARGET_NOT_FIXED_DUPLICATE_PLANK"),
 ("h005","h006","replace lever vocabulary with one literal continuous fallen plank and reach-and-brace roles","ALL_DIMENSIONS_PASS"),
]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def root_hash(value)->str:return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def overall(c):
 vals=c["engineering_review"]["results"].values();return "FAIL" if "FAIL" in vals else "WARN" if "WARN" in vals else "PASS"
def chart(links:list[dict])->None:
 w,h=1600,160+len(links)*175;im=Image.new("RGB",(w,h),(234,237,241));d=ImageDraw.Draw(im);title=ImageFont.truetype(str(FONT),28);body=ImageFont.truetype(str(FONT),16);small=ImageFont.truetype(str(FONT),14)
 d.text((25,18),"CH05 targeted repair paths · exact retained evidence",font=title,fill=(18,25,34));d.text((25,60),"A repair link changes one constraint cluster. Green = all dimensions pass; amber = target fixed but another warning remains; red = target persists.",font=body,fill=(60,70,82))
 colors={"ALL_DIMENSIONS_PASS":(48,139,96),"TARGET_FIXED_RELATED_PHONE_WARN_REMAINS":(197,135,42),"TARGET_NOT_FIXED_DUPLICATE_PLANK":(186,65,61)}
 y=120
 for x in links:
  color=colors[x["outcome"]];d.rounded_rectangle((24,y,210,y+125),12,fill=(248,249,250),outline=(109,119,131),width=2);d.text((48,y+27),x["source_candidate_id"],font=title,fill=(30,38,48));d.text((48,y+70),x["source_overall"],font=body,fill=(105,49,49))
  d.line((220,y+63,425,y+63),fill=color,width=7);d.polygon([(425,y+63),(402,y+50),(402,y+76)],fill=color)
  d.rounded_rectangle((445,y,1130,y+125),12,fill=(250,251,252),outline=color,width=3);d.multiline_text((468,y+19),"\n".join(__import__('textwrap').wrap(x["intervention"],75)),font=body,fill=(38,47,58),spacing=5);d.text((468,y+90),x["outcome"].replace("_"," "),font=small,fill=color)
  d.rounded_rectangle((1160,y,1550,y+125),12,fill=(248,249,250),outline=color,width=3);d.text((1190,y+27),x["result_candidate_id"],font=title,fill=(30,38,48));d.text((1190,y+70),x["result_overall"],font=body,fill=color);y+=175
 CHART.parent.mkdir(parents=True,exist_ok=True);im.save(CHART,optimize=False)
def main()->int:
 initial=json.loads(INITIAL.read_text(encoding="utf-8"));hard=json.loads(HARD.read_text(encoding="utf-8"));density=json.loads(DENSITY.read_text(encoding="utf-8"));lettering=json.loads(LETTERING.read_text(encoding="utf-8"));coverage=json.loads(COVERAGE.read_text(encoding="utf-8"));effort=json.loads(EFFORT.read_text(encoding="utf-8"))
 candidates=initial["candidates"]+hard["candidates"];by_id={c["candidate_id"]:c for c in candidates};nonpass=[]
 for c in candidates:
  misses={k:v for k,v in c["engineering_review"]["results"].items() if v!="PASS"}
  if misses:nonpass.append({"candidate_id":c["candidate_id"],"panel_id":c["panel_id"],"style_id":c["style_id"],"overall":overall(c),"nonpass_dimensions":misses,"note":c["engineering_review"]["note"],"diagnostic_retained":True})
 links=[]
 for source,result,intervention,outcome in REPAIR_LINKS:
  links.append({"source_candidate_id":source,"source_overall":overall(by_id[source]),"result_candidate_id":result,"result_overall":overall(by_id[result]),"intervention":intervention,"outcome":outcome,"prompt_or_pixels_rewritten":False})
 chart(links)
 target_panels=[f"ng-ch05-sc01-p{i:03d}" for i in range(10,14)];coverage_by={r["panel_id"]:r for r in coverage["rows"]};micro=[coverage_by[p] for p in target_panels]
 median=float(effort["observed_basis"]["median_seconds"]);initial_seconds=round(4*median,3);bounded_seconds=round(6*median,3)
 class_summary={"literal_safe_zone_and_spatial_placement":{"attempts":3,"all_dimension_passes":3,"evidence_links":["c003→h002","c007→h003","c009→h004"]},"reference_dominance_role_direction":{"attempts":1,"target_fixed":1,"all_dimension_passes":0,"evidence_links":["c001→c019"]},"lever_terminology":{"attempts":1,"target_fixed":0,"evidence_links":["c011→h005"]},"literal_single_object_causal_chain":{"attempts":1,"target_fixed":1,"all_dimension_passes":1,"evidence_links":["h005→h006"]}}
 next_experiment={"experiment_id":"ch05-tier-a-trail-continuity-microsequence-r1","state":"RECOMMENDED_POST_OWNER_REVIEW_ZERO_EXECUTION_AUTHORITY","comic_panel_plan_ids":target_panels,"plan_count":4,"plan_orders":[10,11,12,13],"coverage_tier":"A","narrative_chain":[r["narrative_beat"] for r in micro],"cast_transition":[r["cast_occupancy"] for r in micro],"motion_transition":[r["motion_mode"] for r in micro],"information_tests":["Sigrid hair/plaid continuity into a Soren-only hand clue","Soren oatmeal-coat/hand identity without overloading the object insert","no-person taut-twine causal direction as a quiet cadence beat","dual-adult re-entry and literal creek-following role order","four-beat style-density rhythm and phone readability"],"candidate_envelope":{"initial_candidates":4,"bounded_targeted_repair_slots":2,"maximum_candidates":6,"observed_median_generation_seconds_initial":initial_seconds,"observed_median_generation_seconds_with_slots":bounded_seconds,"monetary_cost_usd":None},"prompt_count":0,"final_copy_bound":False,"owner_decisions_required":["candidate/style route from current 39-subject review","whether P010–P013 should share one finish or use role-aware cel/clear-line/insert treatment","whether the sequence remains silent or receives plan-level caption semantics"],"animation_shot_plan":None,"e_conte":None,"boundary":"Recommendation only; no prompt, render, upload, budget, acceptance, or plan revision."}
 matrix={"record_type":"ComicFailureClassRepairMatrix","schema_version":"1.0","record_id":"ng-ch05-failure-class-repair-matrix-r1","state":"MEASURED_REPAIR_PATHS_NEXT_EXPERIMENT_RECOMMENDED","medium":"comic","candidate_count":26,"engineering_state_counts":dict(Counter(overall(c) for c in candidates)),"nonpass_candidate_count":len(nonpass),"nonpass_candidates":nonpass,"repair_links":links,"repair_link_count":len(links),"repair_all_dimension_pass_count":sum(x["outcome"]=="ALL_DIMENSIONS_PASS" for x in links),"repair_target_fixed_count":sum(x["outcome"]!="TARGET_NOT_FIXED_DUPLICATE_PLANK" for x in links),"failure_class_summary":class_summary,"post_generation_unresolved":[{"issue":"c005 dense transition and busy safe field","evidence":"edge occupancy 0.308471; owner density decision pending"},{"issue":"c014 semantic lettering overlap","evidence":"tested top-right zone overlaps Soren person/upper arm; opacity cannot fix"},{"issue":"c014→c015 finish jump","evidence":"largest selected adjacent appearance jump 5.6517; punctuation versus unification pending"},{"issue":"c019 phone identity warning","evidence":"direction fixed; identity reads mainly through wardrobe at phone scale"},{"issue":"generation reproducibility","evidence":"built-in model/endpoint/seed unavailable"}],"next_experiment":next_experiment,"route_recommendation":{"route":"role-aware cel-painted character/action plus clear-line transition/composition and genuinely simplified inserts","basis":"cel-painted 5/6 all-pass; clear-line 5/8 all-pass with successful targeted repairs; per-panel density and narrative role outperform uniform style labels","not_based_on":"visual appeal alone","owner_acceptance":False,"commercial_clearance":False},"inputs":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)} for p in (INITIAL,HARD,DENSITY,LETTERING,COVERAGE,EFFORT)],"animation_shot_plan":None,"e_conte":None,"boundary":"No repair is executed and no generated pixel, plan, decision, or acceptance state changes."}
 OUTPUT.parent.mkdir(parents=True,exist_ok=True)
 with OUTPUT.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(matrix,indent=2)+"\n")
 evidence={"record_type":"CH05FailureClassRepairMatrixEvidence","schema_version":"1.0","record_id":"ng-ch05-failure-class-repair-matrix-evidence-r1","state":"SIX_REPAIR_LINKS_AND_FOUR_PLAN_NEXT_EXPERIMENT_BOUND","matrix":{"path":OUTPUT.relative_to(ROOT).as_posix(),"sha256":sha(OUTPUT),"repair_root_sha256":root_hash(links)},"summary":{"candidate_count":26,"engineering_pass":17,"engineering_warn":3,"engineering_fail":6,"nonpass_candidate_count":len(nonpass),"repair_link_count":6,"repair_all_dimension_pass_count":4,"repair_target_fixed_count":5,"next_plan_count":4,"next_initial_candidates":4,"next_maximum_candidates":6,"next_prompt_count":0,"plans_revised":0,"provider_calls":0,"uploads":0,"external_cost_usd":0,"human_review_minutes":None},"chart":{"path":CHART.relative_to(ROOT).as_posix(),"sha256":sha(CHART),"bytes":CHART.stat().st_size},"next_experiment":next_experiment,"limitations":["Six repair links are too few for a general success-rate forecast.","The repair links mix different failure classes and style/reference conditions.","The recommended four-plan microsequence remains owner-review-gated and has no prompts.","Observed seconds exclude queueing, review, layout, and unknown monetary cost."],"activity":{"prompts":0,"renders":0,"provider_calls":0,"uploads":0,"plans_revised":0,"acceptances":0,"external_cost_usd":0},"boundary":matrix["boundary"]}
 with EVIDENCE.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(evidence,indent=2)+"\n")
 print(f"CH05 repair matrix: 26 candidates / {len(nonpass)} nonpass / 6 links / 5 target-fixed / 4 all-pass")
 print(f"next experiment: P010–P013, 4 initial + 2 repair slots, median-only {initial_seconds}/{bounded_seconds}s; prompts/renders/uploads/cost 0/0/0/$0")
 return 0
if __name__=="__main__":raise SystemExit(main())
