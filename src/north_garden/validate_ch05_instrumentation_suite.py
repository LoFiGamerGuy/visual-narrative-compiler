"""Run the complete offline North Garden CH05 instrumentation validation suite."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/results/ch05-instrumentation-validation-suite-r1.json"
PYTHON = sys.executable

CHECKS = [
    ("frozen_v2_1_1", [PYTHON, "research/authoritative/v2.1.1/scripts/validate_research_package.py"]),
    ("production_records", [PYTHON, "src/north_garden/validate_production_records.py"]),
    ("runtime_manifest", [PYTHON, "src/north_garden/validate_runtime_asset_manifest.py", "--manifest", "config/runtime-assets.example.json"]),
    ("aggregate_bakeoff_budget", [PYTHON, "src/north_garden/validate_bakeoff_budget.py"]),
    ("ch05_pre_render", [PYTHON, "src/north_garden/validate_ch05_pre_render_records.py"]),
    ("p036_repair_readiness", [PYTHON, "src/north_garden/validate_ch05_p036_repair_readiness.py"]),
    ("chapter_preflight", [PYTHON, "src/north_garden/validate_ch05_production_preflight.py"]),
    ("comic_input_gate", [PYTHON, "src/north_garden/validate_comic_input_gate.py"]),
    ("comic_input_mutations", [PYTHON, "src/north_garden/validate_comic_input_gate_mutations.py"]),
    ("six_panel_packet", [PYTHON, "src/north_garden/validate_ch05_demonstration_packet.py"]),
    ("sequence_layout_control", [PYTHON, "src/north_garden/validate_ch05_sequence_layout_control.py"]),
    ("comic_run_ledger", [PYTHON, "src/north_garden/validate_comic_run_ledger.py"]),
    ("production_budget_domain", [PYTHON, "src/north_garden/validate_production_budget_domain.py"]),
    ("candidate_intake", [PYTHON, "src/north_garden/validate_comic_base_candidate_intake.py"]),
    ("candidate_promotion", [PYTHON, "src/north_garden/validate_comic_base_candidate_promotion.py"]),
    ("chapter_run_manifest", [PYTHON, "src/north_garden/validate_ch05_chapter_run_manifest.py"]),
    ("timed_review_session", [PYTHON, "src/north_garden/validate_review_session.py"]),
    ("chapter_progress", [PYTHON, "src/north_garden/validate_chapter_progress.py"]),
    ("p036_openai_offline_preflight_build", [PYTHON, "src/north_garden/preflight_openai_p036_submission.py"]),
    ("p036_openai_offline_preflight", [PYTHON, "src/north_garden/validate_openai_p036_offline_preflight.py"]),
    ("submission_journal", [PYTHON, "src/north_garden/validate_submission_journal.py"]),
    ("render_record_schema", [PYTHON, "src/north_garden/validate_render_record.py"]),
    ("g07_evidence_vault", [PYTHON, "src/north_garden/validate_g07_evidence_vault.py"]),
    ("g07_evidence_archive", [PYTHON, "src/north_garden/validate_g07_evidence_archive.py"]),
    ("g07_blinded_review", [PYTHON, "src/north_garden/validate_g07_blinded_review.py"]),
    ("g07_review_rollup", [PYTHON, "src/north_garden/validate_g07_review_rollup.py"]),
    ("selected_route_boundary", [PYTHON, "src/north_garden/validate_openai_boundary_hardening.py"]),
    ("p036_mask_topology", [PYTHON, "src/north_garden/validate_ch05_p036_mask_topology.py"]),
    ("p036_causal_shape", [PYTHON, "src/north_garden/validate_ch05_p036_causal_shape_control.py"]),
    ("p036_readiness_r2", [PYTHON, "src/north_garden/validate_ch05_p036_repair_readiness_r2.py"]),
    ("chapter_repair_coverage", [PYTHON, "src/north_garden/validate_ch05_chapter_repair_policy_coverage.py"]),
    ("next_repair_information_gain", [PYTHON, "src/north_garden/validate_ch05_next_repair_information_gain.py"]),
    ("p044_fixed_boundary_stress", [PYTHON, "src/north_garden/validate_ch05_p044_fixed_boundary_stress.py"]),
    ("p044_adaptive_boundary", [PYTHON, "src/north_garden/validate_ch05_p044_adaptive_boundary.py"]),
    ("scale_aware_boundary_selector", [PYTHON, "src/north_garden/validate_scale_aware_boundary_selector.py"]),
    ("repair_boundary_render_record", [PYTHON, "src/north_garden/validate_render_record_boundary.py"]),
    ("production_cost_ledger_r2", [PYTHON, "src/north_garden/validate_ch05_production_cost_ledger_r2.py"]),
    ("repair_evidence_readiness_matrix", [PYTHON, "src/north_garden/validate_ch05_repair_evidence_readiness_matrix.py"]),
    ("exact_base_boundary_measurement_packet", [PYTHON, "src/north_garden/validate_exact_base_boundary_measurement_packet.py"]),
    ("repair_outcome_finalizer", [PYTHON, "src/north_garden/validate_repair_outcome_finalizer.py"]),
    ("production_cost_ledger_r3", [PYTHON, "src/north_garden/validate_ch05_production_cost_ledger_r3.py"]),
    ("instrumentation_runtime", [PYTHON, "src/north_garden/validate_instrumentation_runtime.py"]),
    ("selected_route_artifact_rebuild", [PYTHON, "src/north_garden/validate_selected_route_artifact_rebuild.py"]),
    ("tracked_source_scope", [PYTHON, "src/north_garden/validate_tracked_source_scope.py"]),
]


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    results = []
    suite_started = time.perf_counter()
    for name, command in CHECKS:
        started = time.perf_counter()
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        elapsed_ms = (time.perf_counter() - started) * 1000
        result = {
            "name": name,
            "passed": completed.returncode == 0,
            "elapsed_ms": round(elapsed_ms, 3),
            "command": command[1:],
            "stdout_tail": completed.stdout.strip().splitlines()[-3:],
            "stderr_tail": completed.stderr.strip().splitlines()[-3:],
        }
        results.append(result)
        print(f"{'PASS' if result['passed'] else 'FAIL'} {name} {result['elapsed_ms']:.3f}ms")
        if not result["passed"]:
            break
    record = {
        "record_type": "NorthGardenOfflineValidationSuite",
        "schema_version": "1.0",
        "record_id": "ng-ch05-instrumentation-validation-suite-r1",
        "started_at": stamp(),
        "network_or_provider_calls": 0,
        "external_uploads": 0,
        "external_cost_usd": "0.000000",
        "checks_expected": len(CHECKS),
        "checks_run": len(results),
        "checks_passed": sum(item["passed"] for item in results),
        "elapsed_ms": round((time.perf_counter() - suite_started) * 1000, 3),
        "passed": len(results) == len(CHECKS) and all(item["passed"] for item in results),
        "checks": results,
        "boundary": "The suite invokes only local builders/validators; the selected-route preflight has no client, request body, or network executor.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if not record["passed"]:
        failed = next(item for item in results if not item["passed"])
        for line in failed["stdout_tail"] + failed["stderr_tail"]:
            print(line)
        return 1
    print(f"0 failures, 0 warnings ({len(CHECKS)}/{len(CHECKS)} offline checks passed in {record['elapsed_ms']:.3f}ms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
