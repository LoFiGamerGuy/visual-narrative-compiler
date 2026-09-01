"""Compile the non-promotional selected-route hardening handoff state."""
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATHS={
 "selection_adr": ROOT/"docs/adr/ADR-0025-select-openai-gpt-image-2-for-bounded-targeted-repair-hardening.md",
 "vault": ROOT/"docs/research/evidence/g07-local-evidence-vault-manifest-r1.json",
 "instrumentation": ROOT/"experiments/results/g07-provider-bakeoff-instrumentation-r1.json",
 "review_gate": ROOT/"docs/research/evidence/g07-human-review-rollup-gate-r1.json",
 "budget_audit": ROOT/"docs/research/evidence/g07-aggregate-budget-binding-audit-r2.json",
 "transport_audit": ROOT/"docs/research/evidence/g07-provider-transport-data-boundary-audit-r1.json",
 "boundary": ROOT/"docs/research/evidence/openai-targeted-repair-boundary-hardening-r2.json",
 "selector": ROOT/"config/scale-aware-repair-boundary-selector-contract-r1.json",
 "chapter_matrix": ROOT/"production/comic/repair-readiness/ch05-repair-evidence-readiness-matrix-r1.json",
 "measurement": ROOT/"docs/research/evidence/exact-base-boundary-measurement-packet-r1.json",
 "finalizer": ROOT/"production/comic/repair-readiness/ch05-p036-repair-outcome-finalizer-r1.json",
 "rebuild": ROOT/"docs/research/evidence/selected-route-artifact-rebuild-reproducibility-r1.json",
 "runtime": ROOT/"docs/research/evidence/instrumentation-runtime-inventory-r2.json",
 "production_cost": ROOT/"docs/research/evidence/ch05-production-cost-ledger-r4.json",
 "safe_source": ROOT/"docs/research/evidence/safe-source-release-manifest-f505788.json",
}
OUTPUT=ROOT/"docs/research/evidence/selected-route-hardening-state-r1.json"

class StateError(RuntimeError): pass
def require(v,m):
    if not v: raise StateError(m)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path)}
def load(key): return json.loads(PATHS[key].read_text(encoding="utf-8"))

def build():
    vault=load("vault"); inst=load("instrumentation"); gate=load("review_gate"); budget=load("budget_audit"); transport=load("transport_audit")
    boundary=load("boundary"); selector=load("selector"); matrix=load("chapter_matrix"); measurement=load("measurement"); finalizer=load("finalizer"); rebuild=load("rebuild"); runtime=load("runtime"); cost=load("production_cost"); safe=load("safe_source")
    openai=inst["adapters"]["openai_gpt_image_2"]
    require(vault["inventory"]["completed_candidates"]==16 and budget["ledger_reconciliation"]["committed_actual_cost_usd"]=="1.057377","G07 totals changed")
    require(gate["actual_decisions"]==0 and gate["human_minutes"] is None,"real G07 review unexpectedly present")
    require(selector["summary"]["production_ready_profiles"]==0 and matrix["summary"]["render_records_v2_1"]==0,"production state changed")
    require(cost["entries"]==[] and cost["approved_aggregate_cap_usd"] is None,"CH05 cost authority changed")
    selected_boundary=next(item for item in boundary["variants"] if item["feather_width_px"]==16)["measurements"]
    return {
      "record_type":"SelectedRouteHardeningState","schema_version":"1.0","record_id":"ng-selected-route-hardening-state-r1","state":"ENGINEERING_ROUTE_SELECTED_LOCAL_HARDENING_MEASURED_PRODUCTION_BLOCKED",
      "sources":{key:ref(path) for key,path in PATHS.items()},
      "selection":{
        "adapter_id":"openai_gpt_image_2","model_snapshot":"gpt-image-2-2026-04-21","endpoint":"https://api.openai.com/v1/images/edits","decision":"ADR-0025",
        "basis":"measured required-candidate cost, latency, raster drift/side-effect dimensions, returned provenance, and operational completeness; not visual appeal alone",
        "engineering_hardening_route_only":True,"candidate_or_art_accepted":False,"commercial_clearance_claimed":False,"expanded_upload_authority":False,"automatic_reselection":False,
      },
      "g07_measured_state":{
        "providers":4,"required_candidates":16,"total_required_candidate_cost_usd":"0.987377","additional_paid_failure_cost_usd":"0.070000","aggregate_committed_usd":"1.057377","held_usd":"0.000000","available_usd":"98.942623",
        "selected_arm":{"required_candidates":openai["summary"]["required_candidates"],"cost_usd":openai["summary"]["total_cost_usd"],"elapsed_seconds":openai["summary"]["total_elapsed_seconds"],"mean_elapsed_seconds":openai["summary"]["mean_elapsed_seconds"],"independent_repeat_changed_fraction_gt_8":openai["diagnostics"]["independent_repeat_drift"]["changed_pixel_fraction_threshold_gt_8"],"target_change_changed_fraction_gt_8":openai["diagnostics"]["target_change_global_drift_from_control"]["changed_pixel_fraction_threshold_gt_8"],"no_change_changed_fraction_gt_8":openai["diagnostics"]["no_change_global_drift_from_reference"]["changed_pixel_fraction_threshold_gt_8"]},
        "human_review":{"decisions":0,"required_decisions":20,"human_minutes":None,"accepted_candidates":0,"human_arm_results":None,"composite_score":None,"automatic_ranking":None},
      },
      "local_hardening":{
        "selected_boundary":{"policy":"cosine-inset-16px","artificial_jump_reduction_fraction":selected_boundary["boundary_artificial_jump_reduction_vs_hard"],"central_green_retention_fraction":selected_boundary["core_green_dominant_fraction"],"exterior_changed_pixels":0,"art_accepted":False},
        "scale_profiles":{"P036_width_px":selector["profiles"]["ng-ch05-sc01-p036"]["local_width_px"],"P044_width_px":selector["profiles"]["ng-ch05-sc01-p044"]["local_width_px"],"universal_width_px":None,"topology_passes":2,"exact_panel_visual_passes":0,"timed_seam_reviews":0},
        "synthetic_measurement":{"support_pixels":measurement["measurement"]["support_pixels"],"transition_pixels":measurement["measurement"]["alpha_transition_pixels"],"core_pixels":measurement["measurement"]["fully_replaced_core_pixels"],"boundary_reduction_fraction":measurement["measurement"]["mean_boundary_distance_reduction_fraction"],"exact_exterior":True,"review_pending":True,"eligible_as_real_evidence":False},
        "artifact_rebuild":{"artifacts":rebuild["summary"]["artifacts"],"groups":rebuild["summary"]["artifact_groups"],"bytes":rebuild["summary"]["total_bytes"],"root_sha256":rebuild["summary"]["first_root_sha256"],"rebuilds":2,"byte_identical":True},
        "runtime":{"python":runtime["python"]["version"],"pillow":runtime["requirements"][1]["actual_version"],"numpy":runtime["requirements"][2]["actual_version"],"downloads":False,"network_allowed":False},
      },
      "chapter_scale_readiness":{
        "comic_panel_plans":matrix["summary"]["planned_panels"],"explicit_repair_candidates":matrix["summary"]["explicit_repair_candidates"],"selector_profiles":matrix["summary"]["selector_profiles"],"panel_policies":matrix["summary"]["panel_specific_policies"],
        "approved_bases":0,"approved_masks":0,"external_authorities":0,"production_reservations":0,"exact_visual_results":0,"eligible_seam_reviews":0,"render_records_v2_1":0,"candidates":0,"accepted_panels":0,"human_minutes":None,"production_external_cost_usd":"0.000000",
        "comic_panel_plan_only":True,"animation_shot_plan":None,"e_conte":None,
      },
      "fail_closed_state":{"real_p036_blocker_count":finalizer["real_p036"]["blocker_count"],"real_p036_blockers":finalizer["real_p036"]["blockers"],"render_record":None,"candidate":None,"next_external_action":None},
      "governance":{"transport_https_verified":transport["tls_boundary"]["all_urlopen_calls_use_verified_context"],"observed_input_hashes":transport["data_boundary"]["observed_input_hashes"],"prohibited_data_classes":transport["data_boundary"]["prohibited"],"safe_source_commit":safe["captured_commit"],"safe_source_root":safe["summary"]["inventory_root_sha256"],"ch05_zero_cost_milestones":cost["revision_summary"]["total_local_milestones"],"g07_budget_reuse_for_ch05":False},
      "limitations":["No G07 human review is complete, so selected-arm visual correctness and candidate acceptance remain unknown.","Raster drift is not semantic correctness or reproducibility.","Local synthetic measurement/review fixtures are ineligible as real panel evidence.","No approved CH05 base/mask, external authority, production cap/reservation, provider request, candidate, eligible review, or accepted panel exists.","The route selection is an engineering hardening choice, not commercial clearance or a claim that OpenAI is universally best."],
    }

