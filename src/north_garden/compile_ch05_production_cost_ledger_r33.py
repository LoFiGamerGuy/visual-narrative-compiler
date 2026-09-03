"""Advance CH05 cost/timing evidence append-only for the premium-cel chapter arm."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r32.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-execution-manifest-r1.json"
CROPS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-crops-r1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json"
SPLIT_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/panels/premium-cel-panel-split-report-r1.json"
REVIEW_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/review/build-report.json"
LETTERING_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/lettered/lettering-build-report.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r33.json"
APPENDED = [
    "ch05_premium_cel_execution_renderrecords_r1",
    "ch05_premium_cel_deterministic_crop_and_assembly_r1",
    "ch05_premium_cel_lettering_and_review_packets_r1",
]
UNAVAILABLE = ["model", "endpoint", "provider_request_ids", "usage", "monetary_cost_usd", "deterministic_seed"]
SOURCES = [EXECUTION, CROPS, ASSEMBLY, SPLIT_REPORT, REVIEW_REPORT, LETTERING_REPORT]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    crops = json.loads(CROPS.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    split_report = json.loads(SPLIT_REPORT.read_text(encoding="utf-8"))
    review_report = json.loads(REVIEW_REPORT.read_text(encoding="utf-8"))
    lettering_report = json.loads(LETTERING_REPORT.read_text(encoding="utf-8"))
    summary = execution["summary"]

    if (
        summary["sequence_outputs"],
        summary["comic_panel_plans_requested"],
        summary["planned_comic_panel_crops"],
        summary["authorized_reference_uses"],
        summary["unique_timing_batches"],
        summary["overlap_adjusted_tool_call_wall_seconds"],
    ) != (11, 50, 50, 23, 6, 1234.0):
        raise ValueError("premium-cel execution summary differs from the authorized accounting facts")
    if crops["summary"].get("planned_crops") != 50 or len(assembly.get("entries", [])) != 50:
        raise ValueError("premium-cel crop/assembly denominator is not 50")
    if split_report.get("summary", {}).get("panels_produced") != 50:
        raise ValueError("premium-cel split report does not prove 50 local derivatives")
    if review_report.get("chapter_complete") is not True or lettering_report.get("summary", {}).get("chapter_panels") != 50:
        raise ValueError("premium-cel review/lettering packet evidence is incomplete")

    rows = list(prior["local_zero_external_cost_evidence"])
    rows.extend(
        {"milestone": name, "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"}
        for name in APPENDED
    )
    current = {
        "arm_id": "ch05_complete_chapter_premium_cel_r1",
        "sequence_tool_calls": 11,
        "raster_outputs": 11,
        "comic_panel_plan_crops": 50,
        "authorized_reference_uses": 23,
        "unique_authorized_reference_hashes": 3,
        "unique_timing_batches": 6,
        "overlap_adjusted_tool_call_wall_seconds": 1234.0,
        "timing_scope": summary["timing_scope"],
        "model": None,
        "endpoint": None,
        "provider_request_ids": None,
        "usage": None,
        "monetary_cost_usd": None,
        "deterministic_seed": None,
    }
    prior_cumulative = prior["built_in_product_activity"]["cumulative_complete_chapter_style_arms"]
    cumulative = {
        "included_arms": [*prior_cumulative["included_arms"], current["arm_id"]],
        "sequence_tool_calls": prior_cumulative["sequence_tool_calls"] + current["sequence_tool_calls"],
        "raster_outputs": prior_cumulative["raster_outputs"] + current["raster_outputs"],
        "comic_panel_plan_crops": prior_cumulative["comic_panel_plan_crops"] + current["comic_panel_plan_crops"],
        "authorized_reference_uses": prior_cumulative["authorized_reference_uses"] + current["authorized_reference_uses"],
        "unique_authorized_reference_hashes": 3,
        "unique_timing_batches": prior_cumulative["unique_timing_batches"] + current["unique_timing_batches"],
        "overlap_adjusted_tool_call_wall_seconds": round(
            prior_cumulative["overlap_adjusted_tool_call_wall_seconds"] + current["overlap_adjusted_tool_call_wall_seconds"], 1
        ),
        "direct_paid_provider_api_calls": 0,
        "direct_paid_api_or_cloud_spend_usd": "0.000000",
        "model": None,
        "endpoint": None,
        "provider_request_ids": None,
        "usage": None,
        "monetary_cost_usd": None,
        "deterministic_seed": None,
    }
    document = {
        **prior,
        "schema_version": "1.32",
        "record_id": "ng-ch05-production-cost-ledger-r33",
        "supersedes": {"record_id": prior["record_id"], "path": PRIOR.relative_to(ROOT).as_posix(), "sha256": sha256(PRIOR)},
        "local_zero_external_cost_evidence": rows,
        "revision_summary": {
            "prior_local_milestones": len(prior["local_zero_external_cost_evidence"]),
            "appended_local_milestones": len(APPENDED),
            "total_local_milestones": len(rows),
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "built_in_product_activity": {
            "product": "OpenAI built-in ImageGen in Codex",
            "evidence_sources": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in SOURCES],
            "current_revision_premium_cel": current,
            "cumulative_complete_chapter_style_arms": cumulative,
            "unavailable_fields": UNAVAILABLE,
            "accounting_note": "Fifty deterministic panel crops are local derivatives and are not counted as tool calls or raster generation outputs.",
        },
        "boundary": (
            "Append-only accounting. Premium-cel and cumulative complete-chapter counts separate 11 built-in sequence outputs from "
            "50 deterministic local crops. Direct paid API/cloud requests/uploads/spend remain 0/0/$0; built-in model, endpoint, "
            "provider request IDs, usage, seed, and monetary cost are unavailable/null, not zero. G07 remains separate."
        ),
    }
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256(OUTPUT),
                "milestones": len(rows),
                "premium_outputs": current["raster_outputs"],
                "premium_crops": current["comic_panel_plan_crops"],
                "cumulative_outputs": cumulative["raster_outputs"],
                "cumulative_crops": cumulative["comic_panel_plan_crops"],
                "cumulative_wall_seconds": cumulative["overlap_adjusted_tool_call_wall_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
