"""Compile deterministic crops for CH05 clear-line watercolor sequence strips."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from PIL import Image
from compile_ch05_complete_chapter_alt_graphic_crop_manifest import panel_boxes,SEPARATOR_DOMINANCE,SEPARATOR_JOIN_DISTANCE_PX,EDGE_CLUSTER_PX
ROOT=Path(__file__).resolve().parents[2];PLANS=ROOT/"production/comic/ch05-sc01-panel-plans-v1.json";EXECUTIONS=ROOT/"production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-execution-manifest-r1.json";OUTPUT=ROOT/"production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-crops-r1.json"
MANUAL_GUTTER_OVERRIDES={"clear-line-watercolor-s04-mill-reveal-bridge-warning":[[371,371],[718,718],[1077,1077],[1409,1413]]}
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 d=json.loads(EXECUTIONS.read_text(encoding="utf-8"));plans=sorted(json.loads(PLANS.read_text(encoding="utf-8"))["plans"],key=lambda x:x["display_order"]);ids=[x["panel_id"] for x in plans];seen=[];seqs=[]
 for r in d["records"]:
  start,end=r["panel_range"];panel_ids=ids[start-1:end];source=r["output"];path=ROOT/source["path"]
  if not path.is_file() or sha256(path)!=source["sha256"]:raise ValueError(f"source binding {r['sequence_id']}")
  with Image.open(path) as im:
   image=im.convert("RGB")
   if r["sequence_id"] in MANUAL_GUTTER_OVERRIDES:
    gutters=MANUAL_GUTTER_OVERRIDES[r["sequence_id"]];top=0;boxes=[]
    for start_gutter,end_gutter in gutters:boxes.append([0,top,image.width,start_gutter]);top=end_gutter+1
    boxes.append([0,top,image.width,image.height])
   else:boxes,gutters=panel_boxes(image,r["panel_count"])
  seen+=panel_ids;seqs.append({"sequence_id":r["source_sequence_id"],"execution_sequence_id":r["sequence_id"],"source":source,"gutter_detection":{"mode":"hash_pinned_manual_override" if r["sequence_id"] in MANUAL_GUTTER_OVERRIDES else "row_dominance","dominance_threshold":SEPARATOR_DOMINANCE,"join_distance_px":SEPARATOR_JOIN_DISTANCE_PX,"edge_cluster_px":EDGE_CLUSTER_PX,"detected_internal_gutter_extents_inclusive":gutters},"crops":[{"panel_id":pid,"box":box} for pid,box in zip(panel_ids,boxes,strict=True)]})
 if seen!=ids:raise ValueError("canonical crop coverage")
 doc={"record_type":"CH05SequenceStripCropManifest","schema_version":"1.0","record_id":"ng-ch05-complete-chapter-clear-line-watercolor-crops-r1","state":"HASH_PINNED_LOCAL_DERIVATIVE_PLAN_UNACCEPTED","medium":"comic","planning_structure":"ComicPanelPlan","animation_shot_plan":None,"e_conte":None,"comic_panel_plan_source":{"path":PLANS.relative_to(ROOT).as_posix(),"sha256":sha256(PLANS)},"execution_manifest":{"path":EXECUTIONS.relative_to(ROOT).as_posix(),"sha256":sha256(EXECUTIONS)},"output_filename_template":"p{panel_number:03d}-clear-line-watercolor-r1.png","summary":{"sequence_sources":11,"planned_crops":50,"complete_plan_coverage":True,"deterministic_gutter_detection":True},"sequences":seqs,"boundary":"Exact source strips and crops remain ignored local research pixels; no acceptance, clearance, or exact-base selection."}
 OUTPUT.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n");print(json.dumps({"output":OUTPUT.relative_to(ROOT).as_posix(),"sha256":sha256(OUTPUT),**doc["summary"]},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
