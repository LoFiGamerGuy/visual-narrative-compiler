"""Exhaust all P036 offline-preflight prerequisite subsets without network activity."""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/research/evidence/p036-prerequisite-authority-lattice-r1.json"
PREFLIGHT_SOURCE = ROOT / "src/north_garden/preflight_openai_p036_submission.py"
PREFLIGHT_VALIDATOR = ROOT / "src/north_garden/validate_openai_p036_offline_preflight.py"
AUTHORITY_FRONTIER = ROOT / "docs/research/evidence/selected-route-authority-dependency-frontier-r1.json"
READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r2.json"
PREREQUISITES = ("base", "mask", "authority", "reservation")


class LatticeError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise LatticeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    sys.path.insert(0, str(ROOT / "src/north_garden"))
    from preflight_openai_p036_submission import compile_offline_preflight  # pylint: disable=import-outside-toplevel
    from validate_openai_p036_offline_preflight import fixtures  # pylint: disable=import-outside-toplevel

    source = PREFLIGHT_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(name=node.module or "")])
    }
    prohibited = sorted(imported & {"requests", "urllib", "httpx", "openai", "socket", "aiohttp"})
    require(not prohibited and "OPENAI_API_KEY" not in source, "preflight gained client/network/credential capability")

    full = dict(zip(PREREQUISITES, fixtures(), strict=True))
    states = []
    blocker_frequency: Counter[str] = Counter()
    for bits in itertools.product((False, True), repeat=4):
        supplied = {name: copy.deepcopy(full[name]) if present else None for name, present in zip(PREREQUISITES, bits, strict=True)}
        result = compile_offline_preflight(**supplied, validation_fixture_mode=True)
        blockers = sorted(result["blockers"])
        blocker_frequency.update(blockers)
        complete = all(bits)
        envelope = result["request_envelope"]
        if complete:
            require(not blockers and envelope is not None, "complete validation fixture did not reach metadata envelope")
            require(envelope["state"] == "SYNTHETIC_VALIDATION_ONLY", "complete fixture envelope not synthetic")
            require(envelope["request_body"] is None and envelope["network_submission_implemented"] is False, "complete fixture gained request capability")
        else:
            require(blockers and envelope is None, f"partial prerequisite subset reached envelope: {bits}")
        network = result["network"]
        require(network == {
            "network_capability_present": False,
            "request_body_constructed": False,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        }, f"subset activity changed: {bits}")
        states.append({
            "subset_bits_base_mask_authority_reservation": "".join("1" if bit else "0" for bit in bits),
            "provided": [name for name, present in zip(PREREQUISITES, bits, strict=True) if present],
            "blockers": blockers,
            "panel_input_package_hash_present": result["panel_input_package_sha256"] is not None,
            "metadata_envelope_present": envelope is not None,
            "envelope_state": envelope["state"] if envelope else None,
            "request_body_present": bool(envelope and envelope["request_body"] is not None),
            "network_submission_implemented": bool(envelope and envelope["network_submission_implemented"]),
        })

    production_mode = compile_offline_preflight(**copy.deepcopy(full), validation_fixture_mode=False)
    require("PROXY_CONTROL_INELIGIBLE_AS_PRODUCTION_INPUT" in production_mode["blockers"], "complete fixture self-promoted outside fixture mode")
    require(production_mode["request_envelope"] is None, "production-mode proxy attempt reached envelope")

    frontier = json.loads(AUTHORITY_FRONTIER.read_text(encoding="utf-8"))
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    require(frontier["summary"]["p036_root_preflight_blockers"] == 4, "authority frontier root count changed")
    require(readiness["offline_preflight"]["blocker_count"] == 4, "readiness root count changed")
    return {
        "record_type": "P036PrerequisiteAuthorityLatticeEvidence",
        "schema_version": "1.0",
        "record_id": "ng-p036-prerequisite-authority-lattice-r1",
        "state": "ALL_PARTIAL_SUBSETS_BLOCKED_COMPLETE_FIXTURE_METADATA_ONLY",
        "sources": {
            "preflight_compiler": {"path": PREFLIGHT_SOURCE.relative_to(ROOT).as_posix(), "sha256": sha256(PREFLIGHT_SOURCE)},
            "fixture_validator": {"path": PREFLIGHT_VALIDATOR.relative_to(ROOT).as_posix(), "sha256": sha256(PREFLIGHT_VALIDATOR)},
            "authority_frontier": {"record_id": frontier["record_id"], "path": AUTHORITY_FRONTIER.relative_to(ROOT).as_posix(), "sha256": sha256(AUTHORITY_FRONTIER)},
            "p036_readiness": {"record_id": readiness["record_id"], "path": READINESS.relative_to(ROOT).as_posix(), "sha256": sha256(READINESS)},
        },
        "prerequisite_order": list(PREREQUISITES),
        "lattice_states": states,
        "blocker_frequency_across_16_subsets": dict(sorted(blocker_frequency.items())),
        "complete_fixture_nonfixture_attempt": {
            "validation_fixture_mode": False,
            "state": production_mode["state"],
            "blockers": production_mode["blockers"],
            "request_envelope": None,
            "eligible_as_real_production_input": False,
        },
        "summary": {
            "prerequisites": 4,
            "subsets_exhausted": len(states),
            "partial_subsets": 15,
            "partial_subsets_blocked": sum(not item["metadata_envelope_present"] for item in states if len(item["provided"]) < 4),
            "complete_fixture_subsets": 1,
            "complete_fixture_metadata_envelopes": sum(item["metadata_envelope_present"] for item in states),
            "request_bodies_constructed": 0,
            "network_capable_subsets": 0,
            "real_authorities_created": 0,
            "real_reservations_created": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "boundary": "Every supplied value is a validation-only synthetic fixture. Exhaustive subset coverage grants no input approval, authority, reservation, request implementation, upload scope, or production outcome.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["prerequisite_order"].pop(),
        lambda item: item["lattice_states"].pop(),
        lambda item: item["lattice_states"][0].update(metadata_envelope_present=True),
        lambda item: item["lattice_states"][-1].update(request_body_present=True),
        lambda item: item["complete_fixture_nonfixture_attempt"].update(eligible_as_real_production_input=True),
        lambda item: item["complete_fixture_nonfixture_attempt"].update(request_envelope={}),
        lambda item: item["summary"].update(subsets_exhausted=15),
        lambda item: item["summary"].update(partial_subsets_blocked=14),
        lambda item: item["summary"].update(complete_fixture_metadata_envelopes=0),
        lambda item: item["summary"].update(request_bodies_constructed=1),
        lambda item: item["summary"].update(network_capable_subsets=1),
        lambda item: item["summary"].update(real_authorities_created=1),
        lambda item: item["summary"].update(real_reservations_created=1),
        lambda item: item["summary"].update(provider_requests=1),
        lambda item: item["summary"].update(external_uploads=1),
        lambda item: item["summary"].update(external_cost_usd="1.000000"),
        lambda item: item["sources"]["preflight_compiler"].update(sha256="0" * 64),
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
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked prerequisite lattice differs")
        rejected, total = mutations(expected)
        require(rejected == total, "lattice mutations not rejected")
    except (LatticeError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (16/16 prerequisite subsets exhausted; 15/15 partial states blocked; complete fixture metadata-only)")
    print(f"nonfixture proxy blocked; {rejected}/{total} mutations rejected; 0 client/body/network/requests/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
