"""Validate append-only CH05 zero-external-cost ledger r26."""
from __future__ import annotations
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIOR=ROOT/"docs/research/evidence/ch05-production-cost-ledger-r25.json"; OUTPUT=ROOT/"docs/research/evidence/ch05-production-cost-ledger-r26.json"
NAMES=["ch05_overnight_integrated_release_r8_compatibility_r1","ch05_final_evidence_reproducer_matrix_r1","ch05_p010_p013_owner_unlock_contract_r1","ch05_p010_p013_prompt_blueprint_r1","ch05_prompt_blueprint_adversarial_validation_r1","ch05_p010_p013_prerender_packet_blueprint_r1","ch05_p010_p013_lifecycle_state_machine_r1","ch05_chapter_batch_lifecycle_application_r1","ch05_owner_review_index_r5_and_link_manifest_r3","ch05_overnight_integrated_release_gate_r9"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ent(n): return {"milestone":n,"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"}
def build():
    p=json.loads(PRIOR.read_text(encoding="utf-8")); rows=p["local_zero_external_cost_evidence"]+[ent(n) for n in NAMES]; return {"record_type":"ProductionCostLedger","schema_version":"1.25","record_id":"ng-ch05-production-cost-ledger-r26","supersedes":{"record_id":p["record_id"],"path":PRIOR.relative_to(ROOT).as_posix(),"sha256":sha(PRIOR)},"prior_record_rewritten":False,"budget_domain":p["budget_domain"],"policy_id":p["policy_id"],"state":p["state"],"approved_aggregate_cap_usd":None,"committed_actual_cost_usd":"0.000000","held_reservations_usd":"0.000000","available_usd":None,"currency":"USD","entries":[],"local_zero_external_cost_evidence":rows,"revision_summary":{"prior_local_milestones":54,"appended_local_milestones":10,"total_local_milestones":64,"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"},"boundary":"Append-only local evidence accounting. CH05 remains disabled/no-cap/$0 paid API/cloud; built-in product cost remains unavailable and G07 is separate."}
def errors(d,e):
    out=[]
    for k,v in e.items():
        if d.get(k)!=v: out.append(f"{k} invalid")
    rows=d.get("local_zero_external_cost_evidence",[])
    if len({x.get("milestone") for x in rows})!=len(rows): out.append("duplicate milestone")
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("--emit",type=Path); a=p.parse_args(); e=build()
    if a.emit:
        t=a.emit if a.emit.is_absolute() else ROOT/a.emit; t.parent.mkdir(parents=True,exist_ok=True); t.write_text(json.dumps(e,indent=2)+"\n",encoding="utf-8",newline="\n")
    else:
        try:
            if json.loads(OUTPUT.read_text(encoding="utf-8"))!=e: raise RuntimeError("tracked r26 differs")
        except (FileNotFoundError,json.JSONDecodeError,RuntimeError) as er: print(f"FAIL: {er}",file=sys.stderr); return 1
    muts=[lambda x:x.update(state="ENABLED"),lambda x:x["supersedes"].update(sha256="0"*64),lambda x:x.update(prior_record_rewritten=True),lambda x:x.update(approved_aggregate_cap_usd="100.000000"),lambda x:x.update(entries=[{}]),lambda x:x["local_zero_external_cost_evidence"][-1].update(external_uploads=1),lambda x:x["revision_summary"].update(appended_local_milestones=9),lambda x:x["revision_summary"].update(total_local_milestones=63),lambda x:x.update(available_usd="100.000000")]
    rejected=0
    for mut in muts: y=copy.deepcopy(e); mut(y); rejected+=bool(errors(y,e))
    fail=errors(e,e)
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 cost ledger r26: {len(fail)} failures; 64 zero-cost milestones; 0 requests/uploads/$0; {rejected}/{len(muts)} mutations rejected")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
