"""Validate and reproduce append-only CH05 overnight integrated release gate r8."""
from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r7.json"; EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r8.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); state=d.get("effective_state",{}); out=[]
    if d.get("state")!="PASS" or tuple(s.get(k) for k in ("base_effective_command_count","extension_command_count","effective_command_count","orchestrator_commands","passed","failed"))!=(46,3,49,4,4,0): out.append("denominator/state invalid")
    if any(s.get(k)!=0 for k in ("network_capable_commands","provider_calls","uploads","downloads","cost_usd","accepted_candidates","commercially_cleared_candidates","executable_panels","owner_decisions")) or s.get("human_review_minutes") is not None: out.append("activity/promotion invalid")
    if d.get("comic_panel_plan_revision_created") is not False or d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    expected={"candidates":29,"ch05_candidates":26,"noncanon_concepts":3,"comic_panel_plans":50,"represented_plans":14,"sequence_batches":12,"review_links":105,"strongest_candidates":14,"remaining_owner_decisions":10,"limitations":8,"observed_generation_seconds":1385.036,"reference_uses":39,"safe_source_capture_commit":"a1454db0ec0fbe80bda7c88a55764047c62618b4","safe_source_paths":735,"safe_source_bytes":11861823,"safe_source_generated_paths":0,"zero_cost_milestones":52,"next_prompts":0,"frozen_paths":16,"baseline_paths":4}
    if state!=expected: out.append("effective state invalid")
    results=d.get("results",[])
    if len(results)!=4 or any(x.get("return_code")!=0 or x.get("network_capable") is not False or x.get("stderr") for x in results): out.append("results invalid")
    return sorted(set(out))
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    if d.get("supersedes")!={"record_id":"ng-ch05-overnight-integrated-release-gate-r7","path":"docs/research/evidence/ch05-overnight-integrated-release-gate-r7.json","sha256":sha(BASE)}: fail.append("base binding invalid")
    for item in d.get("results",[]):
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["script_sha256"]: fail.append(f"script mismatch: {item['path']}"); continue
        done=subprocess.run([sys.executable,str(p),*item.get("arguments",[])],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=360); stdout=done.stdout.replace("\r\n","\n").strip()+"\n"
        if done.returncode!=0 or done.stderr.replace("\r\n","\n") or hashlib.sha256(stdout.encode()).hexdigest()!=item["stdout_sha256"]: fail.append(f"reproducer mismatch: {item['path']}")
    muts=[lambda x:x.update(state="FAIL"),lambda x:x["summary"].update(base_effective_command_count=45),lambda x:x["summary"].update(extension_command_count=2),lambda x:x["summary"].update(effective_command_count=48),lambda x:x["summary"].update(orchestrator_commands=3),lambda x:x["summary"].update(passed=3),lambda x:x["summary"].update(failed=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(cost_usd=1),lambda x:x["summary"].update(accepted_candidates=1),lambda x:x["summary"].update(commercially_cleared_candidates=1),lambda x:x["summary"].update(executable_panels=1),lambda x:x["summary"].update(owner_decisions=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["effective_state"].update(candidates=28),lambda x:x["effective_state"].update(comic_panel_plans=49),lambda x:x["effective_state"].update(review_links=104),lambda x:x["effective_state"].update(strongest_candidates=13),lambda x:x["effective_state"].update(observed_generation_seconds=1385.824),lambda x:x["effective_state"].update(safe_source_paths=734),lambda x:x["effective_state"].update(safe_source_generated_paths=1),lambda x:x["effective_state"].update(zero_cost_milestones=51),lambda x:x["effective_state"].update(next_prompts=1),lambda x:x["results"].pop(),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 overnight integrated release r8: {len(fail)} failures; immutable 46 + 3 = 49 effective checks; {rejected}/{len(muts)} mutations rejected")
    print("29 candidates/50 plans/105 links/735 safe paths/52 zero-cost milestones; frozen 16 + baseline 4; 0 accepted/executable/calls/uploads/$0")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
