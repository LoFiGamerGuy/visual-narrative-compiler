"""Build deterministic ignored review artifacts for the future LitRPG concept trio."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "experiments/review-packets/future-litrpg-visual-concepts-r1"
REGISTRY = RUN_ROOT / "candidate-registry.json"
PLAN = ROOT / "production/comic/concepts/future-litrpg-visual-concepts-r1.json"
OUT = RUN_ROOT / "review"
PACKET = OUT / "review-packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def load(entry: dict) -> Image.Image:
    path = ROOT / entry["output"]["path"]
    if sha256(path) != entry["output"]["sha256"]:
        raise ValueError(f"hash mismatch: {entry['candidate_id']}")
    return Image.open(path).convert("RGB")


def save_grid(path: Path, entries: list[dict], title: str, subtitle: str, phone: bool = False) -> dict:
    cell_w, cell_h = (520, 930) if phone else (720, 720)
    canvas = Image.new("RGB", (40 + len(entries) * (cell_w + 20), cell_h + 150), "#e9e6df")
    draw = ImageDraw.Draw(canvas)
    draw.text((30, 22), title, fill="#17191c", font=font(30))
    draw.text((30, 62), subtitle, fill="#4d535a", font=font(18))
    for index, entry in enumerate(entries):
        x, y = 30 + index * (cell_w + 20), 115
        draw.rectangle((x, y, x + cell_w, y + cell_h), fill="#faf8f2", outline="#6a7076", width=2)
        image = load(entry)
        if phone:
            reduced = ImageOps.contain(image, (390, 844), Image.Resampling.LANCZOS)
            framed = Image.new("RGB", (390, 844), "#111318")
            framed.paste(reduced, ((390 - reduced.width) // 2, (844 - reduced.height) // 2))
            image = framed
        framed = ImageOps.contain(image, (cell_w - 20, cell_h - 80), Image.Resampling.LANCZOS)
        canvas.paste(framed, (x + (cell_w - framed.width) // 2, y + 62 + (cell_h - 72 - framed.height) // 2))
        draw.text((x + 12, y + 10), f"{entry['candidate_id']}  {entry['concept_id']}", fill="#17191c", font=font(16))
        draw.text((x + 12, y + 34), f"{entry['output']['width']}x{entry['output']['height']}  {entry['execution']['elapsed_seconds']:.3f}s", fill="#4d535a", font=font(14))
    canvas.save(path, optimize=False)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "width": canvas.width, "height": canvas.height}


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if len(registry["entries"]) != 3:
        raise SystemExit("concept registry incomplete")
    OUT.mkdir(parents=True, exist_ok=True)
    entries = registry["entries"]
    artifacts = {
        "concept_contact_sheet": save_grid(OUT / "contact-sheet-future-litrpg-concepts.png", entries, "FUTURE LITRPG CONCEPTS - NON-CANON", "Soren kit / Sigrid kit / Mireback coordinated action; unaccepted exploration"),
        "phone_previews": save_grid(OUT / "contact-sheet-future-litrpg-phone-previews.png", entries, "FUTURE LITRPG CONCEPTS - PHONE PREVIEWS", "390x844 viewport reductions; inspect silhouette, equipment, and action", phone=True)
    }
    derivatives = []
    phone_dir = OUT / "phone-previews"
    phone_dir.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        image = load(entry)
        reduced = ImageOps.contain(image, (390, 844), Image.Resampling.LANCZOS)
        preview = Image.new("RGB", (390, 844), "#111318")
        preview.paste(reduced, ((390 - reduced.width) // 2, (844 - reduced.height) // 2))
        path = phone_dir / f"{entry['candidate_id']}-phone-390px.png"
        preview.save(path, optimize=False)
        derivatives.append({"candidate_id": entry["candidate_id"], "phone_preview": {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}})
    packet = {
        "record_type": "FutureLitRPGConceptReviewPacket",
        "schema_version": "1.0",
        "record_id": "ng-future-litrpg-concept-review-packet-r1",
        "state": "READY_FOR_OWNER_REVIEW_NONCANON_UNACCEPTED",
        "plan": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "registry": {"path": REGISTRY.relative_to(ROOT).as_posix(), "sha256": sha256(REGISTRY)},
        "candidate_count": 3,
        "total_elapsed_seconds": registry["total_elapsed_seconds"],
        "artifacts": artifacts,
        "candidate_derivatives": derivatives,
        "boundary": "Non-canon ignored concept pixels only; no CH05 revision, production acceptance, commercial clearance, or new reference-upload authority."
    }
    PACKET.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"built non-canon concept packet: {PACKET.relative_to(ROOT)} {sha256(PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
