"""Validate append-only CH05 production manifest r2 registry rebinding."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-instrumented-production-handoff-r2.json";MANIFEST=ROOT/"production/comic/run-manifests/ch05-instrumented-production-manifest-r2.json";R1=ROOT/"production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json";REGISTRY=ROOT/"docs/research/model-license-registry.md"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});a=d.get("activity",{});out=[]
 if tuple(s.get(k) for k in ("row_count","sequence_count","distinct_panel_plans","accepted_rows","commercially_cleared_rows","lettering_ready_rows","executable_rows","generation_reproducible_rows","comic_panel_plan_revisions"))!=(14,3,14,0,0,0,0,0,0):out.append("row/promotion denominators invalid")
 if any(a.get(k)!=0 for k in ("rows_rewritten","prompts_rewritten","source_pixels_changed","provider_calls","uploads","cost_usd")):out.append("activity fabricated")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));m=json.loads(MANIFEST.read_text(encoding="utf-8"));r1=json.loads(R1.read_text(encoding="utf-8"));fail=errors(d)
 if d["manifest"]["sha256"]!=sha(MANIFEST) or d["extends"]["sha256"]!=sha(R1) or d["extends"]["row_root_sha256"]!=r1["row_root_sha256"]:fail.append("manifest/r1 binding invalid")
 if d["model_license_registry"]["sha256"]!=sha(REGISTRY) or m["model_license_registry"]["sha256"]!=sha(REGISTRY):fail.append("current registry binding invalid")
 if m["animation_shot_plan"] is not None or m["e_conte"] is not None:fail.append("planning boundary invalid")
 mutations=[lambda x:x["summary"].update(row_count=13),lambda x:x["summary"].update(sequence_count=2),lambda x:x["summary"].update(distinct_panel_plans=13),lambda x:x["summary"].update(accepted_rows=1),lambda x:x["summary"].update(commercially_cleared_rows=1),lambda x:x["summary"].update(lettering_ready_rows=1),lambda x:x["summary"].update(executable_rows=1),lambda x:x["summary"].update(generation_reproducible_rows=1),lambda x:x["summary"].update(comic_panel_plan_revisions=1),lambda x:x["activity"].update(rows_rewritten=1),lambda x:x["activity"].update(prompts_rewritten=1),lambda x:x["activity"].update(source_pixels_changed=1),lambda x:x["activity"].update(provider_calls=1),lambda x:x["activity"].update(uploads=1),lambda x:x["activity"].update(cost_usd=1)]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 instrumented manifest r2: {len(fail)} failures; 14 immutable rows/current registry/0 executable; {rejected}/{len(mutations)} mutations rejected")
 print("r1 row root exact; rows/prompts/pixels/calls/uploads/cost rewritten 0/0/0/0/0/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
