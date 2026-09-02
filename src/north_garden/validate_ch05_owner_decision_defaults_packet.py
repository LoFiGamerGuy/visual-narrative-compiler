"""Validate CH05 owner decision defaults and null authority state."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-owner-decision-defaults-packet-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(10,6,4,10,0,0,0,0,0,0,0,0)
    actual=tuple(s.get(k) for k in ("decisions","pilot_roots","deferred","recommended_defaults","resolved","owner_decisions","review_events","production_prompts","renders","accepted","commercially_cleared","executable"))
    if actual!=expected or s.get("human_review_minutes") is not None or d.get("state")!="PASS_OWNER_PENDING": out.append("summary/state invalid")
    if d.get("response_template_valid_for_ingestion") is not False or d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("authority/planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for key in ("packet","markdown"):
        p=ROOT/d[key]["path"]
        if not p.is_file() or sha(p)!=d[key]["sha256"]: fail.append(f"output binding invalid: {key}")
    for item in d["inputs"]:
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["sha256"]: fail.append(f"input binding invalid: {item['path']}")
    packet=json.loads((ROOT/d["packet"]["path"]).read_text(encoding="utf-8")); rows=packet.get("rows",[])
    if len(rows)!=10 or sum(x["pilot_unlock_required"] for x in rows)!=6 or any(x["owner_decision"] is not None or x["reviewer"] is not None or x["human_review_minutes"] is not None or x["resolved"] for x in rows): fail.append("decision rows invalid")
    if any(not (ROOT/x["evidence"]["path"]).is_file() or sha(ROOT/x["evidence"]["path"])!=x["evidence"]["sha256"] for x in rows): fail.append("artifact bindings invalid")
    template=packet.get("response_template",{})
    if template.get("valid_for_ingestion") is not False or len(template.get("required_pilot_roots",[]))!=6 or len(template.get("deferred_decisions",[]))!=4 or any(x["owner_decision"] is not None for x in template.get("required_pilot_roots",[])+template.get("deferred_decisions",[])): fail.append("response template invalid")
    muts=[lambda x:x.update(state="FAIL")]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("decisions","pilot_roots","deferred","recommended_defaults","resolved","owner_decisions","review_events","production_prompts","renders","accepted","commercially_cleared","executable")]+[lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(response_template_valid_for_ingestion=True),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 owner defaults: {len(fail)} failures; 10=6+4 / 0 resolved/ingested; {rejected}/{len(muts)} mutations rejected")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
