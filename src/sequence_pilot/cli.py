"""Standard-library pilot ledger. Visual judgments are supplied, never inferred."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import sys
import zlib
from contextlib import contextmanager
from datetime import datetime, timezone


class PilotError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise PilotError(f"Cannot read JSON {path}: {exc}") from exc


def bounded_text(value, maximum, name):
    if not isinstance(value, str) or len(value) > maximum or "\x00" in value:
        raise PilotError(f"{name} must be text of at most {maximum} characters without NUL")
    return value


def bounded_number(value, low, high, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high or not math.isfinite(value):
        raise PilotError(f"{name} must be a finite number between {low} and {high}")
    return value


def draft_shapes(items, region=False):
    if not isinstance(items, list) or len(items) > 100:
        raise PilotError("Draft shapes must be an array with at most 100 entries")
    result = []
    for item in items:
        if not isinstance(item, dict):
            raise PilotError("Each draft shape must be an object")
        row = {"id": bounded_text(item.get("id"), 120, "Shape ID")}
        if not row["id"]:
            raise PilotError("Shape ID cannot be empty")
        for key in ("x", "y", "w", "h"):
            row[key] = bounded_number(item.get(key), .02 if key in ("w", "h") else 0, 1, key)
        if row["x"] + row["w"] > 1 + 1e-12 or row["y"] + row["h"] > 1 + 1e-12:
            raise PilotError("Draft shape extends outside the planned canvas")
        if region:
            row["label"] = bounded_text(item.get("label"), 160, "Region label")
        else:
            row.update(text=bounded_text(item.get("text"), 4000, "Lettering text"),
                       speaker=bounded_text(item.get("speaker", ""), 100, "Speaker"),
                       font_size=bounded_number(item.get("font_size"), 6, 96, "Font size"))
            if item.get("kind") not in {"dialogue", "ui", "sfx"} or item.get("shape") not in {"rounded", "ellipse"}:
                raise PilotError("Unknown lettering kind or shape")
            row.update(kind=item["kind"], shape=item["shape"], tail=None)
            if item.get("tail") is not None:
                if not isinstance(item["tail"], dict):
                    raise PilotError("Tail must be null or an object")
                row["tail"] = {key: bounded_number(item["tail"].get(key), 0, 1, "Tail " + key) for key in ("x", "y")}
        result.append(row)
    if len({r["id"] for r in result}) != len(result):
        raise PilotError("Duplicate shape IDs")
    return result


def no_symlinks(path):
    path = Path(os.path.abspath(path))
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise PilotError(f"Symlink path is not allowed: {part}")
    return path


def image_info(data):
    """Verify PNG chunk integrity or JPEG segment structure; never infer image content."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        pos, size, have_idat, have_end = 8, None, False, False
        compressed = []
        while pos + 12 <= len(data):
            length = struct.unpack(">I", data[pos:pos + 4])[0]
            kind = data[pos + 4:pos + 8]
            end = pos + 12 + length
            if end > len(data):
                raise PilotError("Truncated PNG chunk")
            chunk = data[pos + 8:pos + 8 + length]
            if zlib.crc32(kind + chunk) & 0xffffffff != struct.unpack(">I", data[end - 4:end])[0]:
                raise PilotError("PNG CRC mismatch")
            if pos == 8 and kind != b"IHDR":
                raise PilotError("PNG must begin with IHDR")
            if kind == b"IHDR":
                if size or length != 13:
                    raise PilotError("Invalid PNG header")
                size = struct.unpack(">II", chunk[:8])
                depth, color, compression, filtering, interlace = chunk[8:]
                depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
                if color not in depths or depth not in depths[color] or compression or filtering or interlace not in (0, 1):
                    raise PilotError("Invalid PNG color/compression format")
            if kind == b"IDAT":
                have_idat = have_idat or bool(chunk)
                compressed.append(chunk)
            if kind == b"IEND":
                have_end = length == 0 and end == len(data)
                break
            pos = end
        if not size or not have_idat or not have_end:
            raise PilotError("Incomplete PNG")
        try:
            decoder = zlib.decompressobj()
            decoded = decoder.decompress(b"".join(compressed), 256_000_001)
            if not decoder.eof or decoder.unused_data or len(decoded) > 256_000_000:
                raise PilotError("PNG data invalid or exceeds decoded size limit")
            if interlace == 0:
                channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
                stride = (size[0] * channels * depth + 7) // 8 + 1
                if len(decoded) != stride * size[1] or any(decoded[offset] > 4 for offset in range(0, len(decoded), stride)):
                    raise PilotError("PNG scanline data is invalid")
        except zlib.error as exc:
            raise PilotError(f"PNG compressed data is invalid: {exc}") from exc
        ext = ".png"
    elif data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"):
        pos, size, have_scan = 2, None, False
        while pos < len(data) - 2:
            if data[pos] != 255:
                raise PilotError("Malformed JPEG segment")
            while pos < len(data) and data[pos] == 255:
                pos += 1
            if pos >= len(data):
                break
            marker = data[pos]
            pos += 1
            if marker in (0xd8, 0xd9):
                break
            if pos + 2 > len(data):
                break
            length = int.from_bytes(data[pos:pos + 2], "big")
            if length < 2 or pos + length > len(data):
                raise PilotError("Truncated JPEG segment")
            if marker in (0xc0, 0xc1, 0xc2):
                if length < 8:
                    raise PilotError("Invalid JPEG frame")
                h, w = struct.unpack(">HH", data[pos + 3:pos + 7])
                size = (w, h)
            if marker == 0xda:
                have_scan = pos + length < len(data) - 2
                break
            pos += length
        if not size or not have_scan:
            raise PilotError("JPEG frame or image scan missing")
        ext = ".jpg"
    else:
        raise PilotError("Only structurally valid PNG or JPEG raster files are accepted")
    if min(size) < 1 or max(size) > 32768 or size[0] * size[1] > 100_000_000:
        raise PilotError("Image dimensions are invalid or exceed the 100 megapixel limit")
    # If available, strengthen validation without making Pillow a dependency.
    try:
        from PIL import Image
    except ImportError:
        pass
    else:
        from io import BytesIO
        try:
            with Image.open(BytesIO(data)) as im:
                im.verify()
        except Exception as exc:
            raise PilotError(f"Image decoder rejected the file: {exc}") from exc
    return {"width": size[0], "height": size[1], "extension": ext}


