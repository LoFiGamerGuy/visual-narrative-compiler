"""Pin and validate an exact safe-source Git commit inventory."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from validate_tracked_source_scope import ALLOWED_TOP, PROHIBITED_SUFFIXES, PROHIBITED_TOP, PUBLIC_CONTROLS


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMMIT = "f5057885b9c953ba102f9b577be229fa42c64ad3"
OUTPUT = ROOT / "docs/research/evidence/safe-source-release-manifest-f505788.json"
SHA1 = re.compile(r"^[0-9a-f]{40}$")


class ReleaseError(RuntimeError): pass


def require(value: bool, message: str) -> None:
    if not value: raise ReleaseError(message)


def git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if result.returncode: raise ReleaseError(f"git {' '.join(args)} failed")
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def inventory(commit: str) -> list[dict]:
    raw = git("ls-tree", "-r", "-l", "-z", commit, binary=True)
    entries = []
    for value in raw.split(b"\0"):
        if not value: continue
        metadata, path_bytes = value.split(b"\t", 1)
        mode, kind, object_id, size = metadata.decode().split()
        require(kind == "blob", "release contains non-blob leaf")
        path = path_bytes.decode("utf-8")
        content = git("cat-file", "blob", object_id, binary=True)
        require(len(content) == int(size), f"blob size mismatch: {path}")
        entries.append({"path": path, "mode": mode, "bytes": int(size), "git_blob_oid": object_id, "sha256": hashlib.sha256(content).hexdigest()})
    return sorted(entries, key=lambda item: item["path"])


def root_hash(entries: list[dict]) -> str:
    return hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def scope_errors(entries: list[dict]) -> list[str]:
    errors = []
    public = {}
    for entry in entries:
        relative = Path(entry["path"]); top = relative.parts[0]
        if top not in ALLOWED_TOP: errors.append(f"out-of-scope path: {entry['path']}")
        if top in PROHIBITED_TOP: errors.append(f"prohibited top: {entry['path']}")
        if relative.suffix.casefold() in PROHIBITED_SUFFIXES: errors.append(f"prohibited suffix: {entry['path']}")
        if entry["bytes"] > 10 * 1024 * 1024: errors.append(f"oversize source: {entry['path']}")
        if top == "public-controls": public[entry["path"]] = entry["sha256"]
    if public != PUBLIC_CONTROLS: errors.append("public controls differ")
    return errors


def build(commit: str) -> dict:
    full_commit = git("rev-parse", commit)
    require(SHA1.fullmatch(full_commit) is not None, "commit invalid")
    entries = inventory(full_commit)
    require(not scope_errors(entries), "; ".join(scope_errors(entries)))
    return {
        "record_type": "SafeSourceReleaseManifest", "schema_version": "1.0",
        "record_id": "ng-safe-source-release-f505788", "state": "PINNED_SAFE_SOURCE_COMMIT_PUSHED",
        "repository": "https://github.com/LoFiGamerGuy/visual-narrative-compiler",
        "captured_commit": full_commit, "captured_tree": git("rev-parse", f"{full_commit}^{{tree}}"),
        "captured_origin_main_commit": full_commit, "remote_parity_at_capture": True,
        "summary": {"tracked_paths": len(entries), "total_bytes": sum(item["bytes"] for item in entries), "inventory_root_sha256": root_hash(entries), "public_controls": 2, "generated_experiment_paths": 0, "prohibited_extensions": 0, "files_over_10_mib": 0},
        "entries": entries,
        "explicit_exclusions": [".env and provider credentials", "experiments and generated candidates/review presentations/runtime records", "model weights, LoRAs, checkpoints, installed runtimes and caches", "datasets and private or likeness references", "local runtime declaration", "same-disk evidence archives"],
        "boundary": "This manifest pins source and non-art evidence only. It is not an artifact release, model package, dataset, candidate review, commercial clearance, or production authority.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    item = copy.deepcopy(expected); item["captured_commit"] = "0" * 40; values.append(item)
    item = copy.deepcopy(expected); item["captured_tree"] = "0" * 40; values.append(item)
    item = copy.deepcopy(expected); item["summary"]["tracked_paths"] -= 1; values.append(item)
    item = copy.deepcopy(expected); item["summary"]["inventory_root_sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["entries"].pop(); values.append(item)
    item = copy.deepcopy(expected); item["entries"][0]["sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["summary"]["generated_experiment_paths"] = 1; values.append(item)
    item = copy.deepcopy(expected); item["explicit_exclusions"].remove(".env and provider credentials"); values.append(item)
    return sum(value != expected for value in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); parser.add_argument("--commit", default=DEFAULT_COMMIT); parser.add_argument("--allow-unpushed-current", action="store_true"); args = parser.parse_args()
    try:
        expected = build(args.commit)
        if args.emit:
            require(git("rev-parse", "HEAD") == expected["captured_commit"], "capture commit is not HEAD")
            require(git("rev-parse", "origin/main") == expected["captured_commit"], "capture commit is not pushed origin/main")
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else: require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked safe-source manifest differs")
        rejected, total = mutations(expected); require(rejected == total, "mutation rejection incomplete")
        require(subprocess.run([sys.executable, "src/north_garden/validate_tracked_source_scope.py"], cwd=ROOT).returncode == 0, "current tracked scope invalid")
        require(subprocess.run(["git", "merge-base", "--is-ancestor", expected["captured_commit"], "HEAD"], cwd=ROOT).returncode == 0, "release commit is not ancestor of HEAD")
        if not args.allow_unpushed_current: require(git("rev-parse", "HEAD") == git("rev-parse", "origin/main"), "current HEAD is not at origin/main")
    except (ReleaseError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    s = expected["summary"]
    print(f"0 failures, 0 warnings ({s['tracked_paths']} paths/{s['total_bytes']} bytes; tree {expected['captured_tree']}; root {s['inventory_root_sha256']})")
    print(f"two public controls; zero generated/prohibited/oversize paths; {rejected}/{total} mutations rejected; current scope and remote parity valid")
    return 0


if __name__ == "__main__": raise SystemExit(main())
