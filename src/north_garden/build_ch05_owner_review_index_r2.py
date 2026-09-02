"""Build an append-only local CH05 owner review hub over r1 and post-r1 evidence."""
from __future__ import annotations
import hashlib,html,json,os
from pathlib import Path
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[2]
R1_PACKET=ROOT/"experiments/review-packets/ch05-owner-review-index-r1/owner-review-index-packet.json";DECISION_PACKET=ROOT/"experiments/review-packets/ch05-owner-decision-worksheet-r1/decision-worksheet-packet.json"
CONTRACT=ROOT/"production/comic/review/ch05-owner-decision-contract-r1.json";OUT=ROOT/"experiments/review-packets/ch05-owner-review-index-r2";INDEX=OUT/"index.html";PACKET=OUT/"owner-review-index-r2-packet.json"
LINKS=[
 {"id":"art_index_r1","title":"All 29 candidates + original packets","kind":"HTML","path":"experiments/review-packets/ch05-owner-review-index-r1/index.html","summary":"Original immutable art hub: 26 CH05 candidates, three non-canon LitRPG concepts, selected sequences, lettering, and density."},
 {"id":"decision_worksheet","title":"39-subject owner decision worksheet","kind":"HTML","path":"experiments/review-packets/ch05-owner-decision-worksheet-r1/index.html","summary":"Offline selections export an uningested draft only; contract remains empty."},
 {"id":"continuity_all","title":"Continuity atlas · all 26 CH05 candidates","kind":"IMAGE","path":"experiments/review-packets/ch05-manual-continuity-atlas-r1/ch05-continuity-atlas-all-26-r1.png","summary":"Alternates grouped by 14 exact plans; compare hair, wardrobe, role staging, anatomy, causality, and lettering."},
 {"id":"continuity_selected","title":"Continuity atlas · selected 14 sequence","kind":"IMAGE","path":"experiments/review-packets/ch05-manual-continuity-atlas-r1/ch05-continuity-atlas-selected-14-r1.png","summary":"Narrative-order full-panel comparison with manual checklists."},
 {"id":"scale_cadence","title":"50-plan conditional scale/cadence map","kind":"IMAGE","path":"experiments/review-packets/ch05-panel-scale-cadence-policy-r1/ch05-panel-scale-cadence-map-r1.png","summary":"Nine role-aware width bands from 520–1200px; ranges are recommendations, not accepted layouts."},
 {"id":"repair_paths","title":"Exact targeted repair paths","kind":"IMAGE","path":"experiments/review-packets/ch05-failure-class-repair-matrix-r1/ch05-targeted-repair-paths-r1.png","summary":"Six retained interventions: five target fixes, four all-dimension passes; literal object/role wording beats lever shorthand."},
 {"id":"next_preflight","title":"P010–P013 zero-prompt preflight storyboard","kind":"IMAGE","path":"experiments/review-packets/ch05-p010-p013-preflight-contract-r1/ch05-p010-p013-preflight-storyboard-r1.png","summary":"Four adjacent trail/twine hypotheses and two unallocated repair slots; no prompt or execution authority."},
]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p:Path)->str:return Path(os.path.relpath(p,OUT)).as_posix()
def main()->int:
 OUT.mkdir(parents=True,exist_ok=True);thumbs=OUT/"thumbnails";thumbs.mkdir(exist_ok=True);items=[]
 for item in LINKS:
  source=ROOT/item["path"]
  if not source.is_file():raise SystemExit(f"missing review link {source}")
  row={**item,"sha256":sha(source),"href":rel(source),"thumbnail_path":None,"thumbnail_sha256":None}
  if item["kind"]=="IMAGE":
   with Image.open(source) as opened:thumb=ImageOps.contain(opened.convert("RGB"),(600,350),Image.Resampling.LANCZOS)
   canvas=Image.new("RGB",(620,370),(26,32,40));canvas.paste(thumb,((620-thumb.width)//2,(370-thumb.height)//2));target=thumbs/f"{item['id']}.png";canvas.save(target,optimize=False);row["thumbnail_path"]=target.relative_to(ROOT).as_posix();row["thumbnail_sha256"]=sha(target);row["thumbnail_href"]=rel(target)
  items.append(row)
 cards=[]
 for row in items:
  visual=f'<img src="{html.escape(row.get("thumbnail_href",""))}" alt="{html.escape(row["title"])}">' if row["kind"]=="IMAGE" else '<div class="html-card">LOCAL HTML</div>'
  cards.append(f'<article><a href="{html.escape(row["href"])}">{visual}<h2>{html.escape(row["title"])}</h2></a><p>{html.escape(row["summary"])}</p><code>{row["sha256"]}</code></article>')
 page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CH05 owner review index r2</title><style>body{margin:0;background:#10151c;color:#edf1f5;font:15px/1.45 system-ui,sans-serif}header,main,footer{max-width:1440px;margin:auto;padding:26px}header{background:#18202a;border-bottom:1px solid #33404f}h1{margin:0 0 10px}.boundary{color:#ffd18a}.stats{display:flex;gap:12px;flex-wrap:wrap}.stats span{background:#253140;border-radius:8px;padding:8px 12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px}article{background:#19222d;border:1px solid #33404f;border-radius:12px;padding:14px;overflow:hidden}article img,.html-card{width:100%;height:220px;object-fit:contain;background:#0e1319;border-radius:8px}.html-card{display:grid;place-items:center;color:#8ecbff;font-size:28px;font-weight:800}a{color:#91ceff;text-decoration:none}code{display:block;color:#8794a3;font-size:10px;overflow-wrap:anywhere}footer{color:#97a2af}</style></head><body><header><h1>North Garden CH05 · owner review index r2</h1><p class="boundary">Local-only review surface. All art remains unaccepted, commercially uncleared, ignored by Git, and nonexecutable.</p><div class="stats"><span>29 candidates</span><span>14 selected</span><span>39 pending decisions</span><span>50 ComicPanelPlans</span><span>0 accepted</span></div></header><main><div class="grid">'''+''.join(cards)+'''</div></main><footer>R2 extends immutable r1 · no remote assets · no network code · no upload · no recorded owner decision</footer></body></html>'''
 with INDEX.open("w",encoding="utf-8",newline="\n") as h:h.write(page)
 contract=json.loads(CONTRACT.read_text(encoding="utf-8"));r1=json.loads(R1_PACKET.read_text(encoding="utf-8"));decision=json.loads(DECISION_PACKET.read_text(encoding="utf-8"))
 artifacts=[{"path":INDEX.relative_to(ROOT).as_posix(),"sha256":sha(INDEX),"bytes":INDEX.stat().st_size}]+[{"path":r["thumbnail_path"],"sha256":r["thumbnail_sha256"],"bytes":(ROOT/r["thumbnail_path"]).stat().st_size} for r in items if r["thumbnail_path"]]
 packet={"record_type":"CH05OwnerReviewIndexPacket","schema_version":"2.0","record_id":"ng-ch05-owner-review-index-r2","state":"LOCAL_REVIEW_HUB_EXTENDS_R1_OWNER_PENDING","supersedes":None,"extends":{"path":R1_PACKET.relative_to(ROOT).as_posix(),"sha256":sha(R1_PACKET),"candidate_count":r1["candidate_count"],"selected_candidate_count":r1["selected_candidate_count"]},"decision_worksheet":{"path":DECISION_PACKET.relative_to(ROOT).as_posix(),"sha256":sha(DECISION_PACKET),"subject_count":decision["subject_count"]},"contract":{"path":CONTRACT.relative_to(ROOT).as_posix(),"sha256":sha(CONTRACT),"completed_decisions":contract["summary"]["completed_decisions"],"events":contract["summary"]["events"],"human_review_minutes":contract["summary"]["human_review_minutes"]},"link_count":len(items),"image_link_count":sum(r["kind"]=="IMAGE" for r in items),"html_link_count":sum(r["kind"]=="HTML" for r in items),"links":items,"artifact_count":len(artifacts),"artifacts":artifacts,"index":{"path":INDEX.relative_to(ROOT).as_posix(),"sha256":sha(INDEX),"bytes":INDEX.stat().st_size},"owner_decisions":0,"accepted_candidates":0,"provider_calls":0,"uploads":0,"cost_usd":0,"boundary":"Append-only local review hub; r1 and the empty decision contract remain unchanged."}
 with PACKET.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(packet,indent=2)+"\n")
 print(f"CH05 owner review index r2: {len(items)} links / {len(artifacts)} artifacts / 29 candidates / 39 pending decisions")
 print(f"index {sha(INDEX)} packet {sha(PACKET)}; decisions/accepted/calls/uploads/cost 0/0/0/0/$0")
 return 0
if __name__=="__main__":raise SystemExit(main())
