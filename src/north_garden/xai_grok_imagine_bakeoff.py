"""Execute or preflight the fictional-only G07 Grok Imagine Image 2 bakeoff."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import ssl
import time
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from bakeoff_budget import CAP_ENV, hold_for_reconciliation, reconcile_reservation, release_unsubmitted_reservation, reserve_bakeoff_request
from envfile import load_project_env
from openai_gpt_image2_bakeoff import ROOT, SSL_CONTEXT, load_plan, prompt_for, sha256, source_provenance


OUT = ROOT / "experiments/outputs/xai_grok_imagine_g07_bakeoff_r1"
RECORDS = ROOT / "experiments/records/xai_grok_imagine_g07_bakeoff_r1"
MODEL = "grok-imagine-image-2.0"
ENDPOINT = "https://api.x.ai/v1/images/edits"
API_DOC = "https://docs.x.ai/developers/model-capabilities/images/editing"


def settle_reservation(reservation: dict, usage: object, request_id: str | None, outcome: str) -> tuple[dict, str | None]:
    if isinstance(usage, dict) and isinstance(usage.get("cost_in_usd_ticks"), int):
        actual = Decimal(usage["cost_in_usd_ticks"]) / Decimal(10_000_000_000)
        entry = reconcile_reservation(
            reservation["reservation_id"], str(actual),
            provider_request_id=request_id, provider_usage=usage,
        )
        return entry, entry["actual_cost_usd"]
    entry = hold_for_reconciliation(
        reservation["reservation_id"], provider_request_id=request_id,
        provider_usage=usage, outcome=outcome,
    )
    return entry, None


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def execute_one(plan: dict, item: dict, api_key: str, reservation_key: str | None = None) -> Path:
    asset_key = item["source_assets"][0]
    asset = plan["source_assets"][asset_key]
    source = ROOT / asset["path"]
    prompt = prompt_for(item["id"])
    image_data_uri = "data:image/png;base64," + base64.b64encode(source.read_bytes()).decode()
    payload = {"model": MODEL, "prompt": prompt, "image": {"type": "image_url", "url": image_data_uri}, "aspect_ratio": "3:2", "resolution": "1k", "quality": "medium", "response_format": "b64_json"}
    request = Request(ENDPOINT, data=json.dumps(payload).encode(), method="POST", headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    ledger_request_key = reservation_key or item["id"]
    reservation = reserve_bakeoff_request("grok_imagine_image_2", ledger_request_key)
    started_at = stamp()
    started = time.perf_counter()
    record = {
        "record_type": "RenderRecord", "schema_version": "1.0", "adapter_id": "grok_imagine_image_2", "provider": "xAI API",
        "endpoint": ENDPOINT, "provider_region": "not_reported_by_image_endpoint", "model_version_or_snapshot": MODEL,
        "request_id": None, "request_body_redacted": {"model": MODEL, "request_id": item["id"], "ledger_request_key": ledger_request_key, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "aspect_ratio": "3:2", "resolution": "1k", "quality": "medium", "response_format": "b64_json", "source_asset": asset_key},
        "input_hashes": {asset_key: asset["sha256"]}, "output_hashes": [], "started_at": started_at, "ended_at": None, "elapsed_seconds": None,
        "provider_usage": "not_reported", "cost_usd": None, "cost_note": "retain provider usage ticks and reconcile with provider billing; do not infer a dollar value", "human_review_status": "not_yet_performed", "human_minutes": None,
        "accepted": False, "failure_tags": [], "case_id": item["case_id"], "request_kind": item["kind"], "semantic_source_sha256": plan["semantic_source"]["sha256"],
        "intent_manifest": plan["intent_manifest"], "data_boundary": plan["data_boundary"], "api_documentation": API_DOC,
        "budget_reservation": reservation,
        "execution_source": source_provenance(Path(__file__).resolve()),
    }
    try:
        with urlopen(request, timeout=180, context=SSL_CONTEXT) as response:
            raw_response = response.read()
            result = json.loads(raw_response)
            record["request_id"] = response.headers.get("x-request-id") or result.get("id")
            record["provider_data_controls"] = {"x_zero_data_retention": response.headers.get("x-zero-data-retention")}
        output = result["data"][0]
        image_bytes = base64.b64decode(output["b64_json"], validate=True)
        mime_type = output.get("mime_type", "image/jpeg")
        suffix = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(mime_type.lower(), ".bin")
        OUT.mkdir(parents=True, exist_ok=True)
        output_path = OUT / f"{item['id']}{suffix}"
        output_path.write_bytes(image_bytes)
    except Exception as error:
        if isinstance(error, HTTPError):
            record["request_id"] = record["request_id"] or error.headers.get("x-request-id")
            provider_error = error.read().decode("utf-8", "replace")[:2000]
        else:
            provider_error = f"{type(error).__name__}: {error}"[:2000]
        usage = locals().get("result", {}).get("usage") if isinstance(locals().get("result"), dict) else None
        record["provider_usage"] = usage if usage is not None else "not_reported"
        if isinstance(locals().get("raw_response"), bytes):
            record["provider_response_sha256"] = hashlib.sha256(raw_response).hexdigest()
        failed_output = locals().get("result", {}).get("data", [{}])[0] if isinstance(locals().get("result"), dict) else {}
        if isinstance(failed_output, dict) and failed_output.get("url"):
            record["provider_output_url_sha256"] = hashlib.sha256(failed_output["url"].encode()).hexdigest()
        tls_pre_submission = isinstance(error, URLError) and isinstance(error.reason, ssl.SSLCertVerificationError) and "result" not in locals()
        if tls_pre_submission:
            record["budget_reservation"] = release_unsubmitted_reservation(
                reservation["reservation_id"], "tls_handshake_failed_before_http_submission",
            )
            record["cost_usd"] = "0.000000"
        else:
            record["budget_reservation"], record["cost_usd"] = settle_reservation(
                reservation, usage, record["request_id"], "provider_request_or_result_processing_failed_cost_pending",
            )
        record.update({"ended_at": stamp(), "elapsed_seconds": round(time.perf_counter() - started, 3), "execution_status": "failed", "failure_tags": ["provider_request_failed" if isinstance(error, (HTTPError, URLError)) else "provider_result_processing_failed"], "provider_error": provider_error})
        RECORDS.mkdir(parents=True, exist_ok=True)
        path = RECORDS / f"{item['id']}-failed.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        raise
    usage = result.get("usage", "not_reported")
    record.update({"ended_at": stamp(), "elapsed_seconds": round(time.perf_counter() - started, 3), "execution_status": "completed", "output_hashes": [sha256(output_path)], "candidate": {"path": output_path.relative_to(ROOT).as_posix(), "sha256": sha256(output_path), "mime_type": mime_type}, "provider_usage": usage, "provider_response_sha256": hashlib.sha256(raw_response).hexdigest()})
    record["budget_reservation"], record["cost_usd"] = settle_reservation(
        reservation, usage, record["request_id"], "completed_cost_pending",
    )
    RECORDS.mkdir(parents=True, exist_ok=True)
    path = RECORDS / f"{item['id']}.json"
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--request-id", choices=["g07a-independent-01", "g07a-independent-02", "g07a-target-change", "g07a-no-change"])
    parser.add_argument("--retry-suffix", help="Auditable ledger suffix for a replacement of a paid failed request.")
    args = parser.parse_args()
    load_project_env()
    plan = load_plan()
    if not args.execute:
        print(json.dumps({"state": "DRY_RUN_NO_NETWORK_NO_FILES_WRITTEN", "adapter": "grok_imagine_image_2", "model": MODEL, "requests": [item["id"] for item in plan["request_set"]], "required_environment": ["XAI_API_KEY", CAP_ENV], "current_api_doc": API_DOC}, indent=2))
        return 0
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key or not os.environ.get(CAP_ENV):
        raise SystemExit(f"--execute requires XAI_API_KEY and a positive {CAP_ENV}; no request was sent")
    if args.retry_suffix and not args.request_id:
        raise SystemExit("--retry-suffix requires --request-id")
    items = [item for item in plan["request_set"] if not args.request_id or item["id"] == args.request_id]
    for item in items:
        reservation_key = f"{item['id']}-retry-{args.retry_suffix}" if args.retry_suffix else item["id"]
        print(execute_one(plan, item, api_key, reservation_key))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
