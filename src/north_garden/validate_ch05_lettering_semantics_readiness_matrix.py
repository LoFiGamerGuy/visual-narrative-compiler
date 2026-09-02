"""Validate CH05 50-plan lettering semantics readiness matrix."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-lettering-semantics-readiness-matrix-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});out=[]
 actual=tuple(s.get(k) for k in ("plan_count","silent_insert_default","silent_action_or_motion_protected","caption_or_silence_pending","speech_or_reaction_semantics_pending","attributed_speech_unbound"))
 if actual!=(50,16,14,13,6,1) or d.get("state")!="PASS_COPY_NULL":out.append("lettering denominator/state invalid")
 if any(s.get(k)!=0 for k in ("final_copy_bound","lettering_accepted","transparent_overlap_permissions","plan_revisions","provider_calls","uploads","cost_usd")) or s.get("human_review_minutes") is not None:out.append("copy/activity/promotion fabricated")
 if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None:out.append("planning boundary invalid")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));fail=errors(d);mp=ROOT/d["matrix"]["path"]
 if not mp.is_file() or sha(mp)!=d["matrix"]["sha256"]:fail.append("matrix binding invalid");m={}
 else:m=json.loads(mp.read_text(encoding="utf-8"))
 for item in d["inputs"]:
  p=ROOT/item["path"]
  if not p.is_file() or sha(p)!=item["sha256"]:fail.append(f"input binding invalid: {item['path']}")
 c=ROOT/d["chart"]["path"]
 if not c.is_file() or sha(c)!=d["chart"]["sha256"] or subprocess.run(["git","check-ignore","-q",str(c)],cwd=ROOT,check=False).returncode:fail.append("chart binding/ignore invalid")
 else:
  with Image.open(c) as im:
   if list(im.size)!=d["chart"]["dimensions"]:fail.append("chart dimensions invalid")
 rows=m.get("rows",[])
 if len(rows)!=50 or [r.get("display_order") for r in rows]!=list(range(1,51)):fail.append("row coverage/order invalid")
 if any(r.get("final_copy") is not None or r.get("font") is not None or r.get("tail_geometry") is not None or r.get("transparent_overlap_permission") is not False or r.get("protected_content_priority") is not True or r.get("lettering_accepted") is not False or r.get("comic_panel_plan_revision_created") is not False for r in rows):fail.append("row fail-closed state invalid")
 p016=next((r for r in rows if r.get("panel_id")=="ng-ch05-sc01-p016"),{})
 if p016.get("lettering_class")!="ATTRIBUTED_SPEECH_UNBOUND" or p016.get("speaker_semantics")!="SOREN_ATTRIBUTED" or p016.get("tested_copy_width_px")!=1200 or p016.get("outside_art_caption_eligible_after_revision") is not False:fail.append("P016 speech boundary invalid")
 if any(r.get("outside_art_caption_eligible_after_revision") and r.get("lettering_class")!="CAPTION_OR_SILENCE_PENDING" for r in rows):fail.append("outside-art semantic boundary invalid")
 muts=[lambda x:x.update(state="FAIL"),lambda x:x["summary"].update(plan_count=49),lambda x:x["summary"].update(silent_insert_default=15),lambda x:x["summary"].update(silent_action_or_motion_protected=13),lambda x:x["summary"].update(caption_or_silence_pending=12),lambda x:x["summary"].update(speech_or_reaction_semantics_pending=5),lambda x:x["summary"].update(attributed_speech_unbound=0),lambda x:x["summary"].update(final_copy_bound=1),lambda x:x["summary"].update(lettering_accepted=1),lambda x:x["summary"].update(transparent_overlap_permissions=1),lambda x:x["summary"].update(plan_revisions=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(cost_usd=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(animation_shot_plan={})]
 rejected=0
 for mut in muts:y=copy.deepcopy(d);mut(y);rejected+=bool(errors(y))
 if rejected!=len(muts):fail.append(f"only {rejected}/{len(muts)} mutations rejected")
 print(f"CH05 lettering semantics: {len(fail)} failures; 50=16 silent insert+14 protected action+13 caption/silence+6 speech/reaction+1 attributed; {rejected}/{len(muts)} mutations rejected")
 print("copy/overlap permissions/accepted/revisions/calls/uploads/cost 0/0/0/0/0/0/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
