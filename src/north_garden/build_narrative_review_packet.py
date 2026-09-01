"""Create a labeled, non-decisional contact sheet for human narrative review."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "production/comic/narrative-sequence-registry-r1.json"
OUTPUT_DIR = ROOT / "experiments/review-packets/narrative-sequences-20260901"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    cards: list[tuple[str, str, str, Path]] = []
    for entry in registry["entries"]:
        edition = json.loads((ROOT / entry["edition"]).read_text(encoding="utf-8"))
        revisions = json.loads((ROOT / edition["panel_revision_collection"]).read_text(encoding="utf-8"))
        by_id = {item["panel_revision_id"]: item for item in revisions["revisions"]}
        for revision_id in edition["selected_panel_revision_ids"]:
            revision = by_id[revision_id]
            cards.append((entry["chapter_label"], revision["panel_id"], revision_id, ROOT / revision["asset_path"]))
    font = ImageFont.load_default()
    border, label_height, gap = 8, 42, 18
    width = 960
    rendered: list[tuple[str, Image.Image]] = []
    for chapter, panel_id, revision_id, path in cards:
        with Image.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((width - 2 * border, 600), Image.Resampling.LANCZOS)
            label = f"{chapter}  {panel_id.rsplit('-', 1)[-1].upper()}  {revision_id}  sha256:{sha256(path)[:12]}"
            card = Image.new("RGB", (width, image.height + label_height + border * 2), "#f4f0e8")
            card.paste(image, ((width - image.width) // 2, border))
            ImageDraw.Draw(card).text((border, image.height + border + 12), label, fill="#141414", font=font)
            rendered.append((label, card))
    height = gap + sum(card.height + gap for _, card in rendered)
    sheet = Image.new("RGB", (width, height), "#202020")
    y = gap
    for _, card in rendered:
        sheet.paste(card, (0, y))
        y += card.height + gap
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    contact_sheet = OUTPUT_DIR / "ch03-ch04-review-contact-sheet-r1.png"
    sheet.save(contact_sheet, optimize=True)
    lines = [
        "# North Garden CH03/CH04 human review packet",
        "",
        "Status: **review aid only**. It cannot accept, publish, or commercially clear a panel.",
        "",
        f"Contact sheet: `{contact_sheet.relative_to(ROOT).as_posix()}`",
        "",
        "For each panel, record a decision (`accept`, `reject`, or `needs_repair`), failure tags, and actual review minutes in a new immutable review revision. Check the declared hard assertions, role binding, wardrobe, props, set continuity, composition, and dialogue/lettering readiness. Do not infer missing provenance or reproducibility from visual quality.",
        "",
        "| Sequence | Panel | Revision | Asset | SHA-256 | Current state |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for chapter, panel_id, revision_id, path in cards:
        lines.append(f"| {chapter} | {panel_id} | {revision_id} | `{path.relative_to(ROOT).as_posix()}` | `{sha256(path)}` | pending human review |")
    lines.extend([
        "",
        "Both sequences are three-panel research drafts, each 47 panels below the 50-panel chapter-scale lower target. The renderer route is provenance-limited and not commercially cleared.",
    ])
    packet = OUTPUT_DIR / "README.md"
    packet.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {contact_sheet} and {packet}")


if __name__ == "__main__":
    main()
