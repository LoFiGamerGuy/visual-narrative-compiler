"""Validate offline CH05 decision worksheet links, contract binding, and zero-decision boundary."""
from __future__ import annotations
import copy,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/"docs/research/evidence/ch05-owner-decision-worksheet-r1.json"
CONTRACT=ROOT/"production/comic/review/ch05-owner-decision-contract-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});out=[]
 if tuple(s.get(k) for k in ("subject_count","linked_candidate_count","linked_higher_order_count"))!=(39,29,10):out.append("denominator invalid")
 if any(s.get(k)!=0 for k in ("network_calls","uploads","repository_writes_from_html","decisions_recorded")) or s.get("human_review_minutes") is not None:out.append("activity/decision/review fabricated")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));c=json.loads(CONTRACT.read_text(encoding="utf-8"));fail=errors(d)
 if sha(CONTRACT)!=d["contract"]["sha256"] or c["summary"]["completed_decisions"]!=0 or c["event_contract"]["events"]!=[]:fail.append("contract binding/state invalid")
 index=ROOT/d["index"]["path"]
 if not index.is_file() or sha(index)!=d["index"]["sha256"]:fail.append("index binding invalid")
 elif subprocess.run(["git","check-ignore","-q",str(index)],cwd=ROOT,check=False).returncode:fail.append("index not ignored")
 else:
  source=index.read_text(encoding="utf-8")
  if any(token in source for token in ("fetch(","XMLHttpRequest","WebSocket","<form","http://","https://")):fail.append("network/form capability found")
  match=re.search(r'<script id="model" type="application/json">(.*?)</script>',source,re.DOTALL)
  if not match:fail.append("embedded subject model missing")
  else:
   model=json.loads(match.group(1))
   if len(model.get("subjects",[]))!=39:fail.append("embedded subject count invalid")
   for item in model.get("subjects",[]):
    for field in ("thumbnail_href","support_href"):
     rel=item.get(field)
     if rel and not (index.parent/rel).resolve().is_file():fail.append(f"broken worksheet link: {rel}")
  if source.count('allowed_decisions')<1 or "LOCAL_UNINGESTED_DRAFT" not in source:fail.append("draft boundary/UI model missing")
 muts=[lambda x:x["summary"].update(subject_count=38),lambda x:x["summary"].update(linked_candidate_count=28),lambda x:x["summary"].update(linked_higher_order_count=9),lambda x:x["summary"].update(network_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(repository_writes_from_html=1),lambda x:x["summary"].update(decisions_recorded=1),lambda x:x["summary"].update(human_review_minutes=1)]
 rejected=0
 for m in muts:y=copy.deepcopy(d);m(y);rejected+=bool(errors(y))
 if rejected!=len(muts):fail.append(f"only {rejected}/{len(muts)} mutations rejected")
 print(f"CH05 owner decision worksheet: {len(fail)} failures; 39 subjects/29 candidate links/10 higher-order links; {rejected}/{len(muts)} mutations rejected")
 print("offline draft export only; contract 0 decisions/events/minutes; no network/upload/repository-write capability")
 for f in fail:print(f"FAIL: {f}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
