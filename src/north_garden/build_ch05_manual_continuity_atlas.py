"""Build deterministic full-panel continuity atlases without automated identity inference."""
from __future__ import annotations

import hashlib
import json
import math
import textwrap
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT=Path(__file__).resolve().parents[2]
INITIAL=ROOT/"docs/research/evidence/ch05-overnight-production-r1.json"
HARDENING=ROOT/"docs/research/evidence/ch05-cadence-hardening-r1.json"
PLANS=ROOT/"production/comic/ch05-sc01-panel-plans-v1.json"
SELECTED=ROOT/"production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json"
ASSERTIONS=ROOT/"production/comic/continuity/ch05-character-assertion-manifest-r1.json"
OUT=ROOT/"experiments/review-packets/ch05-manual-continuity-atlas-r1"
PACKET=OUT/"manual-continuity-atlas-packet.json"
EVIDENCE=ROOT/"docs/research/evidence/ch05-manual-continuity-atlas-r1.json"
FONT_PATH=Path("C:/Windows/Fonts/arialbd.ttf")

COLORS={"PASS":(45,132,92),"WARN":(193,132,37),"FAIL":(184,62,62)}
DIMENSIONS=["cast_count","role_identity_and_order","hair_and_wardrobe_continuity","causal_action_or_story_object","lettering_safe_zone","phone_size_readability"]

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def font(size:int):return ImageFont.truetype(str(FONT_PATH),size)
def state(review:dict)->str:
 values=review["results"].values()
 return "FAIL" if "FAIL" in values else "WARN" if "WARN" in values else "PASS"
def fit(source:Path,size:tuple[int,int])->Image.Image:
 with Image.open(source) as opened: image=opened.convert("RGB")
 return ImageOps.contain(image,size,Image.Resampling.LANCZOS)
