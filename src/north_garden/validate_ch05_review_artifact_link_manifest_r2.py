"""Validate append-only CH05 review-link manifest r2."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-review-artifact-link-manifest-r2.json";BASE=ROOT/"production/comic/review/ch05-review-artifact-link-manifest-r1.json"
EXPECTED={"review_hubs":5,"contact_sheets":10,"sequence_packets":9,"lettering_overlays":34,"strongest_candidates":14,"noncanon_litrpg_concepts":3,"diagnostic_and_policy_sheets":15,"packet_records":14,"review_checklists":1}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});out=[]
 if tuple(s.get(k) for k in ("added_artifacts","effective_unique_artifacts","categorized_links","ignored_local_artifacts","tracked_metadata_links"))!=(6,105,105,104,1) or d.get("category_counts")!=EXPECTED or d.get("state")!="PASS_OWNER_PENDING":out.append("link denominator/state invalid")
 if any(s.get(k)!=0 for k in ("owner_decisions","accepted_candidates","provider_calls","uploads","cost_usd")) or s.get("human_review_minutes") is not None:out.append("review/activity fabricated")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));fail=errors(d);mp=ROOT/d["manifest"]["path"];mdp=ROOT/d["markdown"]["path"]
 if not mp.is_file() or sha(mp)!=d["manifest"]["sha256"] or not mdp.is_file() or sha(mdp)!=d["markdown"]["sha256"]:fail.append("output binding invalid");m={}
 else:m=json.loads(mp.read_text(encoding="utf-8"))
 if sha(BASE)!=d["extends"]["sha256"]:fail.append("base r1 binding invalid")
 base=json.loads(BASE.read_text(encoding="utf-8"));base_by={x["path"]:x for x in base["artifacts"]};effective={x["path"]:x for x in m.get("artifacts",[])}
 if len(effective)!=105 or any(path not in effective or any(effective[path].get(k)!=item.get(k) for k in ("absolute_path","sha256","bytes","categories")) for path,item in base_by.items()):fail.append("base artifact lineage invalid")
 markdown=mdp.read_text(encoding="utf-8") if mdp.is_file() else ""
 for item in m.get("artifacts",[]):
  p=ROOT/item["path"]
  if not p.is_file() or sha(p)!=item["sha256"] or p.stat().st_size!=item["bytes"] or p.resolve().as_posix()!=item["absolute_path"]:fail.append(f"artifact binding invalid: {item['path']}");continue
  ignored=subprocess.run(["git","check-ignore","-q",str(p)],cwd=ROOT,check=False).returncode==0
  tracked=subprocess.run(["git","ls-files","--error-unmatch",p.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True,check=False).returncode==0
  expected="IGNORED_LOCAL" if ignored else "TRACKED_METADATA" if tracked else "UNBOUND"
  if item["git_state"]!=expected or expected=="UNBOUND":fail.append(f"git state invalid: {item['path']}")
  if f"]({item['absolute_path']})" not in markdown:fail.append(f"Markdown link missing: {item['path']}")
 if markdown.count("\n- [")!=105:fail.append("Markdown denominator invalid")
 muts=[lambda x:x.update(state="FAIL"),lambda x:x["summary"].update(added_artifacts=5),lambda x:x["summary"].update(effective_unique_artifacts=104),lambda x:x["summary"].update(categorized_links=104),lambda x:x["summary"].update(ignored_local_artifacts=103),lambda x:x["summary"].update(tracked_metadata_links=0),lambda x:x["summary"].update(owner_decisions=1),lambda x:x["summary"].update(accepted_candidates=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(cost_usd=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["category_counts"].update(review_hubs=4),lambda x:x["category_counts"].update(diagnostic_and_policy_sheets=14)]
 rejected=0
 for mut in muts:y=copy.deepcopy(d);mut(y);rejected+=bool(errors(y))
 if rejected!=len(muts):fail.append(f"only {rejected}/{len(muts)} mutations rejected")
 print(f"CH05 review links r2: {len(fail)} failures; 105=99+6 artifacts / 104 ignored + 1 tracked; {rejected}/{len(muts)} mutations rejected")
 print("decisions/accepted/calls/uploads/cost 0/0/0/0/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
