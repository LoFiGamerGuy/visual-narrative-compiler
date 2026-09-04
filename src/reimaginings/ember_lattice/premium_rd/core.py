from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable


class PremiumRDError(ValueError):
    """A deterministic input or integrity failure."""


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PremiumRDError(f"cannot parse JSON {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative_path(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise PremiumRDError(f"{field} must be a non-empty POSIX relative path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise PremiumRDError(f"{field} escapes its declared root: {value!r}")
    return candidate


def resolve_under(root: Path, relative: str, field: str) -> Path:
    rel = safe_relative_path(relative, field)
    base = root.resolve()
    target = (base / rel).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise PremiumRDError(f"{field} resolves outside root: {relative!r}") from exc
    return target


def rel_href(source: Path, target_parent: Path) -> str:
    return Path(os.path.relpath(source, target_parent)).as_posix()


def slug(value: Any, field: str = "id") -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", value):
        raise PremiumRDError(f"{field} must match [a-z0-9][a-z0-9._-]*")
    return value


def duplicate_values(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def esc(value: Any) -> str:
    import html

    return html.escape(str(value), quote=True)
