"""Validate the current CH05 complete-chapter review handoff links and claims."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "docs/research/ch05-complete-chapter-review-handoff-r7.md"
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HASH_PATTERN = re.compile(r"SHA-256 `([0-9a-f]+)`")
LINK_HASH_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)[^\[]*?SHA-256 `([0-9a-f]+)`")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_link(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else HANDOFF.parent / path


def validate(text: str, verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(text.startswith("# CH05 complete-chapter review handoff r7\n"), "title")
    links = LINK_PATTERN.findall(text)
    check(len(links) == 41, "link count")
    check(len(set(links)) == 41, "unique links")
    required_phrases = [
        "47 PASS / 3 WARN / 0 FAIL",
        "two route transitions",
        "P003",
        "P032",
        "P045",
        "11 built-in outputs, 50 crops, 0 references, 0 uploads",
        "1,027.652 seconds",
        "Direct paid API/cloud spend: `$0`",
        "built-in product monetary cost unavailable",
        "Human-reviewed: 0; accepted: 0; rights/commercially cleared: 0; exact production bases: 0",
        "Route switching is not isolated as the cause",
        "do not request a new render or edit from these proxies",
    ]
    for phrase in required_phrases:
        check(phrase in text, f"required phrase:{phrase}")

    claims: list[tuple[str, str]] = []
    for line in text.splitlines():
        claims.extend(LINK_HASH_PATTERN.findall(line))
    check(len(claims) == 23, "hash claim count")
    check(all(len(value) == 64 and re.fullmatch(r"[0-9a-f]{64}", value) for _, value in claims), "hash claim syntax")

    if verify_files:
        for value in links:
            path = resolve_link(value)
            check(path.is_file(), f"link exists:{value}")
        for value, expected in claims:
            path = resolve_link(value)
            if path.is_file():
                check(sha256(path) == expected, f"hash claim:{value}")
    return errors


def self_test(text: str) -> tuple[int, int]:
    mutations: list[Callable[[str], str]] = [
        lambda value: value.replace("handoff r7", "handoff r6", 1),
        lambda value: value.replace("47 PASS / 3 WARN / 0 FAIL", "46 PASS / 4 WARN / 0 FAIL", 1),
        lambda value: value.replace("two route transitions", "three route transitions", 1),
        lambda value: value.replace("P003", "P004"),
        lambda value: value.replace("P032", "P031"),
        lambda value: value.replace("P045", "P044"),
        lambda value: value.replace("11 built-in outputs, 50 crops, 0 references, 0 uploads", "11 built-in outputs, 50 crops, 1 reference, 1 upload", 1),
        lambda value: value.replace("1,027.652 seconds", "0 seconds", 1),
        lambda value: value.replace("Direct paid API/cloud spend: `$0`", "Direct paid API/cloud spend: `$1`", 1),
        lambda value: value.replace("built-in product monetary cost unavailable", "built-in product monetary cost $0", 1),
        lambda value: value.replace("Human-reviewed: 0; accepted: 0; rights/commercially cleared: 0; exact production bases: 0", "Human-reviewed: 1; accepted: 1; rights/commercially cleared: 1; exact production bases: 1", 1),
        lambda value: value.replace("Route switching is not isolated as the cause", "Route switching is proven as the cause", 1),
        lambda value: value.replace("do not request a new render or edit from these proxies", "request a new render now", 1),
        lambda value: value.replace("SHA-256 `", "SHA-256 `0", 1),
        lambda value: value.replace("[Lettered phone scroll]", "Lettered phone scroll", 1),
    ]
    caught = 0
    for mutation in mutations:
        candidate = mutation(text)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    text = HANDOFF.read_text(encoding="utf-8")
    errors = validate(text)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(text)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps({
            "status": "PASS" if not errors else "FAIL",
            "errors": errors,
            "links": len(LINK_PATTERN.findall(text)),
            "hash_claims": len(HASH_PATTERN.findall(text)),
            "self_test": f"{caught}/{total}" if args.self_test else None,
        }, sort_keys=True)
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
