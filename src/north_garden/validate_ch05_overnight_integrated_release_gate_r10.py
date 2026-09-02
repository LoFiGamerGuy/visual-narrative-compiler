"""Validate and reproduce append-only CH05 integrated release r10."""
from __future__ import annotations
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r9.json"; EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r10.json"
NORMALIZED={"src/north_garden/validate_tracked_source_scope.py":"decimal count in '<N> tracked safe-source paths' only"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(path,text):
    if path in NORMALIZED: return re.sub(r"\d+ tracked safe-source paths","<LIVE_COUNT> tracked safe-source paths",text)
    return text
def errors(d):
    s=d.get("summary",{}); state=d.get("effective_state",{}); out=[]
    if d.get("state")!="PASS" or tuple(s.get(k) for k in ("base_effective_command_count","extension_command_count","effective_command_count","orchestrator_commands","passed","failed","normalized_live_diagnostics"))!=(58,8,66,9,9,0,1): out.append("state/denominator invalid")
    if any(s.get(k)!=0 for k in ("network_capable_commands","provider_calls","uploads","downloads","cost_usd","accepted_candidates","commercially_cleared_candidates","executable_panels","owner_decisions")) or s.get("human_review_minutes") is not None: out.append("activity/promotion invalid")
    expected={"candidates":29,"comic_panel_plans":50,"sequence_batches":12,"review_links":117,"current_owner_hub_links":5,"strongest_candidates":14,"route_decisions":10,"pilot_owner_roots":6,"resolved_pilot_roots":0,"production_prompts":0,"prerender_artifacts_built":0,"lifecycle_states":11,"chapter_batches_entered":1,"chapter_batches_not_entered":11,"chapter_review_artifacts_planned":49,"remaining_planning_candidates":49,"fresh_arm_candidates":68,"operating_steps":12,"shell_validation_commands":11,"zero_cost_milestones":68,"frozen_paths":16,"baseline_paths":4}
    if state!=expected: out.append("effective state invalid")
    if len(d.get("results",[]))!=9 or any(x.get("return_code")!=0 or x.get("network_capable") is not False or x.get("stderr") for x in d.get("results",[])): out.append("results invalid")
    normal=[x for x in d.get("results",[]) if x.get("normalization") is not None]
    if len(normal)!=1 or normal[0].get("path") not in NORMALIZED or normal[0].get("normalization")!=NORMALIZED[normal[0]["path"]]: out.append("normalization scope invalid")
    if d.get("comic_panel_plan_revision_created") is not False or d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return sorted(set(out))
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    if d.get("supersedes")!={"record_id":"ng-ch05-overnight-integrated-release-gate-r9","path":BASE.relative_to(ROOT).as_posix(),"sha256":sha(BASE)}: fail.append("base binding invalid")
    for item in d.get("results",[]):
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["script_sha256"]: fail.append(f"script mismatch: {item['path']}"); continue
        done=subprocess.run([sys.executable,str(p)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=600); raw=done.stdout.replace("\r\n","\n").strip()+"\n"; stdout=normalize(item["path"],raw)
        if done.returncode!=0 or done.stderr.replace("\r\n","\n") or hashlib.sha256(stdout.encode()).hexdigest()!=item["stdout_sha256"]: fail.append(f"reproducer mismatch: {item['path']}")
    muts=[lambda x:x.update(state="FAIL")]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("base_effective_command_count","extension_command_count","effective_command_count","orchestrator_commands","passed","failed","normalized_live_diagnostics","provider_calls","uploads","cost_usd","accepted_candidates","commercially_cleared_candidates","executable_panels","owner_decisions")]+[lambda x:x["summary"].update(human_review_minutes=1)]+[lambda x,k=k:x["effective_state"].update({k:-1}) for k in ("review_links","current_owner_hub_links","strongest_candidates","route_decisions","pilot_owner_roots","resolved_pilot_roots","production_prompts","prerender_artifacts_built","chapter_batches_entered","remaining_planning_candidates","fresh_arm_candidates","operating_steps","zero_cost_milestones","frozen_paths","baseline_paths")]+[lambda x:x["results"].pop(),lambda x:x["results"][0].update(normalization="broad"),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 integrated release r10: {len(fail)} failures; immutable 58 + 8 = 66 effective checks; {rejected}/{len(muts)} mutations rejected")
    print("29 candidates/50 plans/117 links/49 remaining/68 fresh/68 zero-cost; provider/promotion 0")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
