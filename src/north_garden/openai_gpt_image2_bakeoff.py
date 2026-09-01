"""Execute or preflight the fictional-only G07 OpenAI GPT Image 2 bakeoff.

Dry runs never call a provider or write a record. Execution requires both an
API key and an explicit local spend-cap environment variable. No likeness,
child, or personal input is accepted by this adapter.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import subprocess
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from bakeoff_budget import CAP_ENV, hold_for_reconciliation, reserve_bakeoff_request
from envfile import load_project_env


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"
OUT = ROOT / "experiments/outputs/openai_gpt_image2_g07_bakeoff_r1"
RECORDS = ROOT / "experiments/records/openai_gpt_image2_g07_bakeoff_r1"
MODEL = "gpt-image-2-2026-04-21"
ENDPOINT = "https://api.openai.com/v1/images/edits"
API_DOC = "https://developers.openai.com/api/docs/guides/image-generation"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def source_provenance(adapter_path: Path) -> dict:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False,
    )
    return {
        "git_commit": result.stdout.strip() if result.returncode == 0 else "UNAVAILABLE",
        "adapter_path": adapter_path.relative_to(ROOT).as_posix(),
        "adapter_sha256": sha256(adapter_path),
    }


def load_plan() -> dict:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    assert plan["state"] == "PLANNED_NO_PROVIDER_CREDENTIALS_PRESENT"
    assert plan["semantic_source"]["mutation"] == "none"
    assert plan["data_boundary"]["adult_likeness_external_upload"] == "NOT_AUTHORIZED"
    assert {item["id"] for item in plan["adapters"]} >= {"openai_gpt_image_2"}
    for asset in plan["source_assets"].values():
        path = ROOT / asset["path"]
        assert path.exists() and sha256(path) == asset["sha256"], path
    return plan


def prompt_for(request_id: str) -> str:
    base = (
        "Use the supplied original geometry-control image as the exact composition reference. "
        "This is a fictional non-person control: render exactly two abstract rectangular tile proxies only, "
        "at a shared kitchen table with a central occluder, non-touching. Preserve the grounded camera layout: "
        "orange SOREN proxy on screen-left and teal SIGRID proxy on screen-right. "
        "Do not add people, faces, animals, text, panels, extra objects, or a different scene. "
        "Return one landscape drawn-comic staging image."
    )
    if request_id == "g07a-target-change":
        return base.replace("teal SIGRID proxy", "green SIGRID proxy") + " Change only the right target proxy from teal to green; preserve all other composition information."
    if request_id == "g07a-no-change":
        return base + " Preserve the declared target state without any requested change; retain teal on the right."
    return base + " Independently compose this same declared state from the supplied control."


def multipart(fields: dict[str, str], image_path: Path) -> tuple[bytes, str]:
    boundary = f"----northgarden{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend([f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(), value.encode(), b"\r\n"])
    mime = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
    chunks.extend([
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="image[]"; filename="{image_path.name}"\r\n'.encode(),
        f"Content-Type: {mime}\r\n\r\n".encode(), image_path.read_bytes(), b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ])
    return b"".join(chunks), boundary


def execute_one(plan: dict, item: dict, api_key: str) -> Path:
    asset_key = item["source_assets"][0]
    asset = plan["source_assets"][asset_key]
    image_path = ROOT / asset["path"]
    fields = {"model": MODEL, "prompt": prompt_for(item["id"]), "size": "1536x1024", "quality": "medium", "output_format": "png"}
    body, boundary = multipart(fields, image_path)
    request = Request(ENDPOINT, data=body, method="POST", headers={"Authorization": f"Bearer {api_key}", "Content-Type": f"multipart/form-data; boundary={boundary}"})
    reservation = reserve_bakeoff_request("openai_gpt_image_2", item["id"])
    started_at = stamp()
    started = time.perf_counter()
    record = {
        "record_type": "RenderRecord", "schema_version": "1.0", "adapter_id": "openai_gpt_image_2", "provider": "OpenAI API",
        "endpoint": ENDPOINT, "provider_region": "not_reported_by_image_endpoint", "model_version_or_snapshot": MODEL,
        "request_id": None, "request_body_redacted": {"model": MODEL, "request_id": item["id"], "prompt_sha256": hashlib.sha256(fields["prompt"].encode()).hexdigest(), "size": fields["size"], "quality": fields["quality"], "source_asset": asset_key},
        "input_hashes": {asset_key: asset["sha256"]}, "output_hashes": [], "started_at": started_at, "ended_at": None, "elapsed_seconds": None,
        "provider_usage": "not_reported", "cost_usd": "not_reported; reconcile against provider billing/usage", "human_review_status": "not_yet_performed", "human_minutes": None,
        "accepted": False, "failure_tags": [], "case_id": item["case_id"], "request_kind": item["kind"],
        "semantic_source_sha256": plan["semantic_source"]["sha256"], "intent_manifest": plan["intent_manifest"],
        "data_boundary": plan["data_boundary"], "api_documentation": API_DOC,
        "budget_reservation": reservation,
        "execution_source": source_provenance(Path(__file__).resolve()),
    }
    try:
        with urlopen(request, timeout=180) as response:
            payload = json.load(response)
            record["request_id"] = response.headers.get("x-request-id")
        image_bytes = base64.b64decode(payload["data"][0]["b64_json"])
        OUT.mkdir(parents=True, exist_ok=True)
        output_path = OUT / f"{item['id']}.png"
        output_path.write_bytes(image_bytes)
    except Exception as error:
        if isinstance(error, HTTPError):
            record["request_id"] = record["request_id"] or error.headers.get("x-request-id")
            provider_error = error.read().decode("utf-8", "replace")[:2000]
        else:
            provider_error = f"{type(error).__name__}: {error}"[:2000]
        record["budget_reservation"] = hold_for_reconciliation(
            reservation["reservation_id"], provider_request_id=record["request_id"],
            provider_usage=locals().get("payload", {}).get("usage") if isinstance(locals().get("payload"), dict) else None,
            outcome="provider_request_or_result_processing_failed_cost_pending",
        )
        record.update({"ended_at": stamp(), "elapsed_seconds": round(time.perf_counter() - started, 3), "execution_status": "failed", "failure_tags": ["provider_request_failed" if isinstance(error, HTTPError) else "provider_result_processing_failed"], "provider_error": provider_error})
        RECORDS.mkdir(parents=True, exist_ok=True)
        path = RECORDS / f"{item['id']}-failed.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        raise
    usage = payload.get("usage", "not_reported")
    record.update({"ended_at": stamp(), "elapsed_seconds": round(time.perf_counter() - started, 3), "execution_status": "completed", "output_hashes": [sha256(output_path)], "candidate": {"path": output_path.relative_to(ROOT).as_posix(), "sha256": sha256(output_path)}, "provider_usage": usage})
    record["budget_reservation"] = hold_for_reconciliation(
        reservation["reservation_id"], provider_request_id=record["request_id"],
        provider_usage=usage, outcome="completed_cost_pending",
    )
    RECORDS.mkdir(parents=True, exist_ok=True)
    path = RECORDS / f"{item['id']}.json"
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Make the four paid API calls after local cap/key checks.")
    args = parser.parse_args()
    load_project_env()
    plan = load_plan()
    items = plan["request_set"]
    if not args.execute:
        print(json.dumps({"state": "DRY_RUN_NO_NETWORK_NO_FILES_WRITTEN", "adapter": "openai_gpt_image_2", "model": MODEL, "requests": [item["id"] for item in items], "required_environment": ["OPENAI_API_KEY", CAP_ENV], "current_api_doc": API_DOC}, indent=2))
        return 0
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not os.environ.get(CAP_ENV):
        raise SystemExit(f"--execute requires OPENAI_API_KEY and a positive {CAP_ENV}; no request was sent")
    for item in items:
        print(execute_one(plan, item, api_key))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
