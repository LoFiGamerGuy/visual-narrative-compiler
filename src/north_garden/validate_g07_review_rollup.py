"""Fail-closed G07 human-review deblinding and evidence rollup."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from validate_g07_blinded_review import (
    PACKET_PATH,
    build_packet,
    g07_session_errors,
    synthetic_session,
)
from validate_g07_evidence_vault import MANIFEST, ROOT, build_snapshot, canonical_sha256


INSTRUMENTATION = ROOT / "experiments/results/g07-provider-bakeoff-instrumentation-r1.json"
GATE = ROOT / "docs/research/evidence/g07-human-review-rollup-gate-r1.json"


class RollupError(RuntimeError):
    """Human-review rollup cannot be compiled safely."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RollupError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def measured_arm_evidence(instrumentation: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_records = {item["path"]: item for item in manifest["records"] if item["candidate"]}
    arms: dict[str, Any] = {}
    require(set(instrumentation["adapters"]) == {
        "openai_gpt_image_2", "gemini_3_1_flash_image", "grok_imagine_image_2", "bfl_flux_2"
    }, "instrumentation adapter inventory changed")
    for adapter, evidence in instrumentation["adapters"].items():
        records = evidence["records"]
        require(len(records) == 4, f"{adapter} does not have four required records")
        for record in records.values():
            manifest_record = manifest_records.get(record["record_path"])
            require(manifest_record is not None, f"instrumentation record is outside vault: {record['record_path']}")
            require(record["record_sha256"] == manifest_record["sha256"], f"instrumentation record hash drift: {record['record_path']}")
            require(record["candidate_sha256"] == manifest_record["candidate"]["sha256"], f"instrumentation candidate hash drift: {record['record_path']}")
            require(record["cost_usd"] == manifest_record["cost_usd"], f"instrumentation cost drift: {record['record_path']}")
            require(record["elapsed_seconds"] == manifest_record["elapsed_seconds"], f"instrumentation timing drift: {record['record_path']}")
        diagnostics = evidence["diagnostics"]
        arms[adapter] = {
            "required_candidates": evidence["summary"]["required_candidates"],
            "required_candidate_cost_usd": evidence["summary"]["total_cost_usd"],
            "total_elapsed_seconds": evidence["summary"]["total_elapsed_seconds"],
            "mean_elapsed_seconds": evidence["summary"]["mean_elapsed_seconds"],
            "raster_diagnostics": {
                "independent_repeat_changed_pixel_fraction_gt_8": diagnostics["independent_repeat_drift"]["changed_pixel_fraction_threshold_gt_8"],
                "target_change_changed_pixel_fraction_gt_8": diagnostics["target_change_global_drift_from_control"]["changed_pixel_fraction_threshold_gt_8"],
                "no_change_changed_pixel_fraction_gt_8": diagnostics["no_change_global_drift_from_reference"]["changed_pixel_fraction_threshold_gt_8"],
            },
            "diagnostic_limit": "Full-frame raster drift after resize is not semantic correctness or reproducibility.",
        }
    return arms


def mapping_root(mapping: dict[str, str]) -> str:
    return canonical_sha256([{"blind_id": key, "adapter_id": mapping[key]} for key in sorted(mapping)])


def build_pending_gate(
    manifest: dict[str, Any], packet: dict[str, Any], mapping: dict[str, str], instrumentation: dict[str, Any]
) -> dict[str, Any]:
    return {
        "record_type": "G07HumanReviewRollupGate",
        "schema_version": "1.0",
        "record_id": "g07-human-review-rollup-gate-r1",
        "state": "PENDING_COMPLETE_ELIGIBLE_HUMAN_SESSION",
        "source_vault_root_sha256": manifest["integrity"]["vault_root_sha256"],
        "review_packet_sha256": packet["packet_sha256"],
        "deblinding_mapping_root_sha256": mapping_root(mapping),
        "instrumentation_path": INSTRUMENTATION.relative_to(ROOT).as_posix(),
        "instrumentation_sha256": sha256_bytes(INSTRUMENTATION.read_bytes()),
        "required_decisions": 20,
        "actual_decisions": 0,
        "human_minutes": None,
        "accepted_candidate_subjects": 0,
        "human_arm_results": None,
        "measured_nonhuman_arm_evidence": measured_arm_evidence(instrumentation, manifest),
        "selection_state": {
            "existing_engineering_hardening_route": "openai_gpt_image_2",
            "source_decision": "ADR-0025",
            "automatic_reselection": False,
            "human_review_selection_change": None,
        },
        "aggregation_boundary": "No composite score, weighted rank, or automatic route selection. Preserve dimensions and limitations separately.",
    }


