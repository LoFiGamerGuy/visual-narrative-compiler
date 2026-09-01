"""Reconstruct r2 records after a dry-run provenance overwrite.

No image is regenerated. The original output bytes, local ComfyUI history, and
the existing r1 review are evidence sources. The overwritten r1 records remain
as incident artifacts; this emits r2 records, review, and correction report.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / "experiments/records/legacy_duo3"
NEW = ROOT / "experiments/records/legacy_duo3_r2_reconstructed"
REVIEW_R1 = ROOT / "experiments/reviews/legacy-duo3-ch03-ridge-signal-review-r1.json"
REVIEW_R2 = ROOT / "experiments/reviews/legacy-duo3-ch03-ridge-signal-review-r2-reconstructed.json"
INCIDENT = ROOT / "experiments/incidents/legacy-duo3-dry-run-overwrite-correction-20260901.json"
PROMPT_IDS = {
    "ng-ch03-sc01-p001": "5b71477e-f387-47dd-8035-7abf7481e974",
    "ng-ch03-sc01-p002": "3d707bc3-b77b-4934-b6d8-0f558f37f6f4",
    "ng-ch03-sc01-p003": "7cd186d9-668d-4fcd-b0b5-0d781032f549",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iso_utc(milliseconds: int) -> str:
    return datetime.fromtimestamp(milliseconds / 1000, UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    review = json.loads(REVIEW_R1.read_text(encoding="utf-8"))
    NEW.mkdir(parents=True, exist_ok=True)
    INCIDENT.parent.mkdir(parents=True, exist_ok=True)
    corrected_candidates = []
    overwritten = []
    for candidate in review["candidates"]:
        panel_id = candidate["panel_id"]
        old_path = ROOT / candidate["record_path"]
        old = json.loads(old_path.read_text(encoding="utf-8"))
        prompt_id = PROMPT_IDS[panel_id]
        with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=10) as response:
            entry = json.load(response)[prompt_id]
        messages = {message[0]: message[1] for message in entry["status"]["messages"]}
        graph = entry["prompt"]
        output_path = ROOT / candidate["candidate_path"]
        assert output_path.exists() and sha256(output_path) == candidate["sha256"]
        record = dict(old)
        record["record_id"] = f"{old['record_id']}-r2-reconstructed"
        record["input_state"] = {
            "seed": old["input_state"]["seed"],
            "workflow_graph": graph,
            "workflow_graph_sha256": hashlib.sha256(json.dumps(graph, sort_keys=True).encode()).hexdigest(),
        }
        record["status"] = "completed"
        record["started_at"] = iso_utc(messages["execution_start"]["timestamp"])
        record["ended_at"] = iso_utc(messages["execution_success"]["timestamp"])
        record["generation_seconds"] = candidate["generation_seconds"]
        record["comfy_prompt_id"] = prompt_id
        record["generated_candidates"] = [{"path": candidate["candidate_path"], "sha256": candidate["sha256"]}]
        record["human_review_status"] = "not_yet_performed"
        record["accepted_output"] = None
        record["provenance_reconstruction"] = {
            "reason": "r1 record was overwritten by a dry-run adapter defect; no raster was regenerated",
            "sources": ["local ComfyUI history", "existing r1 review", "existing output bytes"],
            "overwritten_r1_record_path": str(old_path.relative_to(ROOT)).replace("\\", "/"),
            "overwritten_r1_record_sha256": sha256(old_path),
        }
        new_path = NEW / f"{record['record_id']}.json"
        new_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        corrected = dict(candidate)
        corrected["record_path"] = str(new_path.relative_to(ROOT)).replace("\\", "/")
        corrected_candidates.append(corrected)
        overwritten.append({"path": str(old_path.relative_to(ROOT)).replace("\\", "/"), "sha256_after_overwrite": sha256(old_path), "reconstructed_path": corrected["record_path"], "reconstructed_sha256": sha256(new_path)})
    review_r2 = dict(review)
    review_r2["record_id"] = "ng-review-legacy-duo3-ch03-ridge-signal-r2-reconstructed"
    review_r2["candidates"] = corrected_candidates
    review_r2["correction"] = "R2 replaces r1 review linkage after a dry-run overwrite incident. No image was regenerated or rejudged."
    REVIEW_R2.write_text(json.dumps(review_r2, indent=2) + "\n", encoding="utf-8")
    incident = {
        "record_type": "ProvenanceCorrectionReport",
        "incident_id": "legacy-duo3-dry-run-overwrite-20260901",
        "cause": "--dry-run wrote planned RenderRecords using completed-record paths.",
        "impact": "Three r1 JSON records were overwritten; PNG bytes and ComfyUI history remained intact.",
        "repair": "R2 records were reconstructed from local history, review-linked output hashes, and source fields; no render was repeated.",
        "preserved_overwritten_r1_records": overwritten,
        "review_r2": str(REVIEW_R2.relative_to(ROOT)).replace("\\", "/"),
        "prevention": "legacy_duo3.py dry runs now write no records.",
    }
    INCIDENT.write_text(json.dumps(incident, indent=2) + "\n", encoding="utf-8")
    print("0 failures, 0 warnings (legacy_duo3 r2 provenance reconstruction written)")


if __name__ == "__main__":
    main()
