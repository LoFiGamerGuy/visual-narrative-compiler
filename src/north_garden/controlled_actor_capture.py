"""Local-only controlled adult actor-capture experiment (not a benchmark arm).

Creates the smallest asset set needed to test the G07 compositor hypothesis:
one pose/prop-separable seated-at-table *actor plate* per adult role.  This
uses the installed legacy renderer and local LoRAs only.  It neither changes
the frozen gauntlet nor establishes a commercially cleared likeness asset.
"""
from __future__ import annotations

import argparse
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
OUT = COMFY / "output" / "controlled_actor_capture_v1"
RECORDS = ROOT / "experiments" / "records" / "controlled_actor_capture_v1"
RESULT = ROOT / "experiments" / "results" / "controlled_actor_capture_v1.json"
SPEC = ROOT / "production" / "assets" / "controlled-actor-capture-spec-v1.json"

sys.path.insert(0, str(ROOT / "garden"))
from gen3 import graph, post, wait  # noqa: E402
from action2 import STYLES  # noqa: E402
from canon import BASE_NEG, D0_NEG, ONE_M, ONE_W, PLATE_PROP_NEG, SIGRID_D0, SOREN_D0  # noqa: E402

UNET = COMFY / "models/diffusion_models/anima-aesthetic-v1.1.safetensors"
CLIP = COMFY / "models/text_encoders/qwen_3_06b_base.safetensors"
VAE = COMFY / "models/vae/qwen_image_vae.safetensors"
LORAS = {
    "SOREN": COMFY / "models/loras/soren_v1.safetensors",
    "SIGRID": COMFY / "models/loras/sigrid_v1.safetensors",
}

DRAWN = "strong graphic cel shading, bold ink outline, flat colour blocks, hard edged shadow shapes, drawn illustration, comic panel, "
PLATE = "full body, seated posture at a table, hands held forward at table height but no table visible, plain flat neutral grey background, seamless studio grey backdrop, completely empty background, no scenery, no floor detail, no visible furniture, no props, "
NEG = BASE_NEG + ", " + D0_NEG + ", " + PLATE_PROP_NEG + ", background scenery, room, chair, stool, seat, table edge, desktop, furniture, object held in hands, pattern, texture, gradient background, vignette, shadow on background"

JOBS = [
    {"role": "SOREN", "seed": 5101, "count": ONE_M, "identity": "s0rn, " + SOREN_D0, "brief": "three quarter view, leaning slightly forward, forearms held out at table height, looking down at his hands, headlamp pushed up onto forehead, not looking at viewer", "lora": "soren_v1.safetensors"},
    {"role": "SOREN", "seed": 5102, "count": ONE_M, "identity": "s0rn, " + SOREN_D0, "brief": "three quarter view, seated naturally, both hands held forward at table height, looking across frame right, headlamp pushed up onto forehead, not looking at viewer", "lora": "soren_v1.safetensors"},
    {"role": "SIGRID", "seed": 5201, "count": ONE_W, "identity": "sgrd, " + SIGRID_D0, "brief": "three quarter view, seated naturally, leaning slightly forward, hands held forward at table height, looking across frame left, not looking at viewer", "lora": "sigrid_v1.safetensors"},
    {"role": "SIGRID", "seed": 5202, "count": ONE_W, "identity": "sgrd, " + SIGRID_D0, "brief": "three quarter view, seated naturally, one forearm held forward at table height, looking down and away, not looking at viewer", "lora": "sigrid_v1.safetensors"},
]

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def source_hashes() -> dict:
    paths = {"unet": UNET, "text_encoder": CLIP, "vae": VAE, "capture_spec": SPEC, "graph_builder": ROOT / "garden/gen3.py", "capture_harness": Path(__file__)}
    paths.update({f"lora_{role.lower()}": path for role, path in LORAS.items()})
    return {key: {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)} for key, path in paths.items()}

def job_prompt(job: dict) -> str:
    return STYLES["manhwa"] + ", " + DRAWN + PLATE + job["count"] + job["identity"] + ", " + job["brief"]

def run_job(job: dict) -> dict:
    OUT.mkdir(parents=True, exist_ok=True); RECORDS.mkdir(parents=True, exist_ok=True)
    key = f"{job['role'].lower()}-seed-{job['seed']}"
    record_path = RECORDS / f"{key}.json"
    if record_path.exists():
        return json.loads(record_path.read_text(encoding="utf-8"))
    prompt = job_prompt(job)
    g = graph(base=prompt, regions=[], neg=NEG, w=896, h=1216, seed=job["seed"], steps=42, cfg=4.0, sampler="er_sde", sched="simple", prefix=f"controlled_actor_capture_v1/{key}", loras=[[job["lora"], 0.55]])
    started = time.time(); at = stamp(); pid = post(g, str(uuid.uuid4())); files = wait(pid); elapsed = time.time() - started
    if not files or files[0].startswith(("ERROR", "TIMEOUT")):
        raise RuntimeError(f"capture {key} failed: {files}")
    candidates = []
    for name in files:
        src = OUT / name
        if not src.exists():
            # Comfy history returns a filename only; prefix normally becomes the subdirectory.
            src = COMFY / "output" / name
        if not src.exists(): raise FileNotFoundError(src)
        dest = OUT / f"{key}-{Path(name).name}"
        if src.resolve() != dest.resolve(): shutil.copy2(src, dest)
        candidates.append({"path": dest.relative_to(ROOT).as_posix(), "sha256": sha(dest)})
    record = {"schema_version":"1.0","record_type":"ControlledActorCaptureRenderRecord","record_id":f"ng-controlled-actor-capture-v1-{key}","state":"LOCAL_RESEARCH_ONLY_NOT_COMMERCIAL","role":job["role"],"seed":job["seed"],"input_state":{"pose_id":"seated_at_common_table_actor_only","camera_id":"table_level_three_quarter","set_id":"neutral_plate_not_kitchen","prop_state":"no_embedded_foreign_furniture_or_props","spatial_mode":"2d_only"},"prompt":prompt,"negative_prompt":NEG,"workflow":{"generator":"garden/gen3.py graph","sampler":"er_sde","scheduler":"simple","steps":42,"cfg":4.0,"width":896,"height":1216,"lora_strength":0.55,"prompt_id":pid},"sources":source_hashes(),"started_at":at,"ended_at":stamp(),"generation_seconds":round(elapsed,3),"candidates":candidates,"human_review_status":"pending","human_minutes":None,"accepted_output":None,"limitations":["Existing local adult-character LoRA provenance is not a commercial license/consent clearance.","Legacy neutral-plate keying will require explicit alpha-matte QA.","This is an asset-capture experiment, not a frozen G07 score or canonical grounded-stage evidence."]}
    record_path.write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    return record

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--run", action="store_true"); args=parser.parse_args()
    if not args.run:
        print(json.dumps({"jobs":JOBS,"sources":source_hashes()},indent=2)); return
    records=[run_job(job) for job in JOBS]
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps({"record_type":"ControlledActorCaptureRun","state":"PENDING_VISUAL_QA","jobs":records,"total_generation_seconds":round(sum(x["generation_seconds"] for x in records),3),"cost":{"external_api_usd":0,"paid_service_used":False,"local_electricity":"unmeasured"}},indent=2)+"\n",encoding="utf-8")
    print(RESULT)

if __name__ == "__main__": main()
