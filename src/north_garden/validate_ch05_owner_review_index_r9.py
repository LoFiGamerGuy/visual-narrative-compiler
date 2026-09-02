"""Validate final owner review index r9."""
from __future__ import annotations
import copy,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-owner-review-index-r9.json"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def errors(document):
    summary=document.get("summary",{}); keys=("candidates","strongest_candidates","worksheet_checks","prior_review_links","release_checks","safe_paths","visual_dispositions","owner_decisions_ingested","accepted","commercially_cleared","executable","provider_calls","uploads","cost_usd","human_review_minutes","link_count","image_link_count","html_link_count","text_link_count","artifact_count"); expected=(29,14,112,128,84,934,0,0,0,0,0,0,0,0,None,6,0,1,5,1); out=[]
    if document.get("state")!="LOCAL_FINAL_OWNER_REVIEW_HUB_READY_DISPOSITIONS_ABSENT" or tuple(summary.get(key) for key in keys)!=expected: out.append("state/denominator invalid")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8")); failures=errors(document); packet=ROOT/document["packet"]["path"]
    if not packet.is_file() or sha(packet)!=document["packet"]["sha256"] or subprocess.run(["git","check-ignore","-q",str(packet)],cwd=ROOT).returncode: failures.append("packet invalid")
    prior=ROOT/document["extends"]["path"]
    if not prior.is_file() or sha(prior)!=document["extends"]["sha256"]: failures.append("r8 extension invalid")
    for item in document["links"]:
        path=ROOT/item["path"]
        if not path.is_file() or sha(path)!=item["sha256"]: failures.append(f"link invalid: {item['id']}")
    index=ROOT/document["index"]["path"]
    if not index.is_file() or sha(index)!=document["index"]["sha256"]: failures.append("index invalid")
    else:
        markup=index.read_text(encoding="utf-8")
        if any(token in markup for token in ("fetch(","XMLHttpRequest","WebSocket","<form","http://","https://")) or len(re.findall(r"<article>",markup))!=6: failures.append("HTML boundary/cards invalid")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(animation_shot_plan={})]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("candidates","strongest_candidates","worksheet_checks","prior_review_links","release_checks","safe_paths","visual_dispositions","owner_decisions_ingested","accepted","commercially_cleared","executable","provider_calls","uploads","cost_usd","human_review_minutes","link_count","image_link_count","html_link_count","text_link_count","artifact_count")]; rejected=0
    for mutate in mutations: altered=copy.deepcopy(document); mutate(altered); rejected+=bool(errors(altered))
    if rejected!=len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 owner review index r9: {len(failures)} failures; 6 links/1 HTML/5 text; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__": raise SystemExit(main())
