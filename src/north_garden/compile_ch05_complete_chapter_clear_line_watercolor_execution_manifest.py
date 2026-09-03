"""Compile completed built-in ImageGen executions for CH05 clear-line watercolor r1."""
from __future__ import annotations

import hashlib, json
from pathlib import Path
from typing import Any
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
PROMPTS=ROOT/"production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-prompt-manifest-r1.json"
OUTPUT=ROOT/"production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-execution-manifest-r1.json"
UNAVAILABLE=["model","endpoint","provider_request_id","usage","cost_usd","deterministic_seed"]
RUNS:dict[str,dict[str,Any]]={
"clear-line-watercolor-s01-opening-departure":{"id":"exec-57ef230f-cd1f-491c-990e-c1cb835a4e0c","sha":"0bf88d9e50846a486d1dace27883a78d32c98096a78daa76f29f8396d58807c5","w":841,"h":1870,"bytes":2717682,"batch":"cw01-single","elapsed":104.6,"wall":104.6},
"clear-line-watercolor-s02-runnel-marker-trail":{"id":"exec-ebe3566c-6244-47c6-adbd-d265b47e07c0","sha":"8d7501f600b9846e160d52d0d9bf5c6c9ce066b12a7870d19d4078204e79009e","w":842,"h":1868,"bytes":2866301,"batch":"cw02-parallel","elapsed":None,"wall":194.2},
"clear-line-watercolor-s03-listening-twine-ridge":{"id":"exec-331e252f-649b-40f1-9238-f0628f00a3be","sha":"4d95a014db3d93a92435e7f32cce5e2384403e438b0bed156fab8ffcbdc16ed3","w":841,"h":1870,"bytes":2492997,"batch":"cw02-parallel","elapsed":None,"wall":194.2},
"clear-line-watercolor-s04-mill-reveal-bridge-warning":{"id":"exec-f0e5d18c-7d7a-4c2c-ad0f-82f37a81cb06","sha":"b408e825e1817caf3fa7ec7a107a291c1d11df134c0e80a93db0068d8f25aa40","w":853,"h":1844,"bytes":2599940,"batch":"cw03-parallel","elapsed":None,"wall":199.6},
"clear-line-watercolor-s05-creek-marker-drum":{"id":"exec-e4802f80-a8c1-49c6-a487-8ab872504ad2","sha":"1b771011b1c4e53789b0054245588093591cec65fdc319f33374f7d8ebac426b","w":830,"h":1896,"bytes":2678083,"batch":"cw03-parallel","elapsed":None,"wall":199.6},
"clear-line-watercolor-s06-ember-line-entry":{"id":"exec-46e18e2f-018e-40b3-be53-8b9d77c269c8","sha":"181018c576f4b1007c1dc23a59fd514d10fff03eadbcebcfb3bad1df083c5971","w":795,"h":1979,"bytes":2648019,"batch":"cw04-parallel","elapsed":None,"wall":198.2},
"clear-line-watercolor-s07-impossible-footprints-bell":{"id":"exec-48ddab90-3b1a-4a43-bfbf-db18e56f6d89","sha":"f2c05a78c3d9c940327093ff3050d9023a903dcf7dddcbc2771cd58b5a73853d","w":854,"h":1842,"bytes":2672862,"batch":"cw04-parallel","elapsed":None,"wall":198.2},
"clear-line-watercolor-s08-plank-tin-map":{"id":"exec-a3bda5cd-c756-4c13-911d-fc147951fa46","sha":"e064583a5da8836333c6f7a5532dc79c70b4a514108a21c83bf5741d2150c7f6","w":852,"h":1847,"bytes":3018185,"batch":"cw05-parallel","elapsed":None,"wall":194.6},
"clear-line-watercolor-s09-deduction-retreat-cut":{"id":"exec-f786bdf3-e1b4-49dd-97f2-cf6deec77f47","sha":"b72e90691edda3fa826faec5c40cc9338f378b077227a7b8d208719ceb6c099f","w":831,"h":1891,"bytes":2589362,"batch":"cw05-parallel","elapsed":None,"wall":194.6},
"clear-line-watercolor-s10-silence-return":{"id":"exec-f83ff836-3ea5-4eb9-a3b9-545c860f1a50","sha":"7a88a7e14b4e60c08d187efc309edfc93589a46db6f35e9397052927f73d509c","w":853,"h":1843,"bytes":2524115,"batch":"cw06-parallel","elapsed":None,"wall":198.8},
"clear-line-watercolor-s11-farmhouse-reversal":{"id":"exec-641f4c4c-484b-49a8-a475-eb8039011a45","sha":"3a5afd2edd3fc7861a80e1cf35cac9d249840d5adf99c0bfd44a3b235d1ce3e1","w":853,"h":1843,"bytes":2704994,"batch":"cw06-parallel","elapsed":None,"wall":198.8}}
def sha256(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def main()->int:
 d=json.loads(PROMPTS.read_text(encoding="utf-8")); records=[]; batches={}
 for s in d["sequences"]:
  run=RUNS[s["sequence_id"]];p=ROOT/s["planned_output"]
  if not p.is_file() or sha256(p)!=run["sha"] or p.stat().st_size!=run["bytes"]:raise ValueError(f"output binding: {s['sequence_id']}")
  with Image.open(p) as image:
   if image.format!="PNG" or image.size!=(run["w"],run["h"]):raise ValueError(f"decode/dimensions: {s['sequence_id']}")
  batches.setdefault(run["batch"],run["wall"])
  records.append({"sequence_id":s["sequence_id"],"source_sequence_id":s["source_sequence_id"],"panel_range":s["panel_range"],"panel_count":s["panel_count"],"prompt_text":s["prompt_text"],"prompt_sha256":s["prompt_sha256"],"input_references":s["input_references"],"cross_panel_gate_phrases":s["cross_panel_gate_phrases"],"execution":{"tool_mode":"openai_builtin_imagegen_in_codex","tool_service_execution_id":run["id"],"tool_service_execution_id_is_provider_request_id":False,"timing_batch_id":run["batch"],"elapsed_seconds":run["elapsed"],"parallel_batch_wall_seconds":run["wall"],"model":None,"endpoint":None,"provider_request_id":None,"usage":None,"cost_usd":None,"deterministic_seed":None,"unavailable_fields":UNAVAILABLE},"output":{"path":s["planned_output"],"sha256":run["sha"],"width":run["w"],"height":run["h"],"bytes":run["bytes"]},"human_review_state":"PENDING","human_review_minutes":None,"accepted":False,"commercially_cleared":False,"exact_production_base":False,"generation_reproducible":False})
 doc={"record_type":"CH05CompleteChapterClearLineWatercolorExecutionManifest","schema_version":"1.0","record_id":"ng-ch05-complete-chapter-clear-line-watercolor-executions-r1","state":"EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW","medium":"comic","planning_structure":"ComicPanelPlan","animation_shot_plan":None,"e_conte":None,"input_prompt_manifest":{"path":PROMPTS.relative_to(ROOT).as_posix(),"sha256":sha256(PROMPTS)},"summary":{"sequence_outputs":11,"comic_panel_plans_requested":50,"authorized_reference_uses":23,"unique_timing_batches":6,"overlap_adjusted_tool_call_wall_seconds":round(sum(batches.values()),1),"timing_scope":"Codex ImageGen tool-call wall at 0.1-second precision; includes any queue, generation, and transfer time exposed to the caller.","per_output_elapsed_seconds_available":1,"direct_paid_provider_api_calls":0,"paid_spend_usd":0.0,"human_reviewed_outputs":0,"accepted_outputs":0,"commercially_cleared_outputs":0,"exact_production_base_outputs":0},"timing_batches":[{"timing_batch_id":k,"wall_seconds":v,"member_sequence_ids":[r["sequence_id"] for r in records if r["execution"]["timing_batch_id"]==k]} for k,v in batches.items()],"records":records,"limitations":["The built-in tool exposed no model, endpoint, provider request ID, usage, monetary cost, or deterministic seed.","Codex tool-service execution IDs are provenance aids only and are not provider request IDs.","Parallel execution exposes batch wall only; paired per-output elapsed time remains null.","Prompt-gate presence does not prove pixel compliance.","Outputs remain unaccepted and commercially uncleared."],"boundary":{"permitted_product":"openai_builtin_imagegen","direct_paid_provider_api_calls":0,"bfl_calls":0,"new_upload_classes":0,"real_person_or_child_material":0}}
 OUTPUT.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n");print(json.dumps({"output":OUTPUT.relative_to(ROOT).as_posix(),"sha256":sha256(OUTPUT),**doc["summary"]},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
