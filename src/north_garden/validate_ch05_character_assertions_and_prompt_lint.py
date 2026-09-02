"""Validate CH05 character-assertion manifest and prompt-lint evidence."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-character-assertion-and-prompt-lint-r1.json"; MANIFEST=ROOT/"production/comic/continuity/ch05-character-assertion-manifest-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});out=[]
 if tuple(s.get(k) for k in ("plan_count","no_people_plans","soren_only_plans","sigrid_only_plans","dual_cast_plans"))!=(50,18,8,7,17):out.append("plan/cast denominators invalid")
 if (s.get("prompt_count"),s.get("prompt_pass_count"),s.get("p036_prompt_count"))!=(26,26,4):out.append("prompt denominators invalid")
 if any(s.get(k)!=0 for k in ("rendered_identity_inference_count","prompts_created","plans_revised","provider_calls","uploads","external_cost_usd")):out.append("activity/inference fabricated")
 rows=d.get("prompt_rows",[])
 if len(rows)!=26 or len({x.get("candidate_id") for x in rows})!=26 or any(not x.get("all_checks_pass") or not all(x.get("checks",{}).values()) for x in rows):out.append("prompt rows invalid")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));m=json.loads(MANIFEST.read_text(encoding="utf-8"));fail=errors(d)
 if d["manifest"]["sha256"]!=sha(MANIFEST) or len(m["plans"])!=50 or m["animation_shot_plan"] is not None or m["e_conte"] is not None:fail.append("manifest binding/planning boundary invalid")
 if any(row["comic_panel_plan_only"] is not True or row["animation_shot_plan"] is not None or row["e_conte"] is not None for row in m["plans"]):fail.append("plan row boundary invalid")
 for item in d["inputs"]["prompt_manifests"]:
  if sha(ROOT/item["path"])!=item["sha256"]:fail.append("prompt manifest binding invalid")
 mutations=[lambda x:x["summary"].update(plan_count=49),lambda x:x["summary"].update(no_people_plans=17),lambda x:x["summary"].update(soren_only_plans=7),lambda x:x["summary"].update(sigrid_only_plans=6),lambda x:x["summary"].update(dual_cast_plans=16),lambda x:x["summary"].update(prompt_count=25),lambda x:x["summary"].update(prompt_pass_count=25),lambda x:x["summary"].update(p036_prompt_count=2),lambda x:x["summary"].update(rendered_identity_inference_count=1),lambda x:x["summary"].update(prompts_created=1),lambda x:x["summary"].update(plans_revised=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(external_cost_usd=1),lambda x:x["prompt_rows"][0].update(all_checks_pass=False),lambda x:x["prompt_rows"][0]["checks"].update(prompt_hash_exact=False)]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 character assertions/prompt lint: {len(fail)} failures; 50 plans / 26 prompts / 4 P036 guards; {rejected}/{len(mutations)} mutations rejected")
 print("18 no-person / 8 Soren / 7 Sigrid / 17 dual; 0 identity inference/generation/upload/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
