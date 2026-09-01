"""Validate the BFL fictional G07 adapter without network traffic."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "src/north_garden/bfl_flux2_bakeoff.py"
PLAN = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"


def main() -> None:
    spec = importlib.util.spec_from_file_location("bfl_bakeoff", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    assert module.MODEL == "flux-2-pro" and module.ENDPOINT.endswith("/flux-2-pro")
    assert module.load_plan()["semantic_source"]["sha256"] == plan["semantic_source"]["sha256"]
    assert "may be used to train" in MODULE.read_text(encoding="utf-8")
    assert '"output_format": "png"' in MODULE.read_text(encoding="utf-8")
    assert '"cost_credits"' in MODULE.read_text(encoding="utf-8")
    assert all("child" not in module.prompt_for(item["id"]).lower() for item in plan["request_set"])
    print("0 failures, 0 warnings (BFL FLUX.2 fictional G07 adapter preflight validated)")


if __name__ == "__main__":
    main()
