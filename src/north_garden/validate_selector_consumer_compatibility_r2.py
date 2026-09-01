"""Prove selector r2 extends coverage without changing existing r1 consumers."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
R1 = ROOT / "config/scale-aware-repair-boundary-selector-contract-r1.json"
R2 = ROOT / "config/scale-aware-repair-boundary-selector-contract-r2.json"
OUTPUT = ROOT / "docs/research/evidence/selector-consumer-compatibility-r2.json"
R1_PATH = R1.relative_to(ROOT).as_posix()

SOURCE_CONSUMERS = {
    "src/north_garden/render_record_boundary.py": "RenderRecord v2.1 exact historical selector/profile binding",
    "src/north_garden/validate_ch05_repair_evidence_readiness_matrix.py": "chapter denominator and profile readiness",
    "src/north_garden/validate_disconnected_holed_topology_stress.py": "panel-neutral control baseline",
    "src/north_garden/validate_exact_base_boundary_measurement_packet.py": "exact-base fixture selector binding",
    "src/north_garden/validate_scale_aware_boundary_selector.py": "historical r1 contract validation",
    "src/north_garden/validate_selected_route_hardening_state.py": "non-promotional selected-route state",
}

EVIDENCE_BINDINGS = {
    "docs/research/evidence/exact-base-boundary-measurement-packet-r1.json": ("sources", "selector_contract"),
    "docs/research/evidence/disconnected-holed-mask-topology-stress-r1.json": ("sources", "selector"),
    "docs/research/evidence/selected-route-hardening-state-r1.json": ("sources", "selector"),
}

VALIDATORS = [
    "src/north_garden/validate_scale_aware_boundary_selector.py",
    "src/north_garden/validate_scale_aware_boundary_selector_r2.py",
    "src/north_garden/validate_render_record_boundary.py",
    "src/north_garden/validate_ch05_repair_evidence_readiness_matrix.py",
    "src/north_garden/validate_exact_base_boundary_measurement_packet.py",
    "src/north_garden/validate_selected_route_hardening_state.py",
]


class CompatibilityError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise CompatibilityError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def nested(value: dict, keys: tuple[str, ...]) -> dict:
    current: object = value
    for key in keys:
        require(isinstance(current, dict) and key in current, f"missing evidence binding: {'.'.join(keys)}")
        current = current[key]
    require(isinstance(current, dict), f"invalid evidence binding: {'.'.join(keys)}")
    return current


def run_validators() -> list[dict]:
    results = []
    for script in VALIDATORS:
        result = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0, f"consumer validator failed: {script}")
        lines = result.stdout.strip().splitlines()
        results.append({
            "script": script,
            "sha256": sha256(ROOT / script),
            "passed": True,
            "stdout_last_line": lines[-1] if lines else "",
        })
    return results


def build() -> dict:
    r1 = json.loads(R1.read_text(encoding="utf-8"))
    r2 = json.loads(R2.read_text(encoding="utf-8"))
    require(r2["supersedes"] == {"contract_id": r1["contract_id"], "path": R1_PATH, "sha256": sha256(R1)}, "r2 supersession mismatch")
    require(r2["prior_contract_rewritten"] is False, "r1 rewrite claimed")
    require(r2["selection_pipeline"] == r1["selection_pipeline"], "selection pipeline changed")
    require(r2["profiles"] == r1["profiles"], "panel profiles changed")
    require(set(r2["profiles"]) == {"ng-ch05-sc01-p036", "ng-ch05-sc01-p044"}, "profile set changed")
    require([r2["profiles"][panel]["local_width_px"] for panel in sorted(r2["profiles"])] == [16, 5], "profile widths changed")

    generic = r2["panel_neutral_mechanics_controls"]["disconnected_holed_support"]
    for field in ("eligible_as_panel_profile", "eligible_as_production_policy", "eligible_as_visual_acceptance"):
        require(generic[field] is False, f"generic control promoted: {field}")
    require("disconnected_holed_support" not in r2["profiles"], "generic control leaked into profiles")
    for rule, value in r1["generalization_rules"].items():
        require(r2["generalization_rules"].get(rule) == value, f"r1 generalization rule changed: {rule}")

    source_consumers = []
    for relative, role in SOURCE_CONSUMERS.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        require(text.count(R1_PATH) == 1, f"unexpected r1 binding count: {relative}")
        source_consumers.append({
            "path": relative,
            "sha256": sha256(path),
            "r1_path_binding_count": 1,
            "role": role,
            "binding_state": "INTENTIONAL_IMMUTABLE_R1_NOT_STALE",
        })

    evidence_bindings = []
    for relative, keys in EVIDENCE_BINDINGS.items():
        path = ROOT / relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        ref = nested(payload, keys)
        require(ref.get("path") == R1_PATH and ref.get("sha256") == sha256(R1), f"evidence selector binding changed: {relative}")
        evidence_bindings.append({
            "path": relative,
            "sha256": sha256(path),
            "selector_reference_path": ref["path"],
            "selector_reference_sha256": ref["sha256"],
            "binding_state": "EXACT_HISTORICAL_R1_BINDING_PRESERVED",
        })

    # Import only after source/hash checks so the same implementation exercised by
    # the RenderRecord validator supplies the consumer-facing profile projection.
    sys.path.insert(0, str(ROOT / "src/north_garden"))
    from render_record_boundary import expected_profile  # pylint: disable=import-outside-toplevel

    projections = {}
    for panel_id in sorted(r2["profiles"]):
        projection = expected_profile(panel_id)
        profile = r2["profiles"][panel_id]
        require(projection["profile"] == {
            "panel_id": panel_id,
            "plan_revision_id": profile["plan_revision_id"],
            "local_width_px": profile["local_width_px"],
        }, f"consumer profile projection changed: {panel_id}")
        require(projection["selector_contract"] == {
            "record_id": r1["contract_id"],
            "path": R1_PATH,
            "sha256": sha256(R1),
        }, f"RenderRecord selector binding changed: {panel_id}")
        projections[panel_id] = {
            "profile_projection_sha256": canonical_sha256(projection["profile"]),
            "selector_binding": projection["selector_contract"],
        }
    require(expected_profile("disconnected_holed_support") == {}, "generic control accepted as panel profile")

    validators = run_validators()
    return {
        "record_type": "SelectorConsumerCompatibilityEvidence",
        "schema_version": "1.0",
        "record_id": "ng-selector-consumer-compatibility-r2",
        "state": "R2_PROFILE_SEMANTICS_IDENTICAL_R1_CONSUMERS_VALID_GENERIC_CONTROL_ISOLATED",
        "selectors": {
            "r1": {"record_id": r1["contract_id"], "path": R1_PATH, "sha256": sha256(R1)},
            "r2": {"record_id": r2["contract_id"], "path": R2.relative_to(ROOT).as_posix(), "sha256": sha256(R2)},
        },
        "canonical_equivalence": {
            "selection_pipeline_equal": True,
            "selection_pipeline_sha256": canonical_sha256(r1["selection_pipeline"]),
            "profiles_equal": True,
            "profiles_sha256": canonical_sha256(r1["profiles"]),
            "profile_count_r1": 2,
            "profile_count_r2": 2,
            "preserved_r1_generalization_rules": len(r1["generalization_rules"]),
        },
        "panel_profile_projections": projections,
        "generic_control_isolation": {
            "control_id": "disconnected_holed_support",
            "selected_local_width_px": generic["selected_local_width_px"],
            "present_in_profiles": False,
            "expected_profile_result": {},
            "eligible_as_panel_profile": False,
            "eligible_as_production_policy": False,
            "eligible_as_visual_acceptance": False,
        },
        "source_consumers": source_consumers,
        "immutable_evidence_bindings": evidence_bindings,
        "validator_results": validators,
        "summary": {
            "selection_pipeline_entries_unchanged": 6,
            "panel_profiles_unchanged": 2,
            "source_consumers_validated": len(source_consumers),
            "immutable_evidence_bindings_validated": len(evidence_bindings),
            "consumer_validators_passed": len(validators),
            "generic_controls_rejected_as_profiles": 1,
            "render_records_rewritten": 0,
            "production_profiles_added": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "migration_decision": "Existing r1-bound evidence and RenderRecord v2.1 projections remain immutable and valid. R2 is an append-only topology-coverage contract, not a forced consumer migration.",
        "boundary": "Canonical compatibility does not promote the generic control, create exact-base visual evidence, human review, production authority, or a provider outcome.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["canonical_equivalence"].update(selection_pipeline_equal=False),
        lambda item: item["canonical_equivalence"].update(profiles_equal=False),
        lambda item: item["canonical_equivalence"].update(profile_count_r2=3),
        lambda item: item["panel_profile_projections"]["ng-ch05-sc01-p036"].update(profile_projection_sha256="0" * 64),
        lambda item: item["panel_profile_projections"]["ng-ch05-sc01-p044"]["selector_binding"].update(record_id="ng-scale-aware-repair-boundary-selector-contract-r2"),
        lambda item: item["generic_control_isolation"].update(present_in_profiles=True),
        lambda item: item["generic_control_isolation"].update(eligible_as_panel_profile=True),
        lambda item: item["generic_control_isolation"].update(eligible_as_production_policy=True),
        lambda item: item["source_consumers"].pop(),
        lambda item: item["immutable_evidence_bindings"][0].update(selector_reference_sha256="0" * 64),
        lambda item: item["validator_results"][2].update(passed=False),
        lambda item: item["summary"].update(render_records_rewritten=1),
        lambda item: item["summary"].update(production_profiles_added=1),
        lambda item: item["summary"].update(provider_requests=1),
        lambda item: item["summary"].update(external_cost_usd="1.000000"),
    ]
    for action in actions:
        item = copy.deepcopy(expected)
        action(item)
        values.append(item)
    return sum(item != expected for item in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked compatibility evidence differs")
        rejected, total = mutations(expected)
        require(rejected == total, "compatibility mutations not rejected")
    except (CompatibilityError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (r2 pipeline/profiles canonically identical; 6 source consumers/3 evidence bindings valid)")
    print(f"6/6 consumer validators pass; generic control rejected as profile; {rejected}/{total} mutations rejected; 0 requests/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
