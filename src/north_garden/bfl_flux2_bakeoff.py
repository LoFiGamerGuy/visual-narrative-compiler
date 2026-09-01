"""Execute or preflight the fictional-only pinned FLUX.2 Pro G07 bakeoff.

BFL's documented edit endpoint takes a URL, not a local-file payload. Before
execution, this adapter downloads the configured public fictional-control URL
and refuses to call BFL unless its bytes equal the plan's pinned input hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import truststore

from envfile import load_project_env
from openai_gpt_image2_bakeoff import CAP_ENV, ROOT, load_plan, prompt_for, sha256


OUT = ROOT / "experiments/outputs/bfl_flux2_g07_bakeoff_r1"
RECORDS = ROOT / "experiments/records/bfl_flux2_g07_bakeoff_r1"
MODEL = "flux-2-pro"
ENDPOINT = f"https://api.bfl.ai/v1/{MODEL}"
API_DOC = "https://docs.bfl.ai/flux_2/flux2_image_editing"
TERMS_URL = "https://bfl.ai/legal/flux-api-service-terms"
CONTROL_URL_ENVS = {
    "g07a-control": "NORTH_GARDEN_BFL_G07A_CONTROL_URL",
    "g07a-nochange-reference": "NORTH_GARDEN_BFL_G07A_NOCHANGE_CONTROL_URL",
}
# Use the Windows/macOS/Linux native trust store.  This preserves certificate
# verification when an organization supplies a locally trusted inspection CA.
SSL_CONTEXT = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def verified_control_url(asset_key: str, asset: dict) -> str:
    env_name = CONTROL_URL_ENVS.get(asset_key)
    if env_name is None:
        raise SystemExit(f"no BFL public-control environment mapping exists for {asset_key}; no BFL request was sent")
    url = os.environ.get(env_name, "")
    if not url.startswith("https://"):
        raise SystemExit(f"{env_name} must be an HTTPS URL; no BFL request was sent")
    with urlopen(url, timeout=30, context=SSL_CONTEXT) as response:
        remote_hash = hashlib.sha256(response.read()).hexdigest()
    if remote_hash != asset["sha256"]:
        raise SystemExit("configured public control URL does not equal the frozen local control hash; no BFL request was sent")
    return url


def post_json(url: str, key: str, payload: dict) -> dict:
    request = Request(url, data=json.dumps(payload).encode(), method="POST", headers={"accept": "application/json", "x-key": key, "Content-Type": "application/json"})
    with urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
        return json.load(response)


def poll(url: str, key: str) -> dict:
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        request = Request(url, headers={"accept": "application/json", "x-key": key})
        with urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
            result = json.load(response)
        if result.get("status") == "Ready":
            return result
        if result.get("status") in {"Error", "Failed"}:
            raise RuntimeError(json.dumps(result)[:2000])
        time.sleep(0.5)
    raise TimeoutError("BFL polling exceeded 300 seconds")


def execute_one(plan: dict, item: dict, api_key: str) -> Path:
    asset_key = item["source_assets"][0]
    asset = plan["source_assets"][asset_key]
    prompt = prompt_for(item["id"])
    started_at = stamp()
    started = time.perf_counter()
    record = {
        "record_type": "RenderRecord", "schema_version": "1.0", "adapter_id": "bfl_flux_2", "provider": "Black Forest Labs API",
        "endpoint": ENDPOINT, "provider_region": "not_reported_by_endpoint", "model_version_or_snapshot": MODEL,
        "request_id": None, "request_body_redacted": {"model": MODEL, "request_id": item["id"], "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "source_asset": asset_key, "public_control_url_sha256": None},
        "input_hashes": {asset_key: asset["sha256"]}, "output_hashes": [], "started_at": started_at, "ended_at": None, "elapsed_seconds": None,
        "provider_usage": "not_reported", "cost_usd": None, "cost_note": "reconcile actual BFL credit spend; do not infer a per-request total", "human_review_status": "not_yet_performed", "human_minutes": None,
        "accepted": False, "failure_tags": [], "case_id": item["case_id"], "request_kind": item["kind"], "semantic_source_sha256": plan["semantic_source"]["sha256"],
        "intent_manifest": plan["intent_manifest"], "data_boundary": plan["data_boundary"], "api_documentation": API_DOC,
        "provider_terms": {"url": TERMS_URL, "last_reviewed": "2026-09-01", "critical_boundary": "BFL API terms state inputs/outputs may be used to train and improve services; fictional controls only."},
    }
    try:
        control_url = verified_control_url(asset_key, asset)
        record["request_body_redacted"]["public_control_url_sha256"] = hashlib.sha256(control_url.encode()).hexdigest()
        submitted = post_json(ENDPOINT, api_key, {"prompt": prompt, "input_image": control_url, "width": 1536, "height": 1024})
        record["request_id"] = submitted["id"]
        result = poll(submitted["polling_url"], api_key)
        sample_url = result["result"]["sample"]
        with urlopen(sample_url, timeout=180, context=SSL_CONTEXT) as response:
            image_bytes = response.read()
    except (HTTPError, KeyError, RuntimeError, TimeoutError) as error:
        record.update({"ended_at": stamp(), "elapsed_seconds": round(time.perf_counter() - started, 3), "execution_status": "failed", "failure_tags": ["provider_request_failed"], "provider_error": str(error)[:2000]})
        RECORDS.mkdir(parents=True, exist_ok=True)
        path = RECORDS / f"{item['id']}-failed.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        raise
    OUT.mkdir(parents=True, exist_ok=True)
    output_path = OUT / f"{item['id']}.png"
    output_path.write_bytes(image_bytes)
    record.update({"ended_at": stamp(), "elapsed_seconds": round(time.perf_counter() - started, 3), "execution_status": "completed", "output_hashes": [sha256(output_path)], "candidate": {"path": output_path.relative_to(ROOT).as_posix(), "sha256": sha256(output_path)}, "provider_output_url_sha256": hashlib.sha256(sample_url.encode()).hexdigest()})
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
        print(json.dumps({"state": "DRY_RUN_NO_NETWORK_NO_FILES_WRITTEN", "adapter": "bfl_flux_2", "model": MODEL, "requests": [item["id"] for item in plan["request_set"]], "required_environment": ["BFL_API_KEY", CAP_ENV, *CONTROL_URL_ENVS.values()], "critical_terms_boundary": "fictional controls only; current BFL API terms permit input/output training use"}, indent=2))
        return 0
    cap = float(os.environ.get(CAP_ENV, "0"))
    if not os.environ.get("BFL_API_KEY") or cap <= 0:
        raise SystemExit(f"--execute requires BFL_API_KEY and a positive {CAP_ENV}; no request was sent")
    if cap > 20:
        raise SystemExit(f"{CAP_ENV} exceeds the preflighted $20 cap; no request was sent")
    for item in plan["request_set"]:
        print(execute_one(plan, item, os.environ["BFL_API_KEY"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
