"""Validate the current local main/origin parity without network access."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_REMOTE = "https://github.com/LoFiGamerGuy/visual-narrative-compiler"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8").stdout.strip()


def main() -> int:
    branch = git("branch", "--show-current")
    head = git("rev-parse", "HEAD")
    origin = git("rev-parse", "origin/main")
    remote = git("remote", "get-url", "origin").removesuffix(".git")
    staged_clean = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0
    tracked_clean = subprocess.run(["git", "diff", "--quiet"], cwd=ROOT).returncode == 0
    checks = {
        "branch_main": branch == "main",
        "head_equals_origin_main": head == origin,
        "expected_remote": remote == EXPECTED_REMOTE,
        "staged_index_clean": staged_clean,
        "tracked_worktree_clean": tracked_clean,
    }
    print(json.dumps({"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "head": head, "origin_main": origin, "remote": remote}, sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
