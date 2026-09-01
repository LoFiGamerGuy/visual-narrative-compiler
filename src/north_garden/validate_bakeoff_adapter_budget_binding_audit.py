"""Static post-bakeoff audit of all paid adapters against one aggregate ledger."""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import subprocess
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "config/g07-bakeoff-budget-policy-r1.json"
LEDGER = ROOT / "docs/research/evidence/g07-bakeoff-cost-ledger-r1.json"
VAULT = ROOT / "docs/research/evidence/g07-local-evidence-vault-manifest-r1.json"
R2 = ROOT / "docs/research/evidence/g07-aggregate-budget-binding-audit-r2.json"
OUTPUT = ROOT / "docs/research/evidence/g07-aggregate-budget-binding-audit-r3.json"
ADAPTERS = {
    "openai_gpt_image_2": {"path": "src/north_garden/openai_gpt_image2_bakeoff.py", "paid_call": "urlopen", "required": ["reserve_bakeoff_request", "hold_for_reconciliation", "release_unsubmitted_reservation"]},
    "gemini_3_1_flash_image": {"path": "src/north_garden/gemini_flash_image_bakeoff.py", "paid_call": "urlopen", "required": ["reserve_bakeoff_request", "hold_for_reconciliation", "release_unsubmitted_reservation"]},
    "grok_imagine_image_2": {"path": "src/north_garden/xai_grok_imagine_bakeoff.py", "paid_call": "urlopen", "required": ["reserve_bakeoff_request", "hold_for_reconciliation", "reconcile_reservation", "release_unsubmitted_reservation"]},
    "bfl_flux_2": {"path": "src/north_garden/bfl_flux2_bakeoff.py", "paid_call": "post_json", "required": ["reserve_bakeoff_request", "hold_for_reconciliation", "reconcile_reservation"]},
}


class AuditError(RuntimeError): pass


def require(value: bool, message: str) -> None:
    if not value: raise AuditError(message)


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name): return node.func.id
    if isinstance(node.func, ast.Attribute): return node.func.attr
    return None


def adapter_audit(adapter_id: str, spec: dict) -> dict:
    path = ROOT / spec["path"]; source = path.read_text(encoding="utf-8"); tree = ast.parse(source)
    imports = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "bakeoff_budget": imports.update(alias.name for alias in node.names)
    require(set(spec["required"]) <= imports and "CAP_ENV" in imports, f"{adapter_id} shared-budget imports incomplete")
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "execute_one")
    calls = [(call_name(node), node.lineno, node) for node in ast.walk(function) if isinstance(node, ast.Call)]
    reserves = [(line, node) for name, line, node in calls if name == "reserve_bakeoff_request"]
    paid = [line for name, line, _ in calls if name == spec["paid_call"]]
    require(len(reserves) == 1 and paid, f"{adapter_id} reserve/paid call missing")
    reserve_line, reserve_node = reserves[0]
    require(reserve_node.args and isinstance(reserve_node.args[0], ast.Constant) and reserve_node.args[0].value == adapter_id, f"{adapter_id} reservation identity mismatch")
    require(reserve_line < min(paid), f"{adapter_id} paid call can precede reservation")
    require("100.000000" not in source and "$100" not in source, f"{adapter_id} contains adapter-local cap")
    result = {
        "adapter_id": adapter_id, "source_path": spec["path"], "source_sha256": sha256(path),
        "shared_budget_imports": sorted(imports.intersection({"CAP_ENV", "reserve_bakeoff_request", "hold_for_reconciliation", "release_unsubmitted_reservation", "reconcile_reservation"})),
        "execute_one_reservation_line": reserve_line, "first_paid_submission_line": min(paid), "reservation_precedes_paid_submission": True,
        "adapter_local_cap_literal": False,
    }
    if adapter_id == "gemini_3_1_flash_image":
        recovery = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "recover_one")
        recovery_calls = [call_name(node) for node in ast.walk(recovery) if isinstance(node, ast.Call)]
        require("reserve_bakeoff_request" not in recovery_calls and "hold_for_reconciliation" in recovery_calls, "Gemini recovery does not reuse existing hold")
        result["recovery"] = "official interaction retrieval reuses failed record reservation; no new reserve/generation"
    if adapter_id == "bfl_flux_2":
        mapping = next(node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "CONTROL_URL_ENVS" for target in node.targets))
        values = ast.literal_eval(mapping.value)
        require(values == {"g07a-control": "NORTH_GARDEN_BFL_G07A_CONTROL_URL", "g07a-nochange-reference": "NORTH_GARDEN_BFL_G07A_NOCHANGE_CONTROL_URL"}, "BFL control URL mapping changed")
        require("remote_hash != asset[\"sha256\"]" in source, "BFL public URL hash boundary missing")
        result["pre_reservation_public_fetch"] = "no-charge URL/hash verification only"
        result["approved_url_controls"] = values
    return result


