"""Validate complete CH05 clear-line watercolor execution evidence."""
from __future__ import annotations
import argparse,copy,hashlib,json,subprocess
from pathlib import Path
from typing import Any
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];MANIFEST=ROOT/"production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-execution-manifest-r1.json"
PROMPTS=ROOT/"production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-prompt-manifest-r1.json"
UNAVAILABLE=["model","endpoint","provider_request_id","usage","cost_usd","deterministic_seed"]
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(d:dict[str,Any],verify_files=True)->list[str]:
 e=[];c=lambda x,m:None if x else e.append(m);rows=d.get("records",[]);prompts=json.loads(PROMPTS.read_text(encoding="utf-8"))["sequences"]
 c(d.get("record_type")=="CH05CompleteChapterClearLineWatercolorExecutionManifest","record_type");c(d.get("state")=="EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW","state");c(d.get("planning_structure")=="ComicPanelPlan" and d.get("animation_shot_plan") is None and d.get("e_conte") is None,"planning boundary")
 c(len(rows)==11 and len({r.get("execution",{}).get("tool_service_execution_id") for r in rows})==11,"records/ids");c([n for r in rows for n in range(r["panel_range"][0],r["panel_range"][1]+1)]==list(range(1,51)),"coverage");c([len(r.get("input_references",[])) for r in rows]==[2,2,2,2,2,2,2,3,2,2,2],"reference distribution");c(sum(len(r.get("cross_panel_gate_phrases",[])) for r in rows)==15,"gate bindings")
 for r,prompt in zip(rows,prompts):
  for k in ("sequence_id","source_sequence_id","panel_range","panel_count","prompt_text","prompt_sha256","input_references","cross_panel_gate_phrases"):c(r.get(k)==prompt.get(k),f"prompt parity {r.get('sequence_id')}:{k}")
  c(r.get("output",{}).get("path")==prompt.get("planned_output"),f"output parity {r.get('sequence_id')}");x=r.get("execution",{});c(x.get("unavailable_fields")==UNAVAILABLE and all(x.get(k) is None for k in UNAVAILABLE),f"unavailable {r.get('sequence_id')}");c(x.get("tool_service_execution_id_is_provider_request_id") is False,f"id distinction {r.get('sequence_id')}");c(r.get("human_review_state")=="PENDING" and r.get("human_review_minutes") is None and all(r.get(k) is False for k in ("accepted","commercially_cleared","exact_production_base","generation_reproducible")),f"review boundary {r.get('sequence_id')}")
  if verify_files:
   o=r["output"];path=ROOT/o["path"];c(path.is_file() and sha256(path)==o["sha256"] and path.stat().st_size==o["bytes"],f"output binding {r.get('sequence_id')}")
   if path.is_file():
    with Image.open(path) as im:c(im.format=="PNG" and [im.width,im.height]==[o["width"],o["height"]],f"decode {r.get('sequence_id')}")
    c(subprocess.run(["git","check-ignore","--quiet","--",o["path"]],cwd=ROOT).returncode==0,f"ignored {r.get('sequence_id')}")
 s=d.get("summary",{});c((s.get("sequence_outputs"),s.get("comic_panel_plans_requested"),s.get("authorized_reference_uses"),s.get("unique_timing_batches"),s.get("overlap_adjusted_tool_call_wall_seconds"),s.get("per_output_elapsed_seconds_available"))==(11,50,23,6,1090.0,1),"summary");c(s.get("paid_spend_usd")==0.0 and s.get("direct_paid_provider_api_calls")==0,"spend")
 batches=d.get("timing_batches",[]);c(len(batches)==6 and round(sum(b["wall_seconds"] for b in batches),1)==1090.0 and [len(b["member_sequence_ids"]) for b in batches]==[1,2,2,2,2,2],"timing partition");c([r["execution"]["elapsed_seconds"] for r in rows]==[104.6]+[None]*10,"individual timing")
 c(d.get("boundary")=={"permitted_product":"openai_builtin_imagegen","direct_paid_provider_api_calls":0,"bfl_calls":0,"new_upload_classes":0,"real_person_or_child_material":0},"boundary")
 return e
def self_test(d):
 muts=[lambda x:x.__setitem__("state","ACCEPTED"),lambda x:x.__setitem__("planning_structure","AnimationShotPlan"),lambda x:x["records"].pop(),lambda x:x["records"][0].__setitem__("prompt_text","bad"),lambda x:x["records"][0]["execution"].__setitem__("model","invented"),lambda x:x["records"][0].__setitem__("accepted",True),lambda x:x["summary"].__setitem__("overlap_adjusted_tool_call_wall_seconds",1),lambda x:x["summary"].__setitem__("paid_spend_usd",1),lambda x:x["timing_batches"].pop(),lambda x:x["boundary"].__setitem__("bfl_calls",1)];n=0
 for m in muts:q=copy.deepcopy(d);m(q);n+=bool(validate(q,False))
 return n,len(muts)
def main():
 p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");a=p.parse_args();d=json.loads(MANIFEST.read_text(encoding="utf-8"));e=validate(d);n=t=0
 if a.self_test:n,t=self_test(d);e+=[] if n==t else [f"self-test {n}/{t}"]
 print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,"records":len(d.get("records",[])),"self_test":f"{n}/{t}" if a.self_test else None},sort_keys=True));return 0 if not e else 1
if __name__=="__main__":raise SystemExit(main())
