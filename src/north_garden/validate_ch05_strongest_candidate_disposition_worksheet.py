"""Validate CH05 strongest-candidate disposition template or response."""
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; TEMPLATE=ROOT/"production/comic/review/ch05-strongest-candidate-disposition-worksheet-r1.json"; EVIDENCE=ROOT/"docs/research/evidence/ch05-strongest-candidate-disposition-worksheet-r1.json"; CHECKS=["role_identity","hair_style_color","wardrobe_continuity","causal_action","hands","lettering_clearance","phone_readability","style_density_fit"]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_document(document,mode):
    out=[]; template=json.loads(TEMPLATE.read_text(encoding="utf-8")); expected_ids=[row["candidate_id"] for row in template["candidates"]]; rows=document.get("candidates",[])
    if document.get("record_type")!="CH05StrongestCandidateDispositionWorksheet" or document.get("schema_version")!="1.0" or len(rows)!=14 or [row.get("candidate_id") for row in rows]!=expected_ids: out.append("record/candidate coverage invalid")
    if document.get("allowed_check_values")!=["PASS","WARN","FAIL"] or document.get("allowed_dispositions")!=template["allowed_dispositions"] or document.get("allowed_targeted_repair_classes")!=template["allowed_targeted_repair_classes"]: out.append("allowed values invalid")
    for index,row in enumerate(rows):
        if index>=14: break
        source=template["candidates"][index]
        if any(row.get(key)!=source.get(key) for key in ("candidate_id","panel_id","style","artifact")) or set(row.get("checks",{}))!=set(CHECKS): out.append(f"binding/check schema invalid: {index}"); continue
        if mode=="template":
            if any(value is not None for value in row["checks"].values()) or any(row.get(key) is not None for key in ("disposition","targeted_repair_class","reviewer","human_review_minutes","notes")): out.append(f"template row populated: {row['candidate_id']}")
        else:
            if any(value not in ("PASS","WARN","FAIL") for value in row["checks"].values()): out.append(f"check invalid: {row['candidate_id']}")
            if row.get("disposition") not in template["allowed_dispositions"]: out.append(f"disposition invalid: {row['candidate_id']}")
            repair=row.get("targeted_repair_class")
            if (row.get("disposition")=="REQUEST_ONE_TARGETED_REPAIR")!=(repair in template["allowed_targeted_repair_classes"]): out.append(f"repair parity invalid: {row['candidate_id']}")
            if not isinstance(row.get("reviewer"),str) or not row["reviewer"].strip() or not isinstance(row.get("human_review_minutes"),(int,float)) or isinstance(row.get("human_review_minutes"),bool) or row["human_review_minutes"]<=0: out.append(f"review evidence invalid: {row['candidate_id']}")
    expected=("UNFILLED_TEMPLATE",False) if mode=="template" else ("OWNER_VISUAL_DISPOSITIONS_COMPLETE_NOT_ROLLED_UP",True)
    if (document.get("state"),document.get("valid_for_rollup"))!=expected: out.append("state/rollup invalid")
    if any(document.get(key) is not None for key in ("shortlist_rollup","route_decision","candidate_acceptance","commercial_clearance","exact_base_selection","comic_panel_plan_revision","animation_shot_plan","e_conte")): out.append("authority/cross-medium fields must remain null")
    return sorted(set(out))
