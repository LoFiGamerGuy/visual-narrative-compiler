"""Copy and register a built-in ImageGen output without overwriting local evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "experiments/review-packets/ch05-overnight-production-r1/prompt-manifest.json"
REGISTRY = ROOT / "experiments/review-packets/ch05-overnight-production-r1/candidate-registry.json"
GENERATED_ROOT = (Path.home() / ".codex" / "generated_images").resolve()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--elapsed-seconds", type=float, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    try:
        source.relative_to(GENERATED_ROOT)
    except ValueError as error:
        raise SystemExit("source is outside the built-in generated_images root") from error
    prompt_manifest = json.loads(PROMPTS.read_text(encoding="utf-8"))
    prompt = next((item for item in prompt_manifest["entries"] if item["candidate_id"] == args.candidate), None)
    if prompt is None:
        raise SystemExit("candidate absent from prompt manifest")
    destination = Path(prompt["output_path"]).resolve()
    try:
        destination.relative_to(ROOT.resolve())
    except ValueError as error:
        raise SystemExit("destination escapes workspace") from error
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if sha256(destination) != sha256(source):
            raise SystemExit("destination already exists with different bytes")
    else:
        shutil.copy2(source, destination)
    with Image.open(destination) as image:
        width, height = image.size
        mode = image.mode
    entry = {
        "candidate_id": args.candidate,
        "panel_id": prompt["panel_id"],
        "plan_revision_id": prompt["plan_revision_id"],
        "style_id": prompt["style_id"],
        "format_role": prompt["format_role"],
        "prompt_sha256": prompt["prompt_sha256"],
        "prompt": prompt["prompt"],
        "references": prompt["references"],
        "output": {
            "path": destination.relative_to(ROOT).as_posix(),
            "sha256": sha256(destination),
            "bytes": destination.stat().st_size,
            "width": width,
            "height": height,
            "mode": mode,
        },
        "execution": {
            "tool_mode": "OpenAI built-in ImageGen in Codex",
            "elapsed_seconds": round(args.elapsed_seconds, 3),
            "model": None,
            "endpoint": None,
            "provider_request_id": None,
            "usage": None,
            "cost_usd": None,
            "existing_art_reference_uploads": len(prompt["references"]),
        },
        "state": "GENERATED_UNREVIEWED",
        "human_minutes": None,
        "accepted": False,
    }
    if REGISTRY.exists():
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    else:
        registry = {
            "record_type": "CH05OvernightCandidateRegistry",
            "schema_version": "1.0",
            "record_id": "ng-ch05-overnight-candidate-registry-r1",
            "state": "IN_PROGRESS_UNREVIEWED",
            "prompt_manifest_sha256": sha256(PROMPTS),
            "entries": [],
            "boundary": "Ignored local pixels and exact prompts only; no candidate is accepted or commercially cleared.",
        }
    entries = {item["candidate_id"]: item for item in registry["entries"]}
    if args.candidate in entries and entries[args.candidate] != entry:
        raise SystemExit("candidate already registered with different evidence")
    entries[args.candidate] = entry
    registry["entries"] = [entries[key] for key in sorted(entries)]
    registry["generated_candidates"] = len(registry["entries"])
    registry["distinct_panel_plans"] = len({item["panel_id"] for item in registry["entries"]})
    registry["total_elapsed_seconds"] = round(sum(item["execution"]["elapsed_seconds"] for item in registry["entries"]), 3)
    registry["total_reference_uploads"] = sum(item["execution"]["existing_art_reference_uploads"] for item in registry["entries"])
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"registered {args.candidate}: {destination.relative_to(ROOT)} {entry['output']['sha256']} {width}x{height}")
    print(f"registry: {registry['generated_candidates']} candidates/{registry['distinct_panel_plans']} plans/{registry['total_elapsed_seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
