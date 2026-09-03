"""Fail closed on exact content bindings for every CH05 handoff r7 link."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "docs/research/ch05-complete-chapter-review-handoff-r7.md"
EVIDENCE = (
    ROOT
    / "docs/research/evidence/ch05-complete-chapter-review-handoff-r7-link-integrity-r1.json"
)
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CLAIM_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)[^\[]*?SHA-256 `([0-9a-f]{64})`")
EXPECTED_SUMMARY = {
    "unique_links": 41,
    "inline_hash_claims": 23,
    "supplemental_hash_bindings": 18,
    "total_exact_hash_bindings": 41,
    "png_review_artifacts": 31,
    "json_evidence_or_manifests": 10,
    "ignored_local_artifacts": 32,
    "tracked_safe_sources": 9,
    "missing": 0,
    "hash_mismatches": 0,
    "generated_pixels_modified": 0,
    "accepted": 0,
    "rights_cleared": 0,
    "commercially_cleared": 0,
    "exact_production_base": 0,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_result(*arguments: str) -> int:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, capture_output=True, check=False
    ).returncode


def resolve_link(value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else HANDOFF.parent / path).resolve()


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(
        document.get("record_type") == "CH05CompleteChapterReviewHandoffLinkIntegrity",
        "record_type",
    )
    check(
        document.get("record_id")
        == "ng-ch05-complete-chapter-review-handoff-r7-link-integrity-r1",
        "record_id",
    )
    check(document.get("state") == "PASS_ALL_LINKS_CONTENT_BOUND", "state")
    check(document.get("medium") == "comic", "medium")
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "planning boundary",
    )
    check(
        document.get("handoff")
        == {
            "path": HANDOFF.relative_to(ROOT).as_posix(),
            "sha256": sha256(HANDOFF),
            "bytes": HANDOFF.stat().st_size,
        },
        "handoff binding",
    )
    check(document.get("summary") == EXPECTED_SUMMARY, "summary")

    text = HANDOFF.read_text(encoding="utf-8")
    links = LINK_PATTERN.findall(text)
    claims = dict(CLAIM_PATTERN.findall(text))
    check(len(links) == 41, "handoff link count")
    check(len({target for _, target in links}) == 41, "handoff link uniqueness")
    check(len(claims) == 23, "handoff inline claim count")
    bindings = document.get("bindings", [])
    check(len(bindings) == 41, "binding count")
    for index, (label, target) in enumerate(links, 1):
        if index > len(bindings):
            break
        item = bindings[index - 1]
        prefix = f"binding:{index}"
        path = resolve_link(target)
        check(path.is_relative_to(ROOT), f"{prefix}:workspace boundary")
        relative = (
            path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else ""
        )
        claimed = claims.get(target)
        check(item.get("link_index") == index, f"{prefix}:index")
        check(item.get("label") == label, f"{prefix}:label")
        check(item.get("handoff_target") == target, f"{prefix}:target")
        check(
            item.get("repository_relative_path") == relative, f"{prefix}:relative path"
        )
        check(item.get("inline_hash_claim") == claimed, f"{prefix}:inline claim")
        check(
            item.get("hash_binding_origin")
            == ("HANDOFF_INLINE" if claimed else "INTEGRITY_SUPPLEMENT"),
            f"{prefix}:binding origin",
        )
        check(
            isinstance(item.get("sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None
            and item["sha256"] != "0" * 64,
            f"{prefix}:hash syntax",
        )
        check(
            isinstance(item.get("bytes"), int) and item["bytes"] > 0,
            f"{prefix}:bytes",
        )
        expected_state = (
            "IGNORED_LOCAL_REVIEW_ARTIFACT"
            if relative.startswith("experiments/")
            else "TRACKED_SAFE_SOURCE"
        )
        check(item.get("repository_state") == expected_state, f"{prefix}:state")
        if verify_files and expected_state == "IGNORED_LOCAL_REVIEW_ARTIFACT":
            check(git_result("check-ignore", "-q", relative) == 0, f"{prefix}:ignored")
            check(
                git_result("ls-files", "--error-unmatch", relative) != 0,
                f"{prefix}:untracked",
            )
        elif verify_files:
            check(
                git_result("ls-files", "--error-unmatch", relative) == 0,
                f"{prefix}:tracked",
            )
        if not verify_files:
            continue
        check(path.is_file(), f"{prefix}:exists")
        if not path.is_file():
            continue
        check(sha256(path) == item.get("sha256"), f"{prefix}:hash")
        check(path.stat().st_size == item.get("bytes"), f"{prefix}:byte binding")
        if claimed is not None:
            check(sha256(path) == claimed, f"{prefix}:inline hash")
        if path.suffix.lower() == ".png":
            check(item.get("media_type") == "image/png", f"{prefix}:media type")
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    check(image.format == "PNG", f"{prefix}:format")
                    check(
                        [image.width, image.height]
                        == [item.get("width"), item.get("height")],
                        f"{prefix}:dimensions",
                    )
            except (OSError, SyntaxError) as error:
                errors.append(f"{prefix}:invalid PNG:{error}")
        elif path.suffix.lower() == ".json":
            check(item.get("media_type") == "application/json", f"{prefix}:media type")
            source = json.loads(path.read_text(encoding="utf-8"))
            check(
                item.get("record_type") == source.get("record_type"),
                f"{prefix}:record type",
            )
            check(
                item.get("width") is None and item.get("height") is None,
                f"{prefix}:null dimensions",
            )
        else:
            errors.append(f"{prefix}:unsupported extension")

    boundary = document.get("boundary", "")
    for phrase in (
        "Read-only",
        "no generated pixels modified",
        "accepted",
        "rights-cleared",
        "commercially cleared",
        "exact production base",
    ):
        check(phrase in boundary, f"boundary:{phrase}")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int, list[int]]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "FAIL"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("animation_shot_plan", {}),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["handoff"].__setitem__("sha256", "0" * 64),
        lambda value: value["summary"].__setitem__("unique_links", 40),
        lambda value: value["summary"].__setitem__("inline_hash_claims", 22),
        lambda value: value["summary"].__setitem__("supplemental_hash_bindings", 17),
        lambda value: value["summary"].__setitem__("total_exact_hash_bindings", 40),
        lambda value: value["summary"].__setitem__("missing", 1),
        lambda value: value["summary"].__setitem__("hash_mismatches", 1),
        lambda value: value["summary"].__setitem__("generated_pixels_modified", 1),
        lambda value: value["summary"].__setitem__("accepted", 1),
        lambda value: value["summary"].__setitem__("rights_cleared", 1),
        lambda value: value["summary"].__setitem__("commercially_cleared", 1),
        lambda value: value["summary"].__setitem__("exact_production_base", 1),
        lambda value: value["bindings"].pop(),
        lambda value: value["bindings"][0].__setitem__("link_index", 2),
        lambda value: value["bindings"][0].__setitem__(
            "handoff_target", "C:/wrong.png"
        ),
        lambda value: value["bindings"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["bindings"][0].__setitem__("bytes", 0),
        lambda value: value["bindings"][0].__setitem__(
            "repository_state", "TRACKED_SAFE_SOURCE"
        ),
        lambda value: value["bindings"][0].__setitem__("inline_hash_claim", None),
        lambda value: value.__setitem__("boundary", "write pixels and accept"),
    ]
    caught = 0
    missed: list[int] = []
    for index, mutation in enumerate(mutations, 1):
        candidate = copy.deepcopy(document)
        mutation(candidate)
        if validate(candidate, verify_files=False):
            caught += 1
        else:
            missed.append(index)
    return caught, len(mutations), missed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    missed: list[int] = []
    if args.self_test:
        caught, total, missed = self_test(document)
        if caught != total:
            errors.append(f"self-test:{caught}/{total}:missed={missed}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "links": len(document.get("bindings", [])),
                "inline_hash_claims": document.get("summary", {}).get(
                    "inline_hash_claims"
                ),
                "supplemental_hash_bindings": document.get("summary", {}).get(
                    "supplemental_hash_bindings"
                ),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
