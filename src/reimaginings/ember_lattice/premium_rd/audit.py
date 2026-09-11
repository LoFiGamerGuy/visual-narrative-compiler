from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from .core import PremiumRDError, read_json, sha256_file
from .model import validate_bundle


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        for field in ("href", "src"):
            if values.get(field):
                self.links.append((field, values[field] or ""))


def _resolve_link(source: Path, raw: str) -> tuple[Path | None, str]:
    split = urlsplit(raw)
    if split.scheme in {"http", "https", "mailto", "data"} or split.netloc:
        return None, split.fragment
    path = source if not split.path else (source.parent / Path(unquote(split.path))).resolve()
    return path, split.fragment


def audit_links(site_root: Path) -> dict[str, object]:
    errors: list[str] = []
    checked = 0
    html_ids: dict[Path, set[str]] = {}
    html_links: dict[Path, list[tuple[str, str]]] = {}
    html_files = sorted(site_root.rglob("*.html"))
    for source in html_files:
        parser = _LinkParser()
        try:
            parser.feed(source.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"cannot parse HTML {source}: {exc}")
            continue
        html_ids[source.resolve()] = parser.ids
        html_links[source] = parser.links
    for source, links in html_links.items():
        for field, raw in links:
            checked += 1
            target, fragment = _resolve_link(source.resolve(), raw)
            if target is None:
                continue
            if not target.exists():
                errors.append(f"broken {field} in {source.relative_to(site_root)}: {raw}")
                continue
            if fragment and target.suffix.lower() in {".html", ".htm"}:
                ids = html_ids.get(target.resolve())
                if ids is None:
                    parser = _LinkParser()
                    parser.feed(target.read_text(encoding="utf-8"))
                    ids = parser.ids
                    html_ids[target.resolve()] = ids
                if fragment not in ids:
                    errors.append(f"missing fragment #{fragment} in {target}")
    svg_files = sorted(site_root.rglob("*.svg"))
    for source in svg_files:
        try:
            root = ElementTree.parse(source).getroot()
        except (OSError, ElementTree.ParseError) as exc:
            errors.append(f"cannot parse SVG {source.relative_to(site_root)}: {exc}")
            continue
        for element in root.iter():
            raw = element.attrib.get("href") or element.attrib.get("{http://www.w3.org/1999/xlink}href")
            if not raw or raw.startswith("#") or raw.startswith("data:"):
                continue
            checked += 1
            target, _ = _resolve_link(source.resolve(), raw)
            if target is not None and not target.is_file():
                errors.append(f"broken SVG asset in {source.relative_to(site_root)}: {raw}")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "html_files": len(html_files), "svg_files": len(svg_files), "links_checked": checked}


def reconcile_site(site_root: Path) -> dict[str, object]:
    errors: list[str] = []
    ledger_path = site_root / "build-ledger.json"
    if not ledger_path.is_file():
        return {"status": "FAIL", "errors": ["missing build-ledger.json"], "files_checked": 0}
    try:
        ledger = read_json(ledger_path)
    except PremiumRDError as exc:
        return {"status": "FAIL", "errors": [str(exc)], "files_checked": 0}
    if ledger.get("schema") != "PremiumBuildLedger/1.0" or not isinstance(ledger.get("files"), list):
        return {"status": "FAIL", "errors": ["invalid PremiumBuildLedger/1.0"], "files_checked": 0}
    paths: set[str] = set()
    for index, row in enumerate(ledger["files"]):
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            errors.append(f"files[{index}] is invalid")
            continue
        relative = row["path"]
        if relative in paths:
            errors.append(f"duplicate ledger path {relative}")
        paths.add(relative)
        target = (site_root / relative).resolve()
        try:
            target.relative_to(site_root.resolve())
        except ValueError:
            errors.append(f"ledger path escapes site root: {relative}")
            continue
        if not target.is_file():
            errors.append(f"missing generated file {relative}")
        else:
            if sha256_file(target) != row.get("sha256"):
                errors.append(f"generated hash mismatch {relative}")
            if target.stat().st_size != row.get("bytes"):
                errors.append(f"generated size mismatch {relative}")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "files_checked": len(paths)}


def parse_all_json(*roots: Path) -> dict[str, object]:
    errors: list[str] = []
    files: set[Path] = set()
    for root in roots:
        if root.is_file() and root.suffix.lower() == ".json":
            files.add(root)
        elif root.is_dir():
            files.update(root.rglob("*.json"))
    for path in sorted(files):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"cannot parse JSON {path}: {exc}")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "files_checked": len(files)}


def audit_bundle(manifest: dict, rubric: dict, content_root: Path, site_root: Path) -> dict[str, object]:
    validation = validate_bundle(manifest, rubric, content_root, verify_assets=True)
    links = audit_links(site_root)
    reconciliation = reconcile_site(site_root)
    json_report = parse_all_json(site_root)
    statuses = [validation["status"], links["status"], reconciliation["status"], json_report["status"]]
    unresolved = validation.get("manifest", {}).get("counts", {}).get("unresolved_hard_failures", 0)
    quality_gate = "PASS" if all(value == "PASS" for value in statuses) and unresolved == 0 else "FAIL"
    return {
        "schema": "PremiumAuditReport/1.0",
        "status": quality_gate,
        "quality_gate": quality_gate,
        "validation": validation,
        "link_integrity": links,
        "output_reconciliation": reconciliation,
        "json_integrity": json_report,
    }
