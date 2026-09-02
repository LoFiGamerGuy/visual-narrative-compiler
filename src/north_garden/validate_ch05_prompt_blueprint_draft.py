"""Reusable semantic validator for the P010-P013 prompt-blueprint draft."""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; DEFAULT=ROOT/"production/comic/run-manifests/ch05-p010-p013-prompt-blueprint-r1.json"; MANIFEST=ROOT/"production/comic/run-manifests/ch05-p010-p013-production-manifest-dry-run-r1.json"
PROHIBITED=re.compile(r"\b(?:boy|girl|kid|child|teen|minor|real person|celebrity|photoreal likeness)\b",re.I)
REFS={"p050_dual_identity_action":("experiments/review-packets/ch05-style-density-scale-exploration-r1/P050-wide-action-clean-graphic-r1.png","cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d"),"p040_sigrid_face":("experiments/review-packets/ch05-style-density-scale-exploration-r1/P040-medium-close-cel-painted-r1.png","c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a")}
CANVAS={"m001":[1024,1280],"m002":[1024,1024],"m003":[1024,768],"m004":[1536,1024]}
TOKENS={"m001":["clearly adult woman","dark-brown to near-black","compact low bun","plaid wrap","weight settles","upper-left 18 percent","No text"],"m002":["clearly adult man","light-brown to dark-blond","pale oatmeal work coat","one soot-stained length of twine","upper-right 18 percent"],"m003":["no people","Exactly one twine strand","points distinctly downhill","clean top band","No text"],"m004":["clearly adult fictional characters","Soren remains on viewer-left","Sigrid remains on viewer-right","pale oatmeal work coat","dark-brown to near-black","plaid wrap","water bending around boots","upper-center 16 percent","No text"]}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(data):
    out=[]; manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); source={x["candidate_slot"]:x for x in manifest["rows"]}; rows=data.get("rows",[]); summary=data.get("summary",{})
    if data.get("record_type")!="ComicPromptBlueprint" or data.get("state")!="DRAFT_LINT_PASS_NOT_EXECUTABLE" or data.get("medium")!="comic": out.append("identity/state invalid")
    if len(rows)!=4 or [x.get("candidate_slot") for x in rows]!=["m001","m002","m003","m004"] or len({x.get("candidate_slot") for x in rows})!=4: out.append("row set/order invalid")
    for row in rows:
        slot=row.get("candidate_slot"); src=source.get(slot)
        if not src: out.append(f"unknown slot: {slot}"); continue
        prompt=row.get("draft_prompt","")
        if row.get("panel_id")!=src["panel_id"] or row.get("plan_revision_id")!=src["plan_revision_id"] or row.get("plan_canonical_sha256")!=src["plan_canonical_sha256"]: out.append(f"plan binding invalid: {slot}")
        if row.get("style_id")!=src["style_id"] or row.get("format_role")!=src["format_role"] or row.get("target_width_px")!=src["target_width_px"] or row.get("planning_canvas_px")!=CANVAS[slot]: out.append(f"style/format/canvas invalid: {slot}")
        if row.get("visible_adult_cast")!=src["visible_adult_cast"]: out.append(f"cast invalid: {slot}")
        if hashlib.sha256(prompt.encode()).hexdigest()!=row.get("draft_prompt_sha256") or PROHIBITED.search(prompt): out.append(f"prompt hash/prohibited term invalid: {slot}")
        if any(token not in prompt for token in TOKENS[slot]) or "speech balloons" not in prompt: out.append(f"required prompt semantics missing: {slot}")
        if slot=="m003" and any(name in prompt for name in ("Soren","Sigrid")): out.append("object control gained character")
        refs=row.get("input_references",[]); expected_ids=src["reference_ids"]
        if [x.get("reference_id") for x in refs]!=expected_ids or row.get("reference_count")!=len(refs): out.append(f"reference set invalid: {slot}")
        for ref in refs:
            expected=REFS.get(ref.get("reference_id"))
            if not expected or (ref.get("path"),ref.get("sha256"))!=expected or ref.get("local_hash_verified") is not True or ref.get("upload_authorized_only_for_openai_builtin_imagegen") is not True or ref.get("upload_performed") is not False: out.append(f"reference boundary invalid: {slot}")
        if row.get("lint",{}).get("passed") is not True or row.get("production_manifest_prompt_mutated") is not False or row.get("execution_ready") is not False: out.append(f"lint/promotion invalid: {slot}")
    derived={"rows":len(rows),"lint_pass":sum(x.get("lint",{}).get("passed") is True for x in rows),"reference_uses":sum(len(x.get("input_references",[])) for x in rows),"unique_reference_ids":len({r.get("reference_id") for x in rows for r in x.get("input_references",[])}),"text_only_rows":sum(not x.get("input_references") for x in rows),"production_prompts_mutated":sum(x.get("production_manifest_prompt_mutated") is not False for x in rows),"execution_ready_rows":sum(x.get("execution_ready") is not False for x in rows),"uploads":0,"provider_calls":0,"renders":0,"paid_spend_usd":0}
    if summary!=derived: out.append("summary invalid")
    if data.get("production_manifest_prompt_null_count")!=4 or data.get("owner_unlock_state")!="BLOCKED_EXACT_OWNER_DECISIONS_REQUIRED": out.append("unlock/production state invalid")
    if any(x["prompt"] is not None or x["prompt_sha256"] is not None or x["execution_ready"] is not False for x in manifest["rows"]): out.append("production manifest changed")
    if data.get("animation_shot_plan") is not None or data.get("e_conte") is not None: out.append("planning boundary invalid")
    return sorted(set(out))
def main():
    p=argparse.ArgumentParser(); p.add_argument("path",nargs="?",type=Path,default=DEFAULT); a=p.parse_args(); path=a.path if a.path.is_absolute() else ROOT/a.path
    try: data=json.loads(path.read_text(encoding="utf-8")); fail=validate(data)
    except (FileNotFoundError,json.JSONDecodeError,KeyError) as er: print(f"FAIL: {er}",file=sys.stderr); return 1
    print(f"CH05 prompt blueprint draft: {len(fail)} failures; {len(data.get('rows',[]))} rows; reusable semantic validation")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