def evidence_errors(document):
    summary=document.get("summary",{}); keys=("candidates","checks_per_candidate","total_checks","filled_checks","dispositions","targeted_repairs","reviewers","human_review_minutes","shortlist_rollup","route_decisions","candidate_acceptance","commercial_clearance","exact_base_selection","plan_revisions"); expected=(14,8,112,0,0,0,0,None,0,0,0,0,0,0); out=[]
    if document.get("state")!="PASS_NULL_TEMPLATE" or tuple(summary.get(key) for key in keys)!=expected: out.append("evidence state/denominator invalid")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("document",type=Path,nargs="?"); parser.add_argument("--mode",choices=("template","response"),default="template"); args=parser.parse_args()
    if args.document:
        path=args.document if args.document.is_absolute() else ROOT/args.document; failures=validate_document(json.loads(path.read_text(encoding="utf-8")),args.mode); print(f"CH05 candidate worksheet: {len(failures)} failures; mode {args.mode}; no rollup/acceptance performed"); return 1 if failures else 0
    evidence=json.loads(EVIDENCE.read_text(encoding="utf-8")); failures=evidence_errors(evidence)
    for key in ("worksheet","guide"):
        path=ROOT/evidence[key]["path"]
        if not path.is_file() or sha(path)!=evidence[key]["sha256"]: failures.append(f"binding invalid: {key}")
    template=json.loads(TEMPLATE.read_text(encoding="utf-8")); failures+=validate_document(template,"template"); valid=copy.deepcopy(template); valid.update(state="OWNER_VISUAL_DISPOSITIONS_COMPLETE_NOT_ROLLED_UP",valid_for_rollup=True)
    for index,row in enumerate(valid["candidates"]): row["checks"]={key:"PASS" for key in CHECKS}; row.update(disposition="REQUEST_ONE_TARGETED_REPAIR" if index==0 else "ADVANCE_TO_NEXT_COMPARISON",targeted_repair_class="HAIR_STYLE_COLOR" if index==0 else None,reviewer="synthetic-owner",human_review_minutes=1.0)
    if validate_document(valid,"response"): failures.append("valid synthetic response failed")
    invalid=[]
    def add(mutator): altered=copy.deepcopy(valid); mutator(altered); invalid.append(altered)
    add(lambda x:x["candidates"].pop()); add(lambda x:x["candidates"][0]["checks"].update(hands="MAYBE")); add(lambda x:x["candidates"][0].update(disposition="ACCEPT")); add(lambda x:x["candidates"][0].update(targeted_repair_class=None)); add(lambda x:x["candidates"][1].update(targeted_repair_class="HANDS")); add(lambda x:x["candidates"][0].update(reviewer="")); add(lambda x:x["candidates"][0].update(human_review_minutes=0)); add(lambda x:x.update(shortlist_rollup="ADVANCE")); add(lambda x:x.update(route_decision="SELECT")); add(lambda x:x.update(candidate_acceptance=True)); add(lambda x:x.update(commercial_clearance=True)); add(lambda x:x.update(exact_base_selection="c002")); add(lambda x:x.update(comic_panel_plan_revision={})); add(lambda x:x.update(animation_shot_plan={})); rejected=sum(bool(validate_document(row,"response")) for row in invalid)
    if rejected!=len(invalid): failures.append(f"only {rejected}/{len(invalid)} malformed responses rejected")
    mutations=[lambda x:x.update(state="FAIL"),lambda x:x.update(animation_shot_plan={})]+[lambda x,key=key:x["summary"].update({key:1 if key=="human_review_minutes" else -1}) for key in ("candidates","checks_per_candidate","total_checks","filled_checks","dispositions","targeted_repairs","reviewers","human_review_minutes","shortlist_rollup","route_decisions","candidate_acceptance","commercial_clearance","exact_base_selection","plan_revisions")]; evidence_rejected=0
    for mutate in mutations: altered=copy.deepcopy(evidence); mutate(altered); evidence_rejected+=bool(evidence_errors(altered))
    if evidence_rejected!=len(mutations): failures.append(f"only {evidence_rejected}/{len(mutations)} evidence mutations rejected")
    print(f"CH05 candidate worksheet: {len(failures)} failures; 14 candidates/112 checks; 1 valid + {rejected}/{len(invalid)} malformed; {evidence_rejected}/{len(mutations)} evidence mutations rejected")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0
if __name__=="__main__": raise SystemExit(main())
