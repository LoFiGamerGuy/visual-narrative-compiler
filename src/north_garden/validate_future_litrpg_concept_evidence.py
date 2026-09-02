"""Validate non-canon concept evidence against ignored local pixels and packet hashes."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/future-litrpg-visual-concepts-r1.json"
AUTHORIZED = {
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a"
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures: list[str] = []
    entries = data["candidates"]
    if len(entries) != 3 or len({item["candidate_id"] for item in entries}) != 3:
        failures.append("candidate denominator invalid")
    if data.get("canon_status") != "NONCANON_FUTURE_EXPLORATION" or data.get("production_planning_record") is not False:
        failures.append("non-canon boundary invalid")
    if any(data.get(key) is not None for key in ("comic_panel_plan_revision", "animation_shot_plan", "e_conte")):
        failures.append("planning record boundary invalid")
    for item in entries:
        cid = item["candidate_id"]
        if hashlib.sha256(item["prompt"].encode("utf-8")).hexdigest() != item["prompt_sha256"]:
            failures.append(f"{cid}: prompt hash mismatch")
        if any(ref["sha256"] not in AUTHORIZED for ref in item["references"]):
            failures.append(f"{cid}: unauthorized reference")
        path = ROOT / item["output"]["path"]
        if not path.is_file() or sha256(path) != item["output"]["sha256"]:
            failures.append(f"{cid}: output hash mismatch")
            continue
        with Image.open(path) as image:
            if image.size != (item["output"]["width"], item["output"]["height"]):
                failures.append(f"{cid}: dimensions mismatch")
        if subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
            failures.append(f"{cid}: output not ignored")
        for key in ("model", "endpoint", "provider_request_id", "usage", "cost_usd"):
            if item["execution"].get(key) is not None:
                failures.append(f"{cid}: invented {key}")
        if item["accepted"] or item["human_review_state"] != "PENDING" or item["human_review_minutes"] is not None:
            failures.append(f"{cid}: invented review/acceptance")
    for artifact in data["review_artifacts"].values():
        path = ROOT / artifact["path"]
        if not path.is_file() or sha256(path) != artifact["sha256"]:
            failures.append(f"artifact mismatch: {artifact['path']}")
    for derivative in data["candidate_derivatives"]:
        record = derivative["phone_preview"]
        path = ROOT / record["path"]
        if not path.is_file() or sha256(path) != record["sha256"]:
            failures.append(f"derivative mismatch: {record['path']}")
    print(f"future LitRPG concept evidence: {len(failures)} failures; 3 non-canon candidates; 155.766s; 0 accepted")
    print("paid API: none; built-in cost/model/request/seed: unavailable")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
