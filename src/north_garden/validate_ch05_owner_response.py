"""Validate a CH05 six-root owner response without ingesting it."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; CONTRACT=ROOT/"production/comic/review/ch05-p010-p013-owner-unlock-contract-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def validate_document(d,mode):
    contract=json.loads(CONTRACT.read_text(encoding="utf-8")); roots={x["decision_id"]:x["allowed_decisions"] for x in contract["exact_required_decisions"]}; out=[]
    if d.get("record_type")!="CH05OwnerPilotRootResponse" or d.get("schema_version")!="1.0": out.append("record type/schema invalid")
    if d.get("contract")!={"path":CONTRACT.relative_to(ROOT).as_posix(),"sha256":sha(CONTRACT)}: out.append("contract binding invalid")
    rows=d.get("decisions",[]); ids=[x.get("decision_id") for x in rows]
    if len(rows)!=6 or len(set(ids))!=6 or set(ids)!=set(roots): out.append("six exact unique roots required")
    for row in rows:
        did=row.get("decision_id")
        if did not in roots: continue
        if row.get("allowed_values")!=roots[did]: out.append(f"allowed values invalid: {did}")
        if mode=="template":
            if any(row.get(k) is not None for k in ("owner_decision","reviewer","human_review_minutes","notes")): out.append(f"template row populated: {did}")
        else:
            if row.get("owner_decision") not in roots[did]: out.append(f"decision invalid: {did}")
            if not isinstance(row.get("reviewer"),str) or not row["reviewer"].strip(): out.append(f"reviewer missing: {did}")
            if not isinstance(row.get("human_review_minutes"),(int,float)) or isinstance(row.get("human_review_minutes"),bool) or row["human_review_minutes"]<=0: out.append(f"minutes invalid: {did}")
    expected=("UNFILLED_TEMPLATE",False) if mode=="template" else ("OWNER_RESPONSE_COMPLETE_NOT_INGESTED",True)
    if (d.get("state"),d.get("valid_for_ingestion"))!=expected: out.append("state/ingestion eligibility invalid")
    if d.get("deferred_decisions")!={"lettering_visual_arm":None,"strongest_candidate_shortlist":None,"noncanon_litrpg_direction":None,"commercial_and_exact_base":None}: out.append("deferred boundary invalid")
    if any(d.get(k) is not None for k in ("candidate_acceptance","commercial_clearance","exact_base_selection","comic_panel_plan_revision")): out.append("promotion/plan fields must be null")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("cross-medium planning invalid")
    return sorted(set(out))
def main():
    p=argparse.ArgumentParser(); p.add_argument("document",type=Path); p.add_argument("--mode",choices=("template","response"),required=True); a=p.parse_args(); path=a.document if a.document.is_absolute() else ROOT/a.document
    try: d=json.loads(path.read_text(encoding="utf-8")); fail=validate_document(d,a.mode)
    except (FileNotFoundError,json.JSONDecodeError) as er: print(f"FAIL: {er}",file=sys.stderr); return 1
    print(f"CH05 owner response: {len(fail)} failures; mode {a.mode}; six roots; no ingestion performed")
    for x in fail: print(f"FAIL: {x}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
