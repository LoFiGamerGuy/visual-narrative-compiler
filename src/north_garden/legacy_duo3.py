"""Instrumented local-only adult fictional production demonstration.

This adapter intentionally reuses the existing local Anima/LoRA graph without
changing the frozen baseline arm. It is never a commercial or benchmark route.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMFY = ROOT / "ComfyUI"
PROFILE = ROOT / "experiments/render-profiles/legacy-duo3-local-r1.json"
RECORDS = ROOT / "experiments/records/legacy_duo3"
PROHIBITED = ("1boy", "1girl", " child", " kid", " minor", "underage")

JOBS = [
    {
        "panel_id": "ng-ch03-sc01-p001",
        "seed": 532301,
        "beat": "Two adult protagonists cross a rain-dark ridge; Sigrid leads and Soren looks back toward the threat.",
        "prompt": "drawn dark-fantasy webcomic panel, confident ink linework, flat color blocks, hard-edged shadows, rain-dark wooded ridge at night, deliberate directional composition, two adult protagonists only: adult man Soren, dark wavy hair and short beard, pale oatmeal work coat, looks back over his shoulder; adult woman Sigrid, curly red-auburn hair, freckles, blue knotwork tattoos, plaid wrap and two short axes, leads ahead through wet undergrowth; no one faces the viewer, movement from lower left toward upper right",
    },
    {
        "panel_id": "ng-ch03-sc01-p002",
        "seed": 532302,
        "beat": "Soren holds a small black field at the path while Sigrid clears a route through roots; their roles are spatially distinct.",
        "prompt": "drawn dark-fantasy webcomic panel, confident ink linework, flat color blocks, hard-edged shadows, wet forest path at night, deliberate asymmetric action composition, exactly two adult protagonists: adult man Soren with dark wavy hair, short beard, pale oatmeal work coat, screen-left holding a small controlled black field away from his body; adult woman Sigrid with curly red-auburn hair, freckles, blue knotwork tattoos, plaid wrap and two short axes, screen-right clearing roots from the path; distinct roles, no extra people, no animal, no creature, no one looks at the viewer",
    },
    {
        "panel_id": "ng-ch03-sc01-p003",
        "seed": 532303,
        "beat": "At the farmhouse threshold, Sigrid watches the dark while Soren remains behind her; the quiet composition resolves the movement.",
        "prompt": "drawn dark-fantasy webcomic panel, confident ink linework, flat color blocks, hard-edged shadows, old farmhouse threshold at night with rain-dark woods beyond, quiet narrative composition, exactly two adult protagonists: adult woman Sigrid with curly red-auburn hair, freckles, blue knotwork tattoos, plaid wrap and two short axes at the open doorway facing outward; adult man Soren with dark wavy hair, short beard, pale oatmeal work coat, farther inside in shadow looking past her; clear depth separation, no extra people, no one faces the viewer",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_commit(path: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def validate_profile() -> dict[str, object]:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    assert profile["adapter"] == "legacy_duo3"
    for model in profile["models"]:
        path = ROOT / model["path"]
        assert path.exists() and sha256(path) == model["expected_sha256"], path
    return profile


def assert_safe(prompt: str) -> None:
    lowered = " " + prompt.lower()
    assert "adult man" in lowered and "adult woman" in lowered
    assert not any(token in lowered for token in PROHIBITED), "child-coded token found in adult prompt"


def runtime() -> dict[str, object]:
    return {"python": sys.version, "platform": platform.platform(), "comfy_commit": git_commit(COMFY)}


def run(dry_run: bool) -> list[Path]:
    profile = validate_profile()
    sys.path.insert(0, str(ROOT / "garden"))
    import gen2

    RECORDS.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for job in JOBS:
        assert_safe(job["prompt"])
        prefix = f"{profile['output_prefix']}/{job['panel_id']}"
        # gen2.graph is the established local global-LoRA execution graph.
        graph_inputs = {
            "pos": job["prompt"],
            "neg": "photograph, photorealistic, live action, 3d render, text, watermark, extra person, duplicate person, animal, creature, bull, cow",
            "w": 1216,
            "h": 1216,
            "seed": job["seed"],
            "steps": 42,
            "cfg": 4.0,
            "prefix": prefix,
            "loras": [["soren_v1.safetensors", 0.45], ["sigrid_v1.safetensors", 0.45]],
        }
        # The prompt is full-frame and the two identity LoRAs remain global: document this known limitation instead of claiming regional identity.
        graph = gen2.graph(**graph_inputs)
        record = {
            "record_type": "RenderRecord",
            "schema_version": "1.0",
            "record_id": f"legacy_duo3-{job['panel_id']}-{job['seed']}",
            "adapter": "legacy_duo3",
            "profile_path": str(PROFILE.relative_to(ROOT)).replace("\\", "/"),
            "profile_sha256": sha256(PROFILE),
            "panel_id": job["panel_id"],
            "narrative_beat": job["beat"],
            "intent_boundary": "This execution record is not a ComicPanelPlan and does not contain animation-shot direction.",
            "input_state": {"seed": job["seed"], "workflow_graph": graph, "workflow_graph_sha256": hashlib.sha256(json.dumps(graph, sort_keys=True).encode()).hexdigest()},
            "runtime": runtime(),
            "model_hashes": [{"path": model["path"], "sha256": model["expected_sha256"], "license_state": model["license_state"]} for model in profile["models"]],
            "safety": {"adult_only_prompt_check": "pass", "external_upload": False, "child_data": False},
            "known_execution_limit": "Both adult-likeness LoRAs attach globally to the model. This is a local legacy production demo, not a role-binding benchmark arm.",
            "human_review_status": "pending", "human_minutes": None, "accepted_output": None,
            "status": "planned" if dry_run else "started", "started_at": utc_now(),
        }
        record_path = RECORDS / f"{record['record_id']}.json"
        if dry_run:
            # A dry run validates profile/prompt/graph construction only. It
            # must never overwrite an immutable completed RenderRecord.
            print(f"DRY RUN (no record written): {record_path}")
            continue
        if not dry_run:
            started = time.perf_counter()
            prompt_id = gen2.post(graph, record["record_id"])
            filenames = gen2.wait(prompt_id)
            record["generation_seconds"] = round(time.perf_counter() - started, 3)
            record["comfy_prompt_id"] = prompt_id
            record["ended_at"] = utc_now()
            candidates = []
            for filename in filenames:
                path = COMFY / "output" / Path(prefix).parent / filename
                candidates.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path) if path.exists() else "MISSING"})
            record["generated_candidates"] = candidates
            record["status"] = "completed" if all(item["sha256"] != "MISSING" for item in candidates) else "failed"
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        written.append(record_path)
        print(record_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
