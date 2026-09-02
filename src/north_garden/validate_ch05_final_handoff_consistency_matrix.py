"""Validate CH05 final handoff consistency matrix."""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-final-handoff-consistency-matrix-r1.json"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def errors(document):
    summary=document.get("summary",{}); keys=("input_records","consensus_facts","consistent_facts","unexplained_conflicts","expected_temporal_differences","candidates","plans","batches","review_links","priority_links","pilot_roots","release_checks","safe_paths_current","zero_cost_milestones","owner_inputs","owner_decisions_ingested","accepted","commercially_cleared","executable","provider_calls","uploads","paid_spend_usd","human_review_minutes"); expected=(9,12,12,0,1,29,50,12,128,67,6,84,934,82,0,0,0,0,0,0,0,0,None); out=[]
    if document.get("state")!="PASS_OWNER_INPUTS_ABSENT" or tuple(summary.get(key) for key in keys)!=expected: out.append("state/denominator invalid")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8")); failures=errors(document)
    for key in ("matrix","guide"):
        path=ROOT/document[key]["path"]
        if not path.is_file() or sha(path)!=document[key]["sha256"]: failures.append(f"binding invalid: {key}")
    for item in document["inputs"]:
        path=ROOT/item["path"]
        if not path.is_file() or sha(path)!=item["sha256"]: failures.append(f"input invalid: {item['path']}")
    matrix=json.loads((ROOT/document["matrix"]["path"]).read_text(encoding="utf-8"))
    if len(matrix["consensus"])!=12 or any(row["state"]!="CONSISTENT" or any(value!=row["expected"] for value in row["values"].values()) for row in matrix["consensus"]): failures.append("consensus row invalid")
    if matrix["temporal_lineage"]!=[{"fact":"safe_source_capture_paths","earlier_release_snapshot":873,"later_safe_r4":934,"later_closeout_r3":934,"delta":61,"state":"EXPECTED_APPEND_ONLY_LINEAGE","explanation":"Release r12 immutably binds safe-source r3 (873); safe-source r4 and closeout r3 were compiled later (934)."}]: failures.append("temporal lineage invalid")
    if matrix["route_consistency"]["state"]!="ONE_CURRENT_ENGINEERING_RECOMMENDATION_OWNER_UNRESOLVED" or matrix["limitation_consistency"]["commercial_status"]!="OPEN_PENDING_EXPLICIT_REVIEW": failures.append("route/limitation boundary invalid")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(animation_shot_plan={})]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("input_records","consensus_facts","consistent_facts","unexplained_conflicts","expected_temporal_differences","candidates","plans","batches","review_links","priority_links","pilot_roots","release_checks","safe_paths_current","zero_cost_milestones","owner_inputs","owner_decisions_ingested","accepted","commercially_cleared","executable","provider_calls","uploads","paid_spend_usd","human_review_minutes")]; rejected=0
    for mutate in mutations: altered=copy.deepcopy(document); mutate(altered); rejected+=bool(errors(altered))
    if rejected!=len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 handoff consistency: {len(failures)} failures; 12/12 facts/0 unexplained/1 expected lineage; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__": raise SystemExit(main())
