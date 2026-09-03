"""Validate a complete-chapter prompt manifest against CH05 cross-panel gates."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "production/comic/contracts/ch05-cross-panel-semantic-gates-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_contract(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []; check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "ComicPanelPlanCrossPanelSemanticGateContract", "record_type")
    check(doc.get("state") == "ACTIVE_PRE_PROMPT_FAIL_CLOSED", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan" and doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "planning boundary")
    gates = doc.get("gates", [])
    check(len(gates) == 8 and len({gate.get("gate_id") for gate in gates}) == 8, "gate count")
    expected = {row["panel_id"] for row in json.loads(PLANS.read_text(encoding="utf-8"))["plans"]}
    check(all(set(gate.get("panel_ids", [])) <= expected for gate in gates), "known panels")
    check(all(set(gate.get("required_prompt_phrases", {})) == set(gate.get("panel_ids", [])) for gate in gates), "phrase coverage")
    check(doc.get("summary") == {"gates": 8, "unique_affected_panels": 13, "required_prompt_bindings": 15}, "summary")
    return errors


def validate_prompt(contract: dict[str, Any], prompt_doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sequences = prompt_doc.get("sequences", [])
    for gate in contract["gates"]:
        for panel_id, phrase in gate["required_prompt_phrases"].items():
            order = int(panel_id.rsplit("p", 1)[1])
            matching = [row for row in sequences if row.get("panel_range", [0, -1])[0] <= order <= row.get("panel_range", [0, -1])[1]]
            if len(matching) != 1 or phrase not in matching[0].get("prompt_text", ""):
                errors.append(f"{gate['gate_id']}:{panel_id}")
    return errors


def self_test(contract: dict[str, Any]) -> tuple[int, int]:
    mutations = [lambda d: d.__setitem__("state", "INACTIVE"), lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"), lambda d: d["gates"].pop(), lambda d: d["gates"][0].__setitem__("gate_id", d["gates"][1]["gate_id"]), lambda d: d["gates"][0]["panel_ids"].append("unknown"), lambda d: d["gates"][0]["required_prompt_phrases"].pop("ng-ch05-sc01-p001"), lambda d: d["summary"].__setitem__("gates", 7)]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(contract); mutation(candidate); caught += bool(validate_contract(candidate))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--prompt-manifest", type=Path); parser.add_argument("--self-test", action="store_true"); parser.add_argument("--expect-prompt-failure", action="store_true"); args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8")); errors = validate_contract(contract); prompt_errors: list[str] = []
    if args.prompt_manifest:
        path = args.prompt_manifest if args.prompt_manifest.is_absolute() else ROOT / args.prompt_manifest
        prompt_errors = validate_prompt(contract, json.loads(path.read_text(encoding="utf-8")))
        if prompt_errors and not args.expect_prompt_failure: errors.extend(prompt_errors)
        if args.expect_prompt_failure and not prompt_errors: errors.append("prompt unexpectedly passed")
    caught = total = 0
    if args.self_test:
        caught, total = self_test(contract)
        if caught != total: errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "prompt_gate_failures": prompt_errors, "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__": raise SystemExit(main())
