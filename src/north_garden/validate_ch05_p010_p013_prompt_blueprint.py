"""Validate non-executable P010-P013 prompt blueprints."""
from __future__ import annotations
import copy,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-p010-p013-prompt-blueprint-r1.json"; PROHIBITED=re.compile(r"\b(?:boy|girl|kid|child|teen|minor|real person|celebrity|photoreal likeness)\b",re.I)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]
    expected=(4,4,3,2,1,0,0,0,0,0,0)
    actual=tuple(s.get(k) for k in ("rows","lint_pass","reference_uses","unique_reference_ids","text_only_rows","production_prompts_mutated","execution_ready_rows","uploads","provider_calls","renders","paid_spend_usd"))
    if d.get("state")!="PASS_NOT_EXECUTABLE" or actual!=expected or d.get("production_manifest_prompt_null_count")!=4 or d.get("owner_unlock_state")!="BLOCKED_EXACT_OWNER_DECISIONS_REQUIRED": out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for x in [d["blueprint"],*d["inputs"]]:
        p=ROOT/x["path"]
        if not p.is_file() or sha(p)!=x["sha256"]: fail.append(f"binding invalid: {x['path']}")
    b=json.loads((ROOT/d["blueprint"]["path"]).read_text(encoding="utf-8")); rows=b.get("rows",[])
    if len(rows)!=4 or [x["candidate_slot"] for x in rows]!=["m001","m002","m003","m004"]: fail.append("row identity invalid")
    for x in rows:
        prompt=x["draft_prompt"]
        if hashlib.sha256(prompt.encode()).hexdigest()!=x["draft_prompt_sha256"] or PROHIBITED.search(prompt) or x["lint"]["passed"] is not True: fail.append(f"prompt/lint invalid: {x['candidate_slot']}")
        if x["production_manifest_prompt_mutated"] is not False or x["execution_ready"] is not False: fail.append(f"promotion invalid: {x['candidate_slot']}")
        for ref in x["input_references"]:
            p=ROOT/ref["path"]
            if not p.is_file() or sha(p)!=ref["sha256"] or ref["local_hash_verified"] is not True or ref["upload_performed"] is not False: fail.append(f"reference invalid: {x['candidate_slot']}")
    manifest=json.loads((ROOT/b["inputs"][0]["path"]).read_text(encoding="utf-8"))
    if any(x["prompt"] is not None or x["prompt_sha256"] is not None or x["execution_ready"] is not False for x in manifest["rows"]): fail.append("production manifest mutated")
    muts=[lambda x:x.update(state="EXECUTABLE"),lambda x:x["summary"].update(rows=3),lambda x:x["summary"].update(lint_pass=3),lambda x:x["summary"].update(reference_uses=4),lambda x:x["summary"].update(unique_reference_ids=3),lambda x:x["summary"].update(text_only_rows=0),lambda x:x["summary"].update(production_prompts_mutated=1),lambda x:x["summary"].update(execution_ready_rows=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(renders=1),lambda x:x["summary"].update(paid_spend_usd=1),lambda x:x.update(production_manifest_prompt_null_count=3),lambda x:x.update(owner_unlock_state="READY"),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"P010-P013 prompt blueprint: {len(fail)} failures; 4/4 lint; 3 uses/2 unique + 1 text-only; {rejected}/{len(muts)} mutations rejected")
    print("production prompts/execution/uploads/renders/cost 0/0/0/0/$0")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
