"""Live-readiness preflight with no provider API request and no ledger write."""
from __future__ import annotations

import json
import os

from bakeoff_budget import preflight_bakeoff_budget
from bfl_flux2_bakeoff import verified_control_url
from envfile import load_project_env
from openai_gpt_image2_bakeoff import load_plan


KEYS = {
    "openai_gpt_image_2": ("OPENAI_API_KEY",),
    "gemini_3_1_flash_image": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "grok_imagine_image_2": ("XAI_API_KEY",),
    "bfl_flux_2": ("BFL_API_KEY",),
}


def main() -> None:
    load_project_env()
    plan = load_plan()
    assert plan["data_boundary"]["adult_likeness_external_upload"] == "NOT_AUTHORIZED"
    assert plan["data_boundary"]["input_classification"] == "FICTIONAL_ADULT_DESIGN_AND_ORIGINAL_GEOMETRY_ONLY"
    results = []
    for adapter_id, alternatives in KEYS.items():
        if not any(os.environ.get(name) for name in alternatives):
            raise SystemExit(f"missing configured credential for {adapter_id}; no provider request was sent")
        budget = preflight_bakeoff_budget(adapter_id)
        result = {
            "adapter_id": adapter_id,
            "credential_present": True,
            "data_boundary": "pass",
            "source_hashes": "pass",
            "aggregate_budget": budget,
        }
        if adapter_id == "bfl_flux_2":
            verified = []
            for asset_key in {item["source_assets"][0] for item in plan["request_set"]}:
                verified_control_url(asset_key, plan["source_assets"][asset_key])
                verified.append({"asset_key": asset_key, "sha256": plan["source_assets"][asset_key]["sha256"]})
            result["public_control_hash_verification"] = sorted(verified, key=lambda item: item["asset_key"])
        results.append(result)
    print(json.dumps({
        "state": "READY_NO_PROVIDER_API_REQUEST_NO_LEDGER_WRITE",
        "bakeoff_id": plan["record_id"],
        "requests_per_adapter": len(plan["request_set"]),
        "adapters": results,
    }, indent=2))


if __name__ == "__main__":
    main()
