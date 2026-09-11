from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


THIS_WORKTREE = Path(__file__).resolve().parents[3]
ORIGINAL_ROOT = Path(r"C:\AgentWorkspaces\anime-pipeline")
PROTECTED_WORKTREES = [
    ORIGINAL_ROOT,
    Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining"),
    Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining-20260903"),
    Path(r"C:\AgentWorkspaces\anime-pipeline-reimagining-clean-webtoon-20260903-213010"),
]
OUT_DIR = THIS_WORKTREE / "production" / "reimaginings" / "ember-lattice" / "integrity"


def git(path: Path, *args: str, binary: bool = False) -> str | bytes:
    return subprocess.check_output(
        ["git", "-C", str(path), *args],
        text=not binary,
        encoding=None if binary else "utf-8",
        errors=None if binary else "replace",
    )


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nul_paths(path: Path, *args: str) -> list[str]:
    raw = git(path, *args, "-z", binary=True)
    return sorted(item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item)


def manifest_digest(rows: list[str]) -> str:
    return hashlib.sha256("\n".join(rows).encode("utf-8", "surrogateescape")).hexdigest()


def capture_worktree(path: Path) -> dict[str, Any]:
    tracked_status = git(path, "status", "--porcelain=v1", "--untracked-files=no").splitlines()
    untracked = nul_paths(path, "ls-files", "--others", "--exclude-standard")
    untracked_rows: list[dict[str, Any]] = []
    for rel in untracked:
        target = path / rel
        if target.is_file():
            stat = target.stat()
            untracked_rows.append({"path": rel.replace("\\", "/"), "bytes": stat.st_size, "sha256": file_hash(target)})
    ignored = nul_paths(path, "ls-files", "--others", "--ignored", "--exclude-standard")
    ignored_rows: list[str] = []
    ignored_bytes = 0
    for rel in ignored:
        target = path / rel
        if target.is_file():
            stat = target.stat()
            ignored_bytes += stat.st_size
            ignored_rows.append(f"{rel.replace('\\', '/')}\0{stat.st_size}\0{stat.st_mtime_ns}")
    return {
        "path": str(path),
        "head": git(path, "rev-parse", "HEAD").strip(),
        "branch": git(path, "branch", "--show-current").strip(),
        "tracked_status": tracked_status,
        "untracked_nonignored_count": len(untracked_rows),
        "untracked_nonignored": untracked_rows,
        "ignored_file_count": len(ignored_rows),
        "ignored_total_bytes": ignored_bytes,
        "ignored_path_size_mtime_manifest_sha256": manifest_digest(ignored_rows),
        "ignored_note": "Privacy-preserving digest covers each ignored path, byte size, and nanosecond mtime; ignored names and contents are not written to tracked evidence.",
    }


def capture() -> dict[str, Any]:
    return {
        "schema": "ProtectedWorktreeSnapshot/1.0",
        "protected_worktrees": [capture_worktree(path) for path in PROTECTED_WORKTREES],
        "phase_a_worktree": {
            "path": str(THIS_WORKTREE),
            "head": git(THIS_WORKTREE, "rev-parse", "HEAD").strip(),
            "branch": git(THIS_WORKTREE, "branch", "--show-current").strip(),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("label", choices=["before", "after"])
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    current = capture()
    destination = OUT_DIR / f"protected-state-{args.label}.json"
    destination.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if args.label == "after":
        before = json.loads((OUT_DIR / "protected-state-before.json").read_text(encoding="utf-8"))
        invariant_fields = [
            "path", "head", "branch", "tracked_status", "untracked_nonignored_count",
            "untracked_nonignored", "ignored_file_count", "ignored_total_bytes",
            "ignored_path_size_mtime_manifest_sha256",
        ]
        comparisons = []
        for left, right in zip(before["protected_worktrees"], current["protected_worktrees"], strict=True):
            changed = [field for field in invariant_fields if left[field] != right[field]]
            comparisons.append({"path": left["path"], "status": "PASS" if not changed else "FAIL", "changed_fields": changed})
        report = {
            "schema": "ProtectedWorktreeIntegrityReport/1.0",
            "status": "PASS" if all(row["status"] == "PASS" for row in comparisons) else "FAIL",
            "comparisons": comparisons,
            "phase_a_worktree": current["phase_a_worktree"],
        }
        (OUT_DIR / "integrity-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        if report["status"] != "PASS":
            raise SystemExit("Protected worktree integrity comparison failed")
        print(json.dumps(report, indent=2))
    else:
        print(json.dumps({"status": "CAPTURED", "destination": str(destination)}, indent=2))


if __name__ == "__main__":
    main()
