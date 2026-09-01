"""Append-only selector r2 with panel-neutral disconnected/hole coverage."""
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
R1=ROOT/"config/scale-aware-repair-boundary-selector-contract-r1.json"
STRESS=ROOT/"docs/research/evidence/disconnected-holed-mask-topology-stress-r1.json"
R2=ROOT/"config/scale-aware-repair-boundary-selector-contract-r2.json"

class SelectorError(RuntimeError): pass
def require(v,m):
    if not v: raise SelectorError(m)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    prior=json.loads(R1.read_text(encoding="utf-8")); stress=json.loads(STRESS.read_text(encoding="utf-8"))
    require(prior["summary"]["local_profiles"]==2 and prior["summary"]["universal_width_px"] is None,"r1 profile state changed")
    require(stress["decision"]["selected_width_px"]==8 and stress["decision"]["panel_profile_created"] is False,"stress promotion changed")
    return {"record_type":"ScaleAwareRepairBoundarySelectorContract","schema_version":"1.1","contract_id":"ng-scale-aware-repair-boundary-selector-contract-r2","state":"LOCAL_SELECTOR_CONTRACT_EXPANDED_TOPOLOGY_COVERAGE_NO_PRODUCTION_READY_PROFILES","supersedes":{"contract_id":prior["contract_id"],"path":R1.relative_to(ROOT).as_posix(),"sha256":sha(R1)},"prior_contract_rewritten":False,"selection_pipeline":prior["selection_pipeline"],"profiles":prior["profiles"],"panel_neutral_mechanics_controls":{"disconnected_holed_support":{"source":{"path":STRESS.relative_to(ROOT).as_posix(),"sha256":sha(STRESS)},"selected_local_width_px":stress["decision"]["selected_width_px"],"support_components":2,"protected_holes":1,"ring_core_fraction":stress["decision"]["selected_measurements"]["ring_core_fraction"],"thin_component_core_fraction":stress["decision"]["selected_measurements"]["thin_component_core_fraction"],"exact_hole_and_exterior":True,"eligible_as_panel_profile":False,"eligible_as_production_policy":False,"eligible_as_visual_acceptance":False}},"summary":{"local_profiles":2,"panel_neutral_mechanics_controls":1,"distinct_panel_profile_widths_px":[5,16],"universal_width_px":None,"topology_control_passes":3,"exact_panel_base_visual_boundary_passes":0,"timed_human_seam_reviews":0,"production_ready_profiles":0,"approved_production_masks":0,"provider_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"},"generalization_rules":dict(prior["generalization_rules"],panel_neutral_control_width_inheritance=False,panel_neutral_control_creates_profile=False,panel_neutral_control_creates_policy=False),"boundary":"R2 expands only abstract topology coverage. P036/P044 profiles and all exact-base visual, review, input, budget, authority, and production gates remain unchanged."}

def mutations(expected):
    vals=[]; actions=[lambda x:x["supersedes"].update(sha256="0"*64),lambda x:x.update(prior_contract_rewritten=True),lambda x:x["profiles"]["ng-ch05-sc01-p036"].update(local_width_px=8),lambda x:x["profiles"]["ng-ch05-sc01-p044"].update(local_width_px=8),lambda x:x["panel_neutral_mechanics_controls"]["disconnected_holed_support"].update(eligible_as_panel_profile=True),lambda x:x["panel_neutral_mechanics_controls"]["disconnected_holed_support"].update(eligible_as_production_policy=True),lambda x:x["panel_neutral_mechanics_controls"]["disconnected_holed_support"].update(eligible_as_visual_acceptance=True),lambda x:x["summary"].update(local_profiles=3),lambda x:x["summary"].update(universal_width_px=8),lambda x:x["summary"].update(exact_panel_base_visual_boundary_passes=1),lambda x:x["summary"].update(timed_human_seam_reviews=1),lambda x:x["summary"].update(production_ready_profiles=1),lambda x:x["generalization_rules"].update(panel_neutral_control_width_inheritance=True)]
    for action in actions: item=copy.deepcopy(expected); action(item); vals.append(item)
    return sum(v!=expected for v in vals),len(vals)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--emit",type=Path); args=parser.parse_args()
    try:
        expected=build()
        if args.emit:
            target=args.emit if args.emit.is_absolute() else ROOT/args.emit; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(expected,indent=2)+"\n",encoding="utf-8",newline="\n")
        else: require(json.loads(R2.read_text(encoding="utf-8"))==expected,"tracked selector r2 differs")
        rejected,total=mutations(expected); require(rejected==total,"mutation rejection incomplete")
    except (SelectorError,FileNotFoundError,KeyError,json.JSONDecodeError) as error:
        print(f"FAIL: {error}",file=sys.stderr); return 1
    print("0 failures, 0 warnings (r1 pinned; P036=16/P044=5; one panel-neutral 8px disconnected/hole control)")
    print(f"3 topology controls, 0 exact-panel visual/review/production-ready; {rejected}/{total} promotion/generalization mutations rejected")
    return 0
if __name__=="__main__": raise SystemExit(main())
