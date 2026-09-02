"""Validate and reproduce append-only CH05 integrated release r9."""
from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r8.json"; COMPAT=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-r8-compatibility-r1.json"; EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r9.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); state=d.get("effective_state",{}); out=[]
    if d.get("state")!="PASS" or tuple(s.get(k) for k in ("base_effective_command_count","extension_command_count","effective_command_count","orchestrator_commands","passed","failed"))!=(49,9,58,10,10,0): out.append("state/denominator invalid")
    if any(s.get(k)!=0 for k in ("network_capable_commands","provider_calls","uploads","downloads","cost_usd","accepted_candidates","commercially_cleared_candidates","executable_panels","owner_decisions")) or s.get("human_review_minutes") is not None: out.append("activity/promotion invalid")
    expected={"candidates":29,"comic_panel_plans":50,"sequence_batches":12,"review_links":112,"owner_hub_links":7,"pilot_owner_roots":6,"resolved_pilot_roots":0,"prompt_blueprint_rows":4,"production_prompts":0,"adversarial_fixtures_rejected":28,"prerender_artifacts_planned":5,"prerender_artifacts_built":0,"lifecycle_states":11,"lifecycle_legal_edges":11,"lifecycle_illegal_pairs":110,"chapter_batches_entered":1,"chapter_batches_not_entered":11,"chapter_review_artifacts_planned":49,"final_reproducer_domains":7,"safe_source_capture_paths":735,"frozen_paths":16,"baseline_paths":4,"zero_cost_milestones":54}
    if state!=expected: out.append("effective state invalid")
    if len(d.get("results",[]))!=10 or any(x.get("return_code")!=0 or x.get("network_capable") is not False or x.get("stderr") for x in d.get("results",[])): out.append("results invalid")
    if d.get("comic_panel_plan_revision_created") is not False or d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return sorted(set(out))
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    if d.get("supersedes")!={"record_id":"ng-ch05-overnight-integrated-release-gate-r8","path":BASE.relative_to(ROOT).as_posix(),"sha256":sha(BASE)} or d.get("base_compatibility")!={"path":COMPAT.relative_to(ROOT).as_posix(),"sha256":sha(COMPAT),"state":"PASS_NARROW_DYNAMIC_DIAGNOSTIC_NORMALIZATION"}: fail.append("base/compat binding invalid")
    for item in d.get("results",[]):
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["script_sha256"]: fail.append(f"script mismatch: {item['path']}"); continue
        done=subprocess.run([sys.executable,str(p)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=600); stdout=done.stdout.replace("\r\n","\n").strip()+"\n"
        if done.returncode!=0 or done.stderr.replace("\r\n","\n") or hashlib.sha256(stdout.encode()).hexdigest()!=item["stdout_sha256"]: fail.append(f"reproducer mismatch: {item['path']}")
    muts=[lambda x:x.update(state="FAIL"),lambda x:x["summary"].update(base_effective_command_count=48),lambda x:x["summary"].update(extension_command_count=8),lambda x:x["summary"].update(effective_command_count=57),lambda x:x["summary"].update(orchestrator_commands=9),lambda x:x["summary"].update(passed=9),lambda x:x["summary"].update(failed=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(cost_usd=1),lambda x:x["summary"].update(accepted_candidates=1),lambda x:x["summary"].update(commercially_cleared_candidates=1),lambda x:x["summary"].update(executable_panels=1),lambda x:x["summary"].update(owner_decisions=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["effective_state"].update(review_links=111),lambda x:x["effective_state"].update(pilot_owner_roots=5),lambda x:x["effective_state"].update(resolved_pilot_roots=1),lambda x:x["effective_state"].update(prompt_blueprint_rows=3),lambda x:x["effective_state"].update(production_prompts=1),lambda x:x["effective_state"].update(adversarial_fixtures_rejected=27),lambda x:x["effective_state"].update(prerender_artifacts_built=1),lambda x:x["effective_state"].update(lifecycle_legal_edges=10),lambda x:x["effective_state"].update(lifecycle_illegal_pairs=109),lambda x:x["effective_state"].update(chapter_batches_entered=2),lambda x:x["effective_state"].update(chapter_review_artifacts_planned=48),lambda x:x["effective_state"].update(final_reproducer_domains=6),lambda x:x["effective_state"].update(safe_source_capture_paths=734),lambda x:x["results"].pop(),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 integrated release r9: {len(fail)} failures; immutable compatible 49 + 9 = 58 effective checks; {rejected}/{len(muts)} mutations rejected")
    print("29 candidates/50 plans/112 links/4 drafts/5 NOT_BUILT/11 lifecycle states/12 batches; provider/promotion 0")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
