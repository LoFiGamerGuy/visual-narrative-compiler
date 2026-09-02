"""Validate/reproduce append-only CH05 overnight integrated release gate r3."""
from __future__ import annotations
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r2.json";EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r3.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(path:str,stdout:str)->str:
 return re.sub(r"\d+ tracked safe-source paths","<TRACKED_COUNT> tracked safe-source paths",stdout) if path.endswith("validate_tracked_source_scope.py") else stdout
def errors(d:dict)->list[str]:
 s=d.get("summary",{});state=d.get("effective_state",{});out=[]
 if tuple(s.get(k) for k in ("base_effective_command_count","extension_command_count","effective_command_count","orchestrator_commands","passed","failed"))!=(18,12,30,13,13,0) or d.get("state")!="PASS":out.append("gate denominator/state invalid")
 if any(s.get(k)!=0 for k in ("network_capable_commands","provider_calls","uploads","downloads","cost_usd","accepted_candidates","executable_panels","owner_decisions")) or s.get("human_review_minutes") is not None:out.append("activity/promotion/review fabricated")
 if d.get("comic_panel_plan_revision_created") is not False or d.get("animation_shot_plan") is not None or d.get("e_conte") is not None:out.append("planning boundary invalid")
 expected={"candidates":29,"ch05_candidates":26,"noncanon_concepts":3,"selected":14,"comic_panel_plans":50,"manifest_rows":14,"pending_decision_subjects":39,"completed_decisions":0,"repair_links":6,"next_microsequence_plans":4,"next_prompts":0,"frozen_paths":16,"baseline_paths":4}
 if state!=expected:out.append("effective state invalid")
 results=d.get("results",[])
 if len(results)!=13 or any(x.get("return_code")!=0 or x.get("network_capable") is not False or x.get("stderr") for x in results):out.append("result coverage/state invalid")
 if sum(x.get("stdout_normalization")=="TRACKED_COUNT_ONLY" for x in results)!=1:out.append("normalization scope invalid")
 return sorted(set(out))
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));fail=errors(d)
 if sha(BASE)!=d["supersedes"]["sha256"]:fail.append("base r2 binding mismatch")
 for item in d["results"]:
  path=ROOT/item["path"]
  if not path.is_file() or sha(path)!=item["script_sha256"]:fail.append(f"script mismatch: {item['path']}");continue
  done=subprocess.run([sys.executable,str(path)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=300);stdout=done.stdout.replace("\r\n","\n").strip()+"\n";normalized=normalize(item["path"],stdout)
  if done.returncode!=0 or done.stderr or hashlib.sha256(normalized.encode()).hexdigest()!=item["normalized_stdout_sha256"]:fail.append(f"reproducer mismatch: {item['path']}")
 mutations=[lambda x:x.update(state="FAIL"),lambda x:x["summary"].update(base_effective_command_count=17),lambda x:x["summary"].update(extension_command_count=11),lambda x:x["summary"].update(effective_command_count=29),lambda x:x["summary"].update(orchestrator_commands=12),lambda x:x["summary"].update(passed=12),lambda x:x["summary"].update(failed=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(downloads=1),lambda x:x["summary"].update(cost_usd=1),lambda x:x["summary"].update(accepted_candidates=1),lambda x:x["summary"].update(executable_panels=1),lambda x:x["summary"].update(owner_decisions=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["effective_state"].update(candidates=28),lambda x:x["effective_state"].update(comic_panel_plans=49),lambda x:x["effective_state"].update(manifest_rows=13),lambda x:x["effective_state"].update(pending_decision_subjects=38),lambda x:x["effective_state"].update(next_prompts=1),lambda x:x["results"].pop(),lambda x:x["results"][0].update(return_code=1),lambda x:x.update(animation_shot_plan={})]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 overnight integrated release r3: {len(fail)} failures; immutable 18 + 12 = 30 effective checks; {rejected}/{len(mutations)} mutations rejected")
 print("29 candidates/50 plans/39 pending/0 decisions; frozen 16 + baseline 4 + source pass; 0 accepted/executable/calls/uploads/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
