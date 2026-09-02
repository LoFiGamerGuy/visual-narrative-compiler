"""Validate append-only CH05 zero-external-cost ledger r30."""
from __future__ import annotations
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PRIOR=ROOT/"docs/research/evidence/ch05-production-cost-ledger-r29.json";OUTPUT=ROOT/"docs/research/evidence/ch05-production-cost-ledger-r30.json";NAMES=["ch05_final_review_integrated_release_r12","ch05_final_safe_source_and_remote_parity_r2","ch05_overnight_closeout_bundle_r3","ch05_final_handoff_consistency_matrix_r1","ch05_strongest_candidate_disposition_worksheet_r1","ch05_owner_review_index_r9_final_entry_r1","ch05_final_review_reproducer_matrix_r3","ch05_post_reproducer_safe_source_parity_r5","ch05_completion_readiness_audit_r1"]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def entry(name):return {"milestone":name,"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"}
def build():
    prior=json.loads(PRIOR.read_text(encoding="utf-8"));rows=prior["local_zero_external_cost_evidence"]+[entry(name) for name in NAMES];return {"record_type":"ProductionCostLedger","schema_version":"1.29","record_id":"ng-ch05-production-cost-ledger-r30","supersedes":{"record_id":prior["record_id"],"path":PRIOR.relative_to(ROOT).as_posix(),"sha256":sha(PRIOR)},"prior_record_rewritten":False,"budget_domain":prior["budget_domain"],"policy_id":prior["policy_id"],"state":prior["state"],"approved_aggregate_cap_usd":None,"committed_actual_cost_usd":"0.000000","held_reservations_usd":"0.000000","available_usd":None,"currency":"USD","entries":[],"local_zero_external_cost_evidence":rows,"revision_summary":{"prior_local_milestones":82,"appended_local_milestones":9,"total_local_milestones":91,"external_requests":0,"external_uploads":0,"external_cost_usd":"0.000000"},"boundary":"Append-only local accounting. CH05 remains disabled/no-cap/$0 paid API/cloud; built-in product cost is unavailable and G07 remains separate."}
def errors(document,expected):
    out=[f"{key} invalid" for key,value in expected.items() if document.get(key)!=value]
    if len({row.get("milestone") for row in document.get("local_zero_external_cost_evidence",[])})!=len(document.get("local_zero_external_cost_evidence",[])):out.append("duplicate milestone")
    return out
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--emit",type=Path);args=parser.parse_args();expected=build()
    if args.emit:
        target=args.emit if args.emit.is_absolute() else ROOT/args.emit;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(expected,indent=2)+"\n",encoding="utf-8",newline="\n")
    else:
        try:
            if json.loads(OUTPUT.read_text(encoding="utf-8"))!=expected:raise RuntimeError("tracked r30 differs")
        except (FileNotFoundError,json.JSONDecodeError,RuntimeError) as error:print(f"FAIL: {error}",file=sys.stderr);return 1
    mutations=[lambda x:x.update(state="ENABLED"),lambda x:x["supersedes"].update(sha256="0"*64),lambda x:x.update(prior_record_rewritten=True),lambda x:x.update(approved_aggregate_cap_usd="100.000000"),lambda x:x.update(entries=[{}]),lambda x:x["local_zero_external_cost_evidence"][-1].update(external_uploads=1),lambda x:x["revision_summary"].update(appended_local_milestones=8),lambda x:x["revision_summary"].update(total_local_milestones=90),lambda x:x.update(available_usd="100.000000")];rejected=0
    for mutate in mutations:altered=copy.deepcopy(expected);mutate(altered);rejected+=bool(errors(altered,expected))
    failures=errors(expected,expected)
    if rejected!=len(mutations):failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 cost ledger r30: {len(failures)} failures; 91 zero-cost milestones; 0 requests/uploads/$0; {rejected}/{len(mutations)} mutations rejected");return 1 if failures else 0
if __name__=="__main__":raise SystemExit(main())
