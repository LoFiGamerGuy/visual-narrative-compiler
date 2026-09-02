"""Copy and register one built-in ImageGen non-canon concept output."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "experiments/review-packets/future-litrpg-visual-concepts-r1/prompt-manifest.json"
REGISTRY = ROOT / "experiments/review-packets/future-litrpg-visual-concepts-r1/candidate-registry.json"
GENERATED_ROOT = (Path.home() / ".codex/generated_images").resolve()


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
        raise SystemExit("source is outside built-in generated_images") from error
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prompt = next((item for item in manifest["entries"] if item["candidate_id"] == args.candidate), None)
    if prompt is None:
        raise SystemExit("candidate absent from manifest")
    destination = Path(prompt["output_path"]).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and sha256(destination) != sha256(source):
        raise SystemExit("destination exists with different bytes")
    if not destination.exists():
        shutil.copy2(source, destination)
    with Image.open(destination) as image:
        width, height, mode = image.width, image.height, image.mode
    entry = {
        "candidate_id": prompt["candidate_id"],
        "concept_id": prompt["concept_id"],
        "format_role": prompt["format_role"],
        "prompt": prompt["prompt"],
        "prompt_sha256": prompt["prompt_sha256"],
        "references": prompt["references"],
        "output": {"path": destination.relative_to(ROOT).as_posix(), "sha256": sha256(destination), "bytes": destination.stat().st_size, "width": width, "height": height, "mode": mode},
        "execution": {"tool_mode": "OpenAI built-in ImageGen in Codex", "elapsed_seconds": round(args.elapsed_seconds, 3), "model": None, "endpoint": None, "provider_request_id": None, "usage": None, "cost_usd": None},
        "canon_status": "NONCANON_FUTURE_EXPLORATION",
        "state": "GENERATED_UNREVIEWED",
        "human_minutes": None,
        "accepted": False
    }
    registry = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {"record_type": "FutureLitRPGConceptRegistry", "schema_version": "1.0", "record_id": "ng-future-litrpg-concept-registry-r1", "entries": []}
    by_id = {item["candidate_id"]: item for item in registry["entries"]}
    if args.candidate in by_id and by_id[args.candidate] != entry:
        raise SystemExit("candidate already registered differently")
    by_id[args.candidate] = entry
    registry["entries"] = [by_id[key] for key in sorted(by_id)]
    registry["candidate_count"] = len(registry["entries"])
    registry["total_elapsed_seconds"] = round(sum(item["execution"]["elapsed_seconds"] for item in registry["entries"]), 3)
    registry["state"] = "COMPLETE_UNREVIEWED" if len(registry["entries"]) == 3 else "IN_PROGRESS_UNREVIEWED"
    registry["boundary"] = "Non-canon ignored concepts only; no CH05 revision, acceptance, commercial clearance, or exact-base status."
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"registered {args.candidate}: {destination.relative_to(ROOT)} {entry['output']['sha256']} {width}x{height}; {registry['candidate_count']}/3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
