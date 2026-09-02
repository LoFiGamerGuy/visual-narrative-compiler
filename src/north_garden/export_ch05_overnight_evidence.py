"""Export safe, pixel-free CH05 overnight evidence from the ignored local run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "experiments/review-packets/ch05-overnight-production-r1"
REGISTRY = RUN_ROOT / "candidate-registry.json"
PACKET = RUN_ROOT / "review/review-packet.json"
PLAN = ROOT / "production/comic/overnight/ch05-overnight-production-plan-r1.json"
REVIEW = ROOT / "production/comic/review/ch05-overnight-engineering-review-r1.json"
OUT = ROOT / "docs/research/evidence/ch05-overnight-production-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    production = json.loads(PLAN.read_text(encoding="utf-8"))
    review_by_id = {entry["candidate_id"]: entry for entry in review["entries"]}
    candidates = []
    for entry in registry["entries"]:
        candidates.append({
            "candidate_id": entry["candidate_id"],
            "panel_id": entry["panel_id"],
            "plan_revision_id": entry["plan_revision_id"],
            "style_id": entry["style_id"],
            "format_role": entry["format_role"],
            "exact_prompt": entry["prompt"],
            "prompt_sha256": entry["prompt_sha256"],
            "input_references": entry["references"],
            "output": entry["output"],
            "execution": entry["execution"],
            "engineering_review": review_by_id[entry["candidate_id"]],
            "human_review_state": "PENDING",
            "human_review_minutes": None,
            "accepted": False,
        })
    record = {
        "record_type": "CH05OvernightProductionEvidence",
        "schema_version": "1.0",
        "record_id": "ng-ch05-overnight-production-evidence-r1",
        "state": "GENERATED_AND_ENGINEERING_REVIEWED_OWNER_REVIEW_PENDING",
        "production_plan": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "engineering_review": {"path": REVIEW.relative_to(ROOT).as_posix(), "sha256": sha256(REVIEW)},
        "local_review_packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha256(PACKET)},
        "medium": "comic",
        "comic_panel_plan_only": True,
        "animation_shot_plan": None,
        "e_conte": None,
        "generation_summary": {
            "candidate_count": len(candidates),
            "distinct_panel_plans": len({item["panel_id"] for item in candidates}),
            "sequence_count": len(production["sequences"]),
            "style_family_count": len(production["style_families"]),
            "text_only_control_count": sum(not item["input_references"] for item in candidates),
            "total_elapsed_seconds": registry["total_elapsed_seconds"],
            "total_reference_uploads": registry["total_reference_uploads"],
            "disclosed_spend_usd": None,
            "paid_api_used": False,
        },
        "provider_metadata_limitations": packet["provider_metadata_limitations"],
        "review_artifacts": packet["artifacts"],
        "candidate_derivatives": packet["candidate_derivatives"],
        "candidates": candidates,
        "provisional_findings": review["provisional_findings"],
        "boundaries": [
            "Generated pixels and derivative packets remain ignored local artifacts; only prompts, hashes, paths, measurements, and review metadata are tracked.",
            "No candidate is accepted, commercially cleared, or promoted as an exact production base.",
            "Only the three exact authorized fictional-adult reference hashes were supplied to built-in ImageGen; text-only controls supplied none.",
            "No direct paid provider API, BFL upload, cloud GPU, large-model download, real-person material, or child-related material was used."
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"exported {len(candidates)} safe evidence records: {OUT.relative_to(ROOT)} {sha256(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
