"""Validate safe tracked CH05 overnight evidence against ignored local pixels and packets."""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-overnight-production-r1.json"
AUTHORIZED = {
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    candidates = data["candidates"]
    if len(candidates) != 20:
        failures.append("candidate_count must be 20")
    if len({item["candidate_id"] for item in candidates}) != 20:
        failures.append("candidate IDs are not unique")
    if len({item["panel_id"] for item in candidates}) < 12:
        failures.append("fewer than 12 distinct ComicPanelPlans")
    if data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        failures.append("non-comic planning record present")
    statuses = Counter()
    for entry in candidates:
        cid = entry["candidate_id"]
        prompt_hash = hashlib.sha256(entry["exact_prompt"].encode("utf-8")).hexdigest()
        if prompt_hash != entry["prompt_sha256"]:
            failures.append(f"{cid}: prompt hash mismatch")
        refs = entry["input_references"]
        if any(ref["sha256"] not in AUTHORIZED for ref in refs):
            failures.append(f"{cid}: unauthorized reference hash")
        output = ROOT / entry["output"]["path"]
        if not output.is_file() or sha256(output) != entry["output"]["sha256"]:
            failures.append(f"{cid}: output missing or hash mismatch")
            continue
        with Image.open(output) as image:
            if list(image.size) != [entry["output"]["width"], entry["output"]["height"]]:
                failures.append(f"{cid}: dimensions mismatch")
        ignored = subprocess.run(["git", "check-ignore", "-q", str(output)], cwd=ROOT, check=False).returncode == 0
        if not ignored:
            failures.append(f"{cid}: generated pixel is not gitignored")
        execution = entry["execution"]
        for key in ("model", "endpoint", "provider_request_id", "usage", "cost_usd"):
            if execution.get(key) is not None:
                failures.append(f"{cid}: unavailable provider field {key} was invented")
        values = set(entry["engineering_review"]["results"].values())
        statuses["failure" if "FAIL" in values else "warning" if "WARN" in values else "all_pass"] += 1
        if entry["accepted"] or entry["human_review_state"] != "PENDING" or entry["human_review_minutes"] is not None:
            failures.append(f"{cid}: owner review/acceptance was invented")
    if statuses != Counter({"all_pass": 12, "failure": 5, "warning": 3}):
        failures.append(f"engineering triage rollup mismatch: {dict(statuses)}")
    for artifact in list(data["review_artifacts"].values()):
        records = artifact if isinstance(artifact, list) else [artifact]
        for record in records:
            path = ROOT / record["path"]
            if not path.is_file() or sha256(path) != record["sha256"]:
                failures.append(f"review artifact missing or hash mismatch: {record['path']}")
    for derivative in data["candidate_derivatives"]:
        for key in ("lettering_overlay", "phone_preview"):
            record = derivative[key]
            path = ROOT / record["path"]
            if not path.is_file() or sha256(path) != record["sha256"]:
                failures.append(f"candidate derivative missing or hash mismatch: {record['path']}")
    print(f"CH05 overnight evidence: {len(failures)} failures; {len(candidates)} candidates/{len({item['panel_id'] for item in candidates})} plans")
    print(f"triage: {statuses['all_pass']} all-pass / {statuses['warning']} warn-only / {statuses['failure']} with failures")
    print("paid API spend: none; built-in provider cost metadata: unavailable")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
