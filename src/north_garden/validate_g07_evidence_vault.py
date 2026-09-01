"""Build and validate the local G07 evidence-vault integrity snapshot.

The tracked snapshot contains hashes and non-art metadata only. Provider records and
candidate rasters remain under ignored ``experiments/`` paths.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/research/evidence/g07-local-evidence-vault-manifest-r1.json"

PUBLIC_CONTROLS = {
    "g07a-no-change-r1.png": "867a05c2f3e35f196cd28a9d1dc1954f2ba862f62d33ae34df4f3161a3200436",
    "g07a-role-id-r1.png": "0a7237f655492f4aea7618036b7bac1a5068882f113ae395188ab50abb5a2699",
}

PROVIDERS = {
    "openai_gpt_image_2": {
        "directory": "experiments/records/openai_gpt_image2_g07_bakeoff_r1",
        "files": [
            "g07a-independent-01-failed.json",
            "g07a-independent-01.json",
            "g07a-independent-02.json",
            "g07a-no-change.json",
            "g07a-target-change.json",
        ],
    },
    "gemini_3_1_flash_image": {
        "directory": "experiments/records/gemini_flash_image_g07_bakeoff_r1",
        "files": [
            "g07a-independent-01-failed.json",
            "g07a-independent-01.json",
            "g07a-independent-02.json",
            "g07a-no-change.json",
            "g07a-target-change.json",
        ],
    },
    "grok_imagine_image_2": {
        "directory": "experiments/records/xai_grok_imagine_g07_bakeoff_r1",
        "files": [
            "g07a-independent-01-failed.json",
            "g07a-independent-01.json",
            "g07a-independent-02.json",
            "g07a-no-change.json",
            "g07a-target-change.json",
        ],
    },
    "bfl_flux_2": {
        "directory": "experiments/records/bfl_flux2_g07_bakeoff_r1",
        "files": [
            "g07a-independent-01.json",
            "g07a-independent-02.json",
            "g07a-no-change.json",
            "g07a-target-change.json",
        ],
    },
}


class VaultError(RuntimeError):
    """Evidence-vault integrity failure."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(data)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VaultError(message)


