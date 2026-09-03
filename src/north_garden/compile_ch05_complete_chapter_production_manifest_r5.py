"""Compile CH05 production manifest r5 with P039/P043 object-continuity repairs."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r4.json"
REPAIRS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-targeted-repairs-r4.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r5.json"
BUILD = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r5/review/build-report.json"
LETTERING = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r5/lettered/lettering-build-report.json"
CONTINUITY = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r5/review/continuity-sheet-report.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r5.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def binding(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def artifact(value: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / value["path"]
    if sha256(path) != value["sha256"]:
        raise ValueError(f"artifact hash mismatch: {path}")
    return {"path": value["path"], "sha256": value["sha256"], "width_px": value["width"], "height_px": value["height"]}


def main() -> int:
    manifest = deepcopy(load(BASE))
    repair_doc = load(REPAIRS)
    assembly = load(ASSEMBLY)
    build, lettering, continuity = load(BUILD), load(LETTERING), load(CONTINUITY)
    generation = repair_doc["source_generation"]
    crop_report_path = ROOT / generation["crop_report"]["path"]
    if sha256(crop_report_path) != generation["crop_report"]["sha256"]:
        raise ValueError("object-continuity crop report hash mismatch")
    crops = {row["panel_id"]: row for row in load(crop_report_path)["panels"]}
    panels = {row["panel_id"]: row for row in manifest["panels"]}
    assembly_rows = {row["panel_id"]: row for row in assembly["entries"]}
    prompt = generation["exact_prompt"]
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    for repair in repair_doc["repairs"]:
        panel_id = repair["panel_id"]
        panel, crop, output = panels[panel_id], crops[panel_id], repair["output"]
        if crop["artifact"]["sha256"] != output["sha256"] or assembly_rows[panel_id]["source"]["sha256"] != output["sha256"]:
            raise ValueError(f"repair/crop/assembly mismatch: {panel_id}")
        panel["sequence_id"] = generation["generation_id"]
        panel["source_service_execution_id"] = generation["service"]["service_execution_id"]
        panel["prompt_text"] = prompt
        panel["prompt_sha256"] = prompt_hash
        panel["input_references"] = [{"path": row["path"], "sha256": row["sha256"], "upload_target": "openai_builtin_imagegen"} for row in generation["input_references"]]
        panel["source_strip"] = generation["output_strip"]
        panel["crop_box"] = crop["crop_box"]
        service = generation["service"]
        panel["candidate"] = {
            "path": output["path"], "sha256": output["sha256"], "width_px": output["width"], "height_px": output["height"],
            "elapsed_seconds": service["elapsed_seconds"], "timing_scope": "shared one-strip client observation; do not sum across P039/P043",
            "service": {
                "tool": service["product"], "model": service["model"], "endpoint": service["endpoint"],
                "request_id": service["provider_request_id"], "provider_usage": service["usage"],
                "provider_cost_usd": service["monetary_cost_usd"], "seed": service["seed"],
                "unavailable_fields": ["model", "endpoint", "request_id", "provider_usage", "provider_cost_usd", "seed"],
            },
        }
        panel["repair"] = {"repair_class": repair["repair_class"], "reason": repair["reason"], "smallest_change": repair["smallest_change"]}
    manifest["record_id"] = "ng-ch05-complete-chapter-production-manifest-r5"
    manifest["state"] = "COMPLETE_READING_DRAFT_WITH_OBJECT_CONTINUITY_REPAIRS_PENDING_OWNER_REVIEW"
    manifest["source_bindings"] = manifest["source_bindings"] + [binding(BASE), binding(REPAIRS), binding(ASSEMBLY), binding(BUILD), binding(LETTERING), binding(CONTINUITY)]
    manifest["review_bundle"] = {"artifacts": [
        {"kind": "chapter_scroll", **artifact(lettering["artifacts"]["lettered_long_scroll"])},
        {"kind": "contact_sheet", **artifact(build["artifacts"]["contact_sheet"])},
        {"kind": "phone_preview", **artifact(lettering["artifacts"]["lettered_phone_scroll"])},
        {"kind": "lettering_overlay", **artifact(build["artifacts"]["long_scroll_lettering_overlay"])},
        {"kind": "continuity_sheet", **artifact(continuity["artifact"])},
    ]}
    manifest["limitations"] = manifest["limitations"] + [
        "The original P043 sequence prompt overconstrained the plan by leaving all contents; r5 follows the exact plan by leaving the open tin while preserving the map for P046.",
        "P039's X-like third symbol is provisional; no canon symbol or plan revision is implied.",
        "P039/P043 share one source generation and elapsed observation; count one call, not two.",
    ]
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "panels": len(panels), "repairs": len(repair_doc["repairs"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
