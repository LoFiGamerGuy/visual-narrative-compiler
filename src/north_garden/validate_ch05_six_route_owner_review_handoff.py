"""Validate the CH05 six-route owner-review handoff and ignored artifacts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from compile_ch05_six_route_owner_review_handoff import (
    ARTIFACT_SPECS,
    EVIDENCE,
    MARKDOWN,
    REVIEW_QUESTIONS,
    ROOT,
)
from PIL import Image

EXPECTED_SUMMARY = {
    "artifact_count": 51,
    "section_count": 7,
    "six_route_comparison_sheets": 5,
    "reduced_palette_packet_artifacts": 9,
    "flat_route_packet_artifacts": 9,
    "matched_ablation_comparisons": 4,
    "semantic_pass_hybrid_artifacts": 8,
    "selected_sequence_cadence_packet_artifacts": 10,
    "strongest_reduced_palette_candidates": 6,
    "review_questions": 7,
    "owner_dispositions": 0,
    "accepted": 0,
    "rights_cleared": 0,
    "commercially_cleared": 0,
    "exact_production_base": 0,
}
EXPECTED_STRONGEST = ["P010", "P014", "P035", "P040", "P041", "P046"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_result(*args: str) -> int:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True
    ).returncode


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(
        document.get("record_type") == "CH05SixRouteOwnerReviewHandoff", "record_type"
    )
    check(document.get("schema_version") == "1.0", "schema_version")
    check(
        document.get("record_id") == "ng-ch05-six-route-owner-review-handoff-r1",
        "record_id",
    )
    check(
        document.get("state") == "LOCAL_REVIEW_INDEX_READY_OWNER_DISPOSITIONS_PENDING",
        "state",
    )
    check(document.get("medium") == "comic", "medium")
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "planning boundary",
    )
    check(document.get("summary") == EXPECTED_SUMMARY, "summary")
    check(
        document.get("strongest_reduced_palette_panel_ids") == EXPECTED_STRONGEST,
        "strongest panel ids",
    )
    check(document.get("review_questions") == REVIEW_QUESTIONS, "review questions")
    boundary = document.get("boundary", "")
    for phrase in (
        "Owner-review navigation only",
        "no acceptance",
        "rights clearance",
        "commercial clearance",
        "exact production-base selection",
        "AnimationShotPlan",
        "E-Conte",
    ):
        check(phrase in boundary, f"boundary:{phrase}")

    expected_sections = list(dict.fromkeys(spec[1] for spec in ARTIFACT_SPECS))
    check(document.get("sections") == expected_sections, "section order")
    artifacts = document.get("artifacts", [])
    check(len(artifacts) == len(ARTIFACT_SPECS), "artifact count")

    for index, spec in enumerate(ARTIFACT_SPECS):
        if index >= len(artifacts):
            break
        artifact_id, section, title, relative = spec
        item = artifacts[index]
        prefix = f"artifact:{artifact_id}"
        path = ROOT / relative
        check(item.get("id") == artifact_id, f"{prefix}:id")
        check(item.get("section") == section, f"{prefix}:section")
        check(item.get("title") == title, f"{prefix}:title")
        check(item.get("path") == relative, f"{prefix}:path")
        check(
            item.get("absolute_path") == path.resolve().as_posix(),
            f"{prefix}:absolute_path",
        )
        check(
            item.get("repository_state") == "IGNORED_LOCAL_REVIEW_ARTIFACT",
            f"{prefix}:repository_state",
        )
        check(
            isinstance(item.get("sha256"), str)
            and len(item["sha256"]) == 64
            and item["sha256"] != "0" * 64,
            f"{prefix}:sha256 shape",
        )
        check(
            all(
                isinstance(item.get(field), int) and item[field] > 0
                for field in ("width", "height", "bytes")
            ),
            f"{prefix}:numeric metadata",
        )
        if not verify_files:
            continue
        check(path.is_file(), f"{prefix}:exists")
        if path.is_file():
            check(sha256(path) == item.get("sha256"), f"{prefix}:hash")
            check(path.stat().st_size == item.get("bytes"), f"{prefix}:bytes")
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
        check(git_result("check-ignore", "-q", relative) == 0, f"{prefix}:ignored")
        check(
            git_result("ls-files", "--error-unmatch", relative) != 0,
            f"{prefix}:tracked",
        )

    handoff = document.get("handoff", {})
    check(
        handoff.get("path") == MARKDOWN.relative_to(ROOT).as_posix(),
        "handoff path",
    )
    check(MARKDOWN.is_file(), "handoff exists")
    if MARKDOWN.is_file():
        markdown = MARKDOWN.read_text(encoding="utf-8")
        check(handoff.get("sha256") == sha256(MARKDOWN), "handoff hash")
        check(handoff.get("bytes") == MARKDOWN.stat().st_size, "handoff bytes")
        for _, _, title, relative in ARTIFACT_SPECS:
            check(
                f"[{title}](../../{relative})" in markdown, f"markdown link:{relative}"
            )
        for item in artifacts:
            check(
                f"{item.get('width')}×{item.get('height')}" in markdown,
                f"markdown dimensions:{item.get('id')}",
            )
            check(
                f"`{item.get('sha256')}`" in markdown, f"markdown hash:{item.get('id')}"
            )
        for index, question in enumerate(REVIEW_QUESTIONS, 1):
            check(
                f"{index}. {question}" in markdown, f"markdown review question:{index}"
            )
        for phrase in (
            "Nothing here is accepted",
            "rights-cleared",
            "commercially cleared",
            "exact production base",
        ):
            check(phrase in markdown, f"markdown boundary:{phrase}")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("record_type", "Wrong"),
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("animation_shot_plan", {}),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["summary"].__setitem__("artifact_count", 50),
        lambda value: value["summary"].__setitem__("accepted", 1),
        lambda value: value["summary"].__setitem__("rights_cleared", 1),
        lambda value: value["summary"].__setitem__("commercially_cleared", 1),
        lambda value: value["summary"].__setitem__("exact_production_base", 1),
        lambda value: value["artifacts"].pop(),
        lambda value: value["artifacts"][0].__setitem__("path", "wrong.png"),
        lambda value: value["artifacts"][0].__setitem__(
            "absolute_path", "C:/wrong.png"
        ),
        lambda value: value["artifacts"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["artifacts"][0].__setitem__("width", 1),
        lambda value: value["artifacts"][0].__setitem__("repository_state", "TRACKED"),
        lambda value: value["handoff"].__setitem__("sha256", "0" * 64),
        lambda value: value.__setitem__("review_questions", []),
        lambda value: value.__setitem__("strongest_reduced_palette_panel_ids", []),
        lambda value: value.__setitem__("boundary", "accepted"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test:{caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "artifacts_checked": len(document.get("artifacts", [])),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
