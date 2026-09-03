"""Append final closeout/reconciliation evidence to the CH05 cost ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r36.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r37.json"
SOURCES = [
    ROOT / "docs/research/evidence/ch05-overnight-closeout-release-r1.json",
    ROOT / "docs/research/evidence/ch05-active-goal-art-output-reconciliation-r1.json",
]
MILESTONES = [
    "ch05_overnight_closeout_release_r1",
    "ch05_active_goal_art_output_reconciliation_r1",
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
        "schema_version": "1.36",
        "record_id": "ng-ch05-production-cost-ledger-r37",
        "supersedes": {"record_id": prior["record_id"], **bind(PRIOR)},
        "local_zero_external_cost_evidence": rows,
        "revision_summary": {
            "prior_local_milestones": len(prior["local_zero_external_cost_evidence"]),
            "appended_local_milestones": 2,
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
            "Append-only accounting from r36. The closeout release and count reconciliation "
            "are local evidence operations with zero provider calls, uploads, generation, "
            "candidates, or paid spend. Historical built-in activity and unavailable service "
            "metadata remain unchanged; no review, acceptance, rights, commercial-use, or "
            "exact-production-base state is inferred."
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
                "total_milestones": len(rows),
                "paid_spend_usd": "0.000000",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
