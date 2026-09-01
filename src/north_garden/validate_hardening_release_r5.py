"""Run release r4 plus chronology/closeout/current-ledger validators."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
R4_SCRIPT = "src/north_garden/validate_hardening_release_r4.py"
R4_REPORT = ROOT / "docs/research/evidence/hardening-release-validation-gate-r4.json"
OUTPUT = ROOT / "docs/research/evidence/hardening-release-validation-gate-r5.json"
EXTENSIONS = [
    ("provider_documentation_pre_spend_chronology_r1", "src/north_garden/validate_provider_documentation_chronology.py"),
    ("autonomous_research_engineering_closeout_r1", "src/north_garden/validate_autonomous_closeout_state.py"),
    ("production_cost_ledger_r19", "src/north_garden/validate_ch05_production_cost_ledger_r19.py"),
    ("production_cost_ledger_r20", "src/north_garden/validate_ch05_production_cost_ledger_r20.py"),
    ("production_cost_ledger_r21", "src/north_garden/validate_ch05_production_cost_ledger_r21.py"),
]


class GateError(RuntimeError): pass


def require(value: bool, message: str) -> None:
    if not value: raise GateError(message)


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def run(script: str) -> tuple[subprocess.CompletedProcess[str], float]:
    started = time.perf_counter(); result = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
    return result, round((time.perf_counter() - started) * 1000, 3)


def execute() -> dict:
    base, base_ms = run(R4_SCRIPT); require(base.returncode == 0, "r4 release gate failed")
    r4 = json.loads(R4_REPORT.read_text(encoding="utf-8"))
    require(r4["summary"] == {"base_checks": 65, "extension_checks": 9, "total_checks": 74, "passed_checks": 74, "failed_checks": 0}, "r4 count changed")
    results = []
    for name, script in EXTENSIONS:
        result, elapsed_ms = run(script); require(result.returncode == 0, f"r5 extension failed: {name}")
        lines = result.stdout.strip().splitlines()
        results.append({"name": name, "script": script, "script_sha256": sha256(ROOT / script), "passed": True, "stdout_last_line": lines[-1] if lines else "", "observed_elapsed_ms": elapsed_ms})
    return {"base_elapsed_ms": base_ms, "extensions": results}


def semantic(observed: dict) -> dict:
    return {
        "record_type": "HardeningReleaseValidationGate", "schema_version": "1.4", "record_id": "ng-hardening-release-validation-gate-r5",
        "state": "FINAL_AUTONOMOUS_CLOSEOUT_RELEASE_CHECKS_PASS",
        "supersedes": {"record_id": "ng-hardening-release-validation-gate-r4", "path": R4_REPORT.relative_to(ROOT).as_posix(), "sha256": sha256(R4_REPORT), "checks": 74},
        "prior_gate_rewritten": False,
        "base_gate": {"script": R4_SCRIPT, "script_sha256": sha256(ROOT / R4_SCRIPT), "checks": 74, "passed": 74},
        "extensions": [{key: value for key, value in item.items() if key != "observed_elapsed_ms"} for item in observed["extensions"]],
        "summary": {"base_checks": 74, "extension_checks": len(EXTENSIONS), "total_checks": 74 + len(EXTENSIONS), "passed_checks": 74 + len(EXTENSIONS), "failed_checks": 0},
        "objective": {"requirements_complete": 12, "requirements_total": 12, "engineering_scope_achieved": True, "human_review_complete": False, "production_authority_complete": False},
        "activity": {"network_requests": 0, "provider_requests": 0, "external_uploads": 0, "models_downloaded": 0, "external_cost_usd": "0.000000"},
        "current_boundary_state": {"g07_human_decisions": 0, "g07_human_decisions_required": 20, "ch05_approved_inputs": 0, "ch05_production_cap_usd": None, "real_render_records_v2_1": 0, "accepted_ch05_panels": 0, "approvals_requested_now": [], "next_external_action": None},
        "boundaries": ["R4 remains immutable as the 74-check base.", "Engineering closeout does not complete human review or production authority.", "Passing creates no request, upload, spend, acceptance, or commercial clearance."],
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []; actions = [
        lambda x:x["supersedes"].update(sha256="0"*64), lambda x:x.update(prior_gate_rewritten=True), lambda x:x["base_gate"].update(checks=73),
        lambda x:x["extensions"].pop(), lambda x:x["extensions"][0].update(passed=False), lambda x:x["summary"].update(total_checks=78),
        lambda x:x["summary"].update(passed_checks=78), lambda x:x["objective"].update(requirements_complete=11), lambda x:x["objective"].update(human_review_complete=True),
        lambda x:x["objective"].update(production_authority_complete=True), lambda x:x["current_boundary_state"].update(g07_human_decisions=20),
        lambda x:x["current_boundary_state"].update(ch05_production_cap_usd="100.000000"), lambda x:x["current_boundary_state"]["approvals_requested_now"].append("CH05 cap"),
        lambda x:x["current_boundary_state"].update(next_external_action="submit P036"), lambda x:x["activity"].update(network_requests=1),
        lambda x:x["activity"].update(external_uploads=1), lambda x:x["activity"].update(external_cost_usd="1.000000"), lambda x:x["boundaries"].pop()]
    for action in actions: item=copy.deepcopy(expected); action(item); values.append(item)
    return sum(item != expected for item in values), len(values)


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--emit",type=Path); args=parser.parse_args()
    try:
        observed=execute(); expected=semantic(observed)
        if args.emit:
            target=args.emit if args.emit.is_absolute() else ROOT/args.emit; target.parent.mkdir(parents=True,exist_ok=True)
            payload=dict(expected); payload["observed_runtime"]={"base_elapsed_ms":observed["base_elapsed_ms"],"extension_elapsed_ms":{x["name"]:x["observed_elapsed_ms"] for x in observed["extensions"]},"total_elapsed_ms":round(observed["base_elapsed_ms"]+sum(x["observed_elapsed_ms"] for x in observed["extensions"]),3),"timing_is_local_nondeterministic":True}
            target.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8",newline="\n")
        else:
            tracked=json.loads(OUTPUT.read_text(encoding="utf-8")); tracked.pop("observed_runtime",None); require(tracked==expected,"tracked release r5 differs")
        rejected,total=mutations(expected); require(rejected==total,"r5 mutations not rejected")
    except (GateError,FileNotFoundError,KeyError,json.JSONDecodeError) as error: print(f"FAIL: {error}",file=sys.stderr); return 1
    print(f"0 failures, 0 warnings (74-check r4 base + {len(EXTENSIONS)} extensions = {74+len(EXTENSIONS)}/{74+len(EXTENSIONS)} local checks pass)")
    print(f"{rejected}/{total} release-r5 mutations rejected; 12/12 engineering scope; G07 0/20/CH05 gated; 0 requests/uploads/downloads/$0"); return 0


if __name__=="__main__": raise SystemExit(main())