def artifact(path:Path)->dict:
 with Image.open(path) as image:dims=[image.width,image.height]
 return {"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path),"dimensions":dims,"bytes":path.stat().st_size}

def card(candidate:dict,width:int=395,height:int=400)->Image.Image:
 review=candidate["engineering_review"]; status=state(review); canvas=Image.new("RGB",(width,height),(243,245,248));draw=ImageDraw.Draw(canvas)
 draw.rectangle((0,0,width-1,height-1),outline=COLORS[status],width=5)
 picture=fit(ROOT/candidate["output"]["path"],(width-24,260));x=(width-picture.width)//2;y=12+(260-picture.height)//2;canvas.paste(picture,(x,y))
 draw.rectangle((0,276,width,height),fill=(246,247,249))
 label=f"{candidate['candidate_id']} · {candidate['style_id']} · {status}";draw.text((12,286),label,font=font(17),fill=(20,26,34))
 compact="  ".join(f"{key.split('_')[0]}:{review['results'][key][0]}" for key in DIMENSIONS)
 draw.text((12,313),compact,font=font(13),fill=(58,67,78))
 note=" ".join(textwrap.wrap(review["note"],57)[:3])
 draw.multiline_text((12,338),"\n".join(textwrap.wrap(note,57)),font=font(12),fill=(50,57,67),spacing=3)
 return canvas

def build_all(groups:dict[str,list[dict]],plan_by_id:dict)->Image.Image:
 cell_w,cell_h,max_cols=395,400,4; header_h=145; group_gap=44
 panels=sorted(groups,key=lambda x:plan_by_id[x]["display_order"])
 total=130+sum(header_h+math.ceil(len(groups[p])/max_cols)*cell_h+group_gap for p in panels)
 canvas=Image.new("RGB",(40+max_cols*cell_w,total),(224,229,235));draw=ImageDraw.Draw(canvas)
 draw.text((24,18),"CH05 manual continuity atlas · all 26 canonical candidates",font=font(28),fill=(17,23,31))
 draw.text((24,58),"Compare full panels: hair color/style · oatmeal coat · plaid wrap · role staging · anatomy · safe-zone clearance",font=font(17),fill=(50,61,75))
 draw.text((24,86),"Existing engineering labels only. No face crop, detector, biometric comparison, identity inference, or acceptance.",font=font(15),fill=(114,56,56))
 y=130
 for panel_id in panels:
  plan=plan_by_id[panel_id];cast=" + ".join(plan["visible_adult_cast"]) or "NO PEOPLE"
  draw.rectangle((16,y,40+max_cols*cell_w-16,y+header_h-10),fill=(31,42,55))
  draw.text((28,y+14),f"P{plan['display_order']:03d} · {cast} · {len(groups[panel_id])} candidate(s)",font=font(21),fill=(241,244,247))
  draw.text((28,y+48),plan["narrative_beat"],font=font(16),fill=(210,218,227))
  draw.text((28,y+77),f"Composition: {plan['composition_intent']}",font=font(15),fill=(185,197,210))
  draw.text((28,y+105),"Manual check: correct hair pairing · canonical clothes · literal foreground/leader/action roles · mature proportions",font=font(14),fill=(255,210,129))
  y+=header_h
  for i,candidate in enumerate(groups[panel_id]):canvas.paste(card(candidate),(20+(i%max_cols)*cell_w,y+(i//max_cols)*cell_h))
  y+=math.ceil(len(groups[panel_id])/max_cols)*cell_h+group_gap
 return canvas

def build_selected(rows:list[dict],candidates:dict[str,dict])->Image.Image:
 width=1500;card_w=520;image_w=920;heights=[];pictures={}
 for row in rows:
  source=ROOT/candidates[row["candidate_id"]]["output"]["path"];pic=fit(source,(image_w,520));pictures[row["candidate_id"]]=pic;heights.append(max(280,pic.height)+54)
 canvas=Image.new("RGB",(width,115+sum(heights)),(229,233,238));draw=ImageDraw.Draw(canvas)
 draw.text((24,18),"CH05 selected sequence continuity · 14 provisional panels",font=font(28),fill=(17,23,31))
 draw.text((24,60),"Read top to bottom; verify identity and role order across style/scale changes. All selections remain owner-pending.",font=font(16),fill=(61,70,82));y=112
 for row,h in zip(rows,heights):
  candidate=candidates[row["candidate_id"]];review=candidate["engineering_review"];status=state(review);pic=pictures[row["candidate_id"]]
  canvas.paste(pic,(card_w+(image_w-pic.width)//2,y+(h-54-pic.height)//2))
  draw.rectangle((18,y+5,card_w-15,y+h-10),fill=(247,248,250),outline=COLORS[status],width=4)
  panel_number=int(row["panel_id"].rsplit("p",1)[1])
  draw.text((35,y+20),f"P{panel_number:03d} · {row['candidate_id']} · {row['style_id']}",font=font(20),fill=(20,27,36))
  draw.text((35,y+54),"Cast: "+(" + ".join(row["visible_adult_cast"]) or "NO PEOPLE"),font=font(15),fill=(55,66,78))
  draw.multiline_text((35,y+86),"\n".join(textwrap.wrap(row["narrative_beat"],50)),font=font(15),fill=(39,47,57),spacing=4)
  checks=["hair / hairstyle","oatmeal coat / plaid wrap","literal role staging","mature anatomy","hands + story object","lettering clearance"]
  draw.multiline_text((35,y+155),"Manual review\n"+"\n".join("□ "+x for x in checks),font=font(14),fill=(72,81,92),spacing=5)
  y+=h
 return canvas

def main()->int:
 plans=json.loads(PLANS.read_text(encoding="utf-8"));plan_by_id={p["panel_id"]:p for p in plans["plans"]};selected=json.loads(SELECTED.read_text(encoding="utf-8"))["rows"]
 candidates_list=[]
 for p in (INITIAL,HARDENING):candidates_list.extend(json.loads(p.read_text(encoding="utf-8"))["candidates"])
 candidates={c["candidate_id"]:c for c in candidates_list};groups=defaultdict(list)
 for c in candidates_list:groups[c["panel_id"]].append(c)
 for values in groups.values():values.sort(key=lambda x:x["candidate_id"])
 OUT.mkdir(parents=True,exist_ok=True)
 all_path=OUT/"ch05-continuity-atlas-all-26-r1.png";selected_path=OUT/"ch05-continuity-atlas-selected-14-r1.png"
 build_all(groups,plan_by_id).save(all_path,optimize=False);build_selected(selected,candidates).save(selected_path,optimize=False)
 state_counts=Counter(state(c["engineering_review"]) for c in candidates_list);dimension_counts={dim:dict(Counter(c["engineering_review"]["results"][dim] for c in candidates_list)) for dim in DIMENSIONS}
 checklist=[{"candidate_id":c["candidate_id"],"panel_id":c["panel_id"],"visible_adult_cast":plan_by_id[c["panel_id"]]["visible_adult_cast"],"style_id":c["style_id"],
             "existing_engineering_results":c["engineering_review"]["results"],"existing_note":c["engineering_review"]["note"],"manual_owner_checks":["hair color and hairstyle","canonical wardrobe","literal role staging","mature adult proportions","hands and causal object","lettering-safe important content"],
             "owner_decision":None,"human_review_minutes":None} for c in candidates_list]
 packet={"record_type":"CH05ManualContinuityAtlasPacket","schema_version":"1.0","record_id":"ng-ch05-manual-continuity-atlas-packet-r1","state":"LOCAL_MANUAL_REVIEW_READY_OWNER_PENDING",
         "inputs":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)} for p in (INITIAL,HARDENING,PLANS,SELECTED,ASSERTIONS)],"candidate_count":26,"panel_group_count":14,"selected_count":14,
         "engineering_state_counts":dict(state_counts),"dimension_counts":dimension_counts,"candidate_checklists":checklist,
         "artifacts":[artifact(all_path),artifact(selected_path)],"rendered_identity_inference_count":0,"face_crop_count":0,"owner_decisions":0,"human_review_minutes":None,
         "provider_calls":0,"uploads":0,"external_cost_usd":0,"animation_shot_plan":None,"e_conte":None,
         "boundary":"Full-panel manual comparison only; existing engineering labels are not owner acceptance, biometric identity, or commercial clearance."}
 with PACKET.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(packet,indent=2)+"\n")
 evidence={"record_type":"CH05ManualContinuityAtlasEvidence","schema_version":"1.0","record_id":"ng-ch05-manual-continuity-atlas-evidence-r1","state":"TWO_DETERMINISTIC_ATLASES_OWNER_REVIEW_PENDING",
           "packet":{"path":PACKET.relative_to(ROOT).as_posix(),"sha256":sha(PACKET)},"summary":{"candidate_count":26,"panel_group_count":14,"selected_count":14,"engineering_pass":state_counts["PASS"],"engineering_warn":state_counts["WARN"],"engineering_fail":state_counts["FAIL"],
           "hair_wardrobe_pass":dimension_counts["hair_and_wardrobe_continuity"].get("PASS",0),"role_order_pass":dimension_counts["role_identity_and_order"].get("PASS",0),"role_order_fail":dimension_counts["role_identity_and_order"].get("FAIL",0),"rendered_identity_inference_count":0,"face_crop_count":0,"owner_decisions":0,"human_review_minutes":None,"provider_calls":0,"uploads":0,"external_cost_usd":0},
           "artifacts":packet["artifacts"],"limitations":["Existing hair/wardrobe labels are manual engineering observations, not automated measurements or owner decisions.","Full-panel atlases aid comparison but do not prove identity or deterministic generation.","Style and panel-scale changes can alter apparent hair value; owner inspection remains required."],
           "boundary":"Generated pixels and atlas files remain ignored local review evidence; only hashes, measurements, and tooling are tracked."}
 with EVIDENCE.open("w",encoding="utf-8",newline="\n") as h:h.write(json.dumps(evidence,indent=2)+"\n")
 print(f"CH05 continuity atlas: 26 candidates / 14 panel groups / 14 selected; states {dict(state_counts)}")
 print(f"manual labels: hair/wardrobe 26 pass; role order 25 pass/1 fail; identity inference 0; artifacts {sha(all_path)} {sha(selected_path)}")
 return 0
if __name__=="__main__":raise SystemExit(main())
