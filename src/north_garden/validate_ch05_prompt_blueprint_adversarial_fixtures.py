"""Exercise malformed prompt-blueprint fixtures and emit exact evidence."""
from __future__ import annotations
import argparse,copy,hashlib,json
from pathlib import Path
from validate_ch05_prompt_blueprint_draft import ROOT,DEFAULT,validate
OUTPUT=ROOT/"docs/research/evidence/ch05-prompt-blueprint-adversarial-validation-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rehash(row): row["draft_prompt_sha256"]=hashlib.sha256(row["draft_prompt"].encode()).hexdigest()
def cases(base):
    actions=[]
    actions += [("state_executable",lambda x:x.update(state="EXECUTABLE")),("missing_row",lambda x:x["rows"].pop()),("duplicate_slot",lambda x:x["rows"][3].update(candidate_slot="m003")),("plan_hash",lambda x:x["rows"][0].update(plan_canonical_sha256="0"*64)),("style",lambda x:x["rows"][1].update(style_id="cel_painted")),("canvas",lambda x:x["rows"][2].update(planning_canvas_px=[4096,4096])),("cast",lambda x:x["rows"][0].update(visible_adult_cast=[])),("prompt_hash",lambda x:x["rows"][0].update(draft_prompt_sha256="0"*64))]
    def edit(slot,old,new):
        def apply(x): row=x["rows"][slot]; row["draft_prompt"]=row["draft_prompt"].replace(old,new); rehash(row)
        return apply
    actions += [("child_term",edit(0,"clearly adult woman","girl")),("real_person",edit(1,"clearly adult man","real person")),("sigrid_hair",edit(0,"dark-brown to near-black","bright blond")),("soren_hair",edit(1,"light-brown to dark-blond","black")),("soren_coat",edit(1,"pale oatmeal work coat","red coat")),("role_order",edit(3,"Soren remains on viewer-left","Soren moves nearby")),("causal_object",edit(2,"points distinctly downhill","lies somewhere")),("lettering_zone",edit(3,"upper-center 16 percent","upper area")),("no_text",edit(0,"No text","Text allowed")),("object_character",edit(2,"no people","Soren watches"))]
    actions += [("unauthorized_ref",lambda x:x["rows"][0]["input_references"][0].update(reference_id="p036_geometry")),("ref_hash",lambda x:x["rows"][0]["input_references"][0].update(sha256="0"*64)),("upload_performed",lambda x:x["rows"][0]["input_references"][0].update(upload_performed=True)),("extra_ref",lambda x:x["rows"][2]["input_references"].append(copy.deepcopy(x["rows"][0]["input_references"][0]))),("execution_ready",lambda x:x["rows"][0].update(execution_ready=True)),("production_mutated",lambda x:x["rows"][0].update(production_manifest_prompt_mutated=True)),("lint_false",lambda x:x["rows"][0]["lint"].update(passed=False)),("summary",lambda x:x["summary"].update(reference_uses=4)),("unlock",lambda x:x.update(owner_unlock_state="READY")),("cross_medium",lambda x:x.update(animation_shot_plan={}))]
    out=[]
    for name,action in actions: value=copy.deepcopy(base); action(value); out.append((name,value))
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("--emit",action="store_true"); a=p.parse_args(); base=json.loads(DEFAULT.read_text(encoding="utf-8")); base_errors=validate(base); fixtures=cases(base); rows=[{"fixture":name,"error_count":len(validate(value)),"rejected":bool(validate(value))} for name,value in fixtures]; rejected=sum(x["rejected"] for x in rows)
    evidence={"record_type":"ComicPromptBlueprintAdversarialValidation","schema_version":"1.0","record_id":"ng-ch05-prompt-blueprint-adversarial-validation-r1","state":"PASS" if not base_errors and rejected==len(rows) else "FAIL","blueprint":{"path":DEFAULT.relative_to(ROOT).as_posix(),"sha256":sha(DEFAULT)},"validator":{"path":"src/north_garden/validate_ch05_prompt_blueprint_draft.py","sha256":sha(ROOT/"src/north_garden/validate_ch05_prompt_blueprint_draft.py")},"summary":{"valid_blueprints_passed":int(not base_errors),"malformed_fixtures":len(rows),"malformed_rejected":rejected,"age_or_likeness_fixtures":2,"continuity_or_role_fixtures":5,"causal_or_lettering_fixtures":3,"reference_boundary_fixtures":4,"promotion_or_schema_fixtures":len(rows)-14,"provider_calls":0,"uploads":0,"renders":0,"cost_usd":0},"fixtures":rows,"animation_shot_plan":None,"e_conte":None,"boundary":"Synthetic in-memory validation only. No prompt, reference, provider, generated pixel, or production record is modified."}
    if a.emit: OUTPUT.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n")
    tracked=json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else evidence; fail=[]
    if tracked!=evidence: fail.append("tracked evidence differs")
    if evidence["state"]!="PASS" or rejected!=len(rows) or len(rows)!=28: fail.append("fixture denominator invalid")
    print(f"CH05 prompt blueprint adversarial fixtures: {len(fail)} failures; 1/1 valid pass; {rejected}/{len(rows)} malformed rejected")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
