from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "production" / "reimaginings" / "ember-lattice" / "integrity" / "final-integrity.json"
BASE = "40e7940016ea3c3966752b61f55a931f91a13ac7"
SELF_PATH = "production/reimaginings/ember-lattice/integrity/final-integrity.json"


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True, encoding="utf-8", errors="replace").strip()


def main() -> None:
    branch = git(ROOT, "branch", "--show-current")
    head = git(ROOT, "rev-parse", "HEAD")
    remote_ref = f"refs/remotes/origin/{branch}"
    remote_head = git(ROOT, "rev-parse", remote_ref)
    tracked = sorted(set(git(ROOT, "diff", "--name-only", f"{BASE}..{head}").splitlines()) | {SELF_PATH})
    protected_after = json.loads((OUT.parent / "protected-state-after.json").read_text(encoding="utf-8"))
    protected_report = json.loads((OUT.parent / "integrity-report.json").read_text(encoding="utf-8"))
    original = next(row for row in protected_after["protected_worktrees"] if Path(row["path"]) == Path(r"C:\AgentWorkspaces\anime-pipeline"))
    report = {
        "schema": "FinalIsolatedDeliveryIntegrity/1.0",
        "status": "PASS" if protected_report["status"] == "PASS" and head == remote_head else "FAIL",
        "isolated_worktree": str(ROOT),
        "isolated_branch": branch,
        "baseline_commit": BASE,
        "evidence_head_before_metadata_commit": head,
        "final_commit_ref": f"refs/heads/{branch}",
        "final_commit_contract": "Resolve final_commit_ref after checkout; tracked deltas after evidence_head_before_metadata_commit are limited to this self-describing integrity record and deterministic audit/hub closure updates over already tracked paths.",
        "commit_range": f"{BASE}..{branch}",
        "remote": "origin",
        "remote_branch_ref": remote_ref,
        "remote_parity_at_evidence_capture": {"local": head, "remote": remote_head, "status": "PASS" if head == remote_head else "FAIL"},
        "main": {"expected": BASE, "actual": original["head"], "status": "PASS" if original["head"] == BASE else "FAIL"},
        "origin_main": {"expected": BASE, "actual": git(ROOT, "rev-parse", "refs/remotes/origin/main"), "status": "PASS" if git(ROOT, "rev-parse", "refs/remotes/origin/main") == BASE else "FAIL"},
        "protected_worktrees_and_untracked_roots": protected_report,
        "protected_snapshot": protected_after["protected_worktrees"],
        "exact_tracked_file_list_for_commit_range": tracked,
        "tracked_file_count": len(tracked),
        "generated_raster_policy": "ignored; not committed",
        "direct_paid_cloud_spend_usd": 0,
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS" or report["main"]["status"] != "PASS" or report["origin_main"]["status"] != "PASS":
        raise SystemExit("final integrity evidence failed")


if __name__ == "__main__":
    main()
