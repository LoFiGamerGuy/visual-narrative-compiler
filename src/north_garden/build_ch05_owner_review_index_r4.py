"""Build append-only local CH05 owner review hub r4 over r3 and chapter maps."""
from __future__ import annotations
import hashlib,html,json,os
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[2];R3=ROOT/"experiments/review-packets/ch05-owner-review-index-r3/owner-review-index-r3-packet.json";CONTRACT=ROOT/"production/comic/review/ch05-owner-decision-contract-r1.json";OUT=ROOT/"experiments/review-packets/ch05-owner-review-index-r4";INDEX=OUT/"index.html";PACKET=OUT/"owner-review-index-r4-packet.json"
LINKS=[
 ("index_r3","Prior owner hub r3","HTML","experiments/review-packets/ch05-owner-review-index-r3/index.html","All earlier art, cadence, lettering, continuity, repair, envelope, and RenderRecord review links."),
 ("owner_checklist","Dependency-ordered 24-task owner checklist","TEXT","docs/research/ch05-owner-handoff-checklist-r1.md","Candidate, route, density, lettering, P010, non-canon, and authority review in prerequisite order."),
 ("readiness","50-plan production readiness","IMAGE","experiments/review-packets/ch05-chapter-production-readiness-r1/ch05-chapter-readiness-map-r1.png","Selected evidence, P010–P013 dry run, Tier A, and backlog with exact blockers."),
 ("reference_risk","50-plan hair/wardrobe/reference risk","IMAGE","experiments/review-packets/ch05-reference-use-continuity-risk-r1/ch05-reference-risk-map-r1.png","Minimal reference hypotheses, text-only rows, extra-person risks, and critical P036 guard."),
 ("sequence_batches","12 coherent chapter production batches","IMAGE","experiments/review-packets/ch05-chapter-sequence-production-batches-r1/ch05-sequence-batch-map-r1.png","All 50 plans in contiguous 3–5-panel sequences and four readiness waves."),
 ("lettering_semantics","50-plan lettering semantics readiness","IMAGE","experiments/review-packets/ch05-lettering-semantics-readiness-r1/ch05-lettering-semantics-map-r1.png","Silence, protected action, caption, reaction/speech, and P016 attributed-copy classes."),
]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p:Path)->str:return Path(os.path.relpath(p,OUT)).as_posix()
def main()->int:
 OUT.mkdir(parents=True,exist_ok=True);thumbs=OUT/"thumbnails";thumbs.mkdir(exist_ok=True);items=[]
 for item_id,title,kind,path_text,summary in LINKS:
  source=ROOT/path_text
  if not source.is_file():raise SystemExit(f"missing review link {source}")
  row={"id":item_id,"title":title,"kind":kind,"path":path_text,"sha256":sha(source),"href":rel(source),"summary":summary,"thumbnail_path":None,"thumbnail_sha256":None}
  if kind=="IMAGE":
   with Image.open(source) as opened:thumb=ImageOps.contain(opened.convert("RGB"),(600,350),Image.Resampling.LANCZOS)
   canvas=Image.new("RGB",(620,370),(26,32,40));canvas.paste(thumb,((620-thumb.width)//2,(370-thumb.height)//2));target=thumbs/f"{item_id}.png";canvas.save(target,optimize=False);row["thumbnail_path"]=target.relative_to(ROOT).as_posix();row["thumbnail_sha256"]=sha(target);row["thumbnail_href"]=rel(target)
  items.append(row)
 cards=[]
 for row in items:
  visual=f'<img src="{html.escape(row.get("thumbnail_href",""))}" alt="{html.escape(row["title"])}">' if row["kind"]=="IMAGE" else f'<div class="html-card">LOCAL {row["kind"]}</div>'
  cards.append(f'<article><a href="{html.escape(row["href"])}">{visual}<h2>{html.escape(row["title"])}</h2></a><p>{html.escape(row["summary"])}</p><code>{row["sha256"]}</code></article>')
 page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CH05 owner review index r4</title><style>body{margin:0;background:#10151c;color:#edf1f5;font:15px/1.45 system-ui,sans-serif}header,main,footer{max-width:1440px;margin:auto;padding:26px}header{background:#18202a;border-bottom:1px solid #33404f}h1{margin:0 0 10px}.boundary{color:#ffd18a}.stats{display:flex;gap:12px;flex-wrap:wrap}.stats span{background:#253140;border-radius:8px;padding:8px 12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px}article{background:#19222d;border:1px solid #33404f;border-radius:12px;padding:14px;overflow:hidden}article img,.html-card{width:100%;height:220px;object-fit:contain;background:#0e1319;border-radius:8px}.html-card{display:grid;place-items:center;color:#8ecbff;font-size:28px;font-weight:800}a{color:#91ceff;text-decoration:none}code{display:block;color:#8794a3;font-size:10px;overflow-wrap:anywhere}footer{color:#97a2af}</style></head><body><header><h1>North Garden CH05 · owner review index r4</h1><p class="boundary">Local-only review surface. All art remains unaccepted, commercially uncleared, ignored by Git, and nonexecutable.</p><div class="stats"><span>29 candidates</span><span>50 plans</span><span>12 batches</span><span>24 review tasks</span><span>42 release checks</span><span>0 accepted</span></div></header><main><div class="grid">'''+''.join(cards)+'''</div></main><footer>R4 extends immutable r3 · no remote assets · no network code · no upload · no recorded owner decision</footer></body></html>'''
 INDEX.write_text(page,encoding="utf-8",newline="\n");r3=json.loads(R3.read_text(encoding="utf-8"));contract=json.loads(CONTRACT.read_text(encoding="utf-8"));artifacts=[{"path":INDEX.relative_to(ROOT).as_posix(),"sha256":sha(INDEX),"bytes":INDEX.stat().st_size}]+[{"path":r["thumbnail_path"],"sha256":r["thumbnail_sha256"],"bytes":(ROOT/r["thumbnail_path"]).stat().st_size} for r in items if r["thumbnail_path"]]
 packet={"record_type":"CH05OwnerReviewIndexPacket","schema_version":"4.0","record_id":"ng-ch05-owner-review-index-r4","state":"LOCAL_CHAPTER_REVIEW_HUB_EXTENDS_R3_OWNER_PENDING","extends":{"path":R3.relative_to(ROOT).as_posix(),"sha256":sha(R3),"link_count":r3["link_count"]},"contract":{"path":CONTRACT.relative_to(ROOT).as_posix(),"sha256":sha(CONTRACT),"completed_decisions":contract["summary"]["completed_decisions"],"events":contract["summary"]["events"],"human_review_minutes":contract["summary"]["human_review_minutes"]},"link_count":len(items),"image_link_count":sum(r["kind"]=="IMAGE" for r in items),"html_link_count":sum(r["kind"]=="HTML" for r in items),"text_link_count":sum(r["kind"]=="TEXT" for r in items),"links":items,"artifact_count":len(artifacts),"artifacts":artifacts,"index":{"path":INDEX.relative_to(ROOT).as_posix(),"sha256":sha(INDEX),"bytes":INDEX.stat().st_size},"owner_decisions":0,"accepted_candidates":0,"provider_calls":0,"uploads":0,"cost_usd":0,"boundary":"Append-only local chapter hub; r3 and empty decision contract remain unchanged."}
 PACKET.write_text(json.dumps(packet,indent=2)+"\n",encoding="utf-8",newline="\n");print(f"CH05 owner review index r4: {len(items)} links / {len(artifacts)} artifacts / 50 plans / 24 tasks");print(f"index {sha(INDEX)} packet {sha(PACKET)}; decisions/accepted/calls/uploads/cost 0/0/0/0/$0");return 0
if __name__=="__main__":raise SystemExit(main())