def compile_rollup(
    session: dict[str, Any],
    packet: dict[str, Any],
    mapping: dict[str, str],
    instrumentation: dict[str, Any],
    manifest: dict[str, Any],
    *,
    allow_validation_fixture: bool = False,
    expected_mapping_root_sha256: str | None = None,
) -> dict[str, Any]:
    if expected_mapping_root_sha256 is None:
        _expected_packet, expected_mapping = build_packet(manifest, write=False)
        expected_mapping_root_sha256 = mapping_root(expected_mapping)
    require(mapping_root(mapping) == expected_mapping_root_sha256, "deblinding mapping root mismatch")
    errors = g07_session_errors(session, packet)
    require(not errors, "invalid G07 review session: " + "; ".join(errors))
    require(session.get("state") == "COMPLETED", "review session is incomplete")
    if session.get("validation_fixture"):
        require(allow_validation_fixture, "validation fixture cannot create real review evidence")
    else:
        require(session.get("summary", {}).get("review_evidence_eligible") is True, "review session is not evidence eligible")
    decisions = session["events"][-1]["data"]["decisions"]
    require(len(decisions) == 20, "review session must contain exactly 20 decisions")
    by_subject = {item["subject_record_id"]: item for item in decisions}
    packet_subjects = {item["record_id"]: item for item in packet["subjects"]}
    require(set(by_subject) == set(packet_subjects) == set(mapping), "deblinding subject mapping mismatch")

    automated = measured_arm_evidence(instrumentation, manifest)
    arms: dict[str, Any] = {}
    for adapter in sorted(set(mapping.values())):
        blind_ids = [blind_id for blind_id, mapped in mapping.items() if mapped == adapter]
        candidate_ids = [item for item in blind_ids if packet_subjects[item]["subject_kind"] == "candidate"]
        pair_ids = [item for item in blind_ids if packet_subjects[item]["subject_kind"] == "independent_repeat_pair"]
        require(len(candidate_ids) == 4 and len(pair_ids) == 1, f"deblinding coverage mismatch for {adapter}")
        assertion_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"pass": 0, "fail": 0})
        failure_tags: Counter[str] = Counter()
        accepted_candidates = 0
        decision_evidence = []
        for blind_id in candidate_ids + pair_ids:
            decision = by_subject[blind_id]
            if blind_id in candidate_ids and decision["accepted"]:
                accepted_candidates += 1
            for assertion in decision["hard_assertions"]:
                assertion_counts[assertion["assertion_id"]]["pass" if assertion["passed"] else "fail"] += 1
            failure_tags.update(decision.get("failure_tags", []))
            decision_evidence.append({
                "blind_subject_id": blind_id,
                "subject_kind": packet_subjects[blind_id]["subject_kind"],
                "accepted": decision["accepted"],
                "hard_assertions": copy.deepcopy(decision["hard_assertions"]),
                "failure_tags": copy.deepcopy(decision.get("failure_tags", [])),
            })
        arms[adapter] = {
            "measured_nonhuman_evidence": automated[adapter],
            "human_review": {
                "candidate_decisions": 4,
                "repeat_pair_decisions": 1,
                "accepted_candidates": accepted_candidates,
                "assertion_counts": dict(sorted(assertion_counts.items())),
                "failure_tag_counts": dict(sorted(failure_tags.items())),
                "decision_evidence": decision_evidence,
            },
        }
    return {
        "record_type": "G07HumanReviewRollup",
        "schema_version": "1.0",
        "record_id": f"g07-human-review-rollup-{session['session_id']}",
        "state": "SYNTHETIC_VALIDATION_ONLY" if session.get("validation_fixture") else "COMPLETE_HUMAN_REVIEW",
        "source_vault_root_sha256": manifest["integrity"]["vault_root_sha256"],
        "review_packet_sha256": packet["packet_sha256"],
        "review_session_id": session["session_id"],
        "review_session_digest_sha256": canonical_sha256(session),
        "reviewer_id": session["reviewer_id"],
        "human_minutes": session["summary"]["human_minutes"],
        "decisions": len(decisions),
        "arms": arms,
        "composite_score": None,
        "automatic_ranking": None,
        "automatic_selection_change": None,
        "selection_note": "Review dimensions remain separate; any mechanism decision change requires a new evidence-citing ADR.",
    }


