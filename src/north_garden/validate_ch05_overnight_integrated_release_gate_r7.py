"""Validate and reproduce append-only CH05 overnight integrated release gate r7."""
from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r6.json";EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r7.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});state=d.get("effective_state",{});out=[]
 if tuple(s.get(k) for k in ("base_effective_command_count","extension_command_count","effective_command_count","orchestrator_commands","passed","failed"))!=(42,4,46,5,5,0) or d.get("state")!="PASS":out.append("gate denominator/state invalid")
 if any(s.get(k)!=0 for k in ("network_capable_commands","provider_calls","uploads","downloads","cost_usd","accepted_candidates","executable_panels","owner_decisions")) or s.get("human_review_minutes") is not None:out.append("activity/promotion/review fabricated")
 if d.get("comic_panel_plan_revision_created") is not False or d.get("animation_shot_plan") is not None or d.get("e_conte") is not None:out.append("planning boundary invalid")
 expected={"candidates":29,"comic_panel_plans":50,"sequence_batches":12,"sequence_size_min":3,"sequence_size_max":5,"planned_sequence_artifacts":48,"lettering_silent_inserts":16,"lettering_protected_action":14,"lettering_caption_or_silence":13,"lettering_speech_or_reaction":6,"lettering_attributed_unbound":1,"review_links":105,"owner_hub_links":6,"owner_tasks":24,"next_prompts":0,"frozen_paths":16,"baseline_paths":4}
 if state!=expected:out.append("effective state invalid")
 results=d.get("results",[])
 if len(results)!=5 or any(x.get("return_code")!=0 or x.get("network_capable") is not False or x.get("stderr") for x in results):out.append("result coverage/state invalid")
 return sorted(set(out))
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));fail=errors(d)
 if sha(BASE)!=d["supersedes"]["sha256"]:fail.append("base r6 binding mismatch")
 for item in d["results"]:
  p=ROOT/item["path"]
  if not p.is_file() or sha(p)!=item["script_sha256"]:fail.append(f"script mismatch: {item['path']}");continue
  done=subprocess.run([sys.executable,str(p)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=300);stdout=done.stdout.replace("\r\n","\n").strip()+"\n"
  if done.returncode!=0 or done.stderr or hashlib.sha256(stdout.encode()).hexdigest()!=item["stdout_sha256"]:fail.append(f"reproducer mismatch: {item['path']}")
 muts=[lambda x:x.update(state="FAIL"),lambda x:x["summary"].update(base_effective_command_count=41),lambda x:x["summary"].update(extension_command_count=3),lambda x:x["summary"].update(effective_command_count=45),lambda x:x["summary"].update(orchestrator_commands=4),lambda x:x["summary"].update(passed=4),lambda x:x["summary"].update(failed=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(downloads=1),lambda x:x["summary"].update(cost_usd=1),lambda x:x["summary"].update(accepted_candidates=1),lambda x:x["summary"].update(executable_panels=1),lambda x:x["summary"].update(owner_decisions=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["effective_state"].update(sequence_batches=11),lambda x:x["effective_state"].update(sequence_size_min=2),lambda x:x["effective_state"].update(planned_sequence_artifacts=47),lambda x:x["effective_state"].update(lettering_silent_inserts=15),lambda x:x["effective_state"].update(lettering_attributed_unbound=0),lambda x:x["effective_state"].update(review_links=104),lambda x:x["effective_state"].update(owner_hub_links=5),lambda x:x["effective_state"].update(next_prompts=1),lambda x:x["results"].pop(),lambda x:x.update(animation_shot_plan={})]
 rejected=0
 for mut in muts:y=copy.deepcopy(d);mut(y);rejected+=bool(errors(y))
 if rejected!=len(muts):fail.append(f"only {rejected}/{len(muts)} mutations rejected")
 print(f"CH05 overnight integrated release r7: {len(fail)} failures; immutable 42 + 4 = 46 effective checks; {rejected}/{len(muts)} mutations rejected")
 print("12 sequences/50 lettering rows/105 links/24 tasks; frozen 16 + baseline 4; 0 prompts/review/accepted/executable/calls/uploads/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