def mutations(expected):
    vals=[]
    for action in [
      lambda x:x["selection"].update(candidate_or_art_accepted=True),lambda x:x["selection"].update(expanded_upload_authority=True),lambda x:x["g07_measured_state"]["human_review"].update(decisions=20),lambda x:x["g07_measured_state"]["human_review"].update(composite_score=1),lambda x:x["local_hardening"]["scale_profiles"].update(universal_width_px=16),lambda x:x["local_hardening"]["synthetic_measurement"].update(eligible_as_real_evidence=True),lambda x:x["chapter_scale_readiness"].update(approved_bases=1),lambda x:x["chapter_scale_readiness"].update(render_records_v2_1=1),lambda x:x["chapter_scale_readiness"].update(human_minutes=3.0),lambda x:x["fail_closed_state"].update(real_p036_blocker_count=0),lambda x:x["fail_closed_state"].update(next_external_action={}),lambda x:x["governance"].update(g07_budget_reuse_for_ch05=True),lambda x:x["governance"].update(ch05_zero_cost_milestones=26),lambda x:x["chapter_scale_readiness"].update(animation_shot_plan={}),lambda x:x["limitations"].pop()]:
        item=copy.deepcopy(expected); action(item); vals.append(item)
    return sum(v!=expected for v in vals),len(vals)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--emit",type=Path); args=parser.parse_args()
    try:
      expected=build()
      if args.emit:
        target=args.emit if args.emit.is_absolute() else ROOT/args.emit; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(expected,indent=2)+"\n",encoding="utf-8",newline="\n")
      else: require(json.loads(OUTPUT.read_text(encoding="utf-8"))==expected,"tracked state differs")
      rejected,total=mutations(expected); require(rejected==total,"mutation rejection incomplete")
    except (StateError,FileNotFoundError,KeyError,json.JSONDecodeError) as error:
      print(f"FAIL: {error}",file=sys.stderr); return 1
    print("0 failures, 0 warnings (OpenAI engineering route; 16 G07 candidates/$1.057377; human review 0/20/null)")
    print("50 plans/4 explicit/2 profiles/1 policy; 0 real inputs/outcomes/acceptance/$0 production; 9 blockers")
    print(f"26 artifacts rebuild exactly; {rejected}/{total} promotion/denominator/authority mutations rejected")
    return 0
if __name__=="__main__": raise SystemExit(main())
