"""Narrow compatibility validation for immutable r11 after later append-only lineage."""
from __future__ import annotations
import copy, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-overnight-integrated-release-gate-r11.json"; VALIDATOR=ROOT/"src/north_garden/validate_ch05_overnight_integrated_release_gate_r11.py"
EXPECTED_STDOUT="""CH05 integrated release r11: 1 failures; immutable 66 + 8 = 74 effective checks; 29/29 mutations rejected
29 candidates/50 plans/122 links/67 direct/10 defaults/835 paths/73 zero-cost; provider/promotion 0
FAIL: reproducer mismatch: src/north_garden/validate_ch05_final_evidence_reproducer_matrix_r2.py
"""
def errors(document):
    summary=document.get("summary",{}); state=document.get("effective_state",{}); out=[]
    if document.get("state")!="PASS" or tuple(summary.get(key) for key in ("base_effective_command_count","extension_command_count","effective_command_count","orchestrator_commands","passed","failed"))!=(66,8,74,9,9,0): out.append("r11 state/denominator invalid")
    if any(summary.get(key)!=0 for key in ("provider_calls","uploads","cost_usd","accepted_candidates","commercially_cleared_candidates","executable_panels","owner_decisions")) or summary.get("human_review_minutes") is not None: out.append("r11 activity/promotion invalid")
    if tuple(state.get(key) for key in ("candidates","comic_panel_plans","review_links","zero_cost_milestones","frozen_paths","baseline_paths","production_prompts","accepted_candidates","executable_panels"))!=(29,50,122,73,16,4,0,0,0): out.append("r11 effective state invalid")
    if len(document.get("results",[]))!=9 or any(row.get("return_code")!=0 for row in document.get("results",[])): out.append("r11 recorded results invalid")
    return out
def main():
    document=json.loads(EVIDENCE.read_text(encoding="utf-8")); failures=errors(document); done=subprocess.run([sys.executable,str(VALIDATOR)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=1200); stdout=done.stdout.replace("\r\n","\n")
    if done.returncode!=1 or done.stderr.replace("\r\n","\n") or stdout!=EXPECTED_STDOUT: failures.append("compatibility failure is not the one exact nested reproducer mismatch")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x["summary"].update(effective_command_count=73),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["effective_state"].update(review_links=121),lambda x:x["effective_state"].update(frozen_paths=15),lambda x:x["effective_state"].update(production_prompts=1),lambda x:x["results"].pop()]; rejected=0
    for mutate in mutations: altered=copy.deepcopy(document); mutate(altered); rejected+=bool(errors(altered))
    if rejected!=len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 r11 compatibility: {len(failures)} failures; immutable 74 checks; one exact nested r10-lineage mismatch; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__": raise SystemExit(main())
