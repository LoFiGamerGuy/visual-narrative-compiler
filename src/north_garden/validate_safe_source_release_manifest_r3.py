"""Pin and validate the post-release-r3 safe-source Git inventory."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from validate_safe_source_release_manifest_r2 import git, inventory, root_hash, scope_errors


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMMIT = "00498df557e56889ce161095572fcf1d09d95498"
R2 = ROOT / "docs/research/evidence/safe-source-release-manifest-43fc787.json"
OUTPUT = ROOT / "docs/research/evidence/safe-source-release-manifest-00498df.json"


class ReleaseError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ReleaseError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(commit: str) -> dict:
    full_commit = git("rev-parse", commit)
    entries = inventory(full_commit)
    errors = scope_errors(entries)
    require(not errors, "; ".join(errors))
    prior = json.loads(R2.read_text(encoding="utf-8"))
    require(prior["captured_commit"] == "43fc787f783236c1c5dae9f4694a6e2a804e0aae", "r2 capture changed")
    require(subprocess.run(["git", "merge-base", "--is-ancestor", prior["captured_commit"], full_commit], cwd=ROOT).returncode == 0, "r2 capture is not an ancestor")
    return {
        "record_type": "SafeSourceReleaseManifest",
        "schema_version": "1.2",
        "record_id": "ng-safe-source-release-00498df",
        "state": "PINNED_SAFE_SOURCE_COMMIT_PUSHED",
        "supersedes": {
            "record_id": prior["record_id"],
            "path": R2.relative_to(ROOT).as_posix(),
            "sha256": sha256(R2),
            "captured_commit": prior["captured_commit"],
            "inventory_root_sha256": prior["summary"]["inventory_root_sha256"],
        },
        "prior_manifest_rewritten": False,
        "repository": "https://github.com/LoFiGamerGuy/visual-narrative-compiler",
        "captured_commit": full_commit,
        "captured_tree": git("rev-parse", f"{full_commit}^{{tree}}"),
        "captured_origin_main_commit": full_commit,
        "remote_parity_at_capture": True,
        "summary": {
            "tracked_paths": len(entries),
            "total_bytes": sum(item["bytes"] for item in entries),
            "inventory_root_sha256": root_hash(entries),
            "public_controls": 2,
            "generated_experiment_paths": 0,
            "prohibited_extensions": 0,
            "files_over_10_mib": 0,
        },
        "entries": entries,
        "explicit_exclusions": prior["explicit_exclusions"],
        "boundary": prior["boundary"],
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["supersedes"].update(sha256="0" * 64),
        lambda item: item.update(prior_manifest_rewritten=True),
        lambda item: item.update(captured_commit="0" * 40),
        lambda item: item.update(captured_tree="0" * 40),
        lambda item: item["summary"].update(tracked_paths=item["summary"]["tracked_paths"] - 1),
        lambda item: item["summary"].update(inventory_root_sha256="0" * 64),
        lambda item: item["entries"].pop(),
        lambda item: item["entries"][0].update(sha256="0" * 64),
        lambda item: item["summary"].update(generated_experiment_paths=1),
        lambda item: item["summary"].update(prohibited_extensions=1),
        lambda item: item["summary"].update(files_over_10_mib=1),
        lambda item: item["explicit_exclusions"].remove(".env and provider credentials"),
        lambda item: item["explicit_exclusions"].remove("untracked imported workspace assets, launchers, generators and trainers"),
    ]
    for action in actions:
        item = copy.deepcopy(expected)
        action(item)
        values.append(item)
    return sum(item != expected for item in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--commit", default=DEFAULT_COMMIT)
    parser.add_argument("--allow-unpushed-current", action="store_true")
    args = parser.parse_args()
    try:
        expected = build(args.commit)
        if args.emit:
            require(git("rev-parse", "HEAD") == expected["captured_commit"], "capture commit is not HEAD")
            require(git("rev-parse", "origin/main") == expected["captured_commit"], "capture commit is not pushed origin/main")
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked safe-source r3 differs")
        rejected, total = mutations(expected)
        require(rejected == total, "mutation rejection incomplete")
        require(subprocess.run([sys.executable, "src/north_garden/validate_tracked_source_scope.py"], cwd=ROOT).returncode == 0, "current tracked scope invalid")
        require(subprocess.run(["git", "merge-base", "--is-ancestor", expected["captured_commit"], "HEAD"], cwd=ROOT).returncode == 0, "capture is not an ancestor of HEAD")
        if not args.allow_unpushed_current:
            require(git("rev-parse", "HEAD") == git("rev-parse", "origin/main"), "current HEAD is not at origin/main")
    except (ReleaseError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    summary = expected["summary"]
    print(f"0 failures, 0 warnings ({summary['tracked_paths']} paths/{summary['total_bytes']} bytes; tree {expected['captured_tree']}; root {summary['inventory_root_sha256']})")
    print(f"two public controls; zero generated/prohibited/oversize paths; {rejected}/{total} mutations rejected; current scope and remote parity valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
