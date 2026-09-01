"""Minimal local `.env` loader for North Garden command-line adapters.

It intentionally has no third-party dependency, never prints values, never
overrides a process environment variable, and supports only simple KEY=VALUE
entries (optional matching single/double quotes).  This is not a shell parser.
"""
from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_project_env(path: Path | None = None) -> list[str]:
    path = path or ROOT / ".env"
    if not path.exists():
        return []
    loaded: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or key in os.environ or not value:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key] = value
        loaded.append(key)
    return loaded
