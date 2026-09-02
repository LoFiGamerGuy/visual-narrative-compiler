"""Validate owner review index r2 links, r1 extension, and zero-decision boundary."""
from __future__ import annotations
import copy,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-owner-review-index-r2.json";CONTRACT=ROOT/"production/comic/review/ch05-owner-decision-contract-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});out=[]
 if tuple(s.get(k) for k in ("candidate_count","selected_candidate_count","pending_subject_count","link_count","image_link_count","html_link_count","artifact_count"))!=(29,14,39,7,5,2,6):out.append("index denominators invalid")
 if any(s.get(k)!=0 for k in ("owner_decisions","accepted_candidates","provider_calls","uploads","cost_usd")) or s.get("human_review_minutes") is not None:out.append("review/activity fabricated")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));fail=errors(d);packet=ROOT/d["packet"]["path"]
 if not packet.is_file() or sha(packet)!=d["packet"]["sha256"]:fail.append("packet binding invalid")
 elif subprocess.run(["git","check-ignore","-q",str(packet)],cwd=ROOT,check=False).returncode:fail.append("packet not ignored")
 if sha(ROOT/d["extends"]["path"])!=d["extends"]["sha256"]:fail.append("r1 extension binding invalid")
 contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
 if sha(CONTRACT)!=d["contract"]["sha256"] or contract["summary"]["completed_decisions"]!=0 or contract["event_contract"]["events"]:fail.append("contract binding/state invalid")
 for item in d["links"]:
  path=ROOT/item["path"]
  if not path.is_file() or sha(path)!=item["sha256"]:fail.append(f"broken link {item['id']}")
 index=ROOT/d["index"]["path"]
 if not index.is_file() or sha(index)!=d["index"]["sha256"]:fail.append("index binding invalid")
 else:
  source=index.read_text(encoding="utf-8")
  if any(token in source for token in ("fetch(","XMLHttpRequest","WebSocket","<form","http://","https://")):fail.append("network/form capability found")
  if len(re.findall(r'<article>',source))!=7:fail.append("HTML card denominator invalid")
 mutations=[lambda x:x["summary"].update(candidate_count=28),lambda x:x["summary"].update(selected_candidate_count=13),lambda x:x["summary"].update(pending_subject_count=38),lambda x:x["summary"].update(link_count=6),lambda x:x["summary"].update(image_link_count=4),lambda x:x["summary"].update(html_link_count=1),lambda x:x["summary"].update(artifact_count=5),lambda x:x["summary"].update(owner_decisions=1),lambda x:x["summary"].update(accepted_candidates=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(cost_usd=1),lambda x:x["summary"].update(human_review_minutes=1)]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 owner review index r2: {len(fail)} failures; 7 links/5 images/2 HTML/6 artifacts; {rejected}/{len(mutations)} mutations rejected")
 print("29 candidates/14 selected/39 pending; decisions/accepted/calls/uploads/cost 0/0/0/0/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
