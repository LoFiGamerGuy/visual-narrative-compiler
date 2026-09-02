"""Validate CH05 post-r13 final delivery audit."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-post-r13-final-delivery-audit-r1.json"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def errors(document):
    summary=document.get("summary",{});keys=("steps","candidates","strongest_candidates","worksheet_checks","plans","batches","review_links","priority_links","completion_deliverables","release_commands","release_domains","safe_paths","zero_cost_milestones","remaining_decisions","owner_inputs","owner_decisions_ingested","visual_dispositions","accepted","commercially_cleared","executable","provider_calls","uploads","paid_spend_usd","human_review_minutes");expected=(9,29,14,112,50,12,134,67,12,9,18,971,91,10,0,0,0,0,0,0,0,0,0,None);out=[]
    if document.get("state")!="PASS_OWNER_REVIEW_PENDING" or tuple(summary.get(key) for key in keys)!=expected:out.append("state/denominator invalid")
    source=document.get("source",{})
    if source.get("remote_parity") is not True or source.get("safe_capture_ancestor") is not True:out.append("source parity invalid")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None:out.append("planning boundary invalid")
    return out
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8"));failures=errors(document)
    for key in ("audit","guide"):
        path=ROOT/document[key]["path"]
        if not path.is_file() or sha(path)!=document[key]["sha256"]:failures.append(f"binding invalid: {key}")
    for item in document["inputs"]:
        path=ROOT/item["path"]
        if not path.is_file() or sha(path)!=item["sha256"]:failures.append(f"input invalid: {item['path']}")
    audit=json.loads((ROOT/document["audit"]["path"]).read_text(encoding="utf-8"));steps=audit.get("review_order",[])
    if [row.get("order") for row in steps]!=list(range(1,10)) or len({row.get("id") for row in steps})!=9:failures.append("review order invalid")
    for row in steps:
        path=ROOT/row["resource"]["path"]
        if not path.is_file() or sha(path)!=row["resource"]["sha256"]:failures.append(f"resource invalid: {row['id']}")
    source=audit["source"]
    if subprocess.run(["git","merge-base","--is-ancestor",source["compile_head"],"HEAD"],cwd=ROOT).returncode or source["compile_head"]!=source["origin_main"]:failures.append("compile lineage invalid")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(animation_shot_plan={}),lambda x:x["source"].update(remote_parity=False)]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("steps","candidates","strongest_candidates","worksheet_checks","plans","batches","review_links","priority_links","completion_deliverables","release_commands","release_domains","safe_paths","zero_cost_milestones","remaining_decisions","owner_inputs","owner_decisions_ingested","visual_dispositions","accepted","commercially_cleared","executable","provider_calls","uploads","paid_spend_usd","human_review_minutes")];rejected=0
    for mutate in mutations:altered=copy.deepcopy(document);mutate(altered);rejected+=bool(errors(altered))
    if rejected!=len(mutations):failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 post-r13 delivery: {len(failures)} failures; 9 steps/134 links/14 candidates/10 decisions; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures:print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__":raise SystemExit(main())
