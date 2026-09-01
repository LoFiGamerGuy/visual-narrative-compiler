"""Build a non-gating human-review record from completed G07 adapter records.

The manifest remains the source of panel intent. This tool only links immutable
execution records/candidates to review fields; it never accepts an image,
freezes the executable bundle, or assigns a benchmark score.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"
MANIFEST_PATH = ROOT / "production/comic/hard-assertion-manifests/g07-fictional-proxy-v1.json"
TAXONOMY_PATH = ROOT / "experiments/failure-tags/failure-tag-taxonomy-v2.json"
RECORD_DIRS = {
    "gemini_3_1_flash_image": ROOT / "experiments/records/gemini_flash_image_g07_bakeoff_r1",
    "grok_imagine_image_2": ROOT / "experiments/records/xai_grok_imagine_g07_bakeoff_r1",
    "openai_gpt_image_2": ROOT / "experiments/records/openai_gpt_image2_g07_bakeoff_r1",
    "bfl_flux_2": ROOT / "experiments/records/bfl_flux2_g07_bakeoff_r1",
}
REVIEW_DIR = ROOT / "experiments/reviews/renderer-bakeoff-g07-fictional-r1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def applicable_assertions(request_id: str) -> dict[str, str]:
    assertions = {"two_subjects": "pending_human_review", "role_order": "pending_human_review", "common_table": "pending_human_review", "non_contact": "pending_human_review"}
    if request_id == "g07a-target-change":
        assertions["target_edit"] = "pending_human_review"
    if request_id == "g07a-no-change":
        assertions["target_nochange"] = "pending_human_review"
    return assertions


def candidate_from_record(record_path: Path, request_id: str) -> dict:
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["execution_status"] in {"completed", "completed_recovered_from_interaction"}
    candidate = record["candidate"]
    raster = ROOT / candidate["path"]
    assert raster.exists() and sha256(raster) == candidate["sha256"]
    return {
        "request_id": request_id,
        "record_path": record_path.relative_to(ROOT).as_posix(),
        "record_sha256": sha256(record_path),
        "candidate_path": candidate["path"],
        "candidate_sha256": candidate["sha256"],
        "execution_status": record["execution_status"],
        "hard_assertions": applicable_assertions(request_id),
        "failure_tags": [],
        "human_review_status": "not_yet_performed",
        "human_minutes": None,
        "decision": "pending",
    }


def build(adapter_id: str, write: bool) -> dict:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    assert adapter_id in RECORD_DIRS
    candidates = []
    missing = []
    for item in plan["request_set"]:
        record_path = RECORD_DIRS[adapter_id] / f"{item['id']}.json"
        if record_path.exists():
            candidates.append(candidate_from_record(record_path, item["id"]))
        else:
            missing.append(item["id"])
    review = {
        "record_type": "ComicPanelReviewRecord", "schema_version": "1.0", "record_id": f"ng-review-g07-fictional-{adapter_id}-r1",
        "state": "PENDING_EXECUTION" if missing else "PENDING_HUMAN_REVIEW", "adapter_id": adapter_id,
        "semantic_source": plan["semantic_source"], "intent_manifest": {"path": MANIFEST_PATH.relative_to(ROOT).as_posix(), "sha256": sha256(MANIFEST_PATH)},
        "failure_taxonomy": {"path": TAXONOMY_PATH.relative_to(ROOT).as_posix(), "sha256": sha256(TAXONOMY_PATH)},
        "candidates": candidates, "missing_execution_records": missing,
        "review_protocol": {"timer_rule": "Start on candidate inspection; stop at accepted/rejected decision, including repair time.", "acceptance_rule": "Every applicable hard assertion must pass and an authorized human must record minutes. Proxy passes are not production acceptance.", "vlm_status": "optional_non_gating"},
        "summary": {"generation_count": len(candidates), "accepted": 0, "human_minutes": None, "decision": "pending"},
        "created_at": stamp(),
    }
    if write:
        if missing:
            raise SystemExit("cannot write a review until all four execution records are completed")
        REVIEW_DIR.mkdir(parents=True, exist_ok=True)
        out = REVIEW_DIR / f"{adapter_id}-review-r1.json"
        out.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        print(out)
    else:
        print(json.dumps({"state": review["state"], "adapter_id": adapter_id, "found_records": len(candidates), "missing_execution_records": missing, "no_files_written": True}, indent=2))
    return review


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", choices=sorted(RECORD_DIRS), required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    build(args.adapter, args.write)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
