"""Validate CH05 overnight delivery bundle r2 and reject adversarial mutations."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-overnight-delivery-bundle-r2.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(d: dict) -> list[str]:
    s = d.get("summary", {})
    keys = (
        "candidates", "ch05_candidates", "noncanon_concepts", "distinct_ch05_plans", "selected",
        "chapter_plans", "sequence_batches", "review_links", "strongest_candidates", "remaining_decisions",
        "required_root_decisions", "resolved_root_decisions", "integrated_checks", "operating_steps",
        "planning_candidates", "fresh_arm_candidates", "observed_seconds", "reference_uses", "paid_spend_usd",
        "owner_decisions", "accepted_candidates", "executable_panels",
    )
    expected = (29, 26, 3, 14, 14, 50, 12, 112, 14, 10, 6, 0, 58, 12, 49, 68, 1385.036, 39, 0, 0, 0, 0)
    out = []
    if tuple(s.get(k) for k in keys) != expected:
        out.append("summary denominator invalid")
    if d.get("state") != "PASS_OWNER_PENDING" or d.get("base_remote_parity") is not True:
        out.append("state/parity invalid")
    if s.get("human_review_minutes") is not None:
        out.append("review minutes fabricated")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None:
        out.append("planning boundary invalid")
    return out


def main() -> int:
    d = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    fail = errors(d)
    for key in ("bundle", "summary_document", "changed_files_document"):
        p = ROOT / d[key]["path"]
        if not p.is_file() or sha(p) != d[key]["sha256"]:
            fail.append(f"output binding invalid: {key}")
    for item in d["inputs"]:
        p = ROOT / item["path"]
        if not p.is_file() or sha(p) != item["sha256"]:
            fail.append(f"input binding invalid: {item['path']}")
    bundle = json.loads((ROOT / d["bundle"]["path"]).read_text(encoding="utf-8"))
    art, activity = bundle.get("measured_art", {}), bundle.get("activity", {})
    strongest = art.get("strongest_candidates", [])
    if len(strongest) != 14 or any(
        not (ROOT / x["path"]).is_file() or sha(ROOT / x["path"]) != x["sha256"] for x in strongest
    ):
        fail.append("strongest candidate binding invalid")
    if len(bundle.get("ranked_engineering_recommendations", [])) != 4:
        fail.append("ranked route denominator invalid")
    if len(bundle.get("limitations", [])) != 10:
        fail.append("limitation denominator invalid")
    if len(bundle.get("key_links", [])) != 5 or any(
        not (ROOT / x["path"]).is_file()
        or sha(ROOT / x["path"]) != x["sha256"]
        or (ROOT / x["path"]).resolve().as_posix() != x["absolute_path"]
        for x in bundle.get("key_links", [])
    ):
        fail.append("key links invalid")
    if any(row.get("owner_decision") is not None for row in bundle["owner_frontier"]["rows"]):
        fail.append("owner decision fabricated")
    zero = ("paid_api_calls", "external_uploads", "cloud_gpu_uses", "purchases", "paid_spend_usd",
            "owner_decisions", "accepted_candidates", "commercially_cleared_candidates", "executable_panels",
            "comic_panel_plan_revisions")
    if any(activity.get(k) != 0 for k in zero) or activity.get("built_in_monetary_cost_usd") is not None or activity.get("human_review_minutes") is not None:
        fail.append("activity/promotion fabricated")
    lineage = bundle.get("source_lineage", {})
    commit = lineage.get("base_commit")
    if subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=ROOT, check=False).returncode:
        fail.append("base commit invalid")
    if lineage.get("origin_main_at_compile") != commit or lineage.get("base_remote_parity") is not True:
        fail.append("base lineage invalid")
    muts = [
        lambda x: x.update(state="FAIL"),
        *[lambda x, k=k: x["summary"].update({k: -1}) for k in (
            "candidates", "ch05_candidates", "noncanon_concepts", "distinct_ch05_plans", "selected", "chapter_plans",
            "sequence_batches", "review_links", "strongest_candidates", "remaining_decisions", "required_root_decisions",
            "resolved_root_decisions", "integrated_checks", "operating_steps", "planning_candidates", "fresh_arm_candidates",
            "observed_seconds", "reference_uses", "paid_spend_usd", "owner_decisions", "accepted_candidates", "executable_panels",
        )],
        lambda x: x["summary"].update(human_review_minutes=1),
        lambda x: x.update(base_remote_parity=False),
        lambda x: x.update(animation_shot_plan={}),
        lambda x: x.update(e_conte={}),
    ]
    rejected = 0
    for mutation in muts:
        candidate = copy.deepcopy(d)
        mutation(candidate)
        rejected += bool(errors(candidate))
    if rejected != len(muts):
        fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 delivery r2: {len(fail)} failures; 29/50/12/112/14/10/58; {rejected}/{len(muts)} mutations rejected")
    print("calls/uploads/spend/decisions/accepted/executable/minutes 0/0/$0/0/0/0/null")
    for item in fail:
        print(f"FAIL: {item}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
