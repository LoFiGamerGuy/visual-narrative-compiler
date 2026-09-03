"""Append final local review/inventory audits to the CH05 cost ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r35.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r36.json"
SOURCES = [
    ROOT / "docs/research/evidence/ch05-complete-chapter-review-handoff-r7-link-integrity-r1.json",
    ROOT / "docs/research/evidence/ch05-chapter-scale-production-decision-matrix-r1.json",
    ROOT / "docs/research/evidence/ch05-overnight-safe-source-change-inventory-r1.json",
    ROOT / "docs/research/evidence/ch05-cadence-objective-sensitivity-audit-r1.json",
    ROOT / "docs/research/evidence/ch05-overnight-safe-source-change-inventory-r2.json",
]
MILESTONES = [
    "ch05_complete_chapter_review_handoff_r7_link_integrity_r1",
    "ch05_chapter_scale_production_decision_matrix_r1",
    "ch05_overnight_safe_source_change_inventory_r1",
    "ch05_cadence_objective_sensitivity_audit_r1",
    "ch05_overnight_safe_source_change_inventory_r2",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def main() -> int:
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    rows = list(prior["local_zero_external_cost_evidence"])
    rows.extend(
        {
            "milestone": name,
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        }
        for name in MILESTONES
    )
    document = {
        **prior,
        "schema_version": "1.35",
        "record_id": "ng-ch05-production-cost-ledger-r36",
        "supersedes": {"record_id": prior["record_id"], **bind(PRIOR)},
        "local_zero_external_cost_evidence": rows,
        "revision_summary": {
            "prior_local_milestones": len(prior["local_zero_external_cost_evidence"]),
            "appended_local_milestones": len(MILESTONES),
            "total_local_milestones": len(rows),
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "current_revision_local_evidence_sources": [bind(path) for path in SOURCES],
        "current_revision_activity": {
            "provider_calls": 0,
            "external_uploads": 0,
            "generation_calls": 0,
            "generated_candidates": 0,
            "paid_spend_usd": "0.000000",
            "human_review_minutes": None,
            "accepted": 0,
            "rights_cleared": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "boundary": (
            "Append-only accounting from r35. This revision binds local handoff-link, "
            "decision-matrix, source-inventory, and optimizer-sensitivity evidence only. "
            "It adds zero provider calls, uploads, generation, candidates, or paid spend; "
            "historical built-in activity and unavailable service metadata remain unchanged. "
            "No review, acceptance, rights, commercial-use, or exact-base state is inferred."
        ),
    }
    OUTPUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256(OUTPUT),
                "appended_milestones": len(MILESTONES),
                "total_milestones": len(rows),
                "paid_spend_usd": "0.000000",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
