"""Compile a fail-closed production-manifest dry run for CH05 P010-P013."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "production/comic/repair-readiness/ch05-p010-p013-preflight-contract-r1.json"
ROUTE = ROOT / "production/comic/recommendations/ch05-pipeline-route-recommendation-r1.json"
STYLE = ROOT / "production/comic/style-direction/ch05-mill-signal-r10.json"
RENDER_INDEX = ROOT / "production/comic/run-manifests/ch05-built-in-renderrecord-index-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-p010-p013-production-manifest-dry-run-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-p010-p013-production-manifest-dry-run-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def root_hash(rows: list[dict]) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    rows = []
    for slot, source in enumerate(preflight["rows"], 1):
        candidate_id = f"m{slot:03d}"
        rows.append(
            {
                "candidate_slot": candidate_id,
                "display_order": source["display_order"],
                "panel_id": source["panel_id"],
                "plan_revision_id": source["plan_revision_id"],
                "plan_canonical_sha256": source["plan_canonical_sha256"],
                "narrative_beat": source["narrative_beat"],
                "visible_adult_cast": source["visible_adult_cast"],
                "continuity_assertions": source["continuity_assertions"],
                "style_id": source["style_id"],
                "format_role": source["format_role"],
                "target_width_px": source["target_width_px"],
                "reference_ids": source["reference_ids"],
                "reference_uploads": 0,
                "final_copy": None,
                "prompt": None,
                "prompt_sha256": None,
                "expected_output_path": f"experiments/review-packets/ch05-p010-p013-production-r1/candidates/{candidate_id}-{source['panel_id'].split('-')[-1]}-{source['style_id']}-r1.png",
                "output_sha256": None,
                "dimensions": None,
                "elapsed_seconds": None,
                "model": None,
                "endpoint": None,
                "request_id": None,
                "provider_usage": None,
                "provider_cost_usd": None,
                "seed": None,
                "failure": None,
                "human_review_state": "NOT_RENDERED",
                "human_review_minutes": None,
                "acceptance_decision": None,
                "owner_accepted": False,
                "commercially_cleared": False,
                "execution_ready": False,
                "comic_panel_plan_revision_created": False,
            }
        )
    manifest = {
        "record_type": "ComicMicrosequenceProductionManifestDryRun",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p010-p013-production-manifest-dry-run-r1",
        "state": "FAIL_CLOSED_ZERO_PROMPT_DRY_RUN",
        "medium": "comic",
        "inputs": [binding(path) for path in (PREFLIGHT, ROUTE, STYLE, RENDER_INDEX)],
        "summary": {
            "plan_count": 4,
            "initial_candidate_slots": 4,
            "maximum_repair_slots": 2,
            "maximum_candidate_envelope": 6,
            "prompt_count": 0,
            "rendered_candidates": 0,
            "reference_hypothesis_uses": sum(len(row["reference_ids"]) for row in rows),
            "reference_uploads": 0,
            "execution_ready_rows": 0,
            "accepted_candidates": 0,
            "comic_panel_plan_revisions": 0,
            "provider_calls": 0,
            "uploads": 0,
            "cost_usd": 0,
            "human_review_minutes": None,
        },
        "rows": rows,
        "row_root_sha256": root_hash(rows),
        "repair_slots": preflight["repair_slots"],
        "gates": {
            "owner_route_decision_bound": False,
            "candidate_style_review_bound": False,
            "microsequence_cadence_approved": False,
            "final_copy_or_silence_bound": False,
            "exact_reference_selection_approved": False,
            "commercial_clearance": False,
            "all_required_before_prompt_compilation": True,
            "prompts_may_be_compiled_now": False,
        },
        "planned_review_artifacts": [
            "contact-sheet-p010-p013-candidates.png",
            "contact-sheet-p010-p013-phone-390px.png",
            "sequence-p010-p013-continuity.png",
            "contact-sheet-p010-p013-lettering-safe-zones.png",
            "comparison-p010-p013-style-density-cadence.png",
        ],
        "production_stages": [
            {"order": 1, "stage": "PROMPT_COMPILE_AFTER_ALL_GATES", "state": "BLOCKED"},
            {"order": 2, "stage": "OPENAI_BUILTIN_IMAGEGEN", "state": "NOT_RUN"},
            {"order": 3, "stage": "EXACT_RENDERRECORD_NORMALIZATION", "state": "NOT_RUN"},
            {"order": 4, "stage": "DETERMINISTIC_REVIEW_PACKET_BUILD", "state": "NOT_RUN"},
            {"order": 5, "stage": "OWNER_REVIEW_EVENT", "state": "NOT_RUN"},
        ],
        "reproducers": [
            "python src/north_garden/validate_ch05_p010_p013_preflight_contract.py",
            "python src/north_garden/compile_ch05_p010_p013_production_manifest_dry_run.py",
            "python src/north_garden/validate_ch05_p010_p013_production_manifest_dry_run.py",
        ],
        "animation_shot_plan": None,
        "e_conte": None,
        "boundary": "ComicPanelPlan-only dry run. No prompts, pixels, provider calls, uploads, spend, acceptance, commercial conclusion, or plan revision.",
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    evidence = {
        "record_type": "ComicMicrosequenceProductionManifestDryRunEvidence",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p010-p013-production-manifest-dry-run-evidence-r1",
        "state": "PASS_FAIL_CLOSED_OWNER_GATES_PENDING",
        "manifest": binding(OUTPUT),
        "inputs": manifest["inputs"],
        "summary": manifest["summary"],
        "row_root_sha256": manifest["row_root_sha256"],
        "planned_review_artifact_count": len(manifest["planned_review_artifacts"]),
        "production_stage_count": len(manifest["production_stages"]),
        "animation_shot_plan": None,
        "e_conte": None,
        "limitations": ["This dry run does not compile prompts or test image output.", "Reference IDs remain metadata hypotheses with zero uploads.", "Human review, provider metadata, timing, and monetary cost are unavailable until a separately authorized execution occurs."],
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"CH05 P010-P013 manifest dry run: 4 rows/{manifest['summary']['reference_hypothesis_uses']} reference hypotheses/5 planned review artifacts/0 prompts")
    print("renders/executable/calls/uploads/cost/accepted/plan revisions 0/0/0/0/$0/0/0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
