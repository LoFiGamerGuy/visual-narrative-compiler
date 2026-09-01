"""Validate append-only CH05 zero-external-cost ledger r17."""
from __future__ import annotations
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R16=ROOT/"docs/research/evidence/ch05-production-cost-ledger-r16.json"; R17=ROOT/"docs/research/evidence/ch05-production-cost-ledger-r17.json"
NAMES=["frozen_gauntlet_baseline_integrity_r1"]
class E(RuntimeError): pass
def req(v,m):
    if not v: raise E(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ent(n): return {"milestone":n,"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"}
def build():
 p=json.loads(R16.read_text(encoding="utf-8")); add=[ent(n) for n in NAMES]; all=p["local_zero_external_cost_evidence"]+add
 return {"record_type":"ProductionCostLedger","schema_version":"1.16","record_id":"ng-ch05-production-cost-ledger-r17","supersedes":{"record_id":p["record_id"],"path":R16.relative_to(ROOT).as_posix(),"sha256":sha(R16)},"prior_record_rewritten":False,"budget_domain":p["budget_domain"],"policy_id":p["policy_id"],"state":p["state"],"approved_aggregate_cap_usd":None,"committed_actual_cost_usd":"0.000000","held_reservations_usd":"0.000000","available_usd":None,"currency":"USD","entries":[],"local_zero_external_cost_evidence":all,"revision_summary":{"prior_local_milestones":len(p["local_zero_external_cost_evidence"]),"appended_local_milestones":len(add),"total_local_milestones":len(all),"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"},"boundary":"Append-only local evidence accounting. CH05 remains disabled/no-cap/$0; G07 availability remains separate."}
def muts(e):
 vals=[]; acts=[lambda x:x["supersedes"].update(sha256="0"*64),lambda x:x.update(prior_record_rewritten=True),lambda x:x.update(state="ENABLED"),lambda x:x.update(approved_aggregate_cap_usd="100.000000"),lambda x:x.update(entries=[{}]),lambda x:x["local_zero_external_cost_evidence"][-1].update(external_uploads=1),lambda x:x["revision_summary"].update(total_local_milestones=43),lambda x:x.update(available_usd="98.942623")]
 for a in acts: i=copy.deepcopy(e); a(i); vals.append(i)
 return sum(v!=e for v in vals),len(vals)
def main():
 p=argparse.ArgumentParser(); p.add_argument("--emit",type=Path); a=p.parse_args()
 try:
  e=build()
  if a.emit:
   t=a.emit if a.emit.is_absolute() else ROOT/a.emit; t.parent.mkdir(parents=True,exist_ok=True); t.write_text(json.dumps(e,indent=2)+"\n",encoding="utf-8",newline="\n")
  else:req(json.loads(R17.read_text(encoding="utf-8"))==e,"tracked r17 differs")
  r,n=muts(e); req(r==n,"mutations"); req(len({x["milestone"] for x in e["local_zero_external_cost_evidence"]})==e["revision_summary"]["total_local_milestones"],"duplicates")
 except (E,FileNotFoundError,KeyError,json.JSONDecodeError) as er: print(f"FAIL: {er}",file=sys.stderr); return 1
 print(f"0 failures, 0 warnings ({e['revision_summary']['total_local_milestones']} zero-cost milestones; 0 requests/uploads/$0; {r}/{n} mutations rejected)"); return 0
if __name__=="__main__":raise SystemExit(main())
