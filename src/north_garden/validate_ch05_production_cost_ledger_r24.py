"""Validate append-only CH05 zero-external-cost ledger r24."""
from __future__ import annotations
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; R23=ROOT/"docs/research/evidence/ch05-production-cost-ledger-r23.json"; R24=ROOT/"docs/research/evidence/ch05-production-cost-ledger-r24.json"
NAME="ch05_final_delivery_bundle_manifest_r1"
class E(RuntimeError): pass
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ent(): return {"milestone":NAME,"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"}
def build():
    p=json.loads(R23.read_text(encoding="utf-8")); rows=p["local_zero_external_cost_evidence"]+[ent()]
    return {"record_type":"ProductionCostLedger","schema_version":"1.23","record_id":"ng-ch05-production-cost-ledger-r24","supersedes":{"record_id":p["record_id"],"path":R23.relative_to(ROOT).as_posix(),"sha256":sha(R23)},"prior_record_rewritten":False,"budget_domain":p["budget_domain"],"policy_id":p["policy_id"],"state":p["state"],"approved_aggregate_cap_usd":None,"committed_actual_cost_usd":"0.000000","held_reservations_usd":"0.000000","available_usd":None,"currency":"USD","entries":[],"local_zero_external_cost_evidence":rows,"revision_summary":{"prior_local_milestones":len(p["local_zero_external_cost_evidence"]),"appended_local_milestones":1,"total_local_milestones":len(rows),"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"},"boundary":"Append-only local evidence accounting. CH05 remains disabled/no-cap/$0; G07 availability remains separate."}
def errors(e):
    out=[]; p=json.loads(R23.read_text(encoding="utf-8")); rows=p["local_zero_external_cost_evidence"]+[ent()]
    if e.get("record_type")!="ProductionCostLedger" or e.get("record_id")!="ng-ch05-production-cost-ledger-r24" or e.get("state")!="DISABLED_NO_PRODUCTION_SPEND_OR_UPLOAD_AUTHORITY": out.append("identity/state invalid")
    if e.get("supersedes")!={"record_id":p["record_id"],"path":R23.relative_to(ROOT).as_posix(),"sha256":sha(R23)} or e.get("prior_record_rewritten") is not False: out.append("lineage invalid")
    if e.get("approved_aggregate_cap_usd") is not None or e.get("committed_actual_cost_usd")!="0.000000" or e.get("held_reservations_usd")!="0.000000" or e.get("available_usd") is not None or e.get("entries")!=[]: out.append("budget state invalid")
    if e.get("local_zero_external_cost_evidence")!=rows or len({x["milestone"] for x in rows})!=len(rows): out.append("rows invalid")
    expected={"prior_local_milestones":len(p["local_zero_external_cost_evidence"]),"appended_local_milestones":1,"total_local_milestones":len(rows),"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"}
    if e.get("revision_summary")!=expected: out.append("summary invalid")
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("--emit",type=Path); a=p.parse_args(); e=build()
    if a.emit:
        t=a.emit if a.emit.is_absolute() else ROOT/a.emit; t.parent.mkdir(parents=True,exist_ok=True); t.write_text(json.dumps(e,indent=2)+"\n",encoding="utf-8",newline="\n")
    else:
        try:
            if json.loads(R24.read_text(encoding="utf-8"))!=e: raise E("tracked r24 differs")
        except (E,FileNotFoundError,json.JSONDecodeError) as er: print(f"FAIL: {er}",file=sys.stderr); return 1
    muts=[lambda x:x.update(state="ENABLED"),lambda x:x["supersedes"].update(sha256="0"*64),lambda x:x.update(prior_record_rewritten=True),lambda x:x.update(approved_aggregate_cap_usd="100.000000"),lambda x:x.update(entries=[{}]),lambda x:x["local_zero_external_cost_evidence"][-1].update(external_requests=1),lambda x:x["revision_summary"].update(total_local_milestones=0),lambda x:x.update(available_usd="100.000000")]
    rejected=0
    for mut in muts: y=copy.deepcopy(e); mut(y); rejected+=bool(errors(y))
    fail=errors(e)
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 cost ledger r24: {len(fail)} failures; {e['revision_summary']['total_local_milestones']} zero-cost milestones; 0 requests/uploads/$0; {rejected}/{len(muts)} mutations rejected")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
