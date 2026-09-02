"""Compile CH05 production manifest r4 with the targeted P036 leverage repair."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r3.json"
REPAIRS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-targeted-repairs-r3.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r4.json"
BUILD = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r4/review/build-report.json"
LETTERING = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r4/lettered/lettering-build-report.json"
CONTINUITY = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r4/review/continuity-sheet-report.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r4.json"


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
    if len(repair_doc["repairs"]) != 1:
        raise ValueError("r4 requires exactly one P036 repair")
    repair = repair_doc["repairs"][0]
    panel_id = repair["panel_id"]
    if panel_id != "ng-ch05-sc01-p036":
        raise ValueError("r4 repair must target P036")
    assembly_row = next(row for row in assembly["entries"] if row["panel_id"] == panel_id)
    output = repair["output"]
    if assembly_row["source"]["sha256"] != output["sha256"]:
        raise ValueError("r4 assembly does not bind P036 repair")
    panel = next(row for row in manifest["panels"] if row["panel_id"] == panel_id)
    prompt = repair["exact_prompt"]
    service = repair["service"]
    panel["sequence_id"] = None
    panel["source_service_execution_id"] = service["service_execution_id"]
    panel["prompt_text"] = prompt
    panel["prompt_sha256"] = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    panel["input_references"] = [{"path": row["path"], "sha256": row["sha256"], "upload_target": "openai_builtin_imagegen"} for row in repair["input_references"]]
    panel["source_strip"] = None
    panel["crop_box"] = None
    panel["candidate"] = {
        "path": output["path"], "sha256": output["sha256"], "width_px": output["width"], "height_px": output["height"],
        "elapsed_seconds": service["elapsed_seconds"], "timing_scope": service["timing_basis"],
        "service": {
            "tool": service["product"], "model": service["model"], "endpoint": service["endpoint"],
            "request_id": service["provider_request_id"], "provider_usage": service["usage"],
            "provider_cost_usd": service["monetary_cost_usd"], "seed": service["seed"],
            "unavailable_fields": ["model", "endpoint", "request_id", "provider_usage", "provider_cost_usd", "seed"],
        },
    }
    panel["repair"] = {"repair_class": repair["repair_class"], "reason": repair["reason"], "smallest_change": repair["smallest_change"], "agent_triage": repair["review"]["agent_triage"]}
    manifest["record_id"] = "ng-ch05-complete-chapter-production-manifest-r4"
    manifest["state"] = "COMPLETE_READING_DRAFT_WITH_LEVERAGE_REPAIR_PENDING_OWNER_REVIEW"
    manifest["source_bindings"] = manifest["source_bindings"] + [binding(BASE), binding(REPAIRS), binding(ASSEMBLY), binding(BUILD), binding(LETTERING), binding(CONTINUITY)]
    manifest["review_bundle"] = {"artifacts": [
        {"kind": "chapter_scroll", **artifact(lettering["artifacts"]["lettered_long_scroll"])},
        {"kind": "contact_sheet", **artifact(build["artifacts"]["contact_sheet"])},
        {"kind": "phone_preview", **artifact(lettering["artifacts"]["lettered_phone_scroll"])},
        {"kind": "lettering_overlay", **artifact(build["artifacts"]["long_scroll_lettering_overlay"])},
        {"kind": "continuity_sheet", **artifact(continuity["artifact"])},
    ]}
    manifest["limitations"] = manifest["limitations"] + [
        "P036's one-plank force path is explicit in agent triage, but Soren's raised-beam footing is more dramatic than the original plan implied.",
        "The P036 repair remains pending owner review and grants no acceptance or production-base status.",
    ]
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "panels": len(manifest["panels"]), "repairs": 1}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
