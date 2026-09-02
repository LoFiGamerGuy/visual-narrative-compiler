"""Validate owner review index r7 and immutable r6 extension."""
from __future__ import annotations
import copy,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-owner-review-index-r7.json"; CONTRACT=ROOT/"production/comic/review/ch05-owner-decision-contract-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(29,50,117,66,10,5,0,1,4,1,0,0,0,0,0,0); actual=tuple(s.get(k) for k in ("candidate_count","plan_count","prior_review_links","release_checks","engineering_defaults","link_count","image_link_count","html_link_count","text_link_count","artifact_count","owner_decisions","accepted_candidates","executable_panels","provider_calls","uploads","cost_usd"))
    if actual!=expected or s.get("human_review_minutes") is not None: out.append("index denominator/state invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d); packet=ROOT/d["packet"]["path"]
    if not packet.is_file() or sha(packet)!=d["packet"]["sha256"] or subprocess.run(["git","check-ignore","-q",str(packet)],cwd=ROOT).returncode: fail.append("packet invalid")
    if sha(ROOT/d["extends"]["path"])!=d["extends"]["sha256"]: fail.append("r6 extension invalid")
    for item in d["links"]:
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["sha256"]: fail.append(f"link invalid: {item['id']}")
    index=ROOT/d["index"]["path"]
    if not index.is_file() or sha(index)!=d["index"]["sha256"]: fail.append("index invalid")
    elif any(x in index.read_text(encoding="utf-8") for x in ("fetch(","XMLHttpRequest","WebSocket","<form","http://","https://")) or len(re.findall(r"<article>",index.read_text(encoding="utf-8")))!=5: fail.append("HTML boundary/cards invalid")
    muts=[lambda x,k=k:x["summary"].update({k:-1}) for k in ("candidate_count","plan_count","prior_review_links","release_checks","engineering_defaults","link_count","image_link_count","html_link_count","text_link_count","artifact_count","owner_decisions","accepted_candidates","executable_panels","provider_calls","uploads","cost_usd")]+[lambda x:x["summary"].update(human_review_minutes=1)]; rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 owner review index r7: {len(fail)} failures; 5 links/0 image/1 HTML/4 text/1 artifact; {rejected}/{len(muts)} mutations rejected")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
