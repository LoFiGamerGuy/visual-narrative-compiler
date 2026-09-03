"""Build deterministic full-chapter comparison of r6, alternate graphic, and clear-line watercolor."""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
from typing import Any
from PIL import Image,ImageDraw,ImageFont,ImageOps
from build_ch05_r6_alt_graphic_comparison import metric
ROOT=Path(__file__).resolve().parents[2]
ASSEMBLIES={"r6":ROOT/"production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json","alt_graphic":ROOT/"production/comic/run-manifests/ch05-complete-chapter-alt-graphic-assembly-r1.json","clear_line_watercolor":ROOT/"production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-assembly-r1.json"}
TRIAGES={"r6":ROOT/"docs/research/evidence/ch05-complete-chapter-agent-triage-r6.json","alt_graphic":ROOT/"docs/research/evidence/ch05-complete-chapter-alt-graphic-agent-triage-r1.json","clear_line_watercolor":ROOT/"docs/research/evidence/ch05-complete-chapter-clear-line-watercolor-agent-triage-r1.json"}
PHONES={"r6":ROOT/"experiments/review-packets/ch05-complete-chapter-draft-r6/lettered/ch05-complete-chapter-lettered-phone-390px-r1.png","alt_graphic":ROOT/"experiments/review-packets/ch05-complete-chapter-alt-graphic-r1/lettered/ch05-complete-chapter-alt-graphic-lettered-r1-phone-390px.png","clear_line_watercolor":ROOT/"experiments/review-packets/ch05-complete-chapter-clear-line-watercolor-r1/lettered/ch05-complete-chapter-clear-line-watercolor-lettered-r1-phone-390px.png"}
OUT=ROOT/"experiments/review-packets/ch05-three-route-comparison-r1";EVIDENCE=ROOT/"docs/research/evidence/ch05-three-route-comparison-r1.json";ANCHORS=[1,29,32,36,39,41,43,48,50]
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):
 try:return ImageFont.truetype("DejaVuSans-Bold.ttf" if b else "DejaVuSans.ttf",n)
 except OSError:return ImageFont.load_default(size=n)
def load(entry):
 p=ROOT/entry["source"]["path"]
 if sha256(p)!=entry["source"]["sha256"]:raise ValueError("source hash")
 with Image.open(p) as im:return im.convert("RGB")
def art(p):
 with Image.open(p) as im:w,h=im.size
 return {"path":p.relative_to(ROOT).as_posix(),"sha256":sha256(p),"width":w,"height":h,"bytes":p.stat().st_size,"repository_state":"IGNORED_LOCAL_REVIEW_ARTIFACT"}
def full_sheet(entries,status,path):
 cols,tw,th,gap,margin,head=4,430,230,12,20,86;canvas=Image.new("RGB",(margin*2+cols*tw+(cols-1)*gap,head+margin+math.ceil(50/cols)*th+12*gap),"#e8e4da");d=ImageDraw.Draw(canvas);d.text((margin,14),"CH05 THREE COMPLETE-CHAPTER ROUTES - ALL 50",fill="#20252a",font=font(28,True));d.text((margin,50),"R6 | alternate graphic | clear-line watercolor; R6 FAIL* is supplemental cross-panel audit",fill="#3d464e",font=font(16))
 for i in range(50):
  x=margin+(i%cols)*(tw+gap);y=head+(i//cols)*(th+gap);d.rectangle((x,y,x+tw,y+th),fill="#faf8f2",outline="#65717a",width=2);d.text((x+8,y+6),f"P{i+1:03d}  R6 / ALT / CLW",fill="#303940",font=font(14,True))
  for j,arm in enumerate(("r6","alt_graphic","clear_line_watercolor")):
   im=ImageOps.contain(load(entries[arm][i]),(130,155),Image.Resampling.LANCZOS);px=x+5+j*141+(130-im.width)//2;py=y+32+(155-im.height)//2;canvas.paste(im,(px,py));st=status[arm].get(entries[arm][i]["panel_id"],"-");d.text((x+35+j*141,y+194),f"{arm[:3].upper()} {st}",fill="#303940",font=font(12,True))
 path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path,"PNG",compress_level=6,optimize=False)
def anchor_sheet(entries,status,path):
 tw,th,margin,head,gap=1320,410,24,90,16;canvas=Image.new("RGB",(margin*2+tw,head+margin+len(ANCHORS)*th+(len(ANCHORS)-1)*gap),"#e8e4da");d=ImageDraw.Draw(canvas);d.text((margin,14),"CH05 THREE-ROUTE SEMANTIC ANCHORS",fill="#20252a",font=font(30,True));d.text((margin,52),"Compare story behavior before visual preference; R6 FAIL* is supplemental cross-panel audit",fill="#3d464e",font=font(16))
 for row,n in enumerate(ANCHORS):
  x=margin;y=head+row*(th+gap);d.rectangle((x,y,x+tw,y+th),fill="#faf8f2",outline="#65717a",width=3);d.text((x+10,y+7),f"P{n:03d}",fill="#20252a",font=font(17,True))
  for j,arm in enumerate(("r6","alt_graphic","clear_line_watercolor")):
   im=ImageOps.contain(load(entries[arm][n-1]),(400,310),Image.Resampling.LANCZOS);px=x+20+j*430+(400-im.width)//2;py=y+40+(310-im.height)//2;canvas.paste(im,(px,py));st=status[arm].get(entries[arm][n-1]["panel_id"],"-");d.text((x+155+j*430,y+365),f"{arm.replace('_',' ').upper()}  {st}",fill="#303940",font=font(13,True))
 path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path,"PNG",compress_level=6,optimize=False)
