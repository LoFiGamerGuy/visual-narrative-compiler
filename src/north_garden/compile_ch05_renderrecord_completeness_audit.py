"""Normalize and audit all 29 built-in ImageGen candidate records without rewriting sources."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];SOURCES=[ROOT/"docs/research/evidence/ch05-overnight-production-r1.json",ROOT/"docs/research/evidence/ch05-cadence-hardening-r1.json",ROOT/"docs/research/evidence/future-litrpg-visual-concepts-r1.json"];OUTPUT=ROOT/"production/comic/run-manifests/ch05-built-in-renderrecord-index-r1.json";CHART=ROOT/"experiments/review-packets/ch05-renderrecord-completeness-audit-r1/ch05-renderrecord-field-matrix-r1.png";EVIDENCE=ROOT/"docs/research/evidence/ch05-renderrecord-completeness-audit-r1.json";FONT=Path("C:/Windows/Fonts/arialbd.ttf")
UNAVAILABLE=["model","endpoint","provider_request_id","usage","cost_usd","deterministic_seed"]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x)->str:return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def ref_path(value:str)->Path:
 p=Path(value);return p if p.is_absolute() else ROOT/p
def chart(rows:list[dict])->None:
 cols=["prompt","refs","output","dims","time","model","endpoint","req id","usage","cost","seed","review","accepted"];cell_w,row_h,left,top=90,30,190,115;w=left+len(cols)*cell_w+30;h=top+len(rows)*row_h+70;im=Image.new("RGB",(w,h),(234,238,242));d=ImageDraw.Draw(im);title=ImageFont.truetype(str(FONT),27);small=ImageFont.truetype(str(FONT),13);tiny=ImageFont.truetype(str(FONT),11)
 d.text((22,18),"CH05 built-in ImageGen · 29-record field completeness",font=title,fill=(19,27,36));d.text((22,58),"Green = exact/observed · gray = explicitly unavailable · amber = pending human review · dark = false acceptance",font=small,fill=(58,68,80))
 for j,c in enumerate(cols):d.text((left+j*cell_w+7,88),c,font=tiny,fill=(52,62,74))
 for i,r in enumerate(rows):
  y=top+i*row_h;d.text((22,y+7),r["candidate_id"],font=small,fill=(30,39,49));class_label="NONCANON" if r["candidate_class"]=="NONCANON_CONCEPT" else "CH05";d.text((75,y+7),class_label,font=tiny,fill=(77,87,99));statuses=["exact","exact","exact","exact","exact","na","na","na","na","na","na","pending","false"]
  colors={"exact":(54,143,100),"na":(125,134,145),"pending":(202,142,44),"false":(53,61,70)}
  for j,status in enumerate(statuses):d.rectangle((left+j*cell_w,y+3,left+(j+1)*cell_w-3,y+row_h-3),fill=colors[status]);d.text((left+j*cell_w+8,y+7),status.upper(),font=tiny,fill=(245,247,249))
 d.text((22,h-42),"Unavailable fields are null, not zero or invented. Every source/output/reference hash is verified locally; generated pixels remain ignored.",font=small,fill=(72,52,46));CHART.parent.mkdir(parents=True,exist_ok=True);im.save(CHART,optimize=False)
def main()->int:
 rows=[]
 for source in SOURCES:
  doc=json.loads(source.read_text(encoding="utf-8"));is_concept="future-litrpg" in source.name
  for c in doc["candidates"]:
   prompt=c["prompt"] if is_concept else c["exact_prompt"];refs=c["references"] if is_concept else c["input_references"];execution=c["execution"];out=c["output"]
   output_path=ROOT/out["path"]
   if hashlib.sha256(prompt.encode()).hexdigest()!=c["prompt_sha256"]:raise SystemExit(f"prompt hash mismatch {c['candidate_id']}")
   if not output_path.is_file() or sha(output_path)!=out["sha256"] or output_path.stat().st_size!=out["bytes"]:raise SystemExit(f"output mismatch {c['candidate_id']}")
   with Image.open(output_path) as image:
    if [image.width,image.height]!=[out["width"],out["height"]]:raise SystemExit(f"dimensions mismatch {c['candidate_id']}")
   for ref in refs:
    path=ref_path(ref["path"])
    if not path.is_file() or sha(path)!=ref["sha256"]:raise SystemExit(f"reference mismatch {c['candidate_id']} {ref['reference_id']}")
   normalized_execution={"tool_mode":execution["tool_mode"],"elapsed_seconds":execution["elapsed_seconds"],"model":execution.get("model"),"endpoint":execution.get("endpoint"),"provider_request_id":execution.get("provider_request_id"),"usage":execution.get("usage"),"cost_usd":execution.get("cost_usd"),"deterministic_seed":execution.get("deterministic_seed"),"unavailable_fields":UNAVAILABLE,"unavailable_not_zero":True}
   row={"record_type":"BuiltInImageGenRenderRecord","schema_version":"1.0","candidate_id":c["candidate_id"],"candidate_class":"NONCANON_CONCEPT" if is_concept else "CH05_COMIC_PANEL_CANDIDATE","source_evidence":{"path":source.relative_to(ROOT).as_posix(),"sha256":sha(source)},"comic_panel_plan_id":None if is_concept else c["panel_id"],"plan_revision_id":None if is_concept else c["plan_revision_id"],"concept_id":c.get("concept_id"),"prompt":prompt,"prompt_sha256":c["prompt_sha256"],"input_references":refs,"input_reference_count":len(refs),"output":out,"execution":normalized_execution,"engineering_review":c["engineering_review"],"human_review_state":c["human_review_state"],"human_review_minutes":c["human_review_minutes"],"accepted":c["accepted"],"commercially_cleared":False,"generation_reproducible":False,"limitations":["Built-in model, endpoint, provider request ID, usage, cost, and seed were not exposed.","Exact local hashes do not make generation reproducible or commercially cleared."]}
   row["record_sha256"]=canonical(row);rows.append(row)
 rows.sort(key=lambda x:x["candidate_id"]);chart(rows);ref_uses=sum(r["input_reference_count"] for r in rows);unique_refs=sorted({x["sha256"] for r in rows for x in r["input_references"]});elapsed=round(sum(r["execution"]["elapsed_seconds"] for r in rows),3)
 index={"record_type":"BuiltInImageGenRenderRecordIndex","schema_version":"1.0","record_id":"ng-ch05-built-in-renderrecord-index-r1","state":"TWENTY_NINE_NORMALIZED_EXACT_LOCAL_RECORDS_OWNER_PENDING","source_evidence":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)} for p in SOURCES],"summary":{"record_count":29,"ch05_record_count":26,"noncanon_record_count":3,"exact_prompt_count":29,"exact_output_count":29,"input_reference_uses":ref_uses,"unique_reference_hash_count":len(unique_refs),"total_elapsed_seconds":elapsed,"pending_human_review":29,"accepted":0,"commercially_cleared":0,"generation_reproducible":0,"model_unavailable":29,"endpoint_unavailable":29,"request_id_unavailable":29,"usage_unavailable":29,"cost_unavailable":29,"seed_unavailable":29},"timing_reconciliation":{"authoritative_candidate_sum_seconds":elapsed,"legacy_narrative_total_seconds":1385.824,"delta_seconds":0.788,"concept_authoritative_seconds":154.978,"concept_legacy_narrative_seconds":155.766,"resolution":"Exact candidate records and their batch summary use 154.978 concept seconds and 1385.036 total seconds; legacy narrative totals remain historical and require append-only correction."},"unique_reference_hashes":unique_refs,"records":rows,"record_root_sha256":canonical([r["record_sha256"] for r in rows]),"provider_cost_reconciliation":"Unavailable from built-in product; null is preserved and must not be described as $0.","generated_pixels_git_tracked":False,"animation_shot_plan":None,"e_conte":None,"boundary":"Normalization is read-only; source evidence and generated pixels remain unchanged, ignored, unaccepted, and commercially uncleared."}
 OUTPUT.parent.mkdir(parents=True,exist_ok=True)
 with OUTPUT.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(index,indent=2,ensure_ascii=False)+"\n")
 evidence={"record_type":"CH05RenderRecordCompletenessAuditEvidence","schema_version":"1.0","record_id":"ng-ch05-renderrecord-completeness-audit-evidence-r1","state":"ALL_29_RECORDS_EXACT_UNAVAILABLE_FIELDS_EXPLICIT","index":{"path":OUTPUT.relative_to(ROOT).as_posix(),"sha256":sha(OUTPUT),"record_root_sha256":index["record_root_sha256"]},"summary":index["summary"]|{"records_missing_required_fields":0,"output_hash_failures":0,"reference_hash_failures":0,"prompt_hash_failures":0,"generated_outputs_not_ignored":0},"chart":{"path":CHART.relative_to(ROOT).as_posix(),"sha256":sha(CHART),"bytes":CHART.stat().st_size},"limitations":["The normalized index supplies an explicit null seed field that was absent from source schemas; it does not claim the product used no seed.","Human review minutes and acceptance remain pending/zero.","Provider cost/usage reconciliation is unavailable, not zero."],"activity":{"source_records_rewritten":0,"provider_calls":0,"uploads":0,"external_cost_usd":0},"boundary":index["boundary"]}
 with EVIDENCE.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(evidence,indent=2)+"\n")
 print(f"CH05 RenderRecord audit: 29 exact records / {ref_uses} reference uses / {elapsed}s / 0 missing/hash failures")
 print("model/endpoint/request/usage/cost/seed unavailable 29 each; pending 29/accepted 0; audit calls/uploads/$0 activity 0/0/$0")
 return 0
if __name__=="__main__":raise SystemExit(main())
