from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .audit import audit_bundle
from .author import author_template
from .core import PremiumRDError, read_json, write_json
from .model import rubric_summary, validate_bundle
from .render import build_site


def _paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    return Path(args.manifest).resolve(), Path(args.rubric).resolve(), Path(args.content_root).resolve()


def _emit(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def command_author(args: argparse.Namespace) -> int:
    result = author_template(Path(args.output_dir).resolve(), args.panel_count)
    _emit({"status": "PASS", "note": "Draft placeholders and zero scores require authoring before production use.", **result})
    return 0


def command_validate(args: argparse.Namespace) -> int:
    manifest_path, rubric_path, content_root = _paths(args)
    report = validate_bundle(read_json(manifest_path), read_json(rubric_path), content_root, verify_assets=not args.no_assets)
    _emit(report)
    return 0 if report["status"] == "PASS" else 1


def command_build(args: argparse.Namespace) -> int:
    manifest_path, rubric_path, content_root = _paths(args)
    manifest, rubric = read_json(manifest_path), read_json(rubric_path)
    report = validate_bundle(manifest, rubric, content_root, verify_assets=True)
    if report["status"] != "PASS":
        _emit(report)
        return 1
    result = build_site(manifest, rubric, content_root, Path(args.output_dir).resolve())
    _emit(result)
    return 0


def command_audit(args: argparse.Namespace) -> int:
    manifest_path, rubric_path, content_root = _paths(args)
    result = audit_bundle(read_json(manifest_path), read_json(rubric_path), content_root, Path(args.site_root).resolve())
    if args.report:
        write_json(Path(args.report).resolve(), result)
    _emit(result)
    return 0 if result["status"] == "PASS" else 1


def command_all(args: argparse.Namespace) -> int:
    manifest_path, rubric_path, content_root = _paths(args)
    manifest, rubric = read_json(manifest_path), read_json(rubric_path)
    validation = validate_bundle(manifest, rubric, content_root, verify_assets=True)
    if validation["status"] != "PASS":
        _emit(validation)
        return 1
    output = Path(args.output_dir).resolve()
    build = build_site(manifest, rubric, content_root, output)
    audit = audit_bundle(manifest, rubric, content_root, output)
    write_json(output / "audit-report.json", audit)
    result = {"status": audit["status"], "build": build, "audit": audit, "rubric_summary": rubric_summary(rubric, manifest)}
    _emit(result)
    return 0 if result["status"] == "PASS" else 1


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="premium-rd", description="Deterministic Ember Lattice premium R&D toolchain")
    subparsers = parser.add_subparsers(dest="command", required=True)
    author = subparsers.add_parser("author", help="write a deterministic 24+ panel manifest/rubric starter")
    author.add_argument("--output-dir", required=True)
    author.add_argument("--panel-count", type=int, default=48)
    author.set_defaults(func=command_author)
    for name in ("validate", "build", "audit", "all"):
        command = subparsers.add_parser(name)
        command.add_argument("--manifest", required=True)
        command.add_argument("--rubric", required=True)
        command.add_argument("--content-root", required=True)
        if name == "validate":
            command.add_argument("--no-assets", action="store_true", help="validate structure without reading asset files")
            command.set_defaults(func=command_validate)
        elif name == "build":
            command.add_argument("--output-dir", required=True)
            command.set_defaults(func=command_build)
        elif name == "audit":
            command.add_argument("--site-root", required=True)
            command.add_argument("--report")
            command.set_defaults(func=command_audit)
        else:
            command.add_argument("--output-dir", required=True)
            command.set_defaults(func=command_all)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = make_parser().parse_args(argv)
        return int(args.func(args))
    except (PremiumRDError, OSError, ValueError) as exc:
        _emit({"status": "FAIL", "errors": [str(exc)]})
        return 2


if __name__ == "__main__":
    sys.exit(main())