def phone_sheet(path):
 imgs={}
 for arm,p in PHONES.items():
  with Image.open(p) as im:imgs[arm]=im.convert("RGB")
 margin,gap,head=20,18,72;canvas=Image.new("RGB",(margin*2+3*390+2*gap,head+max(x.height for x in imgs.values())+margin),"#11151a");d=ImageDraw.Draw(canvas)
 for j,arm in enumerate(("r6","alt_graphic","clear_line_watercolor")):x=margin+j*(390+gap);d.text((x,14),arm.replace("_"," ").upper(),fill="#f4f1e8",font=font(17,True));canvas.paste(imgs[arm],(x,head))
 path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path,"PNG",compress_level=6,optimize=False)
def main():
 docs={a:json.loads(p.read_text(encoding="utf-8")) for a,p in ASSEMBLIES.items()};entries={a:d["entries"] for a,d in docs.items()};ids=[x["panel_id"] for x in entries["r6"]]
 if any([x["panel_id"] for x in entries[a]]!=ids for a in entries):raise ValueError("coverage mismatch")
 tri={a:json.loads(p.read_text(encoding="utf-8")) for a,p in TRIAGES.items()};status={a:{x["panel_id"]:x["status"] for x in tri[a]["rows"]} for a in tri};status["r6"]["ng-ch05-sc01-p001"]="FAIL*";status["r6"]["ng-ch05-sc01-p041"]="FAIL*";metrics={};per=[]
 for arm in entries:
  rows=[]
  for e in entries[arm]:im=load(e);p=ROOT/e["source"]["path"];rows.append(metric(im,p.stat().st_size))
  metrics[arm]={k:round(sum(x[k] for x in rows)/50,6) for k in rows[0]}
 for i,pid in enumerate(ids):per.append({"panel_id":pid,**{arm:metric(load(entries[arm][i]),(ROOT/entries[arm][i]["source"]["path"]).stat().st_size) for arm in entries}})
 f=OUT/"ch05-three-route-all-50-contact-sheet.png";a=OUT/"ch05-three-route-semantic-anchors.png";ph=OUT/"ch05-three-route-lettered-phone-comparison.png";full_sheet(entries,status,f);anchor_sheet(entries,status,a);phone_sheet(ph)
 doc={"record_type":"CH05CompleteChapterThreeRouteComparison","schema_version":"1.0","record_id":"ng-ch05-three-route-comparison-r1","state":"ENGINEERING_SELECTION_PENDING_OWNER_REVIEW","medium":"comic","planning_structure":"ComicPanelPlan","animation_shot_plan":None,"e_conte":None,"inputs":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha256(p)} for p in [*ASSEMBLIES.values(),*TRIAGES.values(),*PHONES.values()]],"coverage":{"routes":3,"comic_panel_plans_per_route":50,"paired_panel_ids":50,"total_panel_candidates_compared":150},"semantic_counts":{"r6_supplemental":{"pass":47,"warn":1,"fail":2},"alt_graphic":{"pass":36,"warn":7,"fail":7},"clear_line_watercolor":{"pass":45,"warn":2,"fail":3}},"visual_complexity":{"method":"Same 390px/equal-panel entropy, FIND_EDGES>=32 density, and native PNG bytes/pixel definitions as r6-vs-alt comparison.","aggregate_equal_panel_weight":metrics,"per_panel":per,"interpretation":"Style proxies support comparison only; they do not measure quality."},"gate_transfer":{"clear_line_watercolor":{"improved_to_pass_vs_alt":["independent_entry_roles","continuous_leverage_force_path","drum_fully_out"],"still_fail_or_partial":["departure_vector","impossible_far_bank_prints","third_upstream_mark","map_possession"]}},"ranking":[{"rank":1,"route":"r6_plus_cross_panel_gates","reason":"Lowest measured semantic failure/warning burden and strongest existing causal assembly."},{"rank":2,"route":"clear_line_watercolor","reason":"Strongest style-development arm and large semantic improvement over alternate; still three blocking failures."},{"rank":3,"route":"alt_graphic","reason":"Stable identity but non-separating density and seven failures."}],"recommendation":{"production_mechanism":"sequence-strip generation plus deterministic panel extraction, variable-cadence assembly, phone/lettering review, and hash-isolated selection/repair","current_base":"r6","leading_style_direction":"clear_line_watercolor","next_high_information_step":"owner review of full clear-line chapter and exact anchor comparisons, then a panel-addressable hybrid assembly using only explicitly advanced panels","appearance_only_selection":False},"artifacts":{"all_50_triples":art(f),"semantic_anchors":art(a),"lettered_phone_comparison":art(ph)},"spend":{"direct_paid_api_cloud_usd":0.0,"built_in_product_monetary_cost_usd":None},"limitations":["Agent triage is non-gating.","The r6 supplemental audit does not rewrite frozen evidence.","Prompt gates do not prove pixel compliance.","No route or panel is accepted, commercially cleared, or an exact production base."],"boundary":"Engineering recommendation only; owner disposition and rights remain separate."}
 EVIDENCE.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n");print(json.dumps({"output":EVIDENCE.relative_to(ROOT).as_posix(),"sha256":sha256(EVIDENCE),"metrics":metrics,"artifacts":doc["artifacts"]},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
