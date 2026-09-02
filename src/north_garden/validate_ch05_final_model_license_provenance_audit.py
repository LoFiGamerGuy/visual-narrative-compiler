"""Validate final CH05 model/license/provenance audit."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-final-model-license-provenance-audit-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; keys=("records","ch05_records","noncanon_records","exact_prompts","exact_outputs","reference_uses","unique_authorized_reference_hashes","records_with_exact_unavailable_contract","model_null","endpoint_null","request_id_null","usage_null","cost_null","seed_null","pending_human_review","accepted","commercially_cleared","generation_reproducible","paid_api_calls","new_external_uploads","paid_spend_usd"); expected=(29,26,3,29,29,39,3,29,29,29,29,29,29,29,29,0,0,0,0,0,0)
    if tuple(s.get(k) for k in keys)!=expected or s.get("human_review_minutes") is not None or d.get("state")!="PASS_COMMERCIAL_OPEN": out.append("summary/state invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for key in ("audit","summary_document"):
        p=ROOT/d[key]["path"]
        if not p.is_file() or sha(p)!=d[key]["sha256"]: fail.append(f"output binding invalid: {key}")
    for item in d["inputs"]:
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["sha256"]: fail.append(f"input invalid: {item['path']}")
    audit=json.loads((ROOT/d["audit"]["path"]).read_text(encoding="utf-8")); refs=audit.get("authorized_references",[])
    if len(refs)!=3 or sum(x["renderrecord_uses"] for x in refs)!=39 or any(not x["local_hash_matches"] or x["authorization"]!="OPENAI_BUILT_IN_IMAGEGEN_ONLY" for x in refs): fail.append("reference authorization invalid")
    provider=audit.get("provider",{})
    if any(provider.get(k) is not None for k in ("model","endpoint","monetary_cost_usd","deterministic_seed")) or provider.get("commercial_use_decision")!="OPEN_PENDING_EXPLICIT_REVIEW": fail.append("provider/commercial state invalid")
    boundary=audit.get("reference_boundary",{})
    if any(boundary.get(k) is not False for k in ("real_person_likeness_used","adult_likeness_used","child_related_material_used","private_reference_used","lora_used","dataset_used")) or boundary.get("bfl_uploads")!=0 or boundary.get("other_provider_uploads")!=0: fail.append("data boundary invalid")
    if audit.get("noncanon_boundary",{}).get("comic_panel_plan_revision") is not None or audit.get("noncanon_boundary",{}).get("concept_outputs_reuploaded") is not False: fail.append("noncanon boundary invalid")
    muts=[lambda x:x.update(state="FAIL")]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("records","ch05_records","noncanon_records","exact_prompts","exact_outputs","reference_uses","unique_authorized_reference_hashes","records_with_exact_unavailable_contract","model_null","endpoint_null","request_id_null","usage_null","cost_null","seed_null","pending_human_review","accepted","commercially_cleared","generation_reproducible","paid_api_calls","new_external_uploads","paid_spend_usd")]+[lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(animation_shot_plan={})]; rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 model/license audit: {len(fail)} failures; 29/39/3, unavailable 29x6, commercial open; {rejected}/{len(muts)} mutations rejected")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
