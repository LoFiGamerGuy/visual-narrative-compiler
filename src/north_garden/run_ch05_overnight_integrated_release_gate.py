"""Run the complete no-network CH05 overnight evidence and integrity gate."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r1.json"
COMMANDS = [
    "src/north_garden/validate_ch05_overnight_production_plan.py",
    "src/north_garden/validate_ch05_overnight_evidence.py",
    "src/north_garden/validate_ch05_cadence_hardening_plan.py",
    "src/north_garden/validate_ch05_cadence_hardening_evidence.py",
    "src/north_garden/validate_future_litrpg_concept_plan.py",
    "src/north_garden/validate_future_litrpg_concept_evidence.py",
    "src/north_garden/validate_ch05_variable_cadence_assembly.py",
    "src/north_garden/validate_ch05_transparent_lettering_rehearsal.py",
    "src/north_garden/validate_ch05_lettering_width_copy_sensitivity.py",
    "src/north_garden/validate_ch05_outside_art_lettering_band.py",
    "src/north_garden/validate_ch05_instrumented_production_manifest.py",
    "src/north_garden/validate_ch05_owner_review_index.py",
    "src/north_garden/validate_ch05_continuity_style_density.py",
    "src/north_garden/validate_ch05_style_direction_lineage.py",
    "src/north_garden/validate_frozen_gauntlet_baseline_integrity.py",
    "src/north_garden/validate_tracked_source_scope.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_stdout(value: str) -> str:
    value = value.replace("\r\n", "\n").strip() + "\n"
    return re.sub(r"\d+ tracked safe-source paths", "<dynamic> tracked safe-source paths", value)


def main() -> int:
    results = []
    total_start = time.perf_counter()
    for relative in COMMANDS:
        path = ROOT / relative
        start = time.perf_counter()
        completed = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        elapsed = time.perf_counter() - start
        normalized = normalize_stdout(completed.stdout)
        results.append({
            "path": relative, "script_sha256": sha(path), "command": f"python {relative}", "network_capable": False,
            "return_code": completed.returncode, "elapsed_seconds": round(elapsed, 6),
            "normalized_stdout": normalized, "normalized_stdout_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
            "stderr": completed.stderr.replace("\r\n", "\n"),
        })
        print(f"[{len(results):02d}/{len(COMMANDS)}] {'PASS' if completed.returncode == 0 else 'FAIL'} {relative} {elapsed:.3f}s")
    total = time.perf_counter() - total_start
    passed = sum(item["return_code"] == 0 for item in results)
    evidence = {
        "record_type": "CH05OvernightIntegratedReleaseGate", "schema_version": "1.0",
        "record_id": "ng-ch05-overnight-integrated-release-gate-r1",
        "state": "PASS" if passed == len(results) else "FAIL",
        "medium": "comic", "comic_panel_plan_revision_created": False, "animation_shot_plan": None, "e_conte": None,
        "summary": {
            "command_count": len(results), "passed": passed, "failed": len(results) - passed,
            "observed_total_seconds": round(total, 6), "network_capable_commands": 0,
            "provider_calls": 0, "uploads": 0, "downloads": 0, "cost_usd": 0,
            "accepted_candidates": 0, "executable_panels": 0, "human_review_minutes": None
        },
        "results": results,
        "frozen_integrity_result": next(item for item in results if item["path"].endswith("validate_frozen_gauntlet_baseline_integrity.py"))["normalized_stdout"],
        "source_scope_result": next(item for item in results if item["path"].endswith("validate_tracked_source_scope.py"))["normalized_stdout"],
        "boundaries": [
            "The gate is local and declares every command non-network-capable.",
            "Frozen v2.1.1 and baseline_legacy integrity are validated without rerendering or tuning.",
            "Generated pixels remain ignored; source scope and origin configuration validate.",
            "A passing gate does not accept art, clear commercial use, bind final copy, or create executable production state."
        ]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"integrated release gate: {passed}/{len(results)} passed in {total:.3f}s; evidence {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
