"""Validate immutable execution evidence for the local fictional native-repaint arm.

This intentionally validates execution/provenance only. Comic intent remains in a
separate HardAssertionManifest and review record.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FROZEN = "f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae"
DIRS = [
    "illustrious_xl_v2_xinsir_repaint_matrix_v1",
    "illustrious_xl_v2_xinsir_repaint_strength_matrix_v1",
    "illustrious_xl_v2_xinsir_repaint_replication_v1",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_record(path: Path) -> None:
    r = json.loads(path.read_text())
    assert r["record_type"] == "NativeRepaintMatrixRecord"
    assert r["semantic_source_sha256"] == FROZEN
    assert r["state"] == "LOCAL_FICTIONAL_PROXY_RESEARCH_LICENSE_REVIEW_PENDING"
    assert r["mode"] in {"edit", "nochange"}
    assert isinstance(r["seed"], int) and r["generation_seconds"] > 0
    assert r["accepted_output"] is False
    assert r["human_review_status"] == "pending" and r["human_minutes"] is None
    assert r["cost"] == {"external_api_usd": 0, "paid_service_used": False, "local_electricity": "unmeasured"}
    assert r["workflow"]["xinsir_mode"] == "repaint"
    assert r["workflow"]["post_composite"] == "exact exterior measurement"
    for key in ("raw", "composite"):
        candidate = r["candidates"][key]
        artifact = ROOT / candidate["path"]
        assert artifact.is_file(), f"missing {artifact}"
        assert sha(artifact) == candidate["sha256"], f"candidate hash mismatch {artifact}"
    measured = r["measurements"]
    assert measured["composite_changed_outside_mask_fraction"] == 0.0
    assert 0.0 <= measured["composite_changed_inside_mask_fraction"] <= 1.0
    for source in ("checkpoint", "controlnet", "adapter_source", "profile"):
        assert r["sources"][source]["sha256"]
    assert any("Fictional proxy only" in x for x in r["limitations"])


def main() -> None:
    records = []
    for name in DIRS:
        records.extend(sorted((ROOT / "experiments/records" / name).glob("*.json")))
    assert len(records) == 10, f"expected 10 native repaint records, found {len(records)}"
    for record in records:
        check_record(record)
    review_path = ROOT / "experiments/reviews/g07-fictional-proxy-xinsir-replication-review-v1.json"
    review = json.loads(review_path.read_text())
    assert review["record_type"] == "ComicPanelAssertionReviewRecord"
    assert review["decision"]["accepted"] is False
    assert review["review"]["human_minutes"] is None
    for execution in review["execution_records"]:
        assert sha(ROOT / execution["path"]) == execution["sha256"]
    print(f"0 failures, 0 warnings ({len(records)} native repaint records; intent/execution boundary preserved)")


if __name__ == "__main__":
    main()
