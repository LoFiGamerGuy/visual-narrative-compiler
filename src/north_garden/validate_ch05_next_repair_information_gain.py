"""Select at most one next local repair control by uncovered mechanics dimensions."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSERTIONS = ROOT / "production/comic/hard-assertion-manifests/ch05-mill-signal-r1.json"
COVERAGE = ROOT / "production/comic/repair-readiness/ch05-chapter-repair-policy-coverage-r1.json"
P036_CAUSAL = ROOT / "docs/research/evidence/ch05-p036-causal-shape-topology-control-r2.json"
REPORT = ROOT / "docs/research/evidence/ch05-next-repair-policy-information-gain-r1.json"
CANDIDATES = ["ng-ch05-sc01-p019", "ng-ch05-sc01-p026", "ng-ch05-sc01-p044"]


class InformationGainError(RuntimeError):
    """Next local repair-control selection evidence failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InformationGainError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


def build_report() -> dict[str, Any]:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    assertions = json.loads(ASSERTIONS.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    p036 = json.loads(P036_CAUSAL.read_text(encoding="utf-8"))
    by_panel = {item["panel_id"]: item for item in plans["plans"]}
    by_assertion_panel = {item.get("applicability"): item for item in assertions["assertions"] if item.get("applicability")}
    policy_absent = [
        item["panel_id"] for item in coverage["panels"]
        if item["state"] == "EXPLICIT_CAUSAL_REPAIR_CANDIDATE_PANEL_SPECIFIC_POLICY_ABSENT"
    ]
    require(policy_absent == CANDIDATES, f"policy-absent candidate set changed: {policy_absent}")
    require(p036["decision"]["thin_feature_exercised"] is True, "P036 thin-feature evidence changed")
    require(p036["limitations"][1].startswith("Concavity and a 42-pixel thin reach"), "P036 topology limitation changed")

    declared = {
        "ng-ch05-sc01-p019": {
            "plan_terms": ["foreground hand signal", "open bridge", "second adult held back"],
            "new_dimension": "separated protected-role blocking",
            "bounded_sharp_geometry_testable_with_current_compositor": True,
            "sub_32px_feature_explicit_in_plan": False,
            "tool_contact_crossing_explicit_in_plan": False,
            "diffuse_or_translucent_effect_explicit_in_plan": False,
            "requires_new_effect_mechanism": False,
            "directly_tests_uncovered_boundary_scale": False,
        },
        "ng-ch05-sc01-p026": {
            "plan_terms": ["hand above drum", "ember", "smoke separates fingers"],
            "new_dimension": "diffuse translucent effect boundary",
            "bounded_sharp_geometry_testable_with_current_compositor": False,
            "sub_32px_feature_explicit_in_plan": False,
            "tool_contact_crossing_explicit_in_plan": False,
            "diffuse_or_translucent_effect_explicit_in_plan": True,
            "requires_new_effect_mechanism": True,
            "directly_tests_uncovered_boundary_scale": False,
        },
        "ng-ch05-sc01-p044": {
            "plan_terms": ["hands", "blade", "taut twine"],
            "new_dimension": "fine bounded tool-contact topology below twice the 16px feather width",
            "bounded_sharp_geometry_testable_with_current_compositor": True,
            "sub_32px_feature_explicit_in_plan": True,
            "tool_contact_crossing_explicit_in_plan": True,
            "diffuse_or_translucent_effect_explicit_in_plan": False,
            "requires_new_effect_mechanism": False,
            "directly_tests_uncovered_boundary_scale": True,
        },
    }
    rows = []
    for panel_id in CANDIDATES:
        panel = by_panel[panel_id]
        assertion = by_assertion_panel[panel_id]
        evidence = declared[panel_id]
        qualifies = (
            evidence["bounded_sharp_geometry_testable_with_current_compositor"]
            and evidence["directly_tests_uncovered_boundary_scale"]
            and not evidence["requires_new_effect_mechanism"]
            and assertion["severity"] == "hard"
        )
        rows.append({
            "panel_id": panel_id,
            "plan_revision_id": panel["plan_revision_id"],
            "display_order": panel["display_order"],
            "narrative_beat": panel["narrative_beat"],
            "composition_intent": panel["composition_intent"],
            "hard_assertion_id": assertion["id"],
            "hard_assertion_requirement": assertion["requirement"],
            **evidence,
            "qualifies_for_next_local_control": qualifies,
            "production_mask_inferred": False,
            "policy_authored": False,
            "external_execution_authorized": False,
        })
    qualified = [item for item in rows if item["qualifies_for_next_local_control"]]
    require([item["panel_id"] for item in qualified] == ["ng-ch05-sc01-p044"], "information-gain rule is not uniquely resolved")
    return {
        "record_type": "ComicRepairPolicyInformationGainSelection",
        "schema_version": "1.0",
        "record_id": "ng-ch05-next-repair-policy-information-gain-r1",
        "state": "ONE_LOCAL_CONTROL_TARGET_SELECTED_NO_POLICY_OR_EXECUTION",
        "sources": {
            "comic_panel_plans": source(PLANS),
            "hard_assertion_manifest": source(ASSERTIONS),
            "chapter_policy_coverage": source(COVERAGE),
            "p036_causal_shape_evidence": source(P036_CAUSAL),
        },
        "current_uncovered_dimensions": [
            "bounded feature narrower than twice the fixed 16px inward feather",
            "sharp tool contact with crossing thin geometry",
            "disconnected-support behavior",
            "diffuse or translucent effect boundary",
            "hole topology",
        ],
        "selection_rule": [
            "candidate must be one of the three exact policy-absent explicit causal panels",
            "plan and hard assertion must provide direct geometry terms",
            "control must exercise a boundary/topology dimension not established by P036",
            "control must use the existing local compositor rather than introduce a new effect or renderer mechanism",
            "selection authorizes one deterministic abstract control only, never a production mask or policy",
        ],
        "candidates": rows,
        "decision": {
            "selected_next_local_control_panel_id": "ng-ch05-sc01-p044",
            "selected_dimension": declared["ng-ch05-sc01-p044"]["new_dimension"],
            "reason": "P044 uniquely supplies explicit bounded blade/twine contact that tests a sub-32px feature under the existing 16px policy without introducing a diffuse-effect mechanism.",
            "production_policy_selected": False,
            "production_mask_authored": False,
            "provider_route_changed": False,
            "external_action_authorized": False,
        },
        "activity": {"provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "limitations": [
            "The sub-32px dimension is a proposed deterministic control parameter derived from the 16px policy, not a measured feature width in absent panel art.",
            "P019 and P026 remain valid future research questions; they are not rejected as panels or repair candidates.",
            "P026's smoke/heat boundary implies a different diffuse-effect mechanism and is deliberately not smuggled into the current compositor experiment.",
            "Selection is for local information gain only and creates no art, input approval, policy inheritance, or production authority.",
        ],
    }


def mutation_checks(expected: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changed = copy.deepcopy(expected); changed["candidates"].pop(); mutations.append(changed)
    changed = copy.deepcopy(expected); changed["candidates"][0], changed["candidates"][1] = changed["candidates"][1], changed["candidates"][0]; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["selected_next_local_control_panel_id"] = "ng-ch05-sc01-p019"; mutations.append(changed)
    changed = copy.deepcopy(expected); p026 = next(item for item in changed["candidates"] if item["panel_id"].endswith("p026")); p026["requires_new_effect_mechanism"] = False; mutations.append(changed)
    changed = copy.deepcopy(expected); p044 = next(item for item in changed["candidates"] if item["panel_id"].endswith("p044")); p044["sub_32px_feature_explicit_in_plan"] = False; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["production_policy_selected"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["production_mask_authored"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["external_action_authorized"] = True; mutations.append(changed)
    return sum(item != expected for item in mutations), len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    try:
        expected = build_report()
        if args.emit:
            output = args.emit if args.emit.is_absolute() else ROOT / args.emit
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"wrote {output.relative_to(ROOT).as_posix()}")
        else:
            tracked = json.loads(REPORT.read_text(encoding="utf-8"))
            require(tracked == expected, "tracked next-control information-gain evidence differs")
        rejected, total = mutation_checks(expected)
        require(rejected == total, "information-gain mutation rejection incomplete")
    except (InformationGainError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings")
    print("3/3 policy-absent causal panels compared; P044 selected for one local blade/twine topology control")
    print("0 policies/masks/requests/uploads; $0; provider route unchanged")
    print(f"{rejected}/{total} inventory/order/selection/mechanism/dimension/authority mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
