"""Validate CH05 completion-readiness audit."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-completion-readiness-audit-r1.json"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def errors(document):
    summary=document.get("summary",{});keys=("deliverables","review_links","direct_links","contact_sheets","sequence_packets","lettering_overlays","strongest_candidates","candidates","ch05_candidates","noncanon_concepts","represented_plans","chapter_plans","batches","generated_sequences","selected_candidates","dimension_sets","observed_generation_seconds","ch05_generation_seconds","reference_uses","engineering_recommendations","limitations","remaining_decisions","pilot_roots","deferred_decisions","worksheet_checks","reproducer_domains","safe_paths","zero_cost_milestones","provider_calls","uploads","paid_spend_usd","owner_inputs","owner_decisions_ingested","visual_dispositions","accepted","commercially_cleared","executable","human_review_minutes");expected=(12,134,67,10,9,34,14,29,26,3,14,50,12,3,14,12,1385.036,1230.058,39,4,15,10,6,4,112,10,971,82,0,0,0,0,0,0,0,0,0,None);out=[]
    if document.get("state")!="PASS_OWNER_REVIEW_PENDING" or tuple(summary.get(key) for key in keys)!=expected:out.append("state/denominator invalid")
    source=document.get("source",{})
    if source.get("current_remote_parity") is not True or source.get("capture_is_ancestor") is not True:out.append("source parity invalid")
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
    audit=json.loads((ROOT/document["audit"]["path"]).read_text(encoding="utf-8"))
    if len(audit["deliverables"])!=12 or any(not (ROOT/item["path"]).is_file() or sha(ROOT/item["path"])!=item["sha256"] for item in audit["deliverables"]):failures.append("deliverables invalid")
    if {key:len(value) for key,value in audit["direct_review_links"].items()}!={"contact_sheets":10,"sequence_packets":9,"lettering_overlays":34,"strongest_candidates":14}:failures.append("direct-link groups invalid")
    for rows in audit["direct_review_links"].values():
        for item in rows:
            path=ROOT/item["path"]
            if not path.is_file() or sha(path)!=item["sha256"]:failures.append(f"direct link invalid: {item['path']}")
    source=audit["source"]
    if subprocess.run(["git","merge-base","--is-ancestor",source["current_head"],"HEAD"],cwd=ROOT).returncode or source["current_head"]!=source["origin_main"]:failures.append("compile lineage invalid")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(animation_shot_plan={}),lambda x:x["source"].update(current_remote_parity=False)]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("deliverables","review_links","direct_links","contact_sheets","sequence_packets","lettering_overlays","strongest_candidates","candidates","ch05_candidates","noncanon_concepts","represented_plans","chapter_plans","batches","generated_sequences","selected_candidates","dimension_sets","observed_generation_seconds","ch05_generation_seconds","reference_uses","engineering_recommendations","limitations","remaining_decisions","pilot_roots","deferred_decisions","worksheet_checks","reproducer_domains","safe_paths","zero_cost_milestones","provider_calls","uploads","paid_spend_usd","owner_inputs","owner_decisions_ingested","visual_dispositions","accepted","commercially_cleared","executable","human_review_minutes")];rejected=0
    for mutate in mutations:altered=copy.deepcopy(document);mutate(altered);rejected+=bool(errors(altered))
    if rejected!=len(mutations):failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 completion readiness: {len(failures)} failures; 12 deliverables/134 links/67 direct/29 candidates/50 plans/10 decisions; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures:print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__":raise SystemExit(main())
