"""Capture and validate the exact no-download instrumentation runtime snapshot."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import platform
import sys
from importlib.metadata import version
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "config/runtime-assets.example.json"
BOOTSTRAP = ROOT / "scripts/bootstrap-local.ps1"
SUITE = ROOT / "src/north_garden/validate_ch05_instrumentation_suite.py"
OUTPUT = ROOT / "docs/research/evidence/instrumentation-runtime-inventory-r1.json"


class RuntimeErrorEvidence(RuntimeError): pass


def require(value: bool, message: str) -> None:
    if not value: raise RuntimeErrorEvidence(message)


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> dict: return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def build() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    profile = manifest["profiles"]["instrumentation"]
    requirements = []
    for item in profile["requirements"]:
        actual = platform.python_version() if item["kind"] == "executable" else version(item["distribution"])
        if item["kind"] == "python_module": importlib.import_module(item["name"])
        requirements.append(dict(item, actual_version=actual, exact_match=actual == item["version"]))
    executable = Path(sys.executable)
    return {
        "record_type": "InstrumentationRuntimeInventory", "schema_version": "1.0",
        "record_id": "ng-instrumentation-runtime-inventory-r1", "state": "LOCAL_EXACT_RUNTIME_MATCH_NO_DOWNLOADS",
        "sources": {"runtime_manifest": source(MANIFEST), "bootstrap_script": source(BOOTSTRAP), "instrumentation_suite": source(SUITE)},
        "python": {"implementation": sys.implementation.name, "version": platform.python_version(), "cache_tag": sys.implementation.cache_tag, "executable_basename": executable.name, "executable_sha256": sha256(executable)},
        "platform": {"system": platform.system(), "release": platform.release(), "version": platform.version(), "machine": platform.machine()},
        "requirements": requirements,
        "profile": {"entrypoint": profile["entrypoint"], "downloads": profile["downloads"], "network_allowed": profile["network_allowed"], "provider_credentials_required": profile["provider_credentials_required"]},
        "activity": {"packages_installed": 0, "models_downloaded": 0, "provider_calls": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "limitations": ["This is an exact local runtime snapshot, not a cross-platform dependency resolver or wheel lock.", "A different Python executable or OS must create a new reviewed inventory revision rather than edit this record.", "The instrumentation profile excludes provider execution and heavyweight model runtimes."],
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    item = copy.deepcopy(expected); item["sources"]["bootstrap_script"]["sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["python"]["version"] = "3.13.0"; values.append(item)
    item = copy.deepcopy(expected); item["python"]["executable_sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["requirements"][0]["exact_match"] = False; values.append(item)
    item = copy.deepcopy(expected); item["requirements"][1]["actual_version"] = "0.0.0"; values.append(item)
    item = copy.deepcopy(expected); item["profile"]["downloads"] = True; values.append(item)
    item = copy.deepcopy(expected); item["profile"]["network_allowed"] = True; values.append(item)
    item = copy.deepcopy(expected); item["profile"]["provider_credentials_required"] = True; values.append(item)
    item = copy.deepcopy(expected); item["activity"]["packages_installed"] = 1; values.append(item)
    item = copy.deepcopy(expected); item["activity"]["provider_calls"] = 1; values.append(item)
    return sum(value != expected for value in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); args = parser.parse_args()
    try:
        expected = build()
        require(all(item["exact_match"] for item in expected["requirements"]), "runtime does not match pinned profile")
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else: require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked runtime inventory differs")
        rejected, total = mutations(expected); require(rejected == total, "mutation rejection incomplete")
    except (RuntimeErrorEvidence, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    print(f"0 failures, 0 warnings (Python {expected['python']['version']}; Pillow {expected['requirements'][1]['actual_version']}; numpy {expected['requirements'][2]['actual_version']})")
    print(f"exact executable/profile/source hashes; {rejected}/{total} mutations rejected; no install/download/network/provider activity")
    return 0


if __name__ == "__main__": raise SystemExit(main())
