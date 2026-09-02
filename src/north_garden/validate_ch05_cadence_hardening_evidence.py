"""Validate the safe CH05 cadence-hardening evidence and ignored local artifacts."""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-cadence-hardening-r1.json"
AUTHORIZED = {
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb"
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures: list[str] = []
    entries = data["candidates"]
    if len(entries) != 6 or len({item["candidate_id"] for item in entries}) != 6:
        failures.append("candidate denominator invalid")
    if len({item["panel_id"] for item in entries}) != 5:
        failures.append("panel denominator invalid")
    if data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        failures.append("non-comic planning record present")
    rollup = Counter()
    for item in entries:
        cid = item["candidate_id"]
        if hashlib.sha256(item["exact_prompt"].encode("utf-8")).hexdigest() != item["prompt_sha256"]:
            failures.append(f"{cid}: prompt hash mismatch")
        if any(ref["sha256"] not in AUTHORIZED for ref in item["input_references"]):
            failures.append(f"{cid}: unauthorized reference")
        path = ROOT / item["output"]["path"]
        if not path.is_file() or sha256(path) != item["output"]["sha256"]:
            failures.append(f"{cid}: output hash mismatch")
            continue
        with Image.open(path) as image:
            if image.size != (item["output"]["width"], item["output"]["height"]):
                failures.append(f"{cid}: dimension mismatch")
        if subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
            failures.append(f"{cid}: output not ignored")
        for key in ("model", "endpoint", "provider_request_id", "usage", "cost_usd"):
            if item["execution"].get(key) is not None:
                failures.append(f"{cid}: invented {key}")
        values = set(item["engineering_review"]["results"].values())
        rollup["failure" if "FAIL" in values else "warning" if "WARN" in values else "all_pass"] += 1
        if item["accepted"] or item["human_review_state"] != "PENDING" or item["human_review_minutes"] is not None:
            failures.append(f"{cid}: invented human review or acceptance")
    if rollup != Counter({"all_pass": 5, "failure": 1}):
        failures.append(f"rollup invalid: {dict(rollup)}")
    for artifact in data["review_artifacts"].values():
        records = artifact if isinstance(artifact, list) else [artifact]
        for record in records:
            path = ROOT / record["path"]
            if not path.is_file() or sha256(path) != record["sha256"]:
                failures.append(f"artifact mismatch: {record['path']}")
    for derivative in data["candidate_derivatives"]:
        for key in ("lettering_overlay", "phone_preview"):
            record = derivative[key]
            path = ROOT / record["path"]
            if not path.is_file() or sha256(path) != record["sha256"]:
                failures.append(f"derivative mismatch: {record['path']}")
    print(f"CH05 cadence hardening evidence: {len(failures)} failures; 6 candidates/5 plans; {rollup['all_pass']} all-pass/{rollup['failure']} diagnostic")
    print("observed tool time: 310.669s; paid API: none; built-in cost metadata: unavailable")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
