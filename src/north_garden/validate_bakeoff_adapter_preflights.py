"""Validate no-network, no-write preflight behavior across G07 API adapters."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"
ADAPTERS = {
    "openai_gpt_image_2": ("openai_gpt_image2_bakeoff.py", {"OPENAI_API_KEY", "NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD"}),
    "gemini_3_1_flash_image": ("gemini_flash_image_bakeoff.py", {"GEMINI_API_KEY", "NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD"}),
    "grok_imagine_image_2": ("xai_grok_imagine_bakeoff.py", {"XAI_API_KEY", "NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD"}),
    "bfl_flux_2": ("bfl_flux2_bakeoff.py", {"BFL_API_KEY", "NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD", "NORTH_GARDEN_BFL_G07A_CONTROL_URL", "NORTH_GARDEN_BFL_G07A_NOCHANGE_CONTROL_URL"}),
}


def file_state() -> dict[str, str]:
    roots = [ROOT / "experiments/outputs", ROOT / "experiments/records"]
    return {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for root in roots if root.exists()
        for path in root.rglob("*") if path.is_file()
    }


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    request_ids = [item["id"] for item in plan["request_set"]]
    before = file_state()
    for adapter_id, (script, required_env) in ADAPTERS.items():
        result = subprocess.run([sys.executable, str(ROOT / "src/north_garden" / script)], cwd=ROOT, check=True, capture_output=True, text=True)
        payload = json.loads(result.stdout)
        assert payload["state"] == "DRY_RUN_NO_NETWORK_NO_FILES_WRITTEN"
        assert payload["requests"] == request_ids
        assert required_env <= set(payload["required_environment"])
        assert payload["adapter"]
    assert file_state() == before, "dry-run adapter preflight changed outputs or records"
    print("0 failures, 0 warnings (all G07 API adapter preflights are no-network/no-write and request-set conformant)")


if __name__ == "__main__":
    main()
