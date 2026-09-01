"""Narrow local Sigrid actor-plate retry; separate from baseline_legacy.

This is an immutable r2 asset-capture arm after r1 found furniture leakage in
both Sigrid samples.  It uses only the existing local renderer and local adult
LoRA; outputs are research-only and never a commercial/benchmark claim.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMFY = ROOT / "ComfyUI"
OUT = COMFY / "output" / "controlled_actor_capture_v2"
RECORDS = ROOT / "experiments" / "records" / "controlled_actor_capture_v2"
RESULT = ROOT / "experiments" / "results" / "controlled_actor_capture_v2.json"
sys.path.insert(0, str(ROOT / "garden"))
from gen3 import graph, post, wait  # noqa: E402
from action2 import STYLES  # noqa: E402
from canon import BASE_NEG, D0_NEG, ONE_W, PLATE_PROP_NEG, SIGRID_D0  # noqa: E402

UNET = COMFY / "models/diffusion_models/anima-aesthetic-v1.1.safetensors"
CLIP = COMFY / "models/text_encoders/qwen_3_06b_base.safetensors"
VAE = COMFY / "models/vae/qwen_image_vae.safetensors"
LORA = COMFY / "models/loras/sigrid_v1.safetensors"
JOBS = [
    {"seed": 5301, "brief": "full body, knees and lower legs visibly bent in an unambiguous seated pose on an invisible support, torso upright, hands held forward at table height, looking frame left"},
    {"seed": 5302, "brief": "full body, knees and lower legs visibly bent in an unambiguous seated pose on an invisible support, torso leaning slightly forward, hands held forward at table height, looking down and frame left"},
]
DRAWN = "strong graphic cel shading, bold ink outline, flat colour blocks, hard edged shadow shapes, drawn illustration, comic panel, "
PLATE = "one adult woman only, full body isolated actor plate, seamless flat neutral grey studio background, completely empty background, no floor line, no scenery, no furniture, no props, "
NEG = BASE_NEG + ", " + D0_NEG + ", " + PLATE_PROP_NEG + ", chair, stool, bench, seat, table, desk, tabletop, table edge, furniture, room, kitchen, scenery, floor detail, object held in hands, background pattern, texture, gradient, vignette, background shadow"

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def sources() -> dict:
    paths = {"unet": UNET, "text_encoder": CLIP, "vae": VAE, "lora_sigrid": LORA, "capture_harness": Path(__file__), "graph_builder": ROOT / "garden" / "gen3.py"}
    return {key: {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)} for key, path in paths.items()}

def run(job: dict) -> dict:
    OUT.mkdir(parents=True, exist_ok=True); RECORDS.mkdir(parents=True, exist_ok=True)
    key = f"sigrid-seed-{job['seed']}"; record_path = RECORDS / f"{key}.json"
    if record_path.exists():
        return json.loads(record_path.read_text(encoding="utf-8"))
    prompt = STYLES["manhwa"] + ", " + DRAWN + PLATE + ONE_W + "sgrd, " + SIGRID_D0 + ", " + job["brief"]
    workflow = graph(base=prompt, regions=[], neg=NEG, w=896, h=1216, seed=job["seed"], steps=42, cfg=4.0, sampler="er_sde", sched="simple", prefix=f"controlled_actor_capture_v2/{key}", loras=[["sigrid_v1.safetensors", 0.55]])
    at = stamp(); started = time.time(); prompt_id = post(workflow, str(uuid.uuid4())); files = wait(prompt_id); elapsed = time.time() - started
    if not files or files[0].startswith(("ERROR", "TIMEOUT")):
        raise RuntimeError(f"capture {key} failed: {files}")
    candidates = []
    for name in files:
        source = COMFY / "output" / "controlled_actor_capture_v2" / Path(name).name
        if not source.exists(): source = COMFY / "output" / name
        if not source.exists(): raise FileNotFoundError(source)
        dest = OUT / f"{key}-{Path(name).name}"
        if source.resolve() != dest.resolve(): shutil.copy2(source, dest)
        candidates.append({"path": dest.relative_to(ROOT).as_posix(), "sha256": sha(dest)})
    record = {"schema_version":"1.0","record_type":"ControlledActorCaptureRenderRecord","record_id":f"ng-controlled-actor-capture-v2-{key}","state":"LOCAL_RESEARCH_ONLY_NOT_COMMERCIAL","role":"SIGRID","seed":job["seed"],"input_state":{"pose_id":"seated_at_common_table_actor_only","camera_id":"table_level_three_quarter","set_id":"neutral_plate_not_kitchen","prop_state":"no_embedded_foreign_furniture_or_props","spatial_mode":"2d_only"},"prompt":prompt,"negative_prompt":NEG,"workflow":{"generator":"garden/gen3.py graph","sampler":"er_sde","scheduler":"simple","steps":42,"cfg":4.0,"width":896,"height":1216,"lora_strength":0.55,"prompt_id":prompt_id},"sources":sources(),"started_at":at,"ended_at":stamp(),"generation_seconds":round(elapsed,3),"candidates":candidates,"hard_assertion_manifest":{"single_adult_role":"SIGRID","neutral_empty_background":"required","seated_table_read":"required","no_embedded_foreign_furniture":"required","alpha_matte_verified":"required before use"},"human_review_status":"pending","human_minutes":None,"accepted_output":None,"limitations":["Adult likeness remains local-sensitive; no commercial or external-upload authorization.","This is a distinct asset-capture arm, not a baseline change or frozen benchmark score."]}
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record

if __name__ == "__main__":
    records = [run(job) for job in JOBS]
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps({"record_type":"ControlledActorCaptureRun","state":"PENDING_VISUAL_QA","jobs":records,"total_generation_seconds":round(sum(r["generation_seconds"] for r in records),3),"cost":{"external_api_usd":0,"paid_service_used":False,"local_electricity":"unmeasured"}}, indent=2) + "\n", encoding="utf-8")
    print(RESULT)
