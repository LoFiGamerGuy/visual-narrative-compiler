"""Validate append-only CH05 production cost/timing ledger r35."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r35.json"
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r34.json"
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


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    prior = load(PRIOR)
    prior_rows = prior["local_zero_external_cost_evidence"]
    rows = document.get("local_zero_external_cost_evidence", [])
    check(
        document.get("record_type") == "ProductionCostLedger"
        and document.get("schema_version") == "1.34"
        and document.get("record_id") == "ng-ch05-production-cost-ledger-r35",
        "identity",
    )
    check(
        document.get("supersedes") == {"record_id": prior["record_id"], **bind(PRIOR)},
        "supersedes binding",
    )
    check(document.get("prior_record_rewritten") is False, "prior rewrite boundary")
    check(rows[: len(prior_rows)] == prior_rows, "append-only prefix")
    expected_suffix = [
        {
            "milestone": name,
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        }
        for name in MILESTONES
    ]
    check(rows[len(prior_rows) :] == expected_suffix, "append-only suffix")
    check(
        document.get("revision_summary")
        == {
            "prior_local_milestones": 109,
            "appended_local_milestones": 8,
            "total_local_milestones": 117,
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        }
        and len(rows) == 117,
        "revision summary",
    )
    check(
        document.get("current_revision_local_evidence_sources")
        == [bind(path) for path in SOURCES],
        "evidence bindings",
    )
    activity = document.get("current_revision_activity", {})
    check(
        activity
        == {
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
        "current activity boundary",
    )
    for key in (
        "built_in_product_activity",
        "committed_actual_cost_usd",
        "held_reservations_usd",
        "approved_aggregate_cap_usd",
        "available_usd",
        "entries",
        "state",
        "budget_domain",
        "policy_id",
    ):
        check(document.get(key) == prior.get(key), f"prior field preserved:{key}")
    boundary = document.get("boundary", "")
    check(
        all(
            phrase in boundary
            for phrase in (
                "zero provider calls",
                "unavailable monetary/service metadata",
                "no acceptance",
            )
        ),
        "boundary semantics",
    )
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("record_id", "bad"),
        lambda value: value["supersedes"].__setitem__("sha256", "0" * 64),
        lambda value: value["local_zero_external_cost_evidence"].pop(0),
        lambda value: value["local_zero_external_cost_evidence"].pop(),
        lambda value: value["local_zero_external_cost_evidence"][-1].__setitem__("external_uploads", 1),
        lambda value: value["revision_summary"].__setitem__("total_local_milestones", 116),
        lambda value: value["current_revision_local_evidence_sources"].pop(),
        lambda value: value["current_revision_local_evidence_sources"][0].__setitem__("sha256", "f" * 64),
        lambda value: value["current_revision_activity"].__setitem__("provider_calls", 1),
        lambda value: value["current_revision_activity"].__setitem__("human_review_minutes", 0),
        lambda value: value["current_revision_activity"].__setitem__("accepted", 1),
        lambda value: value["current_revision_activity"].__setitem__("paid_spend_usd", "1.000000"),
        lambda value: value["built_in_product_activity"].__setitem__("unavailable_fields", []),
        lambda value: value.__setitem__("committed_actual_cost_usd", "1.000000"),
        lambda value: value.__setitem__("approved_aggregate_cap_usd", "100.000000"),
        lambda value: value.__setitem__("entries", [{}]),
        lambda value: value.__setitem__("boundary", "all accepted"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = load(LEDGER)
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "sources": len(document.get("current_revision_local_evidence_sources", [])),
                "milestones": len(document.get("local_zero_external_cost_evidence", [])),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
