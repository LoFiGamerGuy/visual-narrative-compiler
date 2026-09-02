"""Export pixel-free evidence for the CH05 cadence-hardening batch."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "experiments/review-packets/ch05-cadence-hardening-r1"
REGISTRY = RUN_ROOT / "candidate-registry.json"
PACKET = RUN_ROOT / "review/review-packet.json"
PLAN = ROOT / "production/comic/overnight/ch05-cadence-hardening-plan-r1.json"
REVIEW = ROOT / "production/comic/review/ch05-cadence-hardening-review-r1.json"
OUT = ROOT / "docs/research/evidence/ch05-cadence-hardening-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    reviews = {item["candidate_id"]: item for item in review["entries"]}
    candidates = []
    for item in registry["entries"]:
        candidates.append({
            "candidate_id": item["candidate_id"],
            "panel_id": item["panel_id"],
            "plan_revision_id": item["plan_revision_id"],
            "style_id": item["style_id"],
            "format_role": item["format_role"],
            "exact_prompt": item["prompt"],
            "prompt_sha256": item["prompt_sha256"],
            "input_references": item["references"],
            "output": item["output"],
            "execution": item["execution"],
            "engineering_review": reviews[item["candidate_id"]],
            "human_review_state": "PENDING",
            "human_review_minutes": None,
            "accepted": False,
        })
    record = {
        "record_type": "CH05CadenceHardeningEvidence",
        "schema_version": "1.0",
        "record_id": "ng-ch05-cadence-hardening-evidence-r1",
        "state": "HARDENING_REVIEWED_OWNER_REVIEW_PENDING",
        "medium": "comic",
        "animation_shot_plan": None,
        "e_conte": None,
        "plan": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "engineering_review": {"path": REVIEW.relative_to(ROOT).as_posix(), "sha256": sha256(REVIEW)},
        "local_review_packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha256(PACKET)},
        "summary": {
            "candidate_count": len(candidates),
            "distinct_panel_plans": len({item["panel_id"] for item in candidates}),
            "total_elapsed_seconds": registry["total_elapsed_seconds"],
            "reference_upload_count": registry["total_reference_uploads"],
            "text_only_controls": sum(not item["input_references"] for item in candidates),
            "all_six_dimensions": review["rollup"]["all_six_dimensions"],
            "one_or_more_failures": review["rollup"]["one_or_more_failures"],
            "disclosed_spend_usd": None,
            "paid_api_used": False
        },
        "candidates": candidates,
        "review_artifacts": packet["artifacts"],
        "candidate_derivatives": packet["candidate_derivatives"],
        "decision": review["decision"],
        "limitations": packet["provider_metadata_limitations"],
        "boundaries": [
            "Generated pixels remain ignored local evidence.",
            "Only the three exact owner-authorized fictional-adult reference hashes were supplied to built-in ImageGen; h003 is text-only.",
            "No output is accepted, commercially cleared, deterministic, or an exact production base.",
            "No paid API, BFL request, cloud GPU, large-model download, real likeness, private material, or child-related material was used."
        ]
    }
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"exported hardening evidence: {OUT.relative_to(ROOT)} {sha256(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
