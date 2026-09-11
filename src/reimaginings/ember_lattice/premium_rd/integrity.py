from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROTECTED_WORKTREES = (
    Path(r"C:\AgentWorkspaces\anime-pipeline"),
    Path(r"C:\AgentWorkspaces\anime-pipeline-ember-lattice-premium-rd-20260904-150943"),
    Path(r"C:\AgentWorkspaces\anime-pipeline-litrpg-manhwa-20260904-001211"),
    Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining"),
    Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining-20260903"),
    Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining-clean-webtoon-20260903-213010"),
)

EXCLUDED_NEW_WORK_MARKERS = (
    "ember-lattice-premium-rd-20260904-150943",
    "ember-lattice-editorial-gear-20260904",
)


def _git(worktree: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=worktree, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def _inventory_digest(worktree: Path, ignored: bool) -> dict[str, Any]:
    args = ["ls-files", "--others", "-z"]
    if ignored:
        args.extend(["--ignored", "--exclude-standard"])
    else:
        args.append("--exclude-standard")
    paths = sorted(value for value in _git(worktree, *args).split("\0") if value)
    digest = hashlib.sha256()
    total_bytes = 0
    present = 0
    for relative in paths:
        target = worktree / relative
        if not target.is_file():
            continue
        stat = target.stat()
        present += 1
        total_bytes += stat.st_size
        digest.update(f"{relative}\0{stat.st_size}\0{stat.st_mtime_ns}\n".encode("utf-8"))
    return {
        "file_count": present,
        "total_bytes": total_bytes,
        "path_size_mtime_sha256": digest.hexdigest(),
    }


def _protected_refs(repo: Path) -> dict[str, str]:
    rows = _git(repo, "for-each-ref", "--format=%(refname)%09%(objectname)").splitlines()
    refs: dict[str, str] = {}
    for row in rows:
        name, object_id = row.split("\t", 1)
        if any(marker in name for marker in EXCLUDED_NEW_WORK_MARKERS):
            continue
        refs[name] = object_id
    return dict(sorted(refs.items()))


def snapshot() -> dict[str, Any]:
    worktrees: dict[str, Any] = {}
    for path in PROTECTED_WORKTREES:
        worktrees[str(path)] = {
            "head": _git(path, "rev-parse", "HEAD").strip(),
            "branch": _git(path, "branch", "--show-current").strip(),
            "status_porcelain": _git(path, "status", "--porcelain=v1", "--untracked-files=all").splitlines(),
            "untracked_inventory": _inventory_digest(path, ignored=False),
            "ignored_inventory": _inventory_digest(path, ignored=True),
        }
    return {
        "schema": "EmberLatticePremiumProtectedState/1.0",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Tracked state is pinned by HEAD/status/ref OIDs. Untracked and ignored assets are fingerprinted by sorted path, byte size, and nanosecond mtime without reading heavyweight model contents.",
        "protected_refs": _protected_refs(PROTECTED_WORKTREES[0]),
        "protected_worktrees": worktrees,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def comparable(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "protected_refs": value["protected_refs"],
        "protected_worktrees": value["protected_worktrees"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Snapshot and compare protected Ember Lattice repository state")
    parser.add_argument("mode", choices=("before", "after"))
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    current = snapshot()
    if args.mode == "before":
        write_json(args.before, current)
        print(json.dumps({"status": "PASS", "output": str(args.before)}, indent=2))
        return 0
    if args.output is None:
        parser.error("after mode requires --output")
    baseline = json.loads(args.before.read_text(encoding="utf-8"))
    matches = comparable(baseline) == comparable(current)
    current["comparison"] = {
        "baseline": str(args.before),
        "protected_state_unchanged": matches,
        "status": "PASS" if matches else "FAIL",
    }
    write_json(args.output, current)
    print(json.dumps(current["comparison"], indent=2))
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
