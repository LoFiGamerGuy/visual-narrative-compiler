"""Compile fail-closed lettering semantics readiness for all 50 CH05 plans."""
from __future__ import annotations

import hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SCALE = ROOT / "production/comic/layout/ch05-panel-scale-cadence-policy-r1.json"
SEQUENCES = ROOT / "production/comic/run-manifests/ch05-chapter-sequence-production-batches-r1.json"
TRANSPARENT = ROOT / "docs/research/evidence/ch05-transparent-lettering-rehearsal-r1.json"
WIDTH = ROOT / "docs/research/evidence/ch05-lettering-width-copy-sensitivity-r1.json"
OUTSIDE = ROOT / "docs/research/evidence/ch05-outside-art-lettering-band-r1.json"
OUTPUT = ROOT / "production/comic/layout/ch05-lettering-semantics-readiness-matrix-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-lettering-semantics-readiness-matrix-r1.json"
CHART = ROOT / "experiments/review-packets/ch05-lettering-semantics-readiness-r1/ch05-lettering-semantics-map-r1.png"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def binding(path: Path) -> dict: return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def classify(row: dict) -> str:
    role = row["scale_role"]
    if row["explicit_dialogue_detected"]: return "ATTRIBUTED_SPEECH_UNBOUND"
    if role.startswith("SMALL_"): return "SILENT_INSERT_DEFAULT"
    if role in {"WIDE_DIRECTIONAL_ANCHOR", "WIDE_ENVIRONMENTAL_MOTION", "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM_SINGLE_CAUSAL"}: return "SILENT_ACTION_OR_MOTION_PROTECTED"
    if role == "MEDIUM_CHARACTER_CLUE": return "CAPTION_OR_SILENCE_PENDING"
    return "SPEECH_OR_REACTION_SEMANTICS_PENDING"


def build_chart(rows: list[dict]) -> None:
    CHART.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1600, 1900), "#10151c"); draw = ImageDraw.Draw(image); font = ImageFont.load_default()
    draw.text((38,24), "CH05 · lettering semantics readiness r1", fill="#eef3f8", font=font)
    draw.text((38,45), "Final copy null in 50/50 · protected content outranks lettering", fill="#ffcf88", font=font)
    colors = {"SILENT_INSERT_DEFAULT":"#5c6570", "SILENT_ACTION_OR_MOTION_PROTECTED":"#3d7654", "CAPTION_OR_SILENCE_PENDING":"#4a7191", "SPEECH_OR_REACTION_SEMANTICS_PENDING":"#806d35", "ATTRIBUTED_SPEECH_UNBOUND":"#924856"}
    x=38
    for label,color in colors.items():
        draw.rectangle((x,68,x+16,84),fill=color);draw.text((x+21,69),label.replace("_"," ")[:24],fill="#dce4ec",font=font);x+=290
    cell_w,cell_h,gap=286,164,10
    for index,row in enumerate(rows):
        col,line=index%5,index//5;left,top=38+col*(cell_w+gap),110+line*(cell_h+gap)
        draw.rounded_rectangle((left,top,left+cell_w,top+cell_h),radius=8,fill=colors[row["lettering_class"]],outline="#8593a3")
        draw.text((left+10,top+8),f"{row['panel_id'].split('-')[-1].upper()} · {row['lettering_class'].replace('_',' ')[:27]}",fill="white",font=font)
        draw.text((left+10,top+32),row["scale_role"].replace("_"," ")[:34],fill="#e7edf3",font=font)
        draw.text((left+10,top+54),f"copy null · bound 0 · overlap 0",fill="#ffe0a8",font=font)
        draw.text((left+10,top+76),f"1200px test {'YES' if row['tested_copy_width_px'] else 'NO'}",fill="#d2dbe4",font=font)
        draw.text((left+10,top+98),f"outside band {'ELIGIBLE' if row['outside_art_caption_eligible_after_revision'] else 'NO'}",fill="#d2dbe4",font=font)
        draw.text((left+10,top+120),row["semantic_blocker"].replace("_"," ")[:39],fill="#ffe0a8",font=font)
    image.save(CHART,optimize=False)


