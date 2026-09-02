"""Run append-only integrated release r3 over all post-r2 CH05 evidence."""
from __future__ import annotations
import hashlib,json,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r2.json";OUTPUT=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r3.json"
COMMANDS=[
 "src/north_garden/validate_ch05_overnight_integrated_release_r2_compat.py",
 "src/north_garden/validate_ch05_instrumented_production_manifest_r2.py",
 "src/north_garden/validate_ch05_tier_a_effort_and_decision_contract.py",
 "src/north_garden/validate_ch05_owner_decision_worksheet.py",
 "src/north_garden/validate_ch05_owner_decision_draft_validator_evidence.py",
 "src/north_garden/validate_ch05_character_assertions_and_prompt_lint.py",
 "src/north_garden/validate_ch05_manual_continuity_atlas.py",
 "src/north_garden/validate_ch05_panel_scale_cadence_policy.py",
 "src/north_garden/validate_ch05_failure_class_repair_matrix.py",
 "src/north_garden/validate_ch05_p010_p013_preflight_contract.py",
 "src/north_garden/validate_ch05_owner_review_index_r2.py",
 "src/north_garden/validate_frozen_gauntlet_baseline_integrity.py",
 "src/north_garden/validate_tracked_source_scope.py",
]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(path:str,stdout:str)->tuple[str,str]:
 if path.endswith("validate_tracked_source_scope.py"):
  return re.sub(r"\d+ tracked safe-source paths","<TRACKED_COUNT> tracked safe-source paths",stdout),"TRACKED_COUNT_ONLY"
 return stdout,"NONE"
def main()->int:
 if OUTPUT.is_file():
  prior=json.loads(OUTPUT.read_text(encoding="utf-8"))
  failed_attempt=OUTPUT.with_name("ch05-overnight-integrated-release-gate-r3-attempt-1-failed.json")
  if prior.get("state")=="FAIL" and not failed_attempt.exists():failed_attempt.write_bytes(OUTPUT.read_bytes())
 base=json.loads(BASE.read_text(encoding="utf-8"));results=[];start_all=time.perf_counter()
 for i,relative in enumerate(COMMANDS,1):
  path=ROOT/relative;start=time.perf_counter();done=subprocess.run([sys.executable,str(path)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=300);elapsed=time.perf_counter()-start;stdout=done.stdout.replace("\r\n","\n").strip()+"\n";normalized,rule=normalize(relative,stdout)
  results.append({"path":relative,"script_sha256":sha(path),"command":f"python {relative}","network_capable":False,"return_code":done.returncode,"elapsed_seconds":round(elapsed,6),"stdout":stdout,"stdout_normalization":rule,"normalized_stdout_sha256":hashlib.sha256(normalized.encode()).hexdigest(),"stderr":done.stderr.replace("\r\n","\n")});print(f"[{i}/{len(COMMANDS)}] {'PASS' if done.returncode==0 else 'FAIL'} {relative} {elapsed:.3f}s")
 total=time.perf_counter()-start_all;passed=sum(x["return_code"]==0 for x in results)
 evidence={"record_type":"CH05OvernightIntegratedReleaseGate","schema_version":"1.2","record_id":"ng-ch05-overnight-integrated-release-gate-r3","state":"PASS" if passed==len(COMMANDS) else "FAIL","medium":"comic","comic_panel_plan_revision_created":False,"animation_shot_plan":None,"e_conte":None,"supersedes":{"record_id":base["record_id"],"path":BASE.relative_to(ROOT).as_posix(),"sha256":sha(BASE)},"summary":{"base_effective_command_count":18,"extension_command_count":12,"effective_command_count":30,"orchestrator_commands":len(COMMANDS),"passed":passed,"failed":len(COMMANDS)-passed,"observed_total_seconds":round(total,6),"network_capable_commands":0,"provider_calls":0,"uploads":0,"downloads":0,"cost_usd":0,"accepted_candidates":0,"executable_panels":0,"owner_decisions":0,"human_review_minutes":None},"results":results,"effective_state":{"candidates":29,"ch05_candidates":26,"noncanon_concepts":3,"selected":14,"comic_panel_plans":50,"manifest_rows":14,"pending_decision_subjects":39,"completed_decisions":0,"repair_links":6,"next_microsequence_plans":4,"next_prompts":0,"frozen_paths":16,"baseline_paths":4},"normalization_boundary":"Only the diagnostic tracked-path integer is normalized because safe additions change it; return code and all remaining text are exact. No validation failure text is normalized.","boundaries":["R2 remains immutable; r3 preserves its 18 effective checks, rebinds the current registry without rewriting r1, and adds eleven other post-r2/frozen/source checks.","All commands are local and non-network-capable.","Passing does not accept art, bind owner decisions/copy, authorize prompts/uploads, revise plans, or grant commercial clearance."]}
 with OUTPUT.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(evidence,indent=2)+"\n")
 print(f"integrated release r3: {passed}/{len(COMMANDS)} orchestrator commands, 30 effective checks in {total:.3f}s; {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}");return 0 if passed==len(COMMANDS) else 1
if __name__=="__main__":raise SystemExit(main())