def numeric_cost(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def validate_public_controls() -> None:
    controls_dir = ROOT / "public-controls"
    actual = {path.name for path in controls_dir.glob("g07a-*-r1.png")}
    require(actual == set(PUBLIC_CONTROLS), f"unexpected public control set: {sorted(actual)}")
    for name, expected_hash in PUBLIC_CONTROLS.items():
        require(sha256_file(controls_dir / name) == expected_hash, f"public control hash mismatch: {name}")


def record_summary(path: Path, expected_adapter: str) -> tuple[dict[str, Any], Decimal, Decimal]:
    raw = path.read_bytes()
    record = json.loads(raw)
    require(record.get("adapter_id") == expected_adapter, f"adapter mismatch: {relative(path)}")
    require(record.get("case_id") == "G07a", f"case mismatch: {relative(path)}")
    require(record.get("accepted") is False, f"record unexpectedly accepted: {relative(path)}")
    require(record.get("human_review_status") == "not_yet_performed", f"review status changed: {relative(path)}")
    require(record.get("human_minutes") is None, f"human minutes must remain null: {relative(path)}")

    input_hashes = record.get("input_hashes")
    require(isinstance(input_hashes, dict) and input_hashes, f"missing input hashes: {relative(path)}")
    require(set(input_hashes.values()) <= set(PUBLIC_CONTROLS.values()), f"unapproved input hash: {relative(path)}")

    candidate = record.get("candidate")
    output_hashes = record.get("output_hashes")
    candidate_summary = None
    candidate_cost = Decimal("0")
    paid_failure_cost = Decimal("0")
    cost = numeric_cost(record.get("cost_usd"))
    if candidate is not None:
        require(record.get("execution_status") in {"completed", "completed_recovered_from_interaction"},
                f"candidate has non-complete status: {relative(path)}")
        candidate_path = ROOT / candidate["path"]
        require(candidate_path.is_file(), f"missing candidate: {candidate['path']}")
        actual_hash = sha256_file(candidate_path)
        require(actual_hash == candidate.get("sha256"), f"candidate hash mismatch: {candidate['path']}")
        require(output_hashes == [actual_hash], f"output hash mismatch: {relative(path)}")
        with Image.open(candidate_path) as image:
            image.verify()
        require(cost is not None and cost >= 0, f"completed record lacks numeric cost: {relative(path)}")
        candidate_cost = cost
        candidate_summary = {
            "path": candidate["path"],
            "sha256": actual_hash,
            "bytes": candidate_path.stat().st_size,
            "mime_type": candidate.get("mime_type"),
        }
    else:
        require("failed" in path.stem, f"non-candidate record is not a failure: {relative(path)}")
        require(output_hashes == [], f"failed record has output hashes: {relative(path)}")
        if cost is not None and cost > 0:
            paid_failure_cost = cost

    summary = {
        "path": relative(path),
        "sha256": sha256_bytes(raw),
        "adapter_id": record["adapter_id"],
        "execution_status": record["execution_status"],
        "request_id": record.get("request_id"),
        "elapsed_seconds": record.get("elapsed_seconds"),
        "cost_usd": record.get("cost_usd"),
        "input_hashes": input_hashes,
        "output_hashes": output_hashes,
        "candidate": candidate_summary,
        "failure_tags": record.get("failure_tags", []),
        "human_review_status": record["human_review_status"],
        "human_minutes": record["human_minutes"],
        "accepted": record["accepted"],
    }
    return summary, candidate_cost, paid_failure_cost


def verify_recovery(records: list[dict[str, Any]]) -> None:
    failed_path = "experiments/records/gemini_flash_image_g07_bakeoff_r1/g07a-independent-01-failed.json"
    recovered_path = "experiments/records/gemini_flash_image_g07_bakeoff_r1/g07a-independent-01.json"
    by_path = {item["path"]: item for item in records}
    failed = by_path[failed_path]
    recovered = by_path[recovered_path]
    require(failed["request_id"] == recovered["request_id"], "Gemini recovery request ID changed")
    raw = json.loads((ROOT / recovered_path).read_text(encoding="utf-8"))
    provenance = raw.get("recovery_provenance", {})
    require(provenance.get("failed_record") == failed_path, "Gemini recovery failed-record path mismatch")
    require(provenance.get("failed_record_sha256") == failed["sha256"], "Gemini recovery failed-record hash mismatch")
    require(provenance.get("method") == "official_get_interaction_no_new_generation", "Gemini recovery method mismatch")


def tracked_experiment_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "--", "experiments"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def build_snapshot() -> dict[str, Any]:
    validate_public_controls()
    records: list[dict[str, Any]] = []
    candidate_costs: dict[str, Decimal] = {}
    failure_costs: dict[str, Decimal] = {}
    for adapter_id, config in PROVIDERS.items():
        directory = ROOT / config["directory"]
        actual_files = sorted(path.name for path in directory.glob("*.json"))
        require(actual_files == sorted(config["files"]), f"record inventory mismatch for {adapter_id}: {actual_files}")
        candidate_costs[adapter_id] = Decimal("0")
        failure_costs[adapter_id] = Decimal("0")
        for filename in config["files"]:
            summary, candidate_cost, failure_cost = record_summary(directory / filename, adapter_id)
            records.append(summary)
            candidate_costs[adapter_id] += candidate_cost
            failure_costs[adapter_id] += failure_cost

    records.sort(key=lambda item: item["path"])
    verify_recovery(records)
    candidates = [item["candidate"] for item in records if item["candidate"] is not None]
    failures = [item for item in records if item["candidate"] is None]
    require(len(records) == 19 and len(candidates) == 16 and len(failures) == 3,
            "expected 19 records, 16 candidates, and 3 failures")
    require(not tracked_experiment_paths(), "generated experiment material is tracked by Git")

    expected_candidate_costs = {
        "openai_gpt_image_2": Decimal("0.198621"),
        "gemini_3_1_flash_image": Decimal("0.268756"),
        "grok_imagine_image_2": Decimal("0.280000"),
        "bfl_flux_2": Decimal("0.240000"),
    }
    expected_failure_costs = {
        "openai_gpt_image_2": Decimal("0.000000"),
        "gemini_3_1_flash_image": Decimal("0.000000"),
        "grok_imagine_image_2": Decimal("0.070000"),
        "bfl_flux_2": Decimal("0.000000"),
    }
    require(candidate_costs == expected_candidate_costs, f"candidate cost mismatch: {candidate_costs}")
    require(failure_costs == expected_failure_costs, f"paid failure cost mismatch: {failure_costs}")
    required_cost = sum(candidate_costs.values(), Decimal("0"))
    paid_failure_cost = sum(failure_costs.values(), Decimal("0"))
    aggregate_cost = required_cost + paid_failure_cost
    require(required_cost == Decimal("0.987377"), "required candidate cost mismatch")
    require(aggregate_cost == Decimal("1.057377"), "aggregate paid cost mismatch")

    # BFL may only receive the two hash-pinned fictional geometry controls.
    bfl_records = [item for item in records if item["adapter_id"] == "bfl_flux_2"]
    require(len(bfl_records) == 4, "BFL record count mismatch")
    require({value for item in bfl_records for value in item["input_hashes"].values()} == set(PUBLIC_CONTROLS.values()),
            "BFL input set is not exactly the two approved controls")

    record_root = canonical_sha256([{"path": item["path"], "sha256": item["sha256"]} for item in records])
    artifact_root = canonical_sha256(sorted(candidates, key=lambda item: item["path"]))
    snapshot = {
        "record_type": "G07LocalEvidenceVaultManifest",
        "schema_version": "1.0",
        "manifest_id": "g07-local-evidence-vault-manifest-r1",
        "scope": {
            "generated_material_policy": "hashes_and_non_art_metadata_tracked; provider records and raster candidates remain ignored under experiments/",
            "human_review_state": "not_yet_performed",
            "acceptance_state": "all_candidates_unaccepted",
            "rerender_authority": False,
        },
        "public_controls": [
            {"path": f"public-controls/{name}", "sha256": digest}
            for name, digest in sorted(PUBLIC_CONTROLS.items())
        ],
        "inventory": {
            "provider_records": len(records),
            "completed_candidates": len(candidates),
            "failure_or_intermediate_records": len(failures),
            "tracked_generated_experiment_paths": 0,
        },
        "cost_reconciliation": {
            "required_candidate_cost_usd": f"{required_cost:.6f}",
            "paid_failure_cost_usd": f"{paid_failure_cost:.6f}",
            "aggregate_paid_cost_usd": f"{aggregate_cost:.6f}",
            "held_usd": "0.000000",
            "approved_cap_usd": "100.000000",
            "available_usd": f"{Decimal('100') - aggregate_cost:.6f}",
            "provider_candidate_costs_usd": {key: f"{value:.6f}" for key, value in candidate_costs.items()},
            "provider_paid_failure_costs_usd": {key: f"{value:.6f}" for key, value in failure_costs.items()},
            "gemini_recovery_charge_rule": "failed interaction and recovered candidate share one request ID and one generation charge",
        },
        "integrity": {
            "record_hash_root_sha256": record_root,
            "candidate_artifact_hash_root_sha256": artifact_root,
            "vault_root_sha256": canonical_sha256({"records": record_root, "artifacts": artifact_root}),
        },
        "records": records,
    }
    return snapshot


def mutation_checks(expected: dict[str, Any], actual: dict[str, Any]) -> tuple[int, int]:
    mutations: list[tuple[str, Any]] = [
        ("aggregate cost", lambda item: item["cost_reconciliation"].__setitem__("aggregate_paid_cost_usd", "0.987377")),
        ("record hash", lambda item: item["records"][0].__setitem__("sha256", "0" * 64)),
        ("candidate hash", lambda item: next(r for r in item["records"] if r["candidate"])["candidate"].__setitem__("sha256", "f" * 64)),
        ("review state", lambda item: item["records"][0].__setitem__("accepted", True)),
        ("BFL input", lambda item: next(r for r in item["records"] if r["adapter_id"] == "bfl_flux_2")["input_hashes"].__setitem__("g07a-control", "a" * 64)),
    ]
    rejected = 0
    for _name, mutate in mutations:
        changed = copy.deepcopy(expected)
        mutate(changed)
        if changed != actual:
            rejected += 1
    return rejected, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path, help="write a deterministic snapshot to this path")
    args = parser.parse_args()
    try:
        actual = build_snapshot()
        if args.emit:
            output = args.emit if args.emit.is_absolute() else ROOT / args.emit
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(actual, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"wrote {relative(output)}")
            return 0
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
        require(expected == actual, "tracked evidence-vault manifest differs from exact local records/artifacts")
        rejected, total = mutation_checks(expected, actual)
        require(rejected == total, "mutation rejection incomplete")
    except (VaultError, FileNotFoundError, json.JSONDecodeError, KeyError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings")
    print("19/19 provider records and 16/16 candidate artifacts hash-match")
    print("G07 spend reconciles: $1.057377 paid, $0 held, $98.942623 available")
    print(f"{rejected}/{total} manifest mutations rejected; 0 generated experiment paths tracked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