def main() -> int:
    policy=json.loads(SCALE.read_text(encoding="utf-8")); rows=[]
    for source in policy["rows"]:
        cls=classify(source); copy_capable=cls in {"ATTRIBUTED_SPEECH_UNBOUND","CAPTION_OR_SILENCE_PENDING","SPEECH_OR_REACTION_SEMANTICS_PENDING"}
        outside_eligible=cls=="CAPTION_OR_SILENCE_PENDING"
        if cls=="ATTRIBUTED_SPEECH_UNBOUND": default="Bind exact Soren-attributed copy and tail geometry; then test at 1200px. Outside-art band is not attributed speech."; blocker="FINAL_COPY_FONT_TAIL_AND_SAFE_ZONE_UNBOUND"
        elif cls=="SILENT_INSERT_DEFAULT": default="Keep silent; do not shrink copy into object/sensory inserts."; blocker="NONE_IF_SILENT_PLAN_REVISION_IF_CAPTION"
        elif cls=="SILENT_ACTION_OR_MOTION_PROTECTED": default="Keep silent/minimal; never trade hands, faces, silhouettes, or causal objects for lettering."; blocker="PROTECTED_ACTION_GEOMETRY"
        elif cls=="CAPTION_OR_SILENCE_PENDING": default="Prefer silence; light outside-art caption is eligible only after plan-level semantic revision."; blocker="CAPTION_SEMANTICS_AND_FINAL_COPY_UNBOUND"
        else: default="Bind speaker/caption semantics first; attributed speech requires a 1200px test and protected-content clearance."; blocker="SPEAKER_OR_CAPTION_SEMANTICS_UNBOUND"
        rows.append({"display_order":source["display_order"],"panel_id":source["panel_id"],"plan_revision_id":source["plan_revision_id"],"scale_role":source["scale_role"],"width_range_px":source["width_range_px"],"explicit_dialogue_detected":source["explicit_dialogue_detected"],"speaker_semantics":"SOREN_ATTRIBUTED" if source["panel_id"]=="ng-ch05-sc01-p016" else None,"lettering_class":cls,"engineering_default":default,"tested_copy_width_px":1200 if copy_capable else None,"tested_phone_type_minimum_px":13 if copy_capable else None,"outside_art_caption_eligible_after_revision":outside_eligible,"outside_art_phone_type_px":13.975 if outside_eligible else None,"transparent_backing_next_arm_percent":88 if copy_capable else None,"transparent_overlap_permission":False,"protected_content_priority":True,"semantic_blocker":blocker,"final_copy":None,"font":None,"tail_geometry":None,"localization_review":None,"accessibility_review":None,"lettering_accepted":False,"comic_panel_plan_revision_created":False})
    build_chart(rows)
    counts={key:sum(row["lettering_class"]==key for row in rows) for key in ("SILENT_INSERT_DEFAULT","SILENT_ACTION_OR_MOTION_PROTECTED","CAPTION_OR_SILENCE_PENDING","SPEECH_OR_REACTION_SEMANTICS_PENDING","ATTRIBUTED_SPEECH_UNBOUND")}
    record={"record_type":"ComicLetteringSemanticsReadinessMatrix","schema_version":"1.0","record_id":"ng-ch05-lettering-semantics-readiness-matrix-r1","state":"FIFTY_PLAN_COPY_NULL_SEMANTICS_OWNER_PENDING","medium":"comic","inputs":[binding(path) for path in (SCALE,SEQUENCES,TRANSPARENT,WIDTH,OUTSIDE)],"measured_contract":{"minimum_phone_type_px":13,"tested_in_art_two_line_width_px":1200,"outside_art_phone_type_px":13.975,"outside_art_scroll_height_addition_percent":3.295,"transparent_backing_next_arm_percent":88,"outside_art_semantics":"caption/direct text only; not attributed speech"},"summary":{"plan_count":50,"silent_insert_default":counts["SILENT_INSERT_DEFAULT"],"silent_action_or_motion_protected":counts["SILENT_ACTION_OR_MOTION_PROTECTED"],"caption_or_silence_pending":counts["CAPTION_OR_SILENCE_PENDING"],"speech_or_reaction_semantics_pending":counts["SPEECH_OR_REACTION_SEMANTICS_PENDING"],"attributed_speech_unbound":counts["ATTRIBUTED_SPEECH_UNBOUND"],"final_copy_bound":0,"lettering_accepted":0,"transparent_overlap_permissions":0,"plan_revisions":0,"provider_calls":0,"uploads":0,"cost_usd":0,"human_review_minutes":None},"rows":rows,"chart":{"path":CHART.relative_to(ROOT).as_posix(),"sha256":sha(CHART),"dimensions":[1600,1900]},"comic_panel_plan_revision_created":False,"animation_shot_plan":None,"e_conte":None,"boundary":"Semantic readiness only. No copy, font, tail, overlap permission, plan revision, provider activity, or lettering acceptance."}
    OUTPUT.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8",newline="\n")
    evidence={"record_type":"ComicLetteringSemanticsReadinessMatrixEvidence","schema_version":"1.0","record_id":"ng-ch05-lettering-semantics-readiness-matrix-evidence-r1","state":"PASS_COPY_NULL","matrix":binding(OUTPUT),"inputs":record["inputs"],"summary":record["summary"],"chart":record["chart"],"animation_shot_plan":None,"e_conte":None}
    EVIDENCE.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"CH05 lettering semantics: 50 = silent inserts {counts['SILENT_INSERT_DEFAULT']} + protected action {counts['SILENT_ACTION_OR_MOTION_PROTECTED']} + caption/silence {counts['CAPTION_OR_SILENCE_PENDING']} + speech/reaction {counts['SPEECH_OR_REACTION_SEMANTICS_PENDING']} + attributed {counts['ATTRIBUTED_SPEECH_UNBOUND']}")
    print("copy/overlap permissions/accepted/revisions/calls/uploads/cost 0/0/0/0/0/0/$0")
    return 0


if __name__=="__main__":raise SystemExit(main())
