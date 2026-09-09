#!/usr/bin/env python3
"""Restore the local inputs named by preserved anchor-return call records."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    source, target = args.source.resolve(), args.target.resolve()
    if source == target or source in target.parents or target in source.parents:
        raise SystemExit("Source and target must be independent directory trees")
    requested = {}
    for call in sorted((target / "production/pilot-chapters/library").rglob("calls/*.json")):
        for ref in json.loads(call.read_text()).get("references", []):
            relative, expected = ref["path"], ref["sha256"]
            if not relative.startswith("production/anchor-return/") or ".." in Path(relative).parts:
                raise SystemExit(f"Unexpected archive reference: {relative}")
            if relative in requested and requested[relative] != expected:
                raise SystemExit(f"Conflicting recorded reference hashes: {relative}")
            requested[relative] = expected
    records = []
    for relative, expected in sorted(requested.items()):
        original, destination = source / relative, target / relative
        if not original.is_file() or original.is_symlink():
            raise SystemExit(f"Missing regular source: {original}")
        source_hash = digest(original)
        if source_hash != expected:
            raise SystemExit(f"Source differs from call reference: {relative}")
        action = "already-present"
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, destination)
            action = "copied"
        if destination.is_symlink() or digest(destination) != expected:
            raise SystemExit(f"Target differs from call reference: {relative}")
        if original.stat().st_ino == destination.stat().st_ino and original.stat().st_dev == destination.stat().st_dev:
            raise SystemExit(f"Unexpected shared inode: {relative}")
        records.append({"path": relative, "sha256": expected, "bytes": destination.stat().st_size, "action": action})
    report = {"schema": "NightglassArchiveInputRestore/1", "source": str(source), "target": str(target),
              "file_count": len(records), "bytes": sum(r["bytes"] for r in records), "files": records}
    (target / "research/nightglass-longform/assets/archive-inputs.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "files"}, indent=2))

if __name__ == "__main__":
    main()
