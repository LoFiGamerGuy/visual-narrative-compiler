"""Validate a no-download runtime-asset declaration."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_KINDS = {"executable", "directory", "executable_or_env_path", "python_module"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def resolve_manifest(value: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to((ROOT / "config").resolve()) or path.suffix.lower() != ".json":
        raise argparse.ArgumentTypeError("manifest must be a JSON file below config")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=resolve_manifest, default=ROOT / "config/runtime-assets.example.json")
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    warnings = 0
    assert data["schema_version"] == "north_garden.runtime_assets.v1"
    assert data["state"] in {"EXAMPLE_NO_DOWNLOADS", "LOCAL_RUNTIME_DECLARATION"}
    expected_profiles = {"documentation", "instrumentation", "baseline_legacy", "blender_stage"}
    actual_profiles = set(data["profiles"])
    is_ignored_local = args.manifest.name == "runtime-assets.local.json"
    if not is_ignored_local and data["state"] == "EXAMPLE_NO_DOWNLOADS":
        assert actual_profiles == expected_profiles
    else:
        legacy_profiles = {"documentation", "baseline_legacy", "blender_stage"}
        assert frozenset(actual_profiles) in {frozenset(expected_profiles), frozenset(legacy_profiles)}
        if actual_profiles == legacy_profiles:
            warnings += 1
    for profile_id, profile in data["profiles"].items():
        assert profile["downloads"] is False, profile_id
        requirements = profile.get("requirements")
        if requirements is None:
            legacy = profile.get("requires")
            assert isinstance(legacy, list) and legacy, profile_id
            requirements = [
                {"kind": "executable", "name": item}
                if item.lower() == "python"
                else {"kind": "directory", "path": item}
                for item in legacy
            ]
            warnings += 1
        assert requirements, profile_id
        for requirement in requirements:
            assert requirement["kind"] in ALLOWED_KINDS
            if requirement["kind"] == "directory":
                path = Path(requirement["path"])
                assert not path.is_absolute() and ".." not in path.parts
            else:
                assert requirement["name"]
            if requirement["kind"] == "python_module":
                assert requirement["distribution"]
            if "version" in requirement:
                assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", requirement["version"])
            if requirement["kind"] == "executable_or_env_path":
                assert requirement["environment"].startswith("NORTH_GARDEN_")
        if profile_id == "instrumentation":
            entrypoint = Path(profile["entrypoint"])
            assert not entrypoint.is_absolute() and ".." not in entrypoint.parts
            assert profile["network_allowed"] is False
            assert profile["provider_credentials_required"] is False
    assert data["assets"]
    for asset in data["assets"]:
        assert asset["id"] and asset["local_path"] and asset["license_artifact"] and asset["source_url"]
        path = Path(asset["local_path"])
        assert not path.is_absolute() and ".." not in path.parts
        if data["state"] == "LOCAL_RUNTIME_DECLARATION":
            assert SHA256.fullmatch(asset["sha256"])
            assert asset["source_url"].startswith("https://")
            assert asset["commercial_state"] != "UNREVIEWED"
        else:
            assert asset["sha256"] == "REPLACE_WITH_EXACT_HASH"
    print(f"0 failures, {warnings} warnings (runtime asset manifest validated: {args.manifest.relative_to(ROOT)})")
    if warnings:
        print("warning: ignored local manifest uses legacy profile 'requires'; refresh it from config/runtime-assets.example.json when convenient")


if __name__ == "__main__":
    main()
