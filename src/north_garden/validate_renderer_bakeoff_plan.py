"""Validate the provider-neutral fictional renderer-bakeoff plan without calling a provider."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"
GAUNTLET_PATH = ROOT / "research/authoritative/v2.1.1/bench/gauntlet.json"
REQUIRED_ADAPTERS = {
    "gemini_3_1_flash_image",
    "grok_imagine_image_2",
    "openai_gpt_image_2",
    "bfl_flux_2",
    "qwen_image_edit_2511_managed_gpu",
}
REQUIRED_RECORD_FIELDS = {
    "adapter_id", "provider", "endpoint", "provider_region", "model_version_or_snapshot",
    "request_body_redacted", "request_id", "input_hashes", "output_hashes", "started_at",
    "ended_at", "elapsed_seconds", "provider_usage", "cost_usd", "human_review_status",
    "human_minutes", "accepted", "failure_tags",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    assert plan["record_type"] == "RendererBakeoffPlan"
    assert plan["state"] == "PLANNED_NO_PROVIDER_CREDENTIALS_PRESENT"
    assert plan["semantic_source"]["mutation"] == "none"
    assert plan["semantic_source"]["sha256"] == sha256(GAUNTLET_PATH)
    assert plan["bundle"]["required_state"].endswith("NOT_FROZEN")
    assert plan["data_boundary"]["input_classification"] == "FICTIONAL_ADULT_DESIGN_AND_ORIGINAL_GEOMETRY_ONLY"
    prohibited = set(plan["data_boundary"]["prohibited"])
    assert {"child imagery", "real-person likeness", "adult-likeness LoRA output"} <= prohibited
    assert plan["data_boundary"]["adult_likeness_external_upload"] == "NOT_AUTHORIZED"
    assert len(plan["request_set"]) == 4
    assert [item["id"] for item in plan["request_set"]] == [
        "g07a-independent-01", "g07a-independent-02", "g07a-target-change", "g07a-no-change"
    ]
    assert {item["case_id"] for item in plan["request_set"]} == {"G07a"}
    assert set(plan["source_assets"]) == {"g07a-control", "g07a-nochange-reference"}
    for asset in plan["source_assets"].values():
        path = ROOT / asset["path"]
        assert path.exists() and sha256(path) == asset["sha256"]
    adapters = {item["id"]: item for item in plan["adapters"]}
    assert set(adapters) == REQUIRED_ADAPTERS
    assert adapters["qwen_image_edit_2511_managed_gpu"]["seed_behavior"] == "explicit_seed_required"
    assert {"PENDING_CREDENTIAL_AND_BOUNDED_SPEND", "PENDING_TERMS_CREDENTIAL_AND_BOUNDED_SPEND", "PENDING_PROVIDER_PROFILE_AND_ARTIFACT_ACQUISITION"} >= {item["status"] for item in adapters.values()}
    assert set(plan["required_render_record"]) == REQUIRED_RECORD_FIELDS
    assert "does not approve a provider" in plan["acceptance_boundary"]
    print("0 failures, 0 warnings (fictional external renderer bakeoff plan validated)")


if __name__ == "__main__":
    main()