def pending_gate_errors(gate: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors = []
    if gate != expected:
        errors.append("pending gate differs from exact evidence")
    if gate.get("human_arm_results") is not None:
        errors.append("pending gate fabricates human arm results")
    if gate.get("human_minutes") is not None or gate.get("actual_decisions") != 0:
        errors.append("pending gate fabricates review activity")
    if gate.get("accepted_candidate_subjects") != 0:
        errors.append("pending gate fabricates acceptance")
    return sorted(set(errors))


def mutation_checks(
    pending: dict[str, Any], fixture: dict[str, Any], packet: dict[str, Any], mapping: dict[str, str],
    instrumentation: dict[str, Any], manifest: dict[str, Any], expected_mapping_root_sha256: str
) -> tuple[int, int]:
    gate_mutations: list[dict[str, Any]] = []
    changed = copy.deepcopy(pending); changed["human_arm_results"] = {}; gate_mutations.append(changed)
    changed = copy.deepcopy(pending); changed["human_minutes"] = 1; gate_mutations.append(changed)
    changed = copy.deepcopy(pending); changed["accepted_candidate_subjects"] = 1; gate_mutations.append(changed)
    changed = copy.deepcopy(pending); changed["instrumentation_sha256"] = "0" * 64; gate_mutations.append(changed)
    changed = copy.deepcopy(pending); first = next(iter(changed["measured_nonhuman_arm_evidence"].values())); first["required_candidate_cost_usd"] = "0"; gate_mutations.append(changed)
    changed = copy.deepcopy(pending); changed["measured_nonhuman_arm_evidence"].pop("bfl_flux_2"); gate_mutations.append(changed)
    rejected = sum(bool(pending_gate_errors(item, pending)) for item in gate_mutations)

    try:
        compile_rollup(fixture, packet, mapping, instrumentation, manifest, expected_mapping_root_sha256=expected_mapping_root_sha256)
    except RollupError:
        rejected += 1
    total = len(gate_mutations) + 1

    incomplete = copy.deepcopy(fixture)
    incomplete["events"][-1]["data"]["decisions"].pop()
    try:
        compile_rollup(incomplete, packet, mapping, instrumentation, manifest, allow_validation_fixture=True, expected_mapping_root_sha256=expected_mapping_root_sha256)
    except RollupError:
        rejected += 1
    total += 1

    wrong_mapping = copy.deepcopy(mapping)
    first, second = list(wrong_mapping)[:2]
    wrong_mapping[first], wrong_mapping[second] = wrong_mapping[second], wrong_mapping[first]
    try:
        compile_rollup(fixture, packet, wrong_mapping, instrumentation, manifest, allow_validation_fixture=True, expected_mapping_root_sha256=expected_mapping_root_sha256)
    except RollupError:
        rejected += 1
    total += 1
    return rejected, total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path, help="write deterministic pending-gate evidence")
    args = parser.parse_args()
    try:
        actual_vault = build_snapshot()
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        require(actual_vault == manifest, "G07 vault differs before rollup")
        packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
        expected_packet, mapping = build_packet(manifest, write=False)
        require(packet == expected_packet, "G07 blinded packet differs before rollup")
        expected_mapping_root_sha256 = mapping_root(mapping)
        instrumentation = json.loads(INSTRUMENTATION.read_text(encoding="utf-8"))
        expected_gate = build_pending_gate(manifest, packet, mapping, instrumentation)
        if args.emit:
            output = args.emit if args.emit.is_absolute() else ROOT / args.emit
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(expected_gate, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
            print(f"wrote {output.relative_to(ROOT).as_posix()}")
        else:
            gate = json.loads(GATE.read_text(encoding="utf-8"))
            errors = pending_gate_errors(gate, expected_gate)
            require(not errors, "; ".join(errors))
        fixture_session = synthetic_session(packet)
        fixture_rollup = compile_rollup(
            fixture_session, packet, mapping, instrumentation, manifest, allow_validation_fixture=True,
            expected_mapping_root_sha256=expected_mapping_root_sha256,
        )
        require(fixture_rollup["state"] == "SYNTHETIC_VALIDATION_ONLY", "fixture leaked into real state")
        require(fixture_rollup["composite_score"] is None, "rollup created a composite score")
        rejected, total = mutation_checks(expected_gate, fixture_session, packet, mapping, instrumentation, manifest, expected_mapping_root_sha256)
        require(rejected == total, "rollup mutation rejection incomplete")
    except (RollupError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings")
    print("4/4 measured arms bound to 16/16 vault candidates; no composite score or automatic ranking")
    print("real review gate: 0/20 decisions, null human minutes, 0 accepted, no human arm results")
    print(f"{rejected}/{total} pending/fixture/coverage/mapping mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
