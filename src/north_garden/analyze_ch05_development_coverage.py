"""Measure CH05 development-script coverage without promoting it to production."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "research/development/clean-ch05-mill-signal-r1.json"
REVIEW = ROOT / "experiments/reviews/ch05-mill-signal-imagegen-smoke-review-r1.json"
OUTPUT = ROOT / "experiments/results/ch05_mill_signal_development_coverage_20260901.json"


def main() -> None:
    script = json.loads(SCRIPT.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    panel_ids = [item["panel_id"] for item in script["panels"]]
    rendered = [item["development_panel_id"] for item in review["candidates"]]
    total_seconds = float(review["summary"]["observed_service_elapsed_seconds"])
    report = {
        "record_type": "DevelopmentChapterCoverageReport",
        "schema_version": "1.0",
        "script": str(SCRIPT.relative_to(ROOT)).replace("\\", "/"),
        "state": "NONCANON_COVERAGE_MEASUREMENT_NOT_PRODUCTION_READINESS",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "counts": {
            "planned_panels": len(panel_ids),
            "renderer_candidates": len(rendered),
            "renderer_candidate_coverage_percent": round(100 * len(rendered) / len(panel_ids), 2),
            "accepted_panels": int(review["summary"]["research_accepted"]),
            "accepted_panel_coverage_percent": 0.0,
            "pending_human_review_panels": len(rendered),
            "unrendered_panels": len(panel_ids) - len(rendered),
        },
        "rendered_development_panel_ids": rendered,
        "unrendered_development_panel_ids": [panel_id for panel_id in panel_ids if panel_id not in set(rendered)],
        "measurement": {
            "observed_service_elapsed_seconds_for_candidates": total_seconds,
            "observed_seconds_per_candidate_mean": round(total_seconds / len(rendered), 3),
            "cost_usd": "NOT_EXPOSED_BY_BUILT_IN_SERVICE",
            "human_minutes": "UNMEASURED_PENDING_AUTHORIZED_REVIEW",
        },
        "not_a_forecast": "A 50-panel time/cost/acceptance forecast is intentionally omitted. Four non-reproducible, unreviewed samples do not establish throughput, acceptance rate, or repair cost.",
        "promotion_gates": [
            "Owner narrative/canon approval of the development script.",
            "A selected renderer path with reproducible provenance and review evidence.",
            "Panel-addressable current StoryState, AssetRegistry, SceneBeat, ComicPanelPlan, HardAssertionManifest, RenderRecord, and edition records.",
            "Timed authorized human review of candidates and resulting immutable revision decisions.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['counts']['renderer_candidate_coverage_percent']}% candidate coverage; wrote {OUTPUT}")


if __name__ == "__main__":
    main()
