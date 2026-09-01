"""Validate the OpenAI G07 adapter without a network request or file output."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "src/north_garden/openai_gpt_image2_bakeoff.py"
PLAN = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    spec = importlib.util.spec_from_file_location("openai_bakeoff", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    assert module.MODEL == "gpt-image-2-2026-04-21"
    assert module.ENDPOINT.endswith("/v1/images/edits")
    assert module.load_plan()["semantic_source"]["sha256"] == plan["semantic_source"]["sha256"]
    prompts = {item["id"]: module.prompt_for(item["id"]) for item in plan["request_set"]}
    assert set(prompts) == {"g07a-independent-01", "g07a-independent-02", "g07a-target-change", "g07a-no-change"}
    assert "green SIGRID proxy" in prompts["g07a-target-change"]
    assert "retain teal" in prompts["g07a-no-change"]
    assert all("child" not in prompt.lower() and "real-person" not in prompt.lower() for prompt in prompts.values())
    body, boundary = module.multipart({"model": module.MODEL, "prompt": prompts["g07a-no-change"]}, ROOT / plan["source_assets"]["g07a-control"]["path"])
    assert boundary.encode() in body and sha256(MODULE)
    print("0 failures, 0 warnings (OpenAI GPT Image 2 fictional G07 adapter preflight validated)")


if __name__ == "__main__":
    main()
