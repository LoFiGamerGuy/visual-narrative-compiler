"""Validate CH05 overnight delivery bundle r1."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-delivery-bundle-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});out=[]
 expected=(29,26,3,14,14,50,12,105,14,10,46,1385.036,39,0,0,0,0)
 actual=tuple(s.get(k) for k in ("candidates","ch05_candidates","noncanon_concepts","distinct_ch05_plans","selected","chapter_plans","sequence_batches","review_links","strongest_candidates","remaining_decisions","integrated_checks","observed_seconds","reference_uses","paid_spend_usd","owner_decisions","accepted_candidates","executable_panels"))
 if actual!=expected or d.get("state")!="PASS_OWNER_PENDING" or s.get("human_review_minutes") is not None or d.get("base_remote_parity") is not True:out.append("bundle denominator/state/parity invalid")
 if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None:out.append("planning boundary invalid")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));fail=errors(d)
 for key in ("bundle","summary_document","changed_files_document"):
  p=ROOT/d[key]["path"]
  if not p.is_file() or sha(p)!=d[key]["sha256"]:fail.append(f"output binding invalid: {key}")
 for item in d["inputs"]:
  p=ROOT/item["path"]
  if not p.is_file() or sha(p)!=item["sha256"]:fail.append(f"input binding invalid: {item['path']}")
 bundle=json.loads((ROOT/d["bundle"]["path"]).read_text(encoding="utf-8"));art=bundle.get("art",{});activity=bundle.get("activity",{})
 if len(art.get("strongest_candidates",[]))!=14 or any(not (ROOT/x["path"]).is_file() or sha(ROOT/x["path"])!=x["sha256"] for x in art.get("strongest_candidates",[])):fail.append("strongest candidate binding invalid")
 if any(row.get("owner_decision") is not None or row.get("reviewer") is not None or row.get("human_review_minutes") is not None for row in bundle.get("remaining_decisions",{}).get("rows",[])):fail.append("remaining decisions fabricated")
 if len(bundle.get("limitations",[]))!=8:fail.append("limitation denominator invalid")
 if any(activity.get(k)!=0 for k in ("paid_api_calls","external_uploads_this_delivery_bundle","cloud_gpu_uses","purchases","disclosed_paid_spend_usd","owner_decisions_recorded","accepted_candidates","executable_panels","comic_panel_plan_revisions")) or activity.get("built_in_monetary_cost_usd") is not None or activity.get("human_review_minutes") is not None:fail.append("activity/promotion fabricated")
 lineage=bundle.get("source_lineage",{});head=lineage.get("base_release_commit")
 if subprocess.run(["git","cat-file","-e",f"{head}^{{commit}}"],cwd=ROOT,check=False).returncode or lineage.get("base_remote_parity") is not True or lineage.get("origin_main_at_compile")!=head:fail.append("source lineage invalid")
 for item in bundle.get("key_links",[]):
  p=ROOT/item["path"]
  if not p.is_file() or sha(p)!=item["sha256"] or p.resolve().as_posix()!=item["absolute_path"]:fail.append(f"key link invalid: {item['id']}")
 muts=[lambda x:x.update(state="FAIL"),lambda x:x["summary"].update(candidates=28),lambda x:x["summary"].update(ch05_candidates=25),lambda x:x["summary"].update(noncanon_concepts=2),lambda x:x["summary"].update(distinct_ch05_plans=13),lambda x:x["summary"].update(selected=13),lambda x:x["summary"].update(chapter_plans=49),lambda x:x["summary"].update(sequence_batches=11),lambda x:x["summary"].update(review_links=104),lambda x:x["summary"].update(strongest_candidates=13),lambda x:x["summary"].update(remaining_decisions=9),lambda x:x["summary"].update(integrated_checks=45),lambda x:x["summary"].update(observed_seconds=1385.824),lambda x:x["summary"].update(reference_uses=38),lambda x:x["summary"].update(paid_spend_usd=1),lambda x:x["summary"].update(owner_decisions=1),lambda x:x["summary"].update(accepted_candidates=1),lambda x:x["summary"].update(executable_panels=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(base_remote_parity=False),lambda x:x.update(animation_shot_plan={})]
 rejected=0
 for mut in muts:y=copy.deepcopy(d);mut(y);rejected+=bool(errors(y))
 if rejected!=len(muts):fail.append(f"only {rejected}/{len(muts)} mutations rejected")
 print(f"CH05 delivery bundle: {len(fail)} failures; 29 candidates/50 plans/12 batches/105 links/10 decisions/46 checks; {rejected}/{len(muts)} mutations rejected")
 print("paid spend/decisions/accepted/executable/minutes $0/0/0/0/null")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
