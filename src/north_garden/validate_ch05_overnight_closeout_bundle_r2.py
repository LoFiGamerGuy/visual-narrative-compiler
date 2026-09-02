"""Validate final CH05 closeout r2 and append-only lineage."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-closeout-bundle-r2.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; keys=("candidates","plans","batches","review_links","direct_review_links","remaining_decisions","resolved_decisions","release_checks","safe_paths","safe_bytes","frozen_paths","baseline_paths","zero_cost_milestones","paid_spend_usd","accepted","executable"); expected=(29,50,12,122,67,10,0,74,873,13394576,16,4,73,0,0,0)
    if tuple(s.get(k) for k in keys)!=expected or s.get("human_review_minutes") is not None or d.get("state")!="PASS_OWNER_PENDING" or d.get("base_remote_parity") is not True or d.get("capture_ancestor") is not True: out.append("summary/state/lineage invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for key in ("bundle","summary_document","changed_files_document"):
        p=ROOT/d[key]["path"]
        if not p.is_file() or sha(p)!=d[key]["sha256"]: fail.append(f"output binding invalid: {key}")
    for item in d["inputs"]:
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["sha256"]: fail.append(f"input binding invalid: {item['path']}")
    bundle=json.loads((ROOT/d["bundle"]["path"]).read_text(encoding="utf-8")); rows=sum((bundle["review_links"][k] for k in ("contact_sheets","sequence_packets","lettering_overlays","strongest_candidates")),[])
    if len(rows)!=67 or any(not (ROOT/x["path"]).is_file() or sha(ROOT/x["path"])!=x["sha256"] for x in rows): fail.append("direct links invalid")
    if len(bundle.get("limitations",[]))!=13 or len(bundle.get("ranked_recommendations",[]))!=4 or any(x["owner_decision"] is not None or x["resolved"] for x in bundle["remaining_decisions"]["rows"]): fail.append("recommendation/decision boundary invalid")
    integrity=bundle.get("final_integrity",{})
    if integrity!={"release_checks":74,"release_commands":9,"release_mutations_rejected":29,"safe_paths":873,"safe_bytes":13394576,"safe_mutations_rejected":17,"frozen_paths":16,"baseline_paths":4,"baseline_accepted":0,"baseline_tuned":False,"remote_parity_at_compile":True}: fail.append("integrity invalid")
    lineage=bundle.get("source_lineage",{}); capture=lineage.get("final_capture_commit"); head=lineage.get("base_commit")
    if subprocess.run(["git","merge-base","--is-ancestor",capture,head],cwd=ROOT).returncode or lineage.get("origin_main_at_compile")!=head: fail.append("Git lineage invalid")
    muts=[lambda x:x.update(state="FAIL")]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("candidates","plans","batches","review_links","direct_review_links","remaining_decisions","resolved_decisions","release_checks","safe_paths","safe_bytes","frozen_paths","baseline_paths","zero_cost_milestones","paid_spend_usd","accepted","executable")]+[lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(base_remote_parity=False),lambda x:x.update(capture_ancestor=False),lambda x:x.update(animation_shot_plan={})]; rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 closeout r2: {len(fail)} failures; 29/50/12/122/67/release74/source873; {rejected}/{len(muts)} mutations rejected")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
