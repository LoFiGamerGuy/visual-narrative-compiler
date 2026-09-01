"""Validate the Gemini fictional G07 adapter without an API request."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "src/north_garden/gemini_flash_image_bakeoff.py"
PLAN = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"


def main() -> None:
    spec = importlib.util.spec_from_file_location("gemini_bakeoff", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    assert module.MODEL == "gemini-3.1-flash-image"
    assert module.ENDPOINT.endswith("/v1beta/interactions")
    assert module.load_plan()["semantic_source"]["sha256"] == plan["semantic_source"]["sha256"]
    assert all("child" not in module.prompt_for(item["id"]).lower() for item in plan["request_set"])
    print("0 failures, 0 warnings (Gemini 3.1 Flash Image fictional G07 adapter preflight validated)")


if __name__ == "__main__":
    main()
