"""Validate CH05 variable-cadence selection, local assembly artifacts, and fail-closed boundaries."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSEMBLY = ROOT / "production/comic/assembly/ch05-variable-cadence-assembly-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-variable-cadence-assembly-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assembly_errors(data: dict) -> list[str]:
    out: list[str] = []
    entries = data.get("entries", [])
    if len(entries) != 14 or [item.get("order") for item in entries] != list(range(1, 15)):
        out.append("panel/order denominator invalid")
    if len({item.get("candidate_id") for item in entries}) != 14 or len({item.get("panel_id") for item in entries}) != 14:
        out.append("candidate/panel uniqueness invalid")
    if len(data.get("sequences", [])) != 3 or sorted(len(item.get("panel_ids", [])) for item in data.get("sequences", [])) != [4, 5, 5]:
        out.append("sequence coverage invalid")
    if len({item.get("target_width") for item in entries}) != 8 or {item.get("alignment") for item in entries} != {"left", "center", "right"}:
        out.append("cadence variation invalid")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        out.append("planning boundary invalid")
    if any(item.get("selection_state") not in {"ENGINEERING_PASS_OWNER_PENDING", "ENGINEERING_WARN_DENSE_SAFE_ZONE_OWNER_PENDING"} for item in entries):
        out.append("selection state invalid")
    if sum(item.get("selection_state") == "ENGINEERING_WARN_DENSE_SAFE_ZONE_OWNER_PENDING" for item in entries) != 1:
        out.append("explicit source warning invalid")
    return sorted(set(out))


def main() -> int:
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    failures = assembly_errors(assembly)
    panel_ids = {item["panel_id"] for item in plans["plans"]}
    for item in assembly["entries"]:
        cid = item["candidate_id"]
        if item["panel_id"] not in panel_ids:
            failures.append(f"{cid}: missing ComicPanelPlan")
        path = ROOT / item["source_path"]
        if not path.is_file() or sha256(path) != item["source_sha256"]:
            failures.append(f"{cid}: source hash mismatch")
            continue
        with Image.open(path) as image:
            if list(image.size) != item["source_dimensions"]:
                failures.append(f"{cid}: source dimensions mismatch")
        if subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
            failures.append(f"{cid}: source pixel not ignored")
    for value in evidence["artifacts"].values():
        records = value if isinstance(value, list) else [value]
        for record in records:
            path = ROOT / record["path"]
            if not path.is_file() or sha256(path) != record["sha256"]:
                failures.append(f"artifact mismatch: {record['path']}")
            elif subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
                failures.append(f"artifact not ignored: {record['path']}")
    clean = ROOT / evidence["artifacts"]["vertical_scroll_clean"]["path"]
    phone = ROOT / evidence["artifacts"]["phone_scroll"]["path"]
    with Image.open(clean) as image:
        if image.size != (1200, 14566): failures.append("full scroll dimensions invalid")
    with Image.open(phone) as image:
        if image.size != (390, 4734): failures.append("phone scroll dimensions invalid")
    slices = evidence["artifacts"]["phone_viewport_slices"]
    if len(slices) != 7:
        failures.append("viewport slice count invalid")
    for item in slices:
        with Image.open(ROOT / item["path"]) as image:
            if image.size != (390, 844): failures.append(f"slice dimensions invalid: {item['path']}")
    outliers = {item["candidate_id"] for item in evidence["safe_zone_texture_measurement"]["outliers"]}
    if outliers != {"c005", "c014"}:
        failures.append("safe-zone texture outlier set invalid")
    det = evidence["determinism"]
    if det["consecutive_build_count"] != 2 or det["packet_sha256_run_a"] != det["packet_sha256_run_b"]:
        failures.append("determinism evidence invalid")
    mutations = [
        lambda d: d["entries"].pop(), lambda d: d["entries"][1].update(order=1),
        lambda d: d["entries"][1].update(candidate_id=d["entries"][0]["candidate_id"]),
        lambda d: d["entries"][1].update(panel_id=d["entries"][0]["panel_id"]),
        lambda d: d["entries"][2].update(target_width=760), lambda d: [item.update(alignment="center") for item in d["entries"]],
        lambda d: d.update(animation_shot_plan={}), lambda d: d.update(comic_panel_plan_revision_created=True),
        lambda d: d["entries"][3].update(selection_state="ACCEPTED"), lambda d: d["sequences"].pop()
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(assembly); mutation(changed); rejected += bool(assembly_errors(changed))
    if rejected != len(mutations):
        failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 variable cadence assembly: {len(failures)} failures; 14 panels/3 sequences/8 widths/3 alignments; {rejected}/{len(mutations)} mutations rejected")
    print("1200x14566 full / 390x4734 phone / 7 viewports; 2 safe-zone texture outliers; 0 provider calls/$0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