class Workspace:
    def __init__(self, root):
        self.root = no_symlinks(root)
        if not self.root.is_dir():
            raise PilotError("Workspace must already exist and contain plan.json")
        self.plan_path = self.path("plan.json")
        self.plan = read_json(self.plan_path)
        if self.plan.get("schema") != "NeutralPilotPlan/2":
            raise PilotError("Expected NeutralPilotPlan/2 plan")
        self.plan_sha = digest(self.plan_path.read_bytes())
        self.panels = {f"P{p['panel']:02d}": p for p in self.plan["panels"]}
        if len(self.panels) != len(self.plan["panels"]):
            raise PilotError("Duplicate panel IDs")
        self.routes = {r["id"] for r in self.plan["routes"]}
        self.events = []
        self.errors = []
        self.load()

    def path(self, value, must_exist=True):
        p = Path(value)
        if ".." in p.parts:
            raise PilotError("Parent traversal is not allowed")
        if not p.is_absolute():
            p = self.root / p
        p = no_symlinks(p)
        if not p.is_relative_to(self.root):
            raise PilotError("Input/output path must remain inside the workspace")
        if must_exist and not p.is_file():
            raise PilotError(f"Expected a regular file: {p}")
        return p

    def relative(self, p):
        return str(p.relative_to(self.root))

    def load(self):
        ledger = self.path("events.jsonl", False)
        if not ledger.exists():
            return
        previous = None
        ledger_text = ledger.read_text(encoding="utf-8")
        if ledger_text and not ledger_text.endswith("\n"):
            self.errors.append("Ledger has an incomplete final line")
        for line in ledger_text.splitlines():
            try:
                event = json.loads(line)
                claimed = event.pop("sha256")
                if event["seq"] != len(self.events) + 1 or event["previous_sha256"] != previous or digest(canonical(event)) != claimed:
                    raise PilotError("Event chain mismatch")
                event["sha256"] = claimed
                previous = claimed
                self.events.append(event)
            except (ValueError, KeyError, TypeError) as exc:
                self.errors.append(f"Ledger integrity failure: {exc}")
                break
        for event in self.events:
            if event.get("plan_sha256") != self.plan_sha:
                self.errors.append("Frozen plan changed; existing evidence is stale")
                break
    def material_errors(self):
        errors = []
        try:
            if digest(self.path("plan.json").read_bytes()) != self.plan_sha:
                errors.append("Frozen plan changed during this operation")
            marker = self.path("plan.sha256", False)
            if marker.exists() and marker.read_text().strip().split()[0] != self.plan_sha:
                errors.append("Plan does not match its frozen plan.sha256 marker")
        except (PilotError, OSError, IndexError) as exc:
            errors.append(str(exc))
        for attempt in self.records("reserved"):
            for ref in attempt["references"]:
                try:
                    if digest(self.path(ref["path"]).read_bytes()) != ref["sha256"]:
                        errors.append(f"Reference changed: {ref['id']}")
                except (PilotError, OSError) as exc:
                    errors.append(str(exc))
        for candidate in self.records("registered"):
            try:
                if digest(self.path(candidate["path"]).read_bytes()) != candidate["sha256"]:
                    errors.append(f"Candidate image changed: {candidate['id']}")
            except (PilotError, OSError) as exc:
                errors.append(str(exc))
        return errors

    def records(self, kind):
        return [e["data"] for e in self.events if e["type"] == kind]

    def ensure(self):
        errors = self.errors + self.material_errors()
        if errors:
            raise PilotError("; ".join(dict.fromkeys(errors)))

    def append(self, kind, data):
        self.ensure()
        event = {"seq": len(self.events) + 1, "time_utc": datetime.now(timezone.utc).isoformat(), "type": kind,
                 "plan_sha256": self.plan_sha, "previous_sha256": self.events[-1]["sha256"] if self.events else None, "data": data}
        event["sha256"] = digest(canonical(event))
        with self.path("events.jsonl", False).open("ab") as fh:
            fh.write(canonical(event) + b"\n")
            fh.flush()
            os.fsync(fh.fileno())
        self.events.append(event)
        return data

    def get(self, kind, identifier):
        for row in self.records(kind):
            if row["id"] == identifier:
                return row
        raise PilotError(f"Unknown {kind} ID: {identifier}")

    def refs(self, wanted):
        manifest = self.path("refs/manifest.json", False)
        if not manifest.exists():
            if wanted:
                raise PilotError("References manifest missing")
            return []
        content = read_json(manifest)
        refs = content.get("references", [])
        ids = [r.get("id") for r in refs]
        if len(set(ids)) != len(ids):
            raise PilotError("Duplicate reference IDs")
        if wanted and not set(wanted).issubset(ids):
            raise PilotError("Unknown original reference ID")
        result = []
        for ref in refs:
            if wanted and ref["id"] not in wanted:
                continue
            if ref.get("original") is not True or ref.get("rights_status") != "original-created-for-pilot":
                raise PilotError(f"Reference lacks original-work declaration: {ref.get('id')}")
            p = self.path(ref["path"])
            sha = digest(p.read_bytes())
            if sha != ref.get("sha256"):
                raise PilotError(f"Reference manifest hash mismatch: {ref['id']}")
            result.append({"id": ref["id"], "path": self.relative(p), "sha256": sha,
                           "rights_status": ref["rights_status"], "original": True})
        return result

    def reserve(self, panel, route, promptfile, retry_of=None, hard_failure=None, refs=None):
        self.ensure()
        if panel not in self.panels or route not in self.routes:
            raise PilotError("Unknown panel or route")
        previous = [r for r in self.records("reserved") if r["panel"] == panel and r["route"] == route]
        if not retry_of:
            if previous or hard_failure:
                raise PilotError("Primary already reserved or retry metadata incomplete")
        else:
            primary = self.get("reserved", retry_of)
            failures = [r for r in self.records("failed") if r["attempt_id"] == retry_of]
            if len(previous) != 1 or primary != previous[0] or primary["retry_of"] or not failures or not hard_failure or not hard_failure.strip():
                raise PilotError("Retry requires this panel/route's explicitly failed primary; one retry only")
        p = self.path(promptfile)
        raw = p.read_bytes()
        prompt = raw.decode("utf-8")
        if not prompt.strip():
            raise PilotError("Prompt cannot be empty")
        return self.append("reserved", {"id": f"A{len(self.records('reserved')) + 1:05d}", "panel": panel,
            "route": route, "prompt": prompt, "prompt_sha256": digest(raw), "prompt_path": self.relative(p),
            "references": self.refs(refs), "retry_of": retry_of, "hard_failure": hard_failure,
            "provider": None, "model": None, "provider_request_id": None, "seed": None,
            "usage": None, "cost_usd": None, "status": "reserved-unaccepted"})

    def fail(self, attempt_id, reason):
        self.get("reserved", attempt_id)
        if not reason.strip() or any(r["attempt_id"] == attempt_id for r in self.records("failed")):
            raise PilotError("Failure needs a reason and can only be logged once")
        return self.append("failed", {"attempt_id": attempt_id, "reason": reason, "failure_class": "hard_failure"})

    def register(self, attempt_id, image):
        self.ensure()
        attempt = self.get("reserved", attempt_id)
        if any(r["attempt_id"] == attempt_id for r in self.records("registered") + self.records("failed")):
            raise PilotError("Attempt already registered or failed; reserve a permitted retry")
        p = self.path(image)
        if p.stat().st_size > 100_000_000:
            raise PilotError("Image exceeds 100MB")
        raw = p.read_bytes()
        info = image_info(raw)
        candidate_id = f"C{len(self.records('registered')) + 1:05d}"
        filename = f"candidates/{candidate_id}-{digest(raw)[:16]}{info.pop('extension')}"
        dest = self.path(filename, False)
        dest.parent.mkdir(exist_ok=True)
        with dest.open("xb") as fh:
            fh.write(raw)
        return self.append("registered", {"id": candidate_id, "attempt_id": attempt_id, "panel": attempt["panel"],
            "route": attempt["route"], "path": filename, "sha256": digest(raw), **info,
            "status": "draft-unaccepted", "owner_review": "pending", "commercial_clearance": "uncleared"})

    def observe(self, candidate_id, jsonfile):
        candidate = self.get("registered", candidate_id)
        observation = read_json(self.path(jsonfile))
        if observation.get("candidate_id") != candidate_id or observation.get("image_sha256") != candidate["sha256"] or observation.get("plan_sha256") != self.plan_sha:
            raise PilotError("Observation must bind exact candidate, image SHA and frozen plan SHA")
        if not isinstance(observation.get("reviewer"), str) or not observation["reviewer"].strip():
            raise PilotError("Observation reviewer attribution is required")
        checks = observation.get("checks")
        if not isinstance(checks, dict) or set(checks) != {"actors", "event", "contact", "props", "state"}:
            raise PilotError("Supply independently observed actors/event/contact/props/state checks")
        for name, check in checks.items():
            if not isinstance(check, dict) or check.get("verdict") not in {"pass", "fail", "not_assessed"} or not isinstance(check.get("observation"), str) or not check["observation"].strip():
                raise PilotError(f"Invalid or unexplained {name} observation")
        return self.append("observed", {"candidate_id": candidate_id, "image_sha256": candidate["sha256"],
            "plan_sha256": self.plan_sha, "reviewer": observation["reviewer"], "checks": checks,
            "method": observation.get("method"), "status": "observation-only-not-approval"})

    def select(self, panel, candidate_id):
        candidate = self.get("registered", candidate_id)
        if panel != candidate["panel"]:
            raise PilotError("Candidate was generated for a different panel")
        return self.append("selected", {"panel": panel, "candidate_id": candidate_id, "status": "draft-only"})

    def selected(self):
        return {r["panel"]: r["candidate_id"] for r in self.records("selected")}

    def layout_matches(self, row):
        cid = self.selected().get(row["id"])
        sha = self.get("registered", cid)["sha256"] if cid else None
        return row.get("candidate_id") == cid and row.get("candidate_sha256") == sha

    def validate_draft(self, raw):
        if not isinstance(raw, dict) or raw.get("schema") != "SequenceReviewDraft/1" or raw.get("plan_sha256") != self.plan_sha:
            raise PilotError("Draft must use SequenceReviewDraft/1 and the exact frozen plan SHA")
        if raw.get("status", "draft-unaccepted") != "draft-unaccepted" or raw.get("reviewer_labels_verified", False) is not False or raw.get("production_eligible", False) is not False:
            raise PilotError("Draft cannot assert acceptance or verified reviewer identity")
        panels = raw.get("panels")
        if not isinstance(panels, list) or len(panels) != len(self.panels) or any(not isinstance(p, dict) for p in panels):
            raise PilotError("Draft must contain the exact full panel set")
        ids = [p.get("id") for p in panels]
        if any(not isinstance(pid, str) for pid in ids) or set(ids) != set(self.panels) or len(set(ids)) != len(ids):
            raise PilotError("Draft panel IDs do not match the full frozen panel set")
        clean = []
        for p in panels:
            if not {"candidate_id", "candidate_sha256"}.issubset(p) or not self.layout_matches(p):
                raise PilotError(f"{p['id']}: stale selected candidate ID or SHA in draft")
            notes = p.get("observations", [])
            if not isinstance(notes, list) or len(notes) > 500:
                raise PilotError("Draft observations must be an array with at most 500 entries")
            unverified = []
            for note in notes:
                if not isinstance(note, dict):
                    raise PilotError("Draft observation must be an object")
                unverified.append({"text": bounded_text(note.get("text", ""), 12000, "Browser note"),
                    "reviewer": bounded_text(note.get("reviewer", ""), 300, "Unverified reviewer label"),
                    "flag": bounded_text(note.get("flag", "note"), 100, "Browser note flag"),
                    "reviewer_kind": "unspecified", "status": "unverified-browser-note-not-semantic-approval"})
            clean.append({"id": p["id"], "candidate_id": p.get("candidate_id"), "candidate_sha256": p.get("candidate_sha256"),
                "lettering": draft_shapes(p.get("lettering", [])), "protected_regions": draft_shapes(p.get("protected_regions", []), True),
                "browser_notes": unverified})
        return clean

    def import_draft(self, jsonfile):
        self.ensure()
        path = self.path(jsonfile)
        if path.stat().st_size > 12_000_000:
            raise PilotError("Draft exceeds the 12 MB import limit")
        panels = self.validate_draft(read_json(path))
        return self.append("draft_imported", {"source_path": self.relative(path), "source_sha256": digest(path.read_bytes()),
            "panels": panels, "status": "draft-unaccepted", "reviewer_labels_verified": False})

    def layouts(self):
        layouts, issues = {}, []
        path = self.path("lettering.json", False)
        if path.exists():
            try:
                if path.stat().st_size > 12_000_000:
                    raise PilotError("lettering.json exceeds the 12 MB limit")
                layouts = {p["id"]: p for p in self.validate_draft(read_json(path))}
            except (PilotError, OSError) as exc:
                issues.append(f"lettering.json ignored: {exc}")
        # Most recent imported layout that matches the current image wins. Never
        # transfer annotations from one candidate to another, including null art.
        for event in self.records("draft_imported"):
            for p in event["panels"]:
                if self.layout_matches(p):
                    layouts[p["id"]] = p
        imported = self.records("draft_imported")
        if imported:
            for p in imported[-1]["panels"]:
                if not self.layout_matches(p):
                    issues.append(f"{p['id']}: latest imported layout is stale for the current selection")
        return layouts, issues

    def copy_drift(self, layouts):
        defects = []
        for pid, layout in layouts.items():
            transcript = []
            for letter in layout["lettering"]:
                prefix = letter["speaker"] + ": " if letter["speaker"] else "SFX: " if letter["kind"] == "sfx" else ""
                transcript.append(prefix + letter["text"])
            if transcript != self.panels[pid].get("copy", []):
                defects.append(f"{pid}: draft lettering copy differs from frozen script (including absent or reordered copy)")
        return defects

    def status(self):
        selected = self.selected()
        semantic, unknown = [], []
        for panel in self.panels:
            cid = selected.get(panel)
            if not cid:
                unknown.append(f"{panel}: no draft selected")
                continue
            reviews = [r for r in self.records("observed") if r["candidate_id"] == cid]
            if not reviews:
                unknown.append(f"{panel}: no independent observations")
            for review in reviews:
                for field, check in review["checks"].items():
                    if check["verdict"] == "fail":
                        semantic.append(f"{panel}/{cid}/{field}: {check['observation']}")
                    if check["verdict"] == "not_assessed":
                        unknown.append(f"{panel}/{cid}/{field}: not assessed")
            candidate = self.get("registered", cid)
            if any(r["attempt_id"] == candidate["attempt_id"] for r in self.records("failed")):
                semantic.append(f"{panel}/{cid}: selected attempt has a logged hard failure")
        layouts, layout_issues = self.layouts()
        copy_drift = self.copy_drift(layouts)
        integrity = list(dict.fromkeys(self.errors + self.material_errors()))
        pending = ["Two independent human comprehension/rubric reviews are pending", "Owner acceptance is pending",
                   "Commercial clearance is unresolved", "Actual phone lettering/delivery review is pending"]
        return {"production_eligible": False, "plan_sha256": self.plan_sha, "integrity_failures": integrity,
                "semantic_defects": semantic, "not_assessed": unknown, "pending_human_owner": pending,
                "draft_layout_issues": layout_issues, "copy_drift": copy_drift,
                "blockers": integrity + semantic + unknown + layout_issues + copy_drift + pending,
                "attempts": len(self.records("reserved")), "failed_attempts": len(self.records("failed")),
                "candidates": len(self.records("registered")), "selected": selected,
                "ledger_integrity_note": "Hash chaining detects local edits; it is not an external signature or proof of independent review."}

    def export(self, output):
        self.ensure()
        # Exports may live alongside the workspace, but must stay inside the current checkout.
        dest = no_symlinks(output)
        checkout = no_symlinks(Path.cwd())
        if not dest.is_relative_to(checkout) or dest == checkout or ".." in Path(output).parts:
            raise PilotError("Export must use a fresh directory inside the current checkout")
        if dest.exists():
            raise PilotError("Export destination exists; choose a fresh directory to preserve earlier reviews")
        lettering, _ = self.layouts()
        rows = []
        selected = self.status()["selected"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.mkdir()
        web = Path(__file__).parent / "web"
        if not (web / "index.html").is_file():
            dest.rmdir()
            raise PilotError("Reader frontend is not installed")
        shutil.copytree(web, dest, dirs_exist_ok=True)
        (dest / "assets").mkdir(exist_ok=True)
        for pid, p in self.panels.items():
            candidate = None
            observations = []
            if pid in selected:
                c = self.get("registered", selected[pid])
                filename = f"assets/{c['id']}{Path(c['path']).suffix}"
                shutil.copyfile(self.path(c["path"]), dest / filename)
                candidate = {k: c[k] for k in ("id", "sha256", "width", "height", "status")}
                candidate["src"] = filename
                observations = [r for r in self.records("observed") if r["candidate_id"] == c["id"]]
            layout = lettering.get(pid, {})
            observations = observations + layout.get("browser_notes", [])
            rows.append({"id": pid, **p, "candidate": candidate, "observations": observations,
                         "lettering": layout.get("lettering", []), "protected_regions": layout.get("protected_regions", [])})
        data = {"schema": "SequenceReview/1", "title": self.plan["title"], "plan_sha256": self.plan_sha,
                "panels": rows, "status": self.status()}
        (dest / "review-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (dest / "review-data.js").write_text("window.SEQUENCE_REVIEW_DATA = " + json.dumps(data, ensure_ascii=True).replace("<", "\\u003c") + ";\n", encoding="utf-8")
        return {"output": str(dest), "panels": len(rows), "production_eligible": False}


@contextmanager
def locked(root):
    path = no_symlinks(Path(root) / ".sequence-pilot.lock")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise PilotError("Workspace is locked by another operation; investigate a stale lock before removing it") from exc
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        path.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("reserve")
    p.add_argument("panel"); p.add_argument("route"); p.add_argument("promptfile")
    p.add_argument("--retry-of"); p.add_argument("--hard-failure"); p.add_argument("--ref", action="append", dest="refs")
    p = subs.add_parser("fail"); p.add_argument("attempt_id"); p.add_argument("reason")
    p = subs.add_parser("register"); p.add_argument("attempt_id"); p.add_argument("image")
    p = subs.add_parser("observe"); p.add_argument("candidate_id"); p.add_argument("jsonfile")
    p = subs.add_parser("select"); p.add_argument("panel"); p.add_argument("candidate_id")
    p = subs.add_parser("import-draft"); p.add_argument("jsonfile")
    subs.add_parser("status")
    p = subs.add_parser("export"); p.add_argument("output")
    args = vars(parser.parse_args(argv))
    root, command = args.pop("workspace"), args.pop("command")
    try:
        if command == "status":
            result = Workspace(root).status()
        else:
            with locked(root):
                result = getattr(Workspace(root), command.replace("-", "_"))(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if command == "status" and result["integrity_failures"] else 0
    except (PilotError, OSError, UnicodeError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc), "production_eligible": False}), file=sys.stderr)
        return 2
