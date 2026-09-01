"""Validate and benchmark the deterministic 50-panel chapter run manifest."""
from __future__ import annotations

import copy
import hashlib
import json
import statistics
import time
import tracemalloc
from pathlib import Path

from comic_run_ledger import canonical_sha256
from compile_ch05_chapter_run_manifest import ROOT, compile_manifest


CONTRACT = ROOT / "production/comic/run-manifests/ch05-50-panel-run-manifest-r1.json"
OUT = ROOT / "experiments/results/ch05-50-panel-run-manifest-validation-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calculated_root(record: dict) -> str:
    return canonical_sha256({
        "panels": [
            {
                "panel_id": item["panel_id"],
                "plan_revision_id": item["plan_revision_id"],
                "applicable_hard_assertion_sha256": item["applicable_hard_assertion_sha256"],
                "chain_head_sha256": item["chain_head_sha256"],
            }
            for item in record["panels"]
        ]
    })


def main() -> int:
    failures = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for relative, expected in contract["sources"].items():
        if sha256(ROOT / relative) != expected:
            failures.append(f"source hash mismatch: {relative}")

    durations = []
    roots = []
    records = []
    tracemalloc.start()
    for _ in range(30):
        started = time.perf_counter()
        record = compile_manifest()
        durations.append((time.perf_counter() - started) * 1000)
        roots.append(record["chapter_root_sha256"])
        records.append(record)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    record = records[-1]
    expected_root = contract["expected_chapter_root_sha256"]
    if set(roots) != {expected_root}:
        failures.append("30 compiles did not reproduce the pinned chapter root")
    if calculated_root(record) != expected_root:
        failures.append("record chapter root does not match panel material")
    panels = record["panels"]
    if len(panels) != 50 or [item["display_order"] for item in panels] != list(range(1, 51)):
        failures.append("panel count/order mismatch")
    for field in ("panel_id", "plan_revision_id", "applicable_hard_assertion_id", "chain_head_sha256"):
        if len({item[field] for item in panels}) != 50:
            failures.append(f"panel field is not unique across 50 rows: {field}")
    if any(item["current_state"] != "BASE_APPROVAL_PENDING" or item["executable"] for item in panels):
        failures.append("one or more panels advanced beyond base pending")
    if any(item["human_minutes"] is not None or item["accepted"] for item in panels):
        failures.append("one or more panels gained review/acceptance")
    summary = record["summary"]
    expected = contract["expected"]
    checks = {
        "panel_count": summary["panel_count"],
        "base_approval_pending": summary["stage_denominators"]["base_approval_pending"],
        "demonstration_slice_panels": summary["demonstration_slice_panels"],
        "review_task_instances": record["review_workload_structure"]["task_instances"],
        "executable_panels": summary["executable_panels"],
        "provider_requests": summary["provider_requests"],
        "external_uploads": summary["external_uploads"],
        "external_cost_usd": summary["external_cost_usd"],
        "accepted_panels": summary["stage_denominators"]["accepted"],
        "human_minutes": summary["human_minutes"],
    }
    for key, value in checks.items():
        if value != expected[key]:
            failures.append(f"contract summary mismatch: {key}")

    tamper_results = []
    for label, mutate in [
        ("chain_head", lambda x: x["panels"][0].update(chain_head_sha256="0" * 64)),
        ("plan_revision", lambda x: x["panels"][1].update(plan_revision_id="wrong")),
        ("assertion", lambda x: x["panels"][2].update(applicable_hard_assertion_sha256="1" * 64)),
        ("panel_order", lambda x: x["panels"].reverse()),
    ]:
        changed = copy.deepcopy(record)
        mutate(changed)
        detected = calculated_root(changed) != expected_root
        tamper_results.append({"mutation": label, "detected": detected})
        if not detected:
            failures.append(f"chapter root missed mutation: {label}")

    sorted_durations = sorted(durations)
    p95 = sorted_durations[max(0, int(len(sorted_durations) * 0.95) - 1)]
    validation = {
        "record_type": "ComicChapterRunManifestValidation",
        "schema_version": "1.0",
        "record_id": "ng-ch05-50-panel-run-manifest-validation-r1",
        "chapter_root_sha256": expected_root,
        "iterations": len(durations),
        "compile_ms": {
            "min": round(min(durations), 3),
            "median": round(statistics.median(durations), 3),
            "mean": round(statistics.mean(durations), 3),
            "p95": round(p95, 3),
            "max": round(max(durations), 3),
        },
        "python_peak_tracemalloc_bytes": peak_bytes,
        "root_reproductions": roots.count(expected_root),
        "tamper_detection": tamper_results,
        "provider_requests": 0,
        "external_uploads": 0,
        "external_cost_usd": "0.000000",
        "limitations": [
            "Local Python compile timing is not provider or human throughput.",
            "tracemalloc peak is interpreter-observed allocation, not process RSS.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print(
        "0 failures, 0 warnings "
        f"(50/50 base-pending; root 30/30; median={validation['compile_ms']['median']}ms; "
        f"p95={validation['compile_ms']['p95']}ms; tamper=4/4)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
