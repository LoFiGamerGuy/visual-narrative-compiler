#!/usr/bin/env python3
"""Copy missing baseline dependencies without modifying or linking source files."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOTS = ("production/pilot-chapters", "research/pilot-chapters/reader/phone-captures/final-v1")

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def reader_dependencies(data):
    found = set()
    def walk(value):
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str):
            if value.startswith("../../"):
                found.add(value[6:])
            elif value.startswith(("production/", "research/")):
                found.add(value)
    walk(data)
    return sorted(found)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    source, target = args.source.resolve(), args.target.resolve()
    if source == target or source in target.parents or target in source.parents:
        raise SystemExit("Source and target must be independent directory trees")
    records = []
    for root in ROOTS:
        for original in sorted((source / root).rglob("*")):
            if not original.is_file():
                continue
            if original.is_symlink():
                raise SystemExit(f"Refusing source symlink: {original}")
            relative = original.relative_to(source)
            destination = target / relative
            action = "already-present"
            source_hash = digest(original)
            if not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original, destination)
                action = "copied"
            if destination.is_symlink():
                raise SystemExit(f"Refusing target symlink: {destination}")
            target_hash = digest(destination)
            if action == "copied" and target_hash != source_hash:
                raise SystemExit(f"Copy verification failed: {relative}")
            if original.stat().st_ino == destination.stat().st_ino and original.stat().st_dev == destination.stat().st_dev:
                raise SystemExit(f"Unexpected shared inode: {relative}")
            records.append({"path": str(relative), "bytes": original.stat().st_size,
                            "source_sha256": source_hash, "target_sha256": target_hash,
                            "action": action, "matches_source": target_hash == source_hash})
    data = json.loads((source / "docs/pilot-chapters/data.json").read_text())
    dependencies = reader_dependencies(data)
    missing = [path for path in dependencies if not (target / path).is_file()]
    native_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    native = [record for record in records if Path(record["path"]).suffix.lower() in native_extensions]
    copied = [record for record in records if record["action"] == "copied"]
    report = {"schema": "NightglassBaselineAssetImport/1", "source": str(source), "target": str(target),
              "roots": ROOTS, "source_file_count": len(records), "source_bytes": sum(x["bytes"] for x in records),
              "copied_file_count": len(copied), "copied_bytes": sum(x["bytes"] for x in copied),
              "native_image_count": len(native), "native_hash_mismatches": [x["path"] for x in native if not x["matches_source"]],
              "reader_dependency_count": len(dependencies), "missing_reader_dependencies": missing,
              "reader_dependencies": dependencies, "files": records}
    output = target / "research/nightglass-longform/assets/baseline-import.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("files", "reader_dependencies")}, indent=2))
    if missing or report["native_hash_mismatches"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
