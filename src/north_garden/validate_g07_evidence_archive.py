"""Build and validate a deterministic, ignored G07 evidence-restoration archive."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from PIL import Image

from validate_g07_evidence_vault import MANIFEST, ROOT, build_snapshot, canonical_sha256


ARCHIVE = ROOT / "experiments/evidence-vault/g07-evidence-vault-r1.zip"
REPORT = ROOT / "docs/research/evidence/g07-evidence-restoration-rehearsal-r1.json"
INTERNAL_MANIFEST = "vault/g07-local-evidence-vault-manifest-r1.json"


class ArchiveError(RuntimeError):
    """Archive construction or restoration validation failure."""


@dataclass(frozen=True)
class ExpectedEntry:
    path: str
    sha256: str
    bytes: int
    kind: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArchiveError(message)


def safe_archive_path(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts and "\\" not in value and str(path) == value


def expected_entries(manifest: dict[str, Any]) -> list[ExpectedEntry]:
    entries: list[ExpectedEntry] = []
    manifest_bytes = MANIFEST.read_bytes()
    entries.append(ExpectedEntry(INTERNAL_MANIFEST, sha256_bytes(manifest_bytes), len(manifest_bytes), "manifest"))
    for control in manifest["public_controls"]:
        source = ROOT / control["path"]
        entries.append(ExpectedEntry(control["path"], control["sha256"], source.stat().st_size, "public_control"))
    for record in manifest["records"]:
        source = ROOT / record["path"]
        entries.append(ExpectedEntry(record["path"], record["sha256"], source.stat().st_size, "provider_record"))
        if record["candidate"]:
            candidate = record["candidate"]
            entries.append(ExpectedEntry(candidate["path"], candidate["sha256"], candidate["bytes"], "candidate"))
    entries.sort(key=lambda item: item.path)
    require(len(entries) == 38, f"expected 38 archive entries, got {len(entries)}")
    require(len({item.path for item in entries}) == len(entries), "duplicate expected archive path")
    require(all(safe_archive_path(item.path) for item in entries), "unsafe expected archive path")
    return entries


def source_bytes(entry: ExpectedEntry) -> bytes:
    if entry.path == INTERNAL_MANIFEST:
        return MANIFEST.read_bytes()
    return (ROOT / entry.path).read_bytes()


def build_archive_bytes(entries: list[ExpectedEntry]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
        for entry in entries:
            data = source_bytes(entry)
            require(len(data) == entry.bytes, f"source byte count changed: {entry.path}")
            require(sha256_bytes(data) == entry.sha256, f"source hash changed: {entry.path}")
            info = zipfile.ZipInfo(entry.path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return output.getvalue()


def validate_members(members: list[tuple[str, bytes]], entries: list[ExpectedEntry]) -> None:
    names = [name for name, _data in members]
    expected_names = [entry.path for entry in entries]
    require(all(safe_archive_path(name) for name in names), "archive contains an unsafe path")
    require(len(names) == len(set(names)), "archive contains duplicate paths")
    require(sorted(names) == expected_names, "archive inventory differs from exact manifest inventory")
    expected_by_path = {entry.path: entry for entry in entries}
    for name, data in members:
        expected = expected_by_path[name]
        require(len(data) == expected.bytes, f"archive byte count mismatch: {name}")
        require(sha256_bytes(data) == expected.sha256, f"archive hash mismatch: {name}")
        if expected.kind == "provider_record":
            record = json.loads(data)
            require(record.get("record_type") == "RenderRecord", f"invalid provider record type: {name}")
        elif expected.kind == "candidate":
            with Image.open(io.BytesIO(data)) as image:
                image.verify()
        elif expected.kind == "manifest":
            require(json.loads(data) == json.loads(MANIFEST.read_bytes()), "embedded manifest content mismatch")


def archive_members(raw: bytes, entries: list[ExpectedEntry]) -> list[tuple[str, bytes]]:
    with zipfile.ZipFile(io.BytesIO(raw), "r") as archive:
        infos = archive.infolist()
        require(all(info.compress_type == zipfile.ZIP_STORED for info in infos), "archive uses unexpected compression")
        require(all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in infos), "archive timestamps are not fixed")
        require(all(not (info.flag_bits & 0x1) for info in infos), "encrypted archive member is forbidden")
        members = [(info.filename, archive.read(info)) for info in infos]
    validate_members(members, entries)
    return members


def mutation_checks(members: list[tuple[str, bytes]], entries: list[ExpectedEntry]) -> tuple[int, int]:
    record_index = next(i for i, (name, _data) in enumerate(members) if name.endswith(".json") and name.startswith("experiments/records/"))
    mutations: list[list[tuple[str, bytes]]] = []
    mutations.append(members[:-1])
    mutations.append(members + [("unexpected.txt", b"unexpected")])
    corrupt = members.copy()
    name, data = corrupt[record_index]
    corrupt[record_index] = (name, data + b"\n")
    mutations.append(corrupt)
    mutations.append(members + [("../escape.txt", b"escape")])
    mutations.append(members + [members[0]])
    rejected = 0
    for mutation in mutations:
        try:
            validate_members(mutation, entries)
        except (ArchiveError, json.JSONDecodeError):
            rejected += 1
    return rejected, len(mutations)


def content_root(entries: list[ExpectedEntry]) -> str:
    content = [
        {"path": item.path, "sha256": item.sha256, "bytes": item.bytes, "kind": item.kind}
        for item in entries
        if item.kind != "manifest"
    ]
    return canonical_sha256(content)


def build_report(raw: bytes, entries: list[ExpectedEntry], mutation_result: tuple[int, int]) -> dict[str, Any]:
    rejected, total = mutation_result
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    counts = {kind: sum(item.kind == kind for item in entries) for kind in {item.kind for item in entries}}
    return {
        "record_type": "G07EvidenceRestorationRehearsal",
        "schema_version": "1.0",
        "record_id": "g07-evidence-restoration-rehearsal-r1",
        "archive_path": ARCHIVE.relative_to(ROOT).as_posix(),
        "archive_sha256": sha256_bytes(raw),
        "archive_bytes": len(raw),
        "archive_entries": len(entries),
        "entry_counts": counts,
        "content_root_sha256": content_root(entries),
        "source_vault_root_sha256": manifest["integrity"]["vault_root_sha256"],
        "deterministic_repeat_byte_match": True,
        "mutations_rejected": rejected,
        "mutations_total": total,
        "provider_calls": 0,
        "external_uploads": 0,
        "external_cost_usd": "0.000000",
        "human_review_state": "not_yet_performed",
        "accepted_candidates": 0,
        "boundary": "Local ignored restoration artifact only; absence or corruption does not authorize rerender, acceptance, or external transfer.",
    }


def build_or_verify_archive(build: bool) -> tuple[bytes, dict[str, Any]]:
    actual_snapshot = build_snapshot()
    tracked_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(actual_snapshot == tracked_manifest, "source evidence no longer matches tracked vault manifest")
    entries = expected_entries(tracked_manifest)
    if build:
        first = build_archive_bytes(entries)
        second = build_archive_bytes(entries)
        require(first == second, "archive construction is not byte-deterministic")
        ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
        if ARCHIVE.exists():
            require(ARCHIVE.read_bytes() == first, "existing archive differs; refusing to overwrite")
        else:
            ARCHIVE.write_bytes(first)
    require(ARCHIVE.is_file(), "local archive is missing; run with --build")
    raw = ARCHIVE.read_bytes()
    members = archive_members(raw, entries)
    mutation_result = mutation_checks(members, entries)
    require(mutation_result[0] == mutation_result[1], "archive mutation rejection incomplete")
    return raw, build_report(raw, entries, mutation_result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="create the archive if absent; refuse to overwrite different bytes")
    parser.add_argument("--emit-report", type=Path, help="write the deterministic rehearsal report")
    args = parser.parse_args()
    try:
        raw, actual_report = build_or_verify_archive(args.build)
        if args.emit_report:
            output = args.emit_report if args.emit_report.is_absolute() else ROOT / args.emit_report
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(actual_report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
            print(f"wrote {output.relative_to(ROOT).as_posix()}")
        else:
            expected_report = json.loads(REPORT.read_text(encoding="utf-8"))
            require(expected_report == actual_report, "tracked restoration report differs from local archive")
    except (ArchiveError, FileNotFoundError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings")
    print(f"38/38 archive entries verified; {len(raw)} bytes; SHA-256 {sha256_bytes(raw)}")
    print("5/5 missing/extra/corrupt/path-escape/duplicate mutations rejected")
    print("0 provider calls, 0 uploads, $0 new cost; candidates remain unaccepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
