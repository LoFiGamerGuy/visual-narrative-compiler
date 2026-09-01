"""Validate no-network review scaffolding for every frontier bakeoff adapter."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "src/north_garden/build_renderer_bakeoff_review.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("review_builder", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for adapter_id in module.RECORD_DIRS:
        review = module.build(adapter_id, write=False)
        assert review["state"] in {"PENDING_EXECUTION", "PENDING_HUMAN_REVIEW"}
        assert len(review["missing_execution_records"]) + len(review["candidates"]) == 4
        if review["candidates"]:
            assert review["state"] == "PENDING_HUMAN_REVIEW"
            assert all(candidate["decision"] == "pending" for candidate in review["candidates"])
    assert module.applicable_assertions("g07a-target-change")["target_edit"] == "pending_human_review"
    assert module.applicable_assertions("g07a-no-change")["target_nochange"] == "pending_human_review"
    print("0 failures, 0 warnings (renderer bakeoff human-review scaffolding validated)")


if __name__ == "__main__":
    main()
