"""Measured wrapper for the existing Anima/ComfyUI regional-conditioning path.

This adapter deliberately reuses ``garden/gen3.py`` rather than improving its
graph.  It records an immutable request/attempt pair for each renderer call.
It is not a production-commercial profile and does not claim a canonical 3D
stage: the frozen gauntlet's semantic spatial mode remains intact while the
legacy execution limitation is stated in the record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GAUNTLET = ROOT / "research/authoritative/v2.1.1/bench/gauntlet.json"
STAGE_A = ROOT / "manifests/benchmark/stage-a-v1.json"
RECORDS = ROOT / "experiments/records/baseline_legacy"
COMFY = ROOT / "ComfyUI"
HOST = "http://127.0.0.1:8188"


@dataclass(frozen=True)
class RenderRequest:
    request_id: str
    benchmark_case_id: str
    semantic_spatial_mode: str
    seed: int
    adapter: str
    adapter_version: str
    prompt_compiler_version: str
    executable_bundle_state: str
    legacy_stage_limitation: str
    graph_inputs: dict[str, Any]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def runtime_snapshot() -> dict[str, Any]:
    snapshot: dict[str, Any] = {
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
    except Exception as exc:  # Runtime discovery must never prevent a record.
        snapshot["comfy_runtime_probe_error"] = repr(exc)
    return snapshot


def custom_node_versions() -> list[dict[str, str | None]]:
    nodes = COMFY / "custom_nodes"
    return [
        {"name": child.name, "commit": git_commit(child)}
        for child in sorted(nodes.iterdir())
        if child.is_dir() and not child.name.startswith("__")
    ]


def model_inventory() -> list[dict[str, str]]:
    relative = [
        "models/diffusion_models/anima-aesthetic-v1.1.safetensors",
        "models/text_encoders/qwen_3_06b_base.safetensors",
        "models/vae/qwen_image_vae.safetensors",
        "models/loras/soren_v1.safetensors",
        "models/loras/sigrid_v1.safetensors",
    ]
    rows = []
    for item in relative:
        path = COMFY / item
        rows.append({"path": item.replace("\\", "/"), "sha256": sha256(path) if path.exists() else "MISSING"})
    return rows


def load_cases() -> dict[str, dict[str, Any]]:
    return {case["id"]: case for case in json.loads(GAUNTLET.read_text(encoding="utf-8"))["render_cases"]}


def selected_stage_a_cases() -> list[tuple[dict[str, Any], int]]:
    source = json.loads(GAUNTLET.read_text(encoding="utf-8"))
    manifest = json.loads(STAGE_A.read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in source["render_cases"]}
    return [(cases[case_id], cases[case_id]["seeds"][index]) for case_id in manifest["case_ids"] for index in range(2)]


def prompt_for(case: dict[str, Any]) -> dict[str, Any]:
    """Translate frozen semantic intent minimally into the unchanged gen3 graph input.

    This compiler does not pretend to make the grounded cases spatially equivalent.
    It only makes its lossy legacy translation explicit and reproducible.
    """
    base = (
        "manhwa comic panel, strong graphic cel shading, bold ink outline, flat colour blocks, "
        "hard-edged shadow shapes, drawn illustration, old farmhouse setting at night, "
        "warm low-key woodstove and lamp light, deep shadow, deliberate narrative composition, "
    )
    desc = case["description"]
    cast = set(case["cast"])
    loras: list[list[Any]] = []
    regions: list[dict[str, Any]] = []
    if "SOREN" in cast:
        loras.append(["soren_v1.safetensors", 0.55])
    if "SIGRID" in cast:
        loras.append(["sigrid_v1.safetensors", 0.55])
    if cast == {"SOREN", "SIGRID"}:
        layout = case["manifest"].get("layout", {})
        left = layout.get("left", "SOREN")
        right = layout.get("right", "SIGRID")
        regions_by_character = {
            "SOREN": {"text": "manhwa, s0rn, adult man with dark wavy hair and short beard, " + desc, "strength": 1.0},
            "SIGRID": {"text": "manhwa, sgrd, adult woman with thick curly red-auburn hair and freckles, " + desc, "strength": 1.0},
        }
        regions_by_character[left]["area"] = [0.46, 1.0, 0.0, 0.0]
        regions_by_character[right]["area"] = [0.46, 1.0, 0.54, 0.0]
        regions = [
            regions_by_character[left],
            regions_by_character[right],
        ]
    elif "SOREN" in cast:
        regions = [{"text": "manhwa, s0rn, adult man with dark wavy hair and short beard, " + desc, "area": [1.0, 1.0, 0.0, 0.0], "strength": 1.0}]
    elif "SIGRID" in cast:
        regions = [{"text": "manhwa, sgrd, adult woman with thick curly red-auburn hair and freckles, " + desc, "area": [1.0, 1.0, 0.0, 0.0], "strength": 1.0}]
    else:
        regions = [{"text": "manhwa comic panel, " + desc, "area": [1.0, 1.0, 0.0, 0.0], "strength": 1.0}]
    return {
        "base": base + desc,
        "regions": regions,
        "neg": "photograph, photorealistic, live action, 3d render, text, watermark, extra people, duplicate character, bad anatomy",
        "w": 1216,
        "h": 832,
        "steps": 42,
        "cfg": 4.0,
        "prefix": f"baseline_legacy/{case['id']}",
        "loras": loras,
    }


def assert_comfy_available() -> None:
    try:
        with urllib.request.urlopen(f"{HOST}/system_stats", timeout=5) as response:
            if response.status != 200:
                raise RuntimeError(f"ComfyUI returned HTTP {response.status}")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("ComfyUI is unavailable at 127.0.0.1:8188; start the existing local service first.") from exc


def candidate_artifacts(results: list[str], prefix: str) -> list[dict[str, str]]:
    artifacts = []
    output_dir = COMFY / "output" / Path(prefix).parent
    for result in results:
        path = output_dir / result
        artifacts.append(
            {
                "comfy_output": result,
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(path) if path.exists() else "MISSING",
            }
        )
    return artifacts


def run_one(case: dict[str, Any], seed: int, dry_run: bool) -> Path:
    graph_inputs = prompt_for(case)
    graph_inputs["seed"] = seed
    request = RenderRequest(
        request_id=f"baseline_legacy-{case['id']}-{seed}",
        benchmark_case_id=case["id"],
        semantic_spatial_mode=case["spatial_mode"],
        seed=seed,
        adapter="baseline_legacy",
        adapter_version="1.0",
        prompt_compiler_version="baseline_legacy_prompt_v1",
        executable_bundle_state="NOT_YET_FROZEN",
        legacy_stage_limitation="No canonical 3D/control bundle exists. This is a lossy text-plus-mask legacy execution and is not comparable grounded-stage evidence.",
        graph_inputs=graph_inputs,
    )
    RECORDS.mkdir(parents=True, exist_ok=True)
    record_path = RECORDS / f"{request.request_id}.json"
    record: dict[str, Any] = {
        "schema_version": "1.0",
        "render_request": asdict(request),
        "input_state": case["manifest"],
        "semantic_description": case["description"],
        "runtime": runtime_snapshot(),
        "custom_node_versions": custom_node_versions(),
        "model_hashes": model_inventory(),
        "human_intervention": "none during renderer execution",
        "human_minutes": None,
        "accepted_output": None,
        "status": "planned" if dry_run else "started",
        "started_at": utc_now(),
    }
    if dry_run:
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return record_path
    assert_comfy_available()
    sys.path.insert(0, str(ROOT / "garden"))
    import gen3  # Existing adapter graph; intentionally imported only for execution.

    started = time.perf_counter()
    prompt_id = gen3.post(gen3.graph(**graph_inputs), request.request_id)
    results = gen3.wait(prompt_id)
    elapsed = time.perf_counter() - started
    record["ended_at"] = utc_now()
    record["generation_seconds"] = round(elapsed, 3)
    record["comfy_prompt_id"] = prompt_id
    record["generated_candidates"] = candidate_artifacts(results, graph_inputs["prefix"])
    record["status"] = "completed" if all(not result.startswith(("ERROR", "TIMEOUT")) for result in results) else "failed"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record_path


def initialize() -> None:
    manifest = json.loads(STAGE_A.read_text(encoding="utf-8"))
    if manifest["semantic_source_sha256"] == "TO_BE_FILLED_BY_BASELINE_INITIALIZATION":
        manifest["semantic_source_sha256"] = sha256(GAUNTLET)
        STAGE_A.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initialize", action="store_true", help="pin the local gauntlet source hash in the Stage-A manifest")
    parser.add_argument("--stage-a", action="store_true", help="run all 24 frozen Stage-A requests")
    parser.add_argument("--resume-stage-a", action="store_true", help="run only Stage-A requests without a completed record")
    parser.add_argument("--case", help="run one gauntlet case ID")
    parser.add_argument("--seed", type=int, help="seed for --case")
    parser.add_argument("--dry-run", action="store_true", help="write planned records without calling ComfyUI")
    args = parser.parse_args()
    if args.initialize:
        initialize()
    if args.stage_a or args.resume_stage_a:
        for case, seed in selected_stage_a_cases():
            record_path = RECORDS / f"baseline_legacy-{case['id']}-{seed}.json"
            if args.resume_stage_a and record_path.exists():
                existing = json.loads(record_path.read_text(encoding="utf-8"))
                if existing.get("status") == "completed":
                    print(f"SKIP completed {record_path}")
                    continue
            print(run_one(case, seed, args.dry_run))
    elif args.case:
        case = load_cases()[args.case]
        seed = args.seed if args.seed is not None else case["seeds"][0]
        print(run_one(case, seed, args.dry_run))
    elif not args.initialize:
        parser.error("choose --initialize, --stage-a, --resume-stage-a, or --case")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
