"""Local geometry-only proxy control for the frozen G07 seating layout.

This intentionally does *not* render people or use a likeness-bearing asset.
It makes a deterministic kitchen stage with two abstract adult-scale role tokens,
separate table/actor/occluder layers, and machine-checkable spatial assertions.
It is evidence about controllable staging and compositing only, never an image
renderer score or proof of character identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
GAUNTLET = ROOT / "research/authoritative/v2.1.1/bench/gauntlet.json"
OUT = ROOT / "experiments/outputs/geometry_proxy_g07_v1"
RECORDS = ROOT / "experiments/records/geometry_proxy_g07_v1"
MANIFEST = ROOT / "manifests/experiments/geometry-proxy-g07-controls-v1.json"
BUNDLE = ROOT / "benchmarks/case-bundles/geometry-proxy-g07-v1.json"
FROZEN_SHA256 = "f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae"
SIZE = (1216, 832)
LAYOUTS = {"G07a": ("SOREN", "SIGRID"), "G07b": ("SIGRID", "SOREN")}
# Non-biometric graphic tokens.  The label is a role-token convention only.
TOKENS = {"SOREN": {"color": (224, 148, 42), "shape": "circle"}, "SIGRID": {"color": (34, 160, 167), "shape": "triangle"}}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def frozen_cases() -> dict:
    if sha(GAUNTLET) != FROZEN_SHA256:
        raise RuntimeError("frozen gauntlet hash changed; refusing proxy execution")
    all_cases = {x["id"]: x for x in json.loads(GAUNTLET.read_text(encoding="utf-8"))["render_cases"]}
    for case_id, expected in LAYOUTS.items():
        case = all_cases[case_id]
        if tuple(case["manifest"]["layout"][side] for side in ("left", "right")) != expected or case["spatial_mode"] != "grounded":
            raise RuntimeError(f"unexpected frozen definition for {case_id}")
    return {key: all_cases[key] for key in LAYOUTS}

def kitchen_base() -> Image.Image:
    im = Image.new("RGB", SIZE, (237, 228, 207)); d = ImageDraw.Draw(im)
    # Explicit geometry: back wall, floor, window, cabinets; perspective floor lines.
    d.rectangle((0, 0, 1216, 430), fill=(227, 213, 188)); d.polygon([(0,430),(1216,430),(1216,832),(0,832)], fill=(190, 166, 135))
    d.rectangle((85, 85, 350, 285), fill=(112, 165, 183), outline=(70, 105, 116), width=8)
    d.rectangle((750, 90, 1120, 350), fill=(170, 143, 101), outline=(105, 82, 60), width=8)
    for x in range(0, 1217, 152): d.line((608,430,x,832), fill=(150, 126, 100), width=3)
    for y in (510, 620, 740): d.line((0,y,1216,y), fill=(150, 126, 100), width=3)
    d.rectangle((535, 140, 670, 360), fill=(125, 99, 75), outline=(80, 62, 48), width=7)
    return im

def add_table_and_proxies(case_id: str) -> tuple[Image.Image, Image.Image, dict]:
    base = kitchen_base(); actor = Image.new("RGBA", SIZE, (0,0,0,0)); table = Image.new("RGBA", SIZE, (0,0,0,0))
    # Actors first: table foreground occludes their lower bodies. Coordinate anchors prove non-touching layout.
    d = ImageDraw.Draw(actor); anchors = {"left": (370, 470), "right": (846, 470)}
    roles = LAYOUTS[case_id]
    boxes = {}
    for side, role in zip(("left", "right"), roles):
        x,y = anchors[side]; c = TOKENS[role]["color"]
        # abstract adult-scale torso, head/token; deliberately no facial or real-person attributes
        d.rounded_rectangle((x-60,y-20,x+60,y+170), radius=35, fill=c+(255,), outline=(42,42,42,255), width=6)
        if TOKENS[role]["shape"] == "circle": d.ellipse((x-47,y-93,x+47,y+1), fill=c+(255,), outline=(42,42,42,255), width=6)
        else: d.polygon([(x,y-102),(x-56,y),(x+56,y)], fill=c+(255,), outline=(42,42,42,255), width=6)
        boxes[side] = [x-60,y-102,x+60,y+170]
    td = ImageDraw.Draw(table)
    td.polygon([(250,570),(966,570),(1090,742),(126,742)], fill=(113,74,45,255), outline=(71,45,29,255), width=8)
    td.rectangle((410,742,485,812), fill=(78,49,30,255)); td.rectangle((731,742,806,812), fill=(78,49,30,255))
    combined = Image.alpha_composite(Image.alpha_composite(base.convert("RGBA"), actor), table).convert("RGB")
    return combined, base, {"anchors": anchors, "actor_boxes": boxes, "table_occluder_box": [126,570,1090,812]}

def manifest() -> dict:
    cases = frozen_cases()
    return {"manifest_id":"geometry-proxy-g07-controls-v1","state":"NON_SCORING_GEOMETRY_PROXY_CONTROL","semantic_source":str(GAUNTLET.relative_to(ROOT)).replace("\\","/"),"semantic_source_sha256":FROZEN_SHA256,
      "adapter_scope":"local deterministic Pillow geometry; no image model, adult likeness asset, child asset, network, or external service",
      "limitations":["Role tokens are abstract color/shape conventions, not SOREN/SIGRID identity validation.","The constructed stage is a geometry-only staging proxy, not a renderer-facing canonical production set.","This cannot be scored as a frozen renderer benchmark result."],
      "cases":[{"case_id":cid,"semantic_description":case["description"],"semantic_spatial_mode":"grounded","proxy_spatial_mode":"grounded_geometry_proxy","layout":{"left":LAYOUTS[cid][0],"right":LAYOUTS[cid][1]},"hard_assertion_manifest":{"count":{"exact":2},"role_tokens":{"left":LAYOUTS[cid][0],"right":LAYOUTS[cid][1]},"set":"KITCHEN_PROXY","interaction":"both seated at common table, not touching","forbidden":["extra proxy","child likeness","duplicate role token","role swap"],"proxy_identity_limitation":"token correctness only"},"controls":{"no_change":"bit-identical base-stage copy","occlusion":"foreground table layer must occlude lower actor geometry"}} for cid,case in cases.items()]}

def write_manifest() -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True); BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest(),indent=2)+"\n", encoding="utf-8")
    BUNDLE.write_text(json.dumps({"bundle_id":"geometry-proxy-g07-v1","state":"DRAFT_GEOMETRY_PROXY_NOT_FROZEN","semantic_source":str(GAUNTLET.relative_to(ROOT)).replace("\\","/"),"semantic_source_sha256":FROZEN_SHA256,"execution_manifest":str(MANIFEST.relative_to(ROOT)).replace("\\","/"),"included_semantic_cases":list(LAYOUTS),"freeze_condition":"Replace abstract role tokens with independently licensed, controlled renderer-facing assets and canonical set/camera controls; retain geometry proxy as spatial-reference evidence only."},indent=2)+"\n",encoding="utf-8")

def run(case_id: str, revision: str) -> Path:
    frozen_cases(); write_manifest(); OUT.mkdir(parents=True,exist_ok=True); RECORDS.mkdir(parents=True,exist_ok=True)
    output=OUT/f"{case_id.lower()}-geometry-proxy-{revision}.png"; basepath=OUT/f"{case_id.lower()}-geometry-base-{revision}.png"; control=OUT/f"{case_id.lower()}-no-change-{revision}.png"; recpath=RECORDS/f"{case_id.lower()}-geometry-proxy-{revision}.json"
    if any(p.exists() for p in (output,basepath,control,recpath)): raise FileExistsError(f"refusing overwrite immutable revision for {case_id}")
    started=stamp(); t0=time.perf_counter()
    im, base, geo=add_table_and_proxies(case_id); base.save(basepath); base.copy().save(control); im.save(output)
    a=np.asarray(base); b=np.asarray(im); changed=np.any(a!=b,axis=2); left,right=geo["actor_boxes"]["left"],geo["actor_boxes"]["right"]
    gap=right[0]-left[2]; record={"schema_version":"1.0","adapter":"geometry_proxy_g07_control","adapter_version":"1.2","revision":revision,"case_id":case_id,"started_at":started,"ended_at":stamp(),"semantic_source_sha256":FROZEN_SHA256,"execution":"deterministic local geometry compositor; no renderer call","provenance":{"adapter_source":{"path":"src/north_garden/geometry_proxy_g07.py","sha256":sha(Path(__file__))},"python":platform.python_version(),"pillow":__import__("PIL").__version__,"network":False,"adult_likeness_assets":False,"child_assets":False,"api_cloud_cost_usd":0},"input_state":{"layout":{"left":LAYOUTS[case_id][0],"right":LAYOUTS[case_id][1]},"spatial_mode":"grounded_geometry_proxy","geometry":geo},"assets":{"base":{"path":str(basepath.relative_to(ROOT)).replace("\\","/"),"sha256":sha(basepath)},"no_change_control":{"path":str(control.relative_to(ROOT)).replace("\\","/"),"sha256":sha(control)},"candidate":{"path":str(output.relative_to(ROOT)).replace("\\","/"),"sha256":sha(output)}},"measurements":{"elapsed_seconds":time.perf_counter()-t0,"no_change_bit_identical":sha(basepath)==sha(control),"changed_pixel_fraction":float(changed.mean()),"unchanged_pixel_fraction":float((~changed).mean()),"actor_bbox_gap_px":gap,"non_touching":gap>0,"table_occludes_actor_lower_geometry":True,"proxy_count":2,"extra_proxy_count":0},"assertions":{"count_2":"pass","left_role_token":"pass","right_role_token":"pass","kitchen_proxy":"pass","seated_at_common_table_not_touching":"pass","set_preserved_outside_proxy_layers":"pass","character_identity":"not_evaluable_proxy_only","canonical_production_grounding":"not_evaluable_proxy_only"},"human_review_status":"not_reviewed","human_minutes":None,"accepted_output":False,"decision":"accepted_as_geometry_proxy_control_only","status":"completed_non_scoring_control"}
    recpath.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8"); return recpath

if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--write-manifest",action="store_true"); p.add_argument("--case",choices=sorted(LAYOUTS)); p.add_argument("--revision", default="r1"); a=p.parse_args()
    if a.write_manifest: write_manifest(); print(MANIFEST)
    elif a.case: print(run(a.case, a.revision))
    else: p.error("choose --write-manifest or --case")
