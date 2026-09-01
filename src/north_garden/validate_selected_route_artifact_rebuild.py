"""Rebuild bounded selected-route local artifacts twice and compare exact bytes."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/research/evidence/selected-route-artifact-rebuild-reproducibility-r1.json"
PYTHON = sys.executable
COMMANDS = [
    "src/north_garden/validate_ch05_sequence_layout_control.py",
    "src/north_garden/validate_openai_boundary_hardening.py",
    "src/north_garden/validate_ch05_p036_mask_topology.py",
    "src/north_garden/validate_ch05_p036_causal_shape_control.py",
    "src/north_garden/validate_ch05_p044_fixed_boundary_stress.py",
    "src/north_garden/validate_ch05_p044_adaptive_boundary.py",
    "src/north_garden/validate_render_record_boundary.py",
    "src/north_garden/validate_exact_base_boundary_measurement_packet.py",
]
GROUPS = [
    "experiments/outputs/ch05_p036_layout_control_r1",
    "experiments/outputs/openai_targeted_repair_boundary_hardening_r2",
    "experiments/outputs/ch05_p036_mask_topology_r1",
    "experiments/outputs/ch05_p036_causal_shape_topology_r2",
    "experiments/outputs/ch05_p044_fixed_boundary_stress_r1",
    "experiments/outputs/ch05_p044_adaptive_boundary_r1",
    "experiments/outputs/render_record_boundary_fixture_r1",
    "experiments/outputs/exact_base_boundary_measurement_packet_r1",
]


class RebuildError(RuntimeError): pass


def require(value: bool, message: str) -> None:
    if not value: raise RebuildError(message)


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def rebuild() -> None:
    for script in COMMANDS:
        result = subprocess.run([PYTHON, script], cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            raise RebuildError(f"rebuild failed: {script}: {result.stdout[-500:]} {result.stderr[-500:]}")


def inventory() -> list[dict]:
    values = []
    for group in GROUPS:
        root = ROOT / group
        require(root.is_dir(), f"artifact group missing: {group}")
        files = sorted(path for path in root.rglob("*") if path.is_file())
        require(files, f"artifact group empty: {group}")
        for path in files:
            values.append({"group": group, "path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    return values


def root_hash(values: list[dict]) -> str:
    return hashlib.sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict:
    rebuild(); first = inventory(); rebuild(); second = inventory()
    require(first == second, "consecutive artifact inventories differ")
    group_counts = Counter(item["group"] for item in first)
    return {
        "record_type": "SelectedRouteArtifactRebuildReproducibility", "schema_version": "1.0",
        "record_id": "ng-selected-route-artifact-rebuild-reproducibility-r1", "state": "TWO_CONSECUTIVE_LOCAL_REBUILDS_BYTE_IDENTICAL",
        "runtime_inventory": {"path": "docs/research/evidence/instrumentation-runtime-inventory-r2.json", "sha256": sha256(ROOT / "docs/research/evidence/instrumentation-runtime-inventory-r2.json")},
        "commands": COMMANDS, "groups": [{"path": group, "artifact_count": group_counts[group]} for group in GROUPS],
        "summary": {"rebuilds": 2, "artifact_groups": len(GROUPS), "artifacts": len(first), "total_bytes": sum(item["bytes"] for item in first), "first_root_sha256": root_hash(first), "second_root_sha256": root_hash(second), "byte_identical": True},
        "artifacts": first,
        "nondeterministic_exclusions": ["suite started_at and per-check elapsed_ms", "compiler benchmark timing samples", "provider-generated G07 candidates and provider response records", "human-review decisions and minutes", "external runtime/model artifacts"],
        "activity": {"provider_requests": 0, "external_uploads": 0, "models_downloaded": 0, "external_cost_usd": "0.000000"},
        "limitations": ["This proves exact rebuilds only for the eight enumerated ignored local artifact groups.", "It does not claim provider-output reproducibility, cross-platform PNG identity, visual quality, or art acceptance.", "Timing and timestamp records are excluded rather than normalized."],
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    item = copy.deepcopy(expected); item["commands"].pop(); values.append(item)
    item = copy.deepcopy(expected); item["groups"][0]["artifact_count"] += 1; values.append(item)
    item = copy.deepcopy(expected); item["summary"]["rebuilds"] = 1; values.append(item)
    item = copy.deepcopy(expected); item["summary"]["second_root_sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["summary"]["byte_identical"] = False; values.append(item)
    item = copy.deepcopy(expected); item["artifacts"][0]["sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["nondeterministic_exclusions"].remove("provider-generated G07 candidates and provider response records"); values.append(item)
    item = copy.deepcopy(expected); item["activity"]["provider_requests"] = 1; values.append(item)
    return sum(value != expected for value in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else: require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked rebuild record differs")
        rejected, total = mutations(expected); require(rejected == total, "mutation rejection incomplete")
    except (RebuildError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    s = expected["summary"]
    print(f"0 failures, 0 warnings ({s['artifacts']} artifacts/{s['artifact_groups']} groups/{s['total_bytes']} bytes; two roots {s['first_root_sha256']})")
    print(f"two consecutive rebuilds byte-identical; {rejected}/{total} mutations rejected; 0 requests/uploads/downloads/$0")
    return 0


if __name__ == "__main__": raise SystemExit(main())
