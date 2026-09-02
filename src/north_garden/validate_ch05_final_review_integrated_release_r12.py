"""Validate and reproduce CH05 final-review integrated release r12."""
from __future__ import annotations
import copy, hashlib, json, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r11.json"; EVIDENCE=ROOT/"docs/research/evidence/ch05-final-review-integrated-release-r12.json"; NORMALIZED={"src/north_garden/validate_tracked_source_scope.py":"decimal tracked-path diagnostic only"}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def normalize(path,text): return re.sub(r"\d+ tracked safe-source paths","<LIVE_COUNT> tracked safe-source paths",text) if path in NORMALIZED else text
def errors(document):
    summary=document.get("summary",{}); state=document.get("effective_state",{}); out=[]
    if document.get("state")!="PASS" or tuple(summary.get(key) for key in ("base_effective_command_count","extension_command_count","effective_command_count","orchestrator_commands","passed","failed","normalized_live_diagnostics"))!=(74,10,84,11,11,0,1): out.append("state/denominator invalid")
    if any(summary.get(key)!=0 for key in ("network_capable_commands","provider_calls","uploads","downloads","cost_usd","accepted_candidates","commercially_cleared_candidates","executable_panels","owner_decisions_ingested","response_files","event_logs")) or summary.get("human_review_minutes") is not None: out.append("activity/promotion invalid")
    expected={"candidates":29,"comic_panel_plans":50,"sequence_batches":12,"review_links":128,"current_owner_hub_links":6,"direct_closeout_links":67,"pilot_roots":6,"resolved_decisions":0,"remaining_planning_candidates":49,"fresh_arm_candidates":68,"safe_source_capture_paths":873,"zero_cost_milestones":82,"frozen_paths":16,"baseline_paths":4,"production_prompts":0,"accepted_candidates":0,"executable_panels":0}
    if state!=expected: out.append("effective state invalid")
    results=document.get("results",[])
    if len(results)!=11 or any(row.get("return_code")!=0 or row.get("network_capable") is not False or row.get("stderr") for row in results): out.append("results invalid")
    if [row.get("path") for row in results if row.get("normalization") is not None]!=list(NORMALIZED): out.append("normalization scope invalid")
    if document.get("comic_panel_plan_revision_created") is not False or document.get("animation_shot_plan") is not None or document.get("e_conte") is not None: out.append("planning boundary invalid")
    return sorted(set(out))
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8")); failures=errors(document)
    if document.get("supersedes")!={"record_id":"ng-ch05-overnight-integrated-release-gate-r11","path":BASE.relative_to(ROOT).as_posix(),"sha256":sha(BASE)}: failures.append("base binding invalid")
    for item in document.get("results",[]):
        path=ROOT/item["path"]
        if not path.is_file() or sha(path)!=item["script_sha256"]: failures.append(f"script mismatch: {item['path']}"); continue
        done=subprocess.run([sys.executable,str(path),*item.get("arguments",[])],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=1200); raw=done.stdout.replace("\r\n","\n").strip()+"\n"; stdout=normalize(item["path"],raw)
        if done.returncode!=0 or done.stderr.replace("\r\n","\n") or hashlib.sha256(stdout.encode()).hexdigest()!=item["stdout_sha256"]: failures.append(f"reproducer mismatch: {item['path']}")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(animation_shot_plan={}),lambda x:x["results"].pop(),lambda x:x["results"][0].update(normalization="broad")]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("base_effective_command_count","extension_command_count","effective_command_count","orchestrator_commands","passed","failed","normalized_live_diagnostics","provider_calls","uploads","cost_usd","accepted_candidates","commercially_cleared_candidates","executable_panels","owner_decisions_ingested","response_files","event_logs","human_review_minutes")]+[lambda x,key=key:x["effective_state"].update({key:-1}) for key in ("candidates","review_links","current_owner_hub_links","pilot_roots","resolved_decisions","safe_source_capture_paths","zero_cost_milestones","frozen_paths","baseline_paths","production_prompts","accepted_candidates","executable_panels")]; rejected=0
    for mutate in mutations: altered=copy.deepcopy(document); mutate(altered); rejected+=bool(errors(altered))
    if rejected!=len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 final review release r12: {len(failures)} failures; immutable 74 + 10 = 84 effective checks; {rejected}/{len(mutations)} mutations rejected")
    print("29 candidates/50 plans/128 links/67 priority/6 roots/873 paths/82 zero-cost; provider/ingestion/promotion 0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__": raise SystemExit(main())
