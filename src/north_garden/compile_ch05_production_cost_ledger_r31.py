"""Advance CH05 cost evidence append-only for alternate-graphic execution and gated preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r30.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-execution-manifest-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r31.json"
APPENDED = ["ch05_alt_graphic_execution_renderrecords_r1", "ch05_alt_graphic_deterministic_crop_and_assembly_r1", "ch05_alt_graphic_lettering_and_review_packets_r1", "ch05_alt_graphic_agent_triage_r1", "ch05_r6_alt_graphic_measured_comparison_r1", "ch05_cross_panel_semantic_gates_r1", "ch05_clear_line_watercolor_full_chapter_preflight_r1"]


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    prior = json.loads(PRIOR.read_text(encoding="utf-8")); execution = json.loads(EXECUTION.read_text(encoding="utf-8")); milestones = list(prior["local_zero_external_cost_evidence"])
    milestones.extend({"milestone": name, "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"} for name in APPENDED)
    doc = {**prior, "schema_version": "1.30", "record_id": "ng-ch05-production-cost-ledger-r31", "supersedes": {"record_id": prior["record_id"], "path": PRIOR.relative_to(ROOT).as_posix(), "sha256": sha256(PRIOR)}, "local_zero_external_cost_evidence": milestones, "revision_summary": {"prior_local_milestones": len(prior["local_zero_external_cost_evidence"]), "appended_local_milestones": len(APPENDED), "total_local_milestones": len(milestones), "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"}, "built_in_product_activity": {"product": "OpenAI built-in ImageGen in Codex", "sequence_tool_calls": execution["summary"]["sequence_outputs"], "raster_outputs": execution["summary"]["sequence_outputs"], "comic_panel_plan_crops": 50, "authorized_reference_uses": execution["summary"]["authorized_reference_uses"], "unique_authorized_reference_hashes": 3, "overlap_adjusted_tool_call_wall_seconds": execution["summary"]["overlap_adjusted_tool_call_wall_seconds"], "model": None, "endpoint": None, "provider_request_ids": None, "usage": None, "monetary_cost_usd": None, "deterministic_seed": None}, "boundary": "Append-only accounting. Direct paid API/cloud requests/uploads/spend remain 0/0/$0; separately authorized built-in ImageGen activity is counted explicitly and its monetary cost is unavailable, not zero. G07 remains separate."}
    OUTPUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"); print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "total_local_milestones": len(milestones), "built_in_calls": doc["built_in_product_activity"]["sequence_tool_calls"]}, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
