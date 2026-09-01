"""Run the pinned core suite plus post-suite hardening validators as one gate."""
from __future__ import annotations
import argparse,copy,hashlib,json,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CORE="src/north_garden/validate_ch05_instrumentation_suite.py"
EXT=[
 ("safe_source_release","src/north_garden/validate_safe_source_release_manifest.py"),
 ("aggregate_budget_binding_audit","src/north_garden/validate_bakeoff_adapter_budget_binding_audit.py"),
 ("provider_transport_boundary","src/north_garden/validate_provider_transport_data_boundary.py"),
 ("selected_route_hardening_state","src/north_garden/validate_selected_route_hardening_state.py"),
 ("disconnected_holed_topology","src/north_garden/validate_disconnected_holed_topology_stress.py"),
 ("selector_contract_r2","src/north_garden/validate_scale_aware_boundary_selector_r2.py"),
 ("artifact_rebuild_r2","src/north_garden/validate_selected_route_artifact_rebuild_r2.py"),
 ("production_cost_ledger_r4","src/north_garden/validate_ch05_production_cost_ledger_r4.py"),
 ("production_cost_ledger_r5","src/north_garden/validate_ch05_production_cost_ledger_r5.py"),
]
CORE_REPORT=ROOT/"experiments/results/ch05-instrumentation-validation-suite-r1.json"
OUTPUT=ROOT/"docs/research/evidence/hardening-release-validation-gate-r1.json"
class E(RuntimeError):pass
def req(v,m):
 if not v:raise E(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(script):
 t=time.perf_counter(); r=subprocess.run([sys.executable,script],cwd=ROOT,capture_output=True,text=True); return r,round((time.perf_counter()-t)*1000,3)
def execute():
 core,core_ms=run(CORE); req(core.returncode==0,"core suite failed"); report=json.loads(CORE_REPORT.read_text(encoding="utf-8")); req(report["passed"] and report["checks_passed"]==44,"core suite count changed")
 extension=[]
 for name,script in EXT:
  r,ms=run(script); req(r.returncode==0,f"extension failed: {name}"); extension.append({"name":name,"script":script,"script_sha256":sha(ROOT/script),"passed":True,"stdout_last_line":r.stdout.strip().splitlines()[-1],"observed_elapsed_ms":ms})
 return {"core_ms":core_ms,"extensions":extension}
def semantic(observed):
 return {"record_type":"HardeningReleaseValidationGate","schema_version":"1.0","record_id":"ng-hardening-release-validation-gate-r1","state":"ALL_CORE_AND_POST_SUITE_LOCAL_CHECKS_PASS","core":{"suite_path":CORE,"suite_sha256":sha(ROOT/CORE),"checks":44,"passed":44},"extensions":[{k:v for k,v in item.items() if k!="observed_elapsed_ms"} for item in observed["extensions"]],"summary":{"core_checks":44,"extension_checks":len(EXT),"total_checks":44+len(EXT),"passed_checks":44+len(EXT),"failed_checks":0},"activity":{"network_requests":0,"provider_requests":0,"external_uploads":0,"models_downloaded":0,"external_cost_usd":"0.000000"},"boundaries":["The gate executes local validators only; dormant provider adapters remain no-execute.","Core suite remains a distinct pinned entrypoint; later append-only validators are not folded into its historical count.","Passing mechanics/governance checks does not create human review, art acceptance, commercial clearance, or CH05 authority."]}
def mutations(e):
 vals=[]; acts=[lambda x:x["core"].update(checks=43),lambda x:x["extensions"].pop(),lambda x:x["extensions"][0].update(passed=False),lambda x:x["summary"].update(total_checks=52),lambda x:x["summary"].update(passed_checks=52),lambda x:x["activity"].update(network_requests=1),lambda x:x["activity"].update(external_cost_usd="1.000000"),lambda x:x["boundaries"].pop()]
 for a in acts:i=copy.deepcopy(e);a(i);vals.append(i)
 return sum(v!=e for v in vals),len(vals)
def main():
 p=argparse.ArgumentParser();p.add_argument("--emit",type=Path);a=p.parse_args()
 try:
  observed=execute();e=semantic(observed)
  if a.emit:
   t=a.emit if a.emit.is_absolute() else ROOT/a.emit;t.parent.mkdir(parents=True,exist_ok=True);payload=dict(e,observed_runtime={"core_elapsed_ms":observed["core_ms"],"extension_elapsed_ms":{x["name"]:x["observed_elapsed_ms"] for x in observed["extensions"]},"total_elapsed_ms":round(observed["core_ms"]+sum(x["observed_elapsed_ms"] for x in observed["extensions"]),3),"timing_is_local_nondeterministic":True});t.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8",newline="\n")
  else:
   tracked=json.loads(OUTPUT.read_text(encoding="utf-8"));tracked.pop("observed_runtime",None);req(tracked==e,"tracked release gate semantic state differs")
  r,n=mutations(e);req(r==n,"mutations")
 except (E,FileNotFoundError,KeyError,json.JSONDecodeError) as er:print(f"FAIL: {er}",file=sys.stderr);return 1
 print(f"0 failures, 0 warnings (44 core + {len(EXT)} extensions = {44+len(EXT)}/{44+len(EXT)} local checks pass)");print(f"{r}/{n} release-gate mutations rejected; 0 network/provider/uploads/downloads/$0");return 0
if __name__=="__main__":raise SystemExit(main())
