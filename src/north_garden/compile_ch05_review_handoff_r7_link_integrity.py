"""Bind every CH05 review-handoff r7 link to exact local content."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "docs/research/ch05-complete-chapter-review-handoff-r7.md"
OUTPUT = (
    ROOT
    / "docs/research/evidence/ch05-complete-chapter-review-handoff-r7-link-integrity-r1.json"
)
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CLAIM_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)[^\[]*?SHA-256 `([0-9a-f]{64})`")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_result(*arguments: str) -> int:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, capture_output=True, check=False
    ).returncode


def resolve_link(value: str) -> Path:
    path = Path(value)
    resolved = (path if path.is_absolute() else HANDOFF.parent / path).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f"handoff link escapes workspace: {value}")
    return resolved


def binding(
    index: int, label: str, target: str, claims: dict[str, str]
) -> dict[str, Any]:
    path = resolve_link(target)
    if not path.is_file():
        raise FileNotFoundError(target)
    relative = path.relative_to(ROOT).as_posix()
    tracked = git_result("ls-files", "--error-unmatch", relative) == 0
    ignored = git_result("check-ignore", "-q", relative) == 0
    if tracked == ignored:
        raise ValueError(f"expected exactly one tracked/ignored state: {relative}")
    actual = sha256(path)
    claimed = claims.get(target)
    if claimed is not None and claimed != actual:
        raise ValueError(f"inline hash mismatch: {relative}")
    result: dict[str, Any] = {
        "link_index": index,
        "label": label,
        "handoff_target": target,
        "repository_relative_path": relative,
        "sha256": actual,
        "bytes": path.stat().st_size,
        "inline_hash_claim": claimed,
        "hash_binding_origin": "HANDOFF_INLINE" if claimed else "INTEGRITY_SUPPLEMENT",
        "repository_state": "TRACKED_SAFE_SOURCE"
        if tracked
        else "IGNORED_LOCAL_REVIEW_ARTIFACT",
    }
    if path.suffix.lower() == ".png":
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValueError(f"not PNG: {relative}")
            result.update(
                {
                    "media_type": "image/png",
                    "width": image.width,
                    "height": image.height,
                }
            )
    elif path.suffix.lower() == ".json":
        document = json.loads(path.read_text(encoding="utf-8"))
        result.update(
            {
                "media_type": "application/json",
                "record_type": document.get("record_type"),
                "width": None,
                "height": None,
            }
        )
    else:
        raise ValueError(f"unsupported linked file: {relative}")
    return result


def main() -> int:
    text = HANDOFF.read_text(encoding="utf-8")
    links = LINK_PATTERN.findall(text)
    claims = dict(CLAIM_PATTERN.findall(text))
    if len(links) != 41 or len({target for _, target in links}) != 41:
        raise ValueError("handoff link topology changed")
    if len(claims) != 23:
        raise ValueError("handoff inline hash-claim count changed")
    bindings = [
        binding(index, label, target, claims)
        for index, (label, target) in enumerate(links, 1)
    ]
    evidence = {
        "record_type": "CH05CompleteChapterReviewHandoffLinkIntegrity",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-review-handoff-r7-link-integrity-r1",
        "state": "PASS_ALL_LINKS_CONTENT_BOUND",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "handoff": {
            "path": HANDOFF.relative_to(ROOT).as_posix(),
            "sha256": sha256(HANDOFF),
            "bytes": HANDOFF.stat().st_size,
        },
        "summary": {
            "unique_links": len(bindings),
            "inline_hash_claims": sum(
                row["inline_hash_claim"] is not None for row in bindings
            ),
            "supplemental_hash_bindings": sum(
                row["inline_hash_claim"] is None for row in bindings
            ),
            "total_exact_hash_bindings": len(bindings),
            "png_review_artifacts": sum(
                row["media_type"] == "image/png" for row in bindings
            ),
            "json_evidence_or_manifests": sum(
                row["media_type"] == "application/json" for row in bindings
            ),
            "ignored_local_artifacts": sum(
                row["repository_state"] == "IGNORED_LOCAL_REVIEW_ARTIFACT"
                for row in bindings
            ),
            "tracked_safe_sources": sum(
                row["repository_state"] == "TRACKED_SAFE_SOURCE" for row in bindings
            ),
            "missing": 0,
            "hash_mismatches": 0,
            "generated_pixels_modified": 0,
            "accepted": 0,
            "rights_cleared": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "bindings": bindings,
        "limitations": [
            "The handoff uses workspace-absolute links; repository-relative bindings preserve portable identity but do not rewrite navigation.",
            "Exact content binding proves integrity and availability, not visual acceptance, rights, commercial clearance, or exact-base suitability.",
        ],
        "boundary": "Read-only link-integrity supplement; no generated pixels modified, copied, tracked, accepted, rights-cleared, commercially cleared, or selected as an exact production base.",
    }
    OUTPUT.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "links": len(bindings),
                "inline": evidence["summary"]["inline_hash_claims"],
                "supplemental": evidence["summary"]["supplemental_hash_bindings"],
                "sha256": sha256(OUTPUT),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
