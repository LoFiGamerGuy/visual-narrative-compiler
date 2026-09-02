"""Apply hash-pinned, panel-local repairs to a complete CH05 assembly manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPAIRS = Path("production/comic/run-manifests/ch05-complete-chapter-targeted-repairs-r1.json")
DEFAULT_OUTPUT = Path("production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r2.json")
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


class RepairError(ValueError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RepairError(f"top-level JSON is not an object: {path}")
    return value


def project_file(raw: str) -> Path:
    rel = Path(raw.replace("\\", "/"))
    if rel.is_absolute() or ".." in rel.parts:
        raise RepairError(f"unsafe project path: {raw}")
    path = (ROOT / rel).resolve()
    path.relative_to(ROOT.resolve())
    if not path.is_file():
        raise RepairError(f"missing project file: {raw}")
    return path


def compile_manifest(repair_path: Path, output_path: Path) -> dict[str, Any]:
    repairs = load(repair_path)
    if repairs.get("record_type") != "ComicChapterTargetedRepairManifest":
        raise RepairError("repair manifest record_type mismatch")
    if repairs.get("animation_shot_plan") is not None or repairs.get("e_conte") is not None:
        raise RepairError("repair manifest must preserve ComicPanelPlan-only production")
    source_record = repairs.get("source_assembly", {})
    source_path = project_file(source_record.get("path", ""))
    if sha256(source_path) != source_record.get("sha256"):
        raise RepairError("source assembly hash mismatch")
    assembly = load(source_path)
    entries = assembly.get("entries")
    if not isinstance(entries, list) or len(entries) != 50:
        raise RepairError("source assembly must contain 50 entries")
    by_panel = {entry.get("panel_id"): entry for entry in entries}
    if len(by_panel) != 50:
        raise RepairError("source assembly panel IDs must be unique")
    seen: set[str] = set()
    plan_revisions = {row["panel_id"]: row["plan_revision_id"] for row in load(PLAN)["plans"]}
    applied: list[dict[str, Any]] = []
    for repair in repairs.get("repairs", []):
        panel_id = repair.get("panel_id")
        if panel_id in seen or panel_id not in by_panel:
            raise RepairError(f"unknown or duplicate repair panel: {panel_id}")
        seen.add(panel_id)
        if repair.get("plan_revision_id") != plan_revisions.get(panel_id):
            raise RepairError(f"repair plan revision mismatch: {panel_id}")
        output = repair.get("output", {})
        candidate_path = project_file(output.get("path", ""))
        if sha256(candidate_path) != output.get("sha256"):
            raise RepairError(f"repair output hash mismatch: {panel_id}")
        from PIL import Image
        with Image.open(candidate_path) as image:
            dimensions = (image.width, image.height)
        if dimensions != (output.get("width"), output.get("height")):
            raise RepairError(f"repair output dimensions mismatch: {panel_id}")
        original = deepcopy(by_panel[panel_id])
        by_panel[panel_id]["candidate_id"] = repair["candidate_id"]
        by_panel[panel_id]["source"] = {
            "path": output["path"],
            "sha256": output["sha256"],
            "width": output["width"],
            "height": output["height"],
        }
        applied.append({
            "panel_id": panel_id,
            "original_candidate_id": original["candidate_id"],
            "original_source_sha256": original["source"]["sha256"],
            "replacement_candidate_id": repair["candidate_id"],
            "replacement_source_sha256": output["sha256"],
            "repair_class": repair["repair_class"],
        })
    if not applied:
        raise RepairError("repair manifest contains no repairs")
    target_record_id = repairs.get("target_assembly_record_id")
    if not isinstance(target_record_id, str) or not target_record_id.strip():
        raise RepairError("target_assembly_record_id is required")
    assembly["record_id"] = target_record_id
    assembly["state"] = (
        "COMPLETE_READING_DRAFT_WITH_TARGETED_REPAIR_PENDING_OWNER_REVIEW"
        if len(applied) == 1
        else "COMPLETE_READING_DRAFT_WITH_TARGETED_REPAIRS_PENDING_OWNER_REVIEW"
    )
    assembly["repair_provenance"] = {
        "source_assembly": source_record,
        "repair_manifest": {
            "path": repair_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(repair_path),
        },
        "applied": applied,
        "unchanged_panel_count": 50 - len(applied),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(assembly, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    result = {
        "output": output_path.relative_to(ROOT).as_posix(),
        "sha256": sha256(output_path),
        "repairs": len(applied),
        "unchanged_panels": 50 - len(applied),
    }
    print(json.dumps(result, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repairs", type=Path, default=DEFAULT_REPAIRS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    compile_manifest((ROOT / args.repairs).resolve(), (ROOT / args.output).resolve())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RepairError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"repair error: {exc}") from exc
