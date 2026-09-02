"""Validate the command-level CH05 production operating playbook."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-chapter-production-operating-playbook-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(12,5,1,6,11,1,1,"DRAFT_BLUEPRINTED",0,0,0,0,0,0,0)
    actual=tuple(s.get(k) for k in ("steps","ready_local_or_dry_run_steps","owner_action_steps","blocked_production_or_review_steps","shell_commands","agent_only_steps","intentionally_unimplemented_compilers","current_lifecycle_state","current_enabled_transitions","production_prompts","renders","review_events","accepted","commercially_cleared","executable"))
    if d.get("state")!="PASS_PRODUCTION_BLOCKED" or actual!=expected or s.get("human_review_minutes") is not None: out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for x in [d["playbook"],d["markdown"],*d["inputs"]]:
        p=ROOT/x["path"]
        if not p.is_file() or sha(p)!=x["sha256"]: fail.append(f"binding invalid: {x['path']}")
    p=json.loads((ROOT/d["playbook"]["path"]).read_text(encoding="utf-8")); steps=p.get("steps",[]); commands=[cmd for x in steps for cmd in x.get("commands",[])]; operator_actions=[cmd for x in steps for cmd in x.get("operator_actions",[])]
    if len(steps)!=12 or [x["order"] for x in steps]!=list(range(1,13)) or len(commands)!=11 or operator_actions!=["git diff --check","git push origin main"]: fail.append("step/command set invalid")
    for cmd in commands:
        if cmd.startswith("python ") and "<event-log.json>" not in cmd:
            script=cmd.split()[1]
            if not (ROOT/script).is_file(): fail.append(f"missing command script: {script}")
    if sum("OPENAI" in x.get("agent_action","").upper() for x in steps)!=1 or p["data_boundary"]["authorized_reference_hash_count"]!=3 or p["data_boundary"]["paid_api_prohibited"] is not True: fail.append("agent/data boundary invalid")
    if p["failure_policy"]!={"preserve_diagnostic":True,"smallest_one_class_repair":True,"maximum_pilot_repairs":2,"broad_reroll":False,"warnings_disclosed":True,"no_destructive_recovery":True}: fail.append("failure policy invalid")
    if any(x not in p["source_boundary"]["prohibited_commit_classes"] for x in (".env or credentials","generated images","weights or LoRAs","datasets or private references","installed runtimes or caches","unrelated workspace material")): fail.append("source boundary invalid")
    muts=[lambda x:x.update(state="PRODUCTION_READY"),lambda x:x["summary"].update(steps=11),lambda x:x["summary"].update(ready_local_or_dry_run_steps=6),lambda x:x["summary"].update(owner_action_steps=0),lambda x:x["summary"].update(blocked_production_or_review_steps=5),lambda x:x["summary"].update(shell_commands=10),lambda x:x["summary"].update(agent_only_steps=0),lambda x:x["summary"].update(intentionally_unimplemented_compilers=0),lambda x:x["summary"].update(current_lifecycle_state="BASE_RENDERED"),lambda x:x["summary"].update(current_enabled_transitions=1),lambda x:x["summary"].update(production_prompts=1),lambda x:x["summary"].update(renders=1),lambda x:x["summary"].update(review_events=1),lambda x:x["summary"].update(accepted=1),lambda x:x["summary"].update(commercially_cleared=1),lambda x:x["summary"].update(executable=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 operating playbook: {len(fail)} failures; 12 steps/11 shell/1 agent; local-owner-blocked 5/1/6; {rejected}/{len(muts)} mutations rejected")
    print("current draft/0 enabled; prompts/renders/review/accepted/executable 0/0/0/0/0")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
