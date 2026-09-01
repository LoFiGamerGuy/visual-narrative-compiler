"""Execute or preflight the fictional-only G07 Gemini 3.1 Flash Image bakeoff.

Dry runs make no network request and write no files. Execution needs a locally
configured Gemini key and explicit local spend-cap signal; it sends only the
hash-pinned original geometry controls in the bakeoff plan.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from envfile import load_project_env
from openai_gpt_image2_bakeoff import CAP_ENV, PLAN_PATH, ROOT, load_plan, prompt_for, sha256


OUT = ROOT / "experiments/outputs/gemini_flash_image_g07_bakeoff_r1"
RECORDS = ROOT / "experiments/records/gemini_flash_image_g07_bakeoff_r1"
MODEL = "gemini-3.1-flash-image"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
API_DOC = "https://ai.google.dev/gemini-api/docs/image-generation"


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def execute_one(plan: dict, item: dict, api_key: str) -> Path:
    asset_key = item["source_assets"][0]
    asset = plan["source_assets"][asset_key]
    image_path = ROOT / asset["path"]
    prompt = prompt_for(item["id"])
    payload = {
        "model": MODEL,
        "input": [
            {"type": "text", "text": prompt},
            {"type": "image", "data": base64.b64encode(image_path.read_bytes()).decode(), "mime_type": "image/png"},
        ],
        "response_format": {"type": "image", "aspect_ratio": "3:2", "image_size": "1K"},
    }
    started_at = stamp()
    started = time.perf_counter()
    request = Request(ENDPOINT, data=json.dumps(payload).encode(), method="POST", headers={"x-goog-api-key": api_key, "Content-Type": "application/json"})
    record = {
        "record_type": "RenderRecord", "schema_version": "1.0", "adapter_id": "gemini_3_1_flash_image", "provider": "Google Gemini API",
        "endpoint": ENDPOINT, "provider_region": "not_reported_by_interactions_endpoint", "model_version_or_snapshot": MODEL,
        "request_id": None, "request_body_redacted": {"model": MODEL, "request_id": item["id"], "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "response_format": payload["response_format"], "source_asset": asset_key},
        "input_hashes": {asset_key: asset["sha256"]}, "output_hashes": [], "started_at": started_at, "ended_at": None, "elapsed_seconds": None,
        "provider_usage": "not_reported", "cost_usd": "not_reported; reconcile against provider billing/usage", "human_review_status": "not_yet_performed", "human_minutes": None,
        "accepted": False, "failure_tags": [], "case_id": item["case_id"], "request_kind": item["kind"],
        "semantic_source_sha256": plan["semantic_source"]["sha256"], "intent_manifest": plan["intent_manifest"], "data_boundary": plan["data_boundary"], "api_documentation": API_DOC,
    }
    try:
        with urlopen(request, timeout=180) as response:
            result = json.load(response)
            record["request_id"] = response.headers.get("x-request-id") or result.get("id")
    except HTTPError as error:
        record.update({"ended_at": stamp(), "elapsed_seconds": round(time.perf_counter() - started, 3), "execution_status": "failed", "failure_tags": ["provider_request_failed"], "provider_error": error.read().decode("utf-8", "replace")[:2000]})
        RECORDS.mkdir(parents=True, exist_ok=True)
        path = RECORDS / f"{item['id']}-failed.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        raise
    image_b64 = result["output_image"]["data"]
    output_path = OUT / f"{item['id']}.png"
    OUT.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(image_b64))
    record.update({"ended_at": stamp(), "elapsed_seconds": round(time.perf_counter() - started, 3), "execution_status": "completed", "output_hashes": [sha256(output_path)], "candidate": {"path": output_path.relative_to(ROOT).as_posix(), "sha256": sha256(output_path)}, "provider_usage": result.get("usage_metadata", "not_reported")})
    RECORDS.mkdir(parents=True, exist_ok=True)
    path = RECORDS / f"{item['id']}.json"
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    load_project_env()
    plan = load_plan()
    if not args.execute:
        print(json.dumps({"state": "DRY_RUN_NO_NETWORK_NO_FILES_WRITTEN", "adapter": "gemini_3_1_flash_image", "model": MODEL, "requests": [item["id"] for item in plan["request_set"]], "required_environment": ["GEMINI_API_KEY", CAP_ENV], "current_api_doc": API_DOC}, indent=2))
        return 0
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    cap = float(os.environ.get(CAP_ENV, "0"))
    if not api_key or cap <= 0:
        raise SystemExit(f"--execute requires GEMINI_API_KEY (or GOOGLE_API_KEY) and a positive {CAP_ENV}; no request was sent")
    if cap > 20:
        raise SystemExit(f"{CAP_ENV} exceeds the preflighted $20 cap; no request was sent")
    for item in plan["request_set"]:
        print(execute_one(plan, item, api_key))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