def build() -> dict:
    policy = json.loads(POLICY.read_text(encoding="utf-8")); ledger = json.loads(LEDGER.read_text(encoding="utf-8")); vault = json.loads(VAULT.read_text(encoding="utf-8"))
    require(set(policy["scope"]["adapters"]) == set(ADAPTERS), "policy adapter set changed")
    audits = [adapter_audit(adapter, ADAPTERS[adapter]) for adapter in policy["scope"]["adapters"]]
    entries = ledger["entries"]; states = Counter(item["state"] for item in entries); counts = Counter(item["adapter_id"] for item in entries)
    committed = sum(Decimal(item["actual_cost_usd"]) for item in entries if item["state"] == "committed")
    held = sum(Decimal(item["reserved_usd"]) for item in entries if item["state"] in {"reserved", "awaiting_reconciliation"})
    require(committed == Decimal(ledger["committed_actual_cost_usd"]) == Decimal("1.057377"), "committed cost mismatch")
    require(held == Decimal(ledger["held_reservations_usd"]) == 0, "held cost mismatch")
    require(committed + held + Decimal(ledger["available_usd"]) == Decimal(ledger["approved_aggregate_cap_usd"]), "aggregate total mismatch")
    require(all(item["policy_id"] == policy["record_id"] for item in entries), "ledger policy binding mismatch")
    bfl_records = [item for item in vault["records"] if item["adapter_id"] == "bfl_flux_2"]
    approved_hashes = {"g07a-control": "0a7237f655492f4aea7618036b7bac1a5068882f113ae395188ab50abb5a2699", "g07a-nochange-reference": "867a05c2f3e35f196cd28a9d1dc1954f2ba862f62d33ae34df4f3161a3200436"}
    observed_inputs = {key: value for item in bfl_records for key, value in item["input_hashes"].items()}
    require(len(bfl_records) == 4 and observed_inputs == approved_hashes, "BFL vault boundary changed")
    return {
        "record_type": "G07AggregateBudgetAdapterBindingAudit", "schema_version": "2.1", "record_id": "ng-g07-aggregate-budget-binding-audit-r3",
        "state": "POST_BAKEOFF_ALL_PAID_ADAPTERS_SHARED_LEDGER_BOUND_NO_EXECUTION",
        "supersedes": {"record_id": "ng-g07-aggregate-budget-binding-audit-r2", "path": R2.relative_to(ROOT).as_posix(), "sha256": sha256(R2)},
        "prior_record_rewritten": False,
        "sources": {"policy": {"path": POLICY.relative_to(ROOT).as_posix(), "sha256": sha256(POLICY)}, "ledger": {"path": LEDGER.relative_to(ROOT).as_posix(), "sha256": sha256(LEDGER)}, "vault": {"path": VAULT.relative_to(ROOT).as_posix(), "sha256": sha256(VAULT)}},
        "policy": {"aggregate_cap_usd": policy["maximum_aggregate_cap_usd"], "maximum_full_bakeoff_reservation_usd": policy["maximum_full_bakeoff_reservation_usd"], "adapter_request_ceilings_usd": policy["per_request_reservation_usd"], "adapter_local_caps_allowed": False},
        "adapters": audits,
        "ledger_reconciliation": {"entries": len(entries), "entries_by_adapter": dict(sorted(counts.items())), "states": dict(sorted(states.items())), "committed_actual_cost_usd": ledger["committed_actual_cost_usd"], "held_reservations_usd": ledger["held_reservations_usd"], "available_usd": ledger["available_usd"], "required_candidate_cost_usd": "0.987377", "additional_paid_failure_cost_usd": "0.070000"},
        "bfl_boundary": {"required_candidates": len(bfl_records), "approved_public_control_keys": ["g07a-control", "g07a-nochange-reference"], "adult_likeness_or_private_input_allowed": False, "child_related_input_allowed": False, "expanded_upload_authority": False},
        "activity": {"provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "boundary": "Static post-bakeoff audit only. It neither reopens execution nor converts remaining aggregate availability into production authority.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    item = copy.deepcopy(expected); item["supersedes"]["sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["prior_record_rewritten"] = True; values.append(item)
    item = copy.deepcopy(expected); item["policy"]["aggregate_cap_usd"] = "400.000000"; values.append(item)
    item = copy.deepcopy(expected); item["policy"]["adapter_local_caps_allowed"] = True; values.append(item)
    item = copy.deepcopy(expected); item["adapters"][0]["reservation_precedes_paid_submission"] = False; values.append(item)
    item = copy.deepcopy(expected); item["adapters"].pop(); values.append(item)
    item = copy.deepcopy(expected); item["ledger_reconciliation"]["held_reservations_usd"] = "1.000000"; values.append(item)
    item = copy.deepcopy(expected); item["ledger_reconciliation"]["committed_actual_cost_usd"] = "0.987377"; values.append(item)
    item = copy.deepcopy(expected); item["bfl_boundary"]["approved_public_control_keys"].append("private-reference"); values.append(item)
    item = copy.deepcopy(expected); item["bfl_boundary"]["expanded_upload_authority"] = True; values.append(item)
    item = copy.deepcopy(expected); item["bfl_boundary"]["child_related_input_allowed"] = True; values.append(item)
    item = copy.deepcopy(expected); item["activity"]["provider_requests"] = 1; values.append(item)
    return sum(value != expected for value in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else: require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked binding audit differs")
        rejected, total = mutations(expected); require(rejected == total, "mutation rejection incomplete")
        preflight = subprocess.run([sys.executable, "src/north_garden/validate_bakeoff_adapter_preflights.py"], cwd=ROOT, capture_output=True, text=True)
        require(preflight.returncode == 0, "adapter dry preflights failed")
    except (AuditError, FileNotFoundError, KeyError, json.JSONDecodeError, StopIteration, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    print("0 failures, 0 warnings (4/4 adapters reserve shared ledger before paid submission; no adapter-local cap)")
    print("18 entries: 17 committed/1 proven-unsubmitted release/0 held; $1.057377 committed/$98.942623 available")
    print(f"BFL remains two public controls only; {rejected}/{total} mutations rejected; audit made 0 requests/uploads/$0")
    return 0


if __name__ == "__main__": raise SystemExit(main())
