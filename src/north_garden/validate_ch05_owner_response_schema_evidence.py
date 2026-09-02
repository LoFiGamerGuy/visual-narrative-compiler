"""Validate CH05 owner-response schema evidence."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-owner-response-schema-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(6,4,1,2,3,20,20,0,0,0,0,0,0,0,0); actual=tuple(s.get(k) for k in ("root_count","deferred_count","template_valid","synthetic_responses_valid","valid_fixtures","invalid_fixtures","invalid_rejected","owner_decisions_ingested","review_events","provider_calls","uploads","paid_spend_usd","accepted","commercially_cleared","executable"))
    if actual!=expected or s.get("human_review_minutes") is not None or d.get("state")!="PASS_TEMPLATE_UNFILLED" or d.get("template_errors")!=[] or d.get("response_schema_errors")!=[]: out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for key in ("template","schema","guide"):
        p=ROOT/d[key]["path"]
        if not p.is_file() or sha(p)!=d[key]["sha256"]: fail.append(f"binding invalid: {key}")
    for item in d["inputs"]:
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["sha256"]: fail.append(f"input invalid: {item['path']}")
    muts=[lambda x:x.update(state="FAIL")]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("root_count","deferred_count","template_valid","synthetic_responses_valid","valid_fixtures","invalid_fixtures","invalid_rejected","owner_decisions_ingested","review_events","provider_calls","uploads","paid_spend_usd","accepted","commercially_cleared","executable")]+[lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(template_errors=["x"]),lambda x:x.update(animation_shot_plan={})]; rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 owner response schema: {len(fail)} failures; 3 valid/20 invalid; 0 ingested; {rejected}/{len(muts)} mutations rejected")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
