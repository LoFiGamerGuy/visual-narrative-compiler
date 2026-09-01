"""Validate the non-promotional CH05 coverage measurement."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "experiments/results/ch05_mill_signal_development_coverage_20260901.json"


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["state"] == "NONCANON_COVERAGE_MEASUREMENT_NOT_PRODUCTION_READINESS"
    assert report["counts"] == {
        "planned_panels": 50, "renderer_candidates": 4, "renderer_candidate_coverage_percent": 8.0,
        "accepted_panels": 0, "accepted_panel_coverage_percent": 0.0,
        "pending_human_review_panels": 4, "unrendered_panels": 46,
    }
    assert len(report["rendered_development_panel_ids"]) == 4
    assert len(report["unrendered_development_panel_ids"]) == 46
    assert "not establish throughput" in report["not_a_forecast"]
    print("0 failures, 0 warnings (CH05 non-canon coverage measurement validated)")


if __name__ == "__main__":
    main()
