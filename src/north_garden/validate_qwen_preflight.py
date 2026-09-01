"""Validate the no-download Qwen INT8 acquisition preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FROZEN = "f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    profile_path = ROOT / "experiments/render-profiles/qwen-image-edit-2511-comfy-int8-preflight-r1.json"
    profile = json.loads(profile_path.read_text())
    assert profile["record_type"] == "RenderProfilePreflight"
    assert profile["state"] == "NOT_ACQUIRED_LOCAL_FICTIONAL_RESEARCH_ONLY_LICENSE_COMPOSITION_UNRESOLVED"
    assert profile["semantic_source"]["sha256"] == FROZEN
    assert sha(ROOT / profile["adapter"]["local_blueprint"]["path"]) == profile["adapter"]["local_blueprint"]["sha256"]
    artifacts = {item["role"]: item for item in profile["expected_artifacts"]}
    assert set(artifacts) == {"diffusion_model", "text_encoder", "vae"}
    assert not (ROOT / artifacts["diffusion_model"]["destination"]).exists()
    assert not (ROOT / artifacts["text_encoder"]["destination"]).exists()
    vae = ROOT / artifacts["vae"]["destination"]
    assert vae.is_file() and sha(vae) == artifacts["vae"]["remote_sha256"]
    assert artifacts["text_encoder"]["license_state"] == "TENCENT_HUNYUAN_COMMUNITY_TERRITORY_AND_DISTRIBUTION_GATE"
    assert profile["first_smoke_protocol"]["inputs"].startswith("fictional neutral")
    assert len(profile["first_smoke_protocol"]["seeds"]) == 2
    assert "No adult likeness/reference input." in profile["prohibited"]
    print("0 failures, 0 warnings (Qwen INT8 preflight is unacquired and fictional-only)")


if __name__ == "__main__":
    main()
