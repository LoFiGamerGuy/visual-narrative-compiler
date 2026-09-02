"""Validate deterministic CH05 manual-continuity atlas evidence and boundaries."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-manual-continuity-atlas-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});out=[]
 if tuple(s.get(k) for k in ("candidate_count","panel_group_count","selected_count","engineering_pass","engineering_warn","engineering_fail"))!=(26,14,14,17,3,6):out.append("candidate/group/state denominators invalid")
 if (s.get("hair_wardrobe_pass"),s.get("role_order_pass"),s.get("role_order_fail"))!=(26,25,1):out.append("manual label denominators invalid")
 if any(s.get(k)!=0 for k in ("rendered_identity_inference_count","face_crop_count","owner_decisions","provider_calls","uploads","external_cost_usd")) or s.get("human_review_minutes") is not None:out.append("activity/review fabricated")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));fail=errors(d);packet=ROOT/d["packet"]["path"]
 if not packet.is_file() or sha(packet)!=d["packet"]["sha256"]:fail.append("packet binding invalid")
 elif subprocess.run(["git","check-ignore","-q",str(packet)],cwd=ROOT,check=False).returncode:fail.append("packet not ignored")
 for item in d.get("artifacts",[]):
  path=ROOT/item["path"]
  if not path.is_file() or sha(path)!=item["sha256"]:fail.append("artifact binding invalid")
  elif subprocess.run(["git","check-ignore","-q",str(path)],cwd=ROOT,check=False).returncode:fail.append("artifact not ignored")
 mutations=[lambda x:x["summary"].update(candidate_count=25),lambda x:x["summary"].update(panel_group_count=13),lambda x:x["summary"].update(selected_count=13),lambda x:x["summary"].update(engineering_pass=16),lambda x:x["summary"].update(engineering_warn=2),lambda x:x["summary"].update(engineering_fail=5),lambda x:x["summary"].update(hair_wardrobe_pass=25),lambda x:x["summary"].update(role_order_pass=24),lambda x:x["summary"].update(role_order_fail=0),lambda x:x["summary"].update(rendered_identity_inference_count=1),lambda x:x["summary"].update(face_crop_count=1),lambda x:x["summary"].update(owner_decisions=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(external_cost_usd=1)]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 manual continuity atlas: {len(fail)} failures; 26 candidates/14 groups/2 artifacts; {rejected}/{len(mutations)} mutations rejected")
 print("manual engineering labels: hair 26 pass; role 25 pass/1 fail; identity inference/face crops/owner decisions 0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
