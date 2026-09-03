"""Append zero-external-cost six-route/cadence evidence to the CH05 ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r34.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r35.json"
SOURCES = [
    ROOT / "docs/research/evidence/ch05-six-route-comparison-r1.json",
    ROOT / "production/comic/run-manifests/ch05-sequence-cadence-review-assembly-r1.json",
    ROOT / "docs/research/evidence/ch05-sequence-cadence-review-triage-r1.json",
    ROOT / "docs/research/evidence/ch05-s01-flat-gouache-reference-ablation-comparison-r1.json",
    ROOT / "docs/research/evidence/ch05-s11-flat-gouache-reference-ablation-comparison-r1.json",
    ROOT / "docs/research/evidence/ch05-sequence-cadence-boundary-audit-r1.json",
    ROOT / "docs/research/evidence/ch05-p005-p006-route-attribution-control-r1.json",
    ROOT / "docs/research/evidence/ch05-six-route-owner-review-handoff-r1.json",
    ROOT / "docs/research/evidence/ch05-six-route-cadence-integrated-release-r1.json",
]
MILESTONES = [
    "ch05_six_route_comparison_r1",
    "ch05_sequence_cadence_review_packet_r1",
    "ch05_s01_s11_matched_reference_ablations_r1",
    "ch05_sequence_cadence_boundary_audit_r1",
    "ch05_p005_p006_route_attribution_control_r1",
    "ch05_six_route_owner_review_handoff_r1",
    "ch05_complete_chapter_review_handoff_r7",
    "ch05_six_route_cadence_integrated_release_r1",
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
        "schema_version": "1.34",
        "record_id": "ng-ch05-production-cost-ledger-r35",
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
            "Append-only accounting from r34. The current revision binds local comparison, "
            "review-packet, ablation, boundary, handoff, and release evidence only: zero "
            "provider calls, uploads, generation, candidates, or paid spend. Historical "
            "built-in activity and unavailable monetary/service metadata are preserved "
            "unchanged; no acceptance, rights, commercial-use, or exact-base decision is implied."
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
                "prior_milestones": len(prior["local_zero_external_cost_evidence"]),
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
