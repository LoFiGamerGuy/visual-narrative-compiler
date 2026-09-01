"""Validate the Grok fictional G07 adapter without an API request."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "src/north_garden/xai_grok_imagine_bakeoff.py"
PLAN = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"


def main() -> None:
    spec = importlib.util.spec_from_file_location("xai_bakeoff", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    assert module.MODEL == "grok-imagine-image-2.0"
    assert module.ENDPOINT.endswith("/v1/images/edits")
    assert '"quality": "medium"' in MODULE.read_text(encoding="utf-8")
    assert '"resolution": "1k"' in MODULE.read_text(encoding="utf-8")
    assert '"response_format": "b64_json"' in MODULE.read_text(encoding="utf-8")
    assert "base64.b64decode(output[\"b64_json\"], validate=True)" in MODULE.read_text(encoding="utf-8")
    assert module.load_plan()["semantic_source"]["sha256"] == plan["semantic_source"]["sha256"]
    assert all("child" not in module.prompt_for(item["id"]).lower() for item in plan["request_set"])
    print("0 failures, 0 warnings (Grok Imagine Image 2 fictional G07 adapter preflight validated)")


if __name__ == "__main__":
    main()
