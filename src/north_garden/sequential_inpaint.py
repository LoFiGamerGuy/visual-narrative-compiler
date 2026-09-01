"""Local-only two-pass identity repair experiment for North Garden.

This is a separate renderer arm from ``baseline_legacy``. It starts with a
fixed legacy empty kitchen plate, inpaints one adult character with only that
character's LoRA active, then inpaints the other into the first result. The
purpose is to measure role isolation and collateral change, not to improve the
baseline arm or claim commercial eligibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
COMFY = ROOT / "ComfyUI"
INPUT = COMFY / "input" / "experiments" / "sequential_inpaint_v1"
OUTPUT = COMFY / "output" / "sequential_inpaint_v1"
RECORDS = ROOT / "experiments" / "records" / "sequential_inpaint_v1"
HOST = "http://127.0.0.1:8188"
W, H = 1216, 832
BASE_PLATE = COMFY / "output" / "pg_bg_table_00002_.png"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_commit(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def runtime_snapshot() -> dict[str, object]:
    snapshot: dict[str, object] = {
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "comfy_commit": git_commit(COMFY),
        "project_git_commit": git_commit(ROOT),
    }
    probe = (
        "import json, torch; print(json.dumps({'torch':torch.__version__,"
        "'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}))"
    )
    try:
        output = subprocess.check_output(
            [str(COMFY / "venv/Scripts/python.exe"), "-c", probe], text=True, stderr=subprocess.DEVNULL
        )
        snapshot.update(json.loads(output))
    except Exception as exc:
        snapshot["comfy_runtime_probe_error"] = repr(exc)
    return snapshot


def model_inventory() -> list[dict[str, str]]:
    paths = [
        "models/diffusion_models/anima-aesthetic-v1.1.safetensors",
        "models/text_encoders/qwen_3_06b_base.safetensors",
        "models/vae/qwen_image_vae.safetensors",
        "models/loras/soren_v1.safetensors",
        "models/loras/sigrid_v1.safetensors",
    ]
    return [{"path": item, "sha256": digest(COMFY / item) if (COMFY / item).exists() else "MISSING"} for item in paths]


def custom_node_versions() -> list[dict[str, str | None]]:
    nodes = COMFY / "custom_nodes"
    return [
        {"name": child.name, "commit": git_commit(child)}
        for child in sorted(nodes.iterdir())
        if child.is_dir() and not child.name.startswith("__")
    ]


def prepare() -> dict[str, Path]:
    """Create fixed, versioned local plate and target masks; never touch source assets."""
    INPUT.mkdir(parents=True, exist_ok=True)
    if not BASE_PLATE.exists():
        raise FileNotFoundError(BASE_PLATE)
    plate = INPUT / "p07_empty_kitchen_v1.png"
    shutil.copy2(BASE_PLATE, plate)
    masks = {}
    for name, rect in {"soren": (120, 260, 560, 760), "sigrid": (650, 235, 1100, 760)}.items():
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rounded_rectangle(rect, radius=28, fill=255)
        path = INPUT / f"p07_{name}_target_mask_v1.png"
        mask.save(path)
        masks[name] = path
    return {"plate": plate, **masks}


def graph(image_name: str, mask_name: str, prompt: str, lora: str, seed: int, prefix: str, denoise: float = 1.0) -> dict:
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "anima-aesthetic-v1.1.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_06b_base.safetensors", "type": "stable_diffusion", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": lora, "strength_model": 0.55, "model": ["1", 0]}},
        "5": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "6": {"class_type": "LoadImageMask", "inputs": {"image": mask_name, "channel": "red"}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "photograph, photorealistic, text, watermark, extra people, duplicate character, bad anatomy"}},
        "9": {"class_type": "VAEEncodeForInpaint", "inputs": {"pixels": ["5", 0], "vae": ["3", 0], "mask": ["6", 0], "grow_mask_by": 12}},
        "10": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["7", 0], "negative": ["8", 0], "latent_image": ["9", 0], "seed": seed, "steps": 42, "cfg": 4.0, "sampler_name": "er_sde", "scheduler": "simple", "denoise": denoise}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["3", 0]}},
        "12": {"class_type": "SaveImage", "inputs": {"images": ["11", 0], "filename_prefix": prefix}}
    }


def post_and_wait(payload: dict, request_id: str) -> tuple[str, str]:
    data = json.dumps({"prompt": payload, "client_id": request_id}).encode()
    req = urllib.request.Request(f"{HOST}/prompt", data=data, headers={"Content-Type": "application/json"})
    prompt_id = json.loads(urllib.request.urlopen(req, timeout=60).read())["prompt_id"]
    until = time.time() + 1800
    while time.time() < until:
        history = json.loads(urllib.request.urlopen(f"{HOST}/history/{prompt_id}", timeout=30).read())
        if prompt_id in history and history[prompt_id].get("status", {}).get("completed"):
            image = next(iter(history[prompt_id]["outputs"]["12"]["images"]))
            return prompt_id, image["filename"]
        time.sleep(3)
    raise TimeoutError(prompt_id)


def metrics(before: Path, after: Path, mask: Path) -> dict[str, float]:
    a = np.asarray(Image.open(before).convert("RGB"), dtype=np.float32) / 255.0
    b = np.asarray(Image.open(after).convert("RGB"), dtype=np.float32) / 255.0
    m = np.asarray(Image.open(mask).convert("L"), dtype=np.float32) > 127
    delta = np.abs(a - b).mean(axis=2)
    return {"target_mean_absolute_change": float(delta[m].mean()), "non_target_mean_absolute_change": float(delta[~m].mean())}


def run(seed: int, record_suffix: str | None = None) -> Path:
    assets = prepare()
    RECORDS.mkdir(parents=True, exist_ok=True)
    prompt_base = "drawn manhwa comic panel, old farmhouse kitchen at night, warm woodstove, table, two-person quiet domestic scene, bold ink outline, cel shading, "
    steps = [
        ("soren", "soren_v1.safetensors", prompt_base + "Soren, adult man with dark wavy hair and short beard, seated at left side of table, looking down, no other person"),
        ("sigrid", "sigrid_v1.safetensors", prompt_base + "Sigrid, adult woman with thick curly red-auburn hair and freckles, seated at right side of table, looking toward Soren, no extra person")
    ]
    prior = assets["plate"]
    record = {
        "schema_version": "1.1",
        "experiment": "sequential_inpaint_per_character",
        "adapter_version": "1.0",
        "seed": seed,
        "started_at": stamp(),
        "runtime": runtime_snapshot(),
        "custom_node_versions": custom_node_versions(),
        "model_hashes": model_inventory(),
        "source_code": {"path": "src/north_garden/sequential_inpaint.py", "sha256": digest(Path(__file__))},
        "base_plate": {"path": str(assets["plate"].relative_to(ROOT)).replace("\\", "/"), "sha256": digest(assets["plate"])},
        "steps": [],
        "commercial_profile": False,
        "human_minutes": None,
    }
    for index, (character, lora, prompt) in enumerate(steps, 1):
        source_name = str(prior.relative_to(COMFY / "input")).replace("\\", "/")
        mask_name = str(assets[character].relative_to(COMFY / "input")).replace("\\", "/")
        prefix = f"sequential_inpaint_v1/p07_seed{seed}_{index}_{character}"
        start = time.perf_counter()
        workflow = graph(source_name, mask_name, prompt, lora, seed + index - 1, prefix)
        prompt_id, filename = post_and_wait(workflow, f"sequential-{seed}-{character}")
        output = OUTPUT / filename
        next_input = INPUT / f"p07_seed{seed}_{index}_{character}.png"
        shutil.copy2(output, next_input)
        record["steps"].append({"character":character,"lora":lora,"prompt":prompt,"workflow":workflow,"workflow_sha256":hashlib.sha256(json.dumps(workflow,sort_keys=True).encode()).hexdigest(),"mask":{"path":str(assets[character].relative_to(ROOT)).replace('\\','/'),"sha256":digest(assets[character])},"input":{"path":str(prior.relative_to(ROOT)).replace('\\','/'),"sha256":digest(prior)},"output":{"path":str(output.relative_to(ROOT)).replace('\\','/'),"sha256":digest(output)},"prompt_id":prompt_id,"generation_seconds":round(time.perf_counter()-start,3),"measurements":metrics(prior,output,assets[character])})
        prior = next_input
    record["ended_at"] = stamp(); record["status"]="completed"; record["accepted_output"]=None
    suffix = f"-{record_suffix}" if record_suffix else ""
    path = RECORDS / f"p07-seed-{seed}{suffix}.json"
    if path.exists():
        raise FileExistsError(f"refusing to overwrite immutable experiment record: {path}; supply a new --record-suffix")
    path.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    return path


if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--prepare",action="store_true"); parser.add_argument("--seed",type=int); parser.add_argument("--record-suffix")
    args=parser.parse_args()
    if args.prepare: print(json.dumps({k:str(v) for k,v in prepare().items()},indent=2))
    elif args.seed is not None: print(run(args.seed, args.record_suffix))
    else: parser.error("choose --prepare or --seed")
