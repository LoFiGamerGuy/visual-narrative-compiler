"""Compile CH05 production manifest r6 with selected P029 and diagnostic P032."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r5.json"
REPAIRS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-targeted-repairs-r5.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json"
BUILD = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/build-report.json"
LETTERING = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/lettered/lettering-build-report.json"
CONTINUITY = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/review/continuity-sheet-report.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r6.json"


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
        raise ValueError("final-ambiguity crop report hash mismatch")
    crops = {row["panel_id"]: row for row in load(crop_report_path)["panels"]}
    if len(repair_doc["repairs"]) != 1 or repair_doc["repairs"][0]["panel_id"] != "ng-ch05-sc01-p029":
        raise ValueError("r6 must select only P029")
    repair = repair_doc["repairs"][0]
    panel = next(row for row in manifest["panels"] if row["panel_id"] == repair["panel_id"])
    assembly_row = next(row for row in assembly["entries"] if row["panel_id"] == repair["panel_id"])
    output = repair["output"]
    if assembly_row["source"]["sha256"] != output["sha256"] or crops[repair["panel_id"]]["artifact"]["sha256"] != output["sha256"]:
        raise ValueError("P029 repair/crop/assembly mismatch")
    prompt = generation["exact_prompt"]
    service = generation["service"]
    refs = [{"path": row["path"], "sha256": row["sha256"], "upload_target": "openai_builtin_imagegen"} for row in generation["input_references"]]
    panel["sequence_id"] = generation["generation_id"]
    panel["source_service_execution_id"] = service["service_execution_id"]
    panel["prompt_text"] = prompt
    panel["prompt_sha256"] = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    panel["input_references"] = refs
    panel["source_strip"] = generation["output_strip"]
    panel["crop_box"] = crops[repair["panel_id"]]["crop_box"]
    panel["candidate"] = {
        "path": output["path"], "sha256": output["sha256"], "width_px": output["width"], "height_px": output["height"],
        "elapsed_seconds": service["elapsed_seconds"], "timing_scope": "shared one-strip client observation; P032 diagnostic uses the same call",
        "service": {
            "tool": service["product"], "model": service["model"], "endpoint": service["endpoint"],
            "request_id": service["provider_request_id"], "provider_usage": service["usage"],
            "provider_cost_usd": service["monetary_cost_usd"], "seed": service["seed"],
            "unavailable_fields": ["model", "endpoint", "request_id", "provider_usage", "provider_cost_usd", "seed"],
        },
    }
    panel["repair"] = {"repair_class": repair["repair_class"], "reason": repair["reason"], "smallest_change": repair["smallest_change"]}
    diagnostic = deepcopy(repair_doc["diagnostic_candidates"][0])
    diagnostic["exact_prompt"] = prompt
    diagnostic["prompt_sha256"] = panel["prompt_sha256"]
    diagnostic["input_references"] = refs
    diagnostic["service"] = panel["candidate"]["service"] | {"elapsed_seconds": service["elapsed_seconds"], "timing_scope": panel["candidate"]["timing_scope"]}
    diagnostic["human_review_state"] = "PENDING"
    diagnostic["accepted"] = False
    manifest["diagnostic_candidates"] = [diagnostic]
    manifest["record_id"] = "ng-ch05-complete-chapter-production-manifest-r6"
    manifest["state"] = "COMPLETE_READING_DRAFT_P029_REPAIRED_P032_WARN_PENDING_OWNER_REVIEW"
    manifest["source_bindings"] = manifest["source_bindings"] + [binding(BASE), binding(REPAIRS), binding(ASSEMBLY), binding(BUILD), binding(LETTERING), binding(CONTINUITY)]
    manifest["review_bundle"] = {"artifacts": [
        {"kind": "chapter_scroll", **artifact(lettering["artifacts"]["lettered_long_scroll"])},
        {"kind": "contact_sheet", **artifact(build["artifacts"]["contact_sheet"])},
        {"kind": "phone_preview", **artifact(lettering["artifacts"]["lettered_phone_scroll"])},
        {"kind": "lettering_overlay", **artifact(build["artifacts"]["long_scroll_lettering_overlay"])},
        {"kind": "continuity_sheet", **artifact(continuity["artifact"])},
    ]}
    manifest["limitations"] = manifest["limitations"] + [
        "P029 passes role-separation triage and is selected; P032 remains WARN after two repair attempts and its newest candidate is diagnostic-only.",
        "Further stochastic P032 prompting is deferred in favor of owner review or deterministic local annotation/compositing research.",
    ]
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "panels": len(manifest["panels"]), "selected_repairs": 1, "diagnostic_candidates": 1}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
