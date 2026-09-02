"""Validate CH05 overnight closeout bundle r3."""
from __future__ import annotations
import copy, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-closeout-bundle-r3.json"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def errors(document):
    summary=document.get("summary",{}); keys=("candidates","plans","batches","review_links","direct_review_links","remaining_decisions","resolved_decisions","release_checks","safe_paths","safe_bytes","frozen_paths","baseline_paths","zero_cost_milestones","provenance_records","response_files","event_logs","paid_spend_usd","accepted","commercially_cleared","executable","human_review_minutes"); expected=(29,50,12,128,67,10,0,84,934,14070835,16,4,82,29,0,0,0,0,0,0,None); out=[]
    if document.get("state")!="PASS_OWNER_INPUTS_ABSENT" or tuple(summary.get(key) for key in keys)!=expected or document.get("base_remote_parity") is not True or document.get("capture_ancestor") is not True: out.append("summary/state/lineage invalid")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8")); failures=errors(document)
    for key in ("bundle","summary_document","changed_files_document"):
        path=ROOT/document[key]["path"]
        if not path.is_file() or sha(path)!=document[key]["sha256"]: failures.append(f"binding invalid: {key}")
    for item in document["inputs"]:
        path=ROOT/item["path"]
        if not path.is_file() or sha(path)!=item["sha256"]: failures.append(f"input invalid: {item['path']}")
    bundle=json.loads((ROOT/document["bundle"]["path"]).read_text(encoding="utf-8")); lineage=bundle["source_lineage"]
    if subprocess.run(["git","cat-file","-e",f"{lineage['base_commit']}^{{commit}}"],cwd=ROOT).returncode or subprocess.run(["git","merge-base","--is-ancestor",lineage["base_commit"],"HEAD"],cwd=ROOT).returncode or lineage["origin_main_at_compile"]!=lineage["base_commit"]: failures.append("base commit lineage invalid")
    if bundle["final_integrity"]!={"release_checks":84,"release_commands":11,"release_mutations_rejected":33,"safe_paths":934,"safe_bytes":14070835,"safe_mutations_rejected":19,"review_links":128,"zero_cost_milestones":82,"frozen_paths":16,"baseline_paths":4,"baseline_accepted":0,"baseline_tuned":False,"provenance_records":29,"remote_parity_at_compile":True}: failures.append("integrity invalid")
    if bundle["remaining_decisions"]["response_files"]!=0 or bundle["remaining_decisions"]["event_logs"]!=0 or bundle["review_session"]["eligible_for_ingestion"] is not False: failures.append("owner-input boundary invalid")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(base_remote_parity=False),lambda x:x.update(capture_ancestor=False),lambda x:x.update(animation_shot_plan={})]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("candidates","plans","batches","review_links","direct_review_links","remaining_decisions","resolved_decisions","release_checks","safe_paths","safe_bytes","frozen_paths","baseline_paths","zero_cost_milestones","provenance_records","response_files","event_logs","paid_spend_usd","accepted","commercially_cleared","executable","human_review_minutes")]; rejected=0
    for mutate in mutations: altered=copy.deepcopy(document); mutate(altered); rejected+=bool(errors(altered))
    if rejected!=len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 closeout r3: {len(failures)} failures; 29/50/12/128/67; release 84/source 934/cost 82; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__": raise SystemExit(main())
