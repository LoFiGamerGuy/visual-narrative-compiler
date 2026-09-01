"""Validate taxonomy coverage for the active cross-arm failure-profile synthesis."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main() -> None:
    taxonomy = json.loads((ROOT / "experiments/failure-tags/failure-tag-taxonomy-v2.json").read_text())
    known = {tag for values in taxonomy["categories"].values() for tag in values}
    assert taxonomy["state"] == "ACTIVE_NON_GATING_CLASSIFICATION"
    profile = json.loads((ROOT / "experiments/results/cross-arm-failure-profile-20260901.json").read_text())
    assert profile["state"] == "EVIDENCE_SYNTHESIS_NOT_BENCHMARK_SCORE"
    assert len(profile["arms"]) == 7
    for arm in profile["arms"]:
        for tag in arm.get("primary_failure_tags", []):
            assert tag in known or tag.endswith("_not_evaluable") or tag in {"global_nochange_drift", "proxy_shape_semantics_invalid"}
        for tag in arm.get("primary_failure_counts", {}):
            assert tag in known
    assert "target_nochange_drift" in known and "external_composite_exact" in known and "sexualized_wardrobe" in known
    print("0 failures, 0 warnings (cross-arm failure taxonomy/profile validated)")

if __name__ == "__main__":
    main()
