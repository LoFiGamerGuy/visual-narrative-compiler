"""Validate CH05 overnight closeout and direct-review completeness."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-closeout-bundle-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; keys=("candidates","ch05_candidates","noncanon_concepts","plans","represented_plans","batches","review_links","direct_review_links","contact_sheets","sequence_packets","lettering_overlays","strongest_candidates","release_checks","reproducer_domains","safe_paths","remaining_decisions","resolved_decisions","paid_spend_usd","accepted","executable"); expected=(29,26,3,50,14,12,122,67,10,9,34,14,66,7,835,10,0,0,0,0)
    if tuple(s.get(k) for k in keys)!=expected or s.get("human_review_minutes") is not None or d.get("state")!="PASS_OWNER_PENDING" or d.get("base_remote_parity") is not True: out.append("summary/state/parity invalid")
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
    bundle=json.loads((ROOT/d["bundle"]["path"]).read_text(encoding="utf-8")); review=bundle.get("review_links",{}); rows=sum((review.get(k,[]) for k in ("contact_sheets","sequence_packets","lettering_overlays","strongest_candidates")),[])
    if len(rows)!=67 or any(not (ROOT/x["path"]).is_file() or sha(ROOT/x["path"])!=x["sha256"] or (ROOT/x["path"]).resolve().as_posix()!=x["absolute_path"] for x in rows): fail.append("direct review links invalid")
    if len(bundle.get("ranked_recommendations",[]))!=4 or len(bundle.get("limitations",[]))!=12 or len(bundle.get("remaining_decisions",{}).get("rows",[]))!=10: fail.append("recommendation/limitation/decision denominator invalid")
    if any(x["owner_decision"] is not None or x["resolved"] for x in bundle["remaining_decisions"]["rows"]): fail.append("owner decision fabricated")
    activity=bundle.get("activity",{}); zero=("provider_calls","uploads","downloads","purchases","paid_spend_usd","owner_decisions","review_events","accepted","commercially_cleared","executable","comic_panel_plan_revisions")
    if any(activity.get(k)!=0 for k in zero) or activity.get("human_review_minutes") is not None: fail.append("activity/promotion invalid")
    lineage=bundle.get("source_lineage",{}); commit=lineage.get("base_commit")
    if subprocess.run(["git","cat-file","-e",f"{commit}^{{commit}}"],cwd=ROOT).returncode or lineage.get("origin_main_at_compile")!=commit or lineage.get("base_remote_parity") is not True: fail.append("source lineage invalid")
    muts=[lambda x:x.update(state="FAIL")]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("candidates","ch05_candidates","noncanon_concepts","plans","represented_plans","batches","review_links","direct_review_links","contact_sheets","sequence_packets","lettering_overlays","strongest_candidates","release_checks","reproducer_domains","safe_paths","remaining_decisions","resolved_decisions","paid_spend_usd","accepted","executable")]+[lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(base_remote_parity=False),lambda x:x.update(animation_shot_plan={})]; rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 closeout: {len(fail)} failures; 29/50/12/122/67 direct/10 decisions; {rejected}/{len(muts)} mutations rejected")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
