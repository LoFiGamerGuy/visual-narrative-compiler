"""Validate the no-network CH05 P033-P038 demonstration packet."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "src/north_garden/build_ch05_demonstration_packet.py"
OUT = ROOT / "experiments/results/ch05-p033-p038-no-network-packet-r1.json"


def main() -> int:
    completed = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, capture_output=True, text=True)
    failures = []
    if completed.returncode:
        failures.append(f"builder failed: {completed.stderr.strip()}")
    else:
        record = json.loads(OUT.read_text(encoding="utf-8"))
        summary = record["summary"]
        expected_zero = (
            "executable_panels",
            "approved_base_rasters",
            "approved_repair_masks",
            "render_records",
            "accepted_panels",
            "external_uploads",
            "provider_requests",
        )
        failures.extend(f"{name} must be zero" for name in expected_zero if summary[name] != 0)
        if summary["new_external_cost_usd"] != "0.000000":
            failures.append("new external cost must be exactly zero")
        if [item["display_order"] for item in record["panels"]] != list(range(33, 39)):
            failures.append("packet must contain contiguous P033-P038 order")
        if any(item["executable"] for item in record["panels"]):
            failures.append("no panel may be executable")
        if any(item["human_minutes"] is not None for item in record["panels"]):
            failures.append("unperformed panel review minutes must remain null")
        if record["review_workload"]["human_minutes"] is not None:
            failures.append("workload minutes must not be invented")
        if record["review_workload"]["total_task_instances"] != 36:
            failures.append("expected 36 structured review task instances")
        if len(record["continuity_contracts"]) != 3 or any(
            not item["source_terms_verified"] for item in record["continuity_contracts"]
        ):
            failures.append("three source-derived continuity contracts must verify")
        if record.get("medium") != "comic" or record.get("animation_shot_plan") is not None:
            failures.append("ComicPanelPlan/AnimationShotPlan boundary violated")

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (P033-P038 packet has 0 executable panels and 36 untimed review tasks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
