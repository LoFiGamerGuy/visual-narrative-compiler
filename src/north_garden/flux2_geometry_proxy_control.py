"""Reproducible local FLUX.2 Klein paired geometry-proxy stability control.

The frozen gauntlet is read and hash-checked, never edited.  Abstract proxy
tokens deliberately avoid identity/likeness evidence; this tests only whether
reference-conditioned rendering retains declared proxy role/count/block state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
COMFY = ROOT / "ComfyUI"
GAUNTLET = ROOT / "research" / "authoritative" / "v2.1.1" / "bench" / "gauntlet.json"
MANIFEST = ROOT / "manifests" / "experiments" / "flux2-klein-geometry-proxy-g07-stage-v1.json"
OUT = COMFY / "output" / "flux2_klein_geometry_proxy_v2"
RECORDS = ROOT / "experiments" / "records" / "flux2_klein_geometry_proxy_v2"
STAGE_DIR = ROOT / "experiments" / "outputs" / "geometry_proxy_g07_v1"
OUTPUT_SUBDIR = "flux2_klein_geometry_proxy_v2"
HOST = "http://127.0.0.1:8188"
FROZEN_SHA256 = "f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae"
CASES = {
    "G07a": {"reference": "g07a-geometry-proxy-r3.png", "left": "orange circle", "right": "teal triangle"},
    "G07b": {"reference": "g07b-geometry-proxy-r3.png", "left": "teal triangle", "right": "orange circle"},
}
TILE_CASES = {
    "G07a": {"reference": "g07a-role-tiles-r1.png", "left": "orange rectangular tile", "right": "teal rectangular tile"},
    "G07b": {"reference": "g07b-role-tiles-r1.png", "left": "teal rectangular tile", "right": "orange rectangular tile"},
}
BLENDER_CONTROL_CASES = {
    "G07a": {"reference": "g07a-role-id-r1.png", "left": "orange rectangular tile", "right": "teal rectangular tile"},
    "G07b": {"reference": "g07b-role-id-r1.png", "left": "teal rectangular tile", "right": "orange rectangular tile"},
}

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def assert_semantics(case_id: str) -> None:
    if sha(GAUNTLET) != FROZEN_SHA256:
        raise RuntimeError("frozen gauntlet hash differs; refusing execution")
    cases = {c["id"]: c for c in json.loads(GAUNTLET.read_text(encoding="utf-8"))["render_cases"]}
    case = cases[case_id]
    expected = ("SOREN", "SIGRID") if case_id == "G07a" else ("SIGRID", "SOREN")
    if case["spatial_mode"] != "grounded" or tuple(case["manifest"]["layout"][side] for side in ("left", "right")) != expected:
        raise RuntimeError(f"unexpected frozen definition for {case_id}")

def component_hashes() -> dict:
    paths = {
        "transformer": COMFY / "models" / "diffusion_models" / "flux2-klein-4b-fp8" / "flux-2-klein-4b-fp8.safetensors",
        "text_encoder": COMFY / "models" / "text_encoders" / "qwen_3_4b.safetensors",
        "vae": COMFY / "models" / "vae" / "flux2-vae.safetensors",
        "adapter_source": Path(__file__),
        "execution_manifest": MANIFEST,
    }
    return {key: {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)} for key, path in paths.items()}

def ensure_input(case_id: str) -> str:
    source = STAGE_DIR / CASES[case_id]["reference"]
    dest = COMFY / "input" / "experiments" / STAGE_DIR.name / source.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(source, dest)
    if sha(source) != sha(dest):
        raise RuntimeError("reference stage copy hash mismatch")
    return f"experiments/{STAGE_DIR.name}/{source.name}"

def graph(case_id: str, seed: int, image_name: str, no_change: bool = False) -> dict:
    layout = CASES[case_id]
    if no_change:
        positive = ("Preserve the supplied reference control exactly: retain its two abstract rectangular tokens, their left/right color order, "
                    "common table, camera, framing, occlusion, background, and every other visual element. Do not add, remove, move, recolor, restyle, or alter anything.")
    else:
        positive = ("Use the reference geometry stage as the composition authority. Render a drawn comic-panel kitchen with exactly two abstract adult-sized proxy tokens: "
                    f"{layout['left']} token on the left and {layout['right']} token on the right; both seated at the same table without touching. "
                    "Preserve the stage camera, table occlusion, and left/right order. No people, faces, children, text, or extra tokens.")
    negative = "photorealistic, face, person, child, text, watermark, extra token, duplicate token, role swap, touching, changed camera, changed table placement"
    return {
        "1": {"class_type":"UNETLoader","inputs":{"unet_name":"flux2-klein-4b-fp8\\flux-2-klein-4b-fp8.safetensors","weight_dtype":"default"}},
        "2": {"class_type":"CLIPLoader","inputs":{"clip_name":"qwen_3_4b.safetensors","type":"flux2","device":"default"}},
        "3": {"class_type":"VAELoader","inputs":{"vae_name":"flux2-vae.safetensors"}},
        "4": {"class_type":"CLIPTextEncode","inputs":{"text":positive,"clip":["2",0]}},
        "5": {"class_type":"CLIPTextEncode","inputs":{"text":negative,"clip":["2",0]}},
        "6": {"class_type":"EmptyFlux2LatentImage","inputs":{"width":["15",0],"height":["15",1],"batch_size":1}},
        "7": {"class_type":"RandomNoise","inputs":{"noise_seed":seed}},
        "8": {"class_type":"KSamplerSelect","inputs":{"sampler_name":"euler"}},
        "9": {"class_type":"Flux2Scheduler","inputs":{"steps":20,"width":["15",0],"height":["15",1]}},
        "10": {"class_type":"CFGGuider","inputs":{"model":["1",0],"positive":["18",0],"negative":["19",0],"cfg":5.0}},
        "11": {"class_type":"SamplerCustomAdvanced","inputs":{"noise":["7",0],"guider":["10",0],"sampler":["8",0],"sigmas":["9",0],"latent_image":["6",0]}},
        "12": {"class_type":"VAEDecode","inputs":{"samples":["11",0],"vae":["3",0]}},
        "13": {"class_type":"SaveImage","inputs":{"images":["12",0],"filename_prefix":f"{OUTPUT_SUBDIR}/{case_id.lower()}_seed{seed}{'-nochange' if no_change else ''}"}},
        "14": {"class_type":"LoadImage","inputs":{"image":image_name}},
        "15": {"class_type":"GetImageSize","inputs":{"image":["14",0]}},
        "16": {"class_type":"VAEEncode","inputs":{"pixels":["14",0],"vae":["3",0]}},
        "18": {"class_type":"ReferenceLatent","inputs":{"conditioning":["4",0],"latent":["16",0]}},
        "19": {"class_type":"ReferenceLatent","inputs":{"conditioning":["5",0],"latent":["16",0]}},
    }

def run(case_id: str, seed: int, no_change: bool = False) -> Path:
    assert_semantics(case_id); RECORDS.mkdir(parents=True, exist_ok=True)
    suffix = "-nochange" if no_change else ""
    record_path = RECORDS / f"{case_id.lower()}-seed-{seed}{suffix}.json"
    if record_path.exists(): return record_path
    image_name = ensure_input(case_id); payload = graph(case_id, seed, image_name, no_change)
    at = stamp(); started = time.time()
    response = requests.post(f"{HOST}/prompt", json={"prompt":payload, "client_id":str(uuid.uuid4())}, timeout=30)
    response.raise_for_status(); prompt_id = response.json()["prompt_id"]
    history = None
    while time.time() - started < 240:
        found = requests.get(f"{HOST}/history/{prompt_id}", timeout=20).json()
        if prompt_id in found:
            history = found[prompt_id]; break
        time.sleep(1)
    if history is None or history["status"]["status_str"] != "success":
        raise RuntimeError(f"generation did not complete: {prompt_id}")
    image = history["outputs"]["13"]["images"][0]
    candidate = COMFY / "output" / image["subfolder"] / image["filename"]
    assertions = {"reference_visual_preservation":"required"} if no_change else {"exactly_two_tokens":"required","role_order":"required","common_table_non_touching":"required","kitchen_proxy":"required"}
    record = {"schema_version":"1.0","record_type":"RenderRecord","record_id":f"ng-flux2-geometry-proxy-v2-{case_id.lower()}-{seed}{suffix}","state":"LOCAL_PROXY_RESEARCH_NOT_COMMERCIAL","case_id":case_id,"seed":seed,"semantic_source_sha256":FROZEN_SHA256,"input_state":{"spatial_mode":"grounded_geometry_proxy_reference","stage_reference":image_name,"proxy_layout":CASES[case_id],"control_type":"renderer_no_change" if no_change else "paired_composition"},"workflow":{"prompt_id":prompt_id,"graph":payload,"scheduler":"Flux2Scheduler","steps":20,"sampler":"euler","cfg":5.0},"sources":component_hashes(),"started_at":at,"ended_at":stamp(),"generation_seconds":round(time.time()-started,3),"candidate":{"path":candidate.relative_to(ROOT).as_posix(),"sha256":sha(candidate)},"hard_assertion_manifest":assertions,"human_review_status":"pending","human_minutes":None,"accepted_output":False,"cost":{"external_api_usd":0,"paid_service_used":False,"local_electricity":"unmeasured"},"limitations":["Fictional proxy only; no identity or production-grounding claim.","No-change reference control is known to drift globally.","Agent or human review must be recorded separately."]}
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--case", choices=sorted(CASES)); parser.add_argument("--seed", type=int, required=True); parser.add_argument("--tile-proxy", action="store_true"); parser.add_argument("--blender-control-v2", action="store_true"); parser.add_argument("--no-change", action="store_true"); args = parser.parse_args()
    if args.tile_proxy and args.blender_control_v2:
        raise SystemExit("choose only one control source")
    if args.tile_proxy:
        CASES = TILE_CASES
        STAGE_DIR = ROOT / "experiments" / "outputs" / "geometry_proxy_tiles_g07_v1"
        OUT = COMFY / "output" / "flux2_klein_geometry_tile_proxy_v1"
        RECORDS = ROOT / "experiments" / "records" / "flux2_klein_geometry_tile_proxy_v1"
        OUTPUT_SUBDIR = "flux2_klein_geometry_tile_proxy_v1"
        MANIFEST = ROOT / "manifests" / "experiments" / "flux2-klein-geometry-tile-proxy-g07-stage-v1.json"
    if args.blender_control_v2:
        CASES = BLENDER_CONTROL_CASES
        STAGE_DIR = ROOT / "experiments" / "outputs" / "blender_kitchen_control_bundle_v2"
        OUT = COMFY / "output" / "flux2_klein_blender_kitchen_control_g07_v1"
        RECORDS = ROOT / "experiments" / "records" / "flux2_klein_blender_kitchen_control_g07_v1"
        OUTPUT_SUBDIR = "flux2_klein_blender_kitchen_control_g07_v1"
        MANIFEST = ROOT / "manifests" / "experiments" / "flux2-klein-blender-kitchen-control-g07-stage-v1.json"
    print(run(args.case, args.seed, args.no_change))
