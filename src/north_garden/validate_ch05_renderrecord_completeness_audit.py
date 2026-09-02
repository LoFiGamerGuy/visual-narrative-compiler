"""Validate all-29 built-in RenderRecord completeness audit evidence."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-renderrecord-completeness-audit-r1.json";INDEX=ROOT/"production/comic/run-manifests/ch05-built-in-renderrecord-index-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});a=d.get("activity",{});out=[]
 expected=(29,26,3,29,29,39,3,1385.036,29,0,0,0,29,29,29,29,29,29,0,0,0,0,0)
 keys=("record_count","ch05_record_count","noncanon_record_count","exact_prompt_count","exact_output_count","input_reference_uses","unique_reference_hash_count","total_elapsed_seconds","pending_human_review","accepted","commercially_cleared","generation_reproducible","model_unavailable","endpoint_unavailable","request_id_unavailable","usage_unavailable","cost_unavailable","seed_unavailable","records_missing_required_fields","output_hash_failures","reference_hash_failures","prompt_hash_failures","generated_outputs_not_ignored")
 if tuple(s.get(k) for k in keys)!=expected:out.append("record/completeness denominators invalid")
 if any(a.get(k)!=0 for k in ("source_records_rewritten","provider_calls","uploads","external_cost_usd")):out.append("activity fabricated")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));index=json.loads(INDEX.read_text(encoding="utf-8"));fail=errors(d)
 if d["index"]["sha256"]!=sha(INDEX) or len(index["records"])!=29 or len({r["candidate_id"] for r in index["records"]})!=29:fail.append("index binding/records invalid")
 for r in index["records"]:
  path=ROOT/r["output"]["path"]
  if not path.is_file() or sha(path)!=r["output"]["sha256"]:fail.append("output binding invalid")
  elif subprocess.run(["git","check-ignore","-q",str(path)],cwd=ROOT,check=False).returncode:fail.append("generated output not ignored")
  if any(r["execution"][k] is not None for k in ("model","endpoint","provider_request_id","usage","cost_usd","deterministic_seed")):fail.append("unavailable metadata invented")
 chart=ROOT/d["chart"]["path"]
 if not chart.is_file() or sha(chart)!=d["chart"]["sha256"]:fail.append("chart binding invalid")
 mutations=[]
 for key in ("record_count","ch05_record_count","noncanon_record_count","exact_prompt_count","exact_output_count","input_reference_uses","unique_reference_hash_count","total_elapsed_seconds","pending_human_review","model_unavailable","endpoint_unavailable","request_id_unavailable","usage_unavailable","cost_unavailable","seed_unavailable"):
  mutations.append(lambda x,k=key:x["summary"].update({k:(x["summary"][k]-1)}))
 for key in ("accepted","commercially_cleared","generation_reproducible","records_missing_required_fields","output_hash_failures","reference_hash_failures","prompt_hash_failures","generated_outputs_not_ignored"):
  mutations.append(lambda x,k=key:x["summary"].update({k:1}))
 for key in ("source_records_rewritten","provider_calls","uploads","external_cost_usd"):mutations.append(lambda x,k=key:x["activity"].update({k:1}))
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 RenderRecord completeness: {len(fail)} failures; 29 records/39 refs/1385.036s; {rejected}/{len(mutations)} mutations rejected")
 print("29 each explicit null model/endpoint/request/usage/cost/seed; outputs ignored; pending 29/accepted 0; audit activity 0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
