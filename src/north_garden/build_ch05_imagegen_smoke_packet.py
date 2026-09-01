"""Create a project-local contact sheet for the CH05 non-canon visual smoke."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "experiments/reviews/ch05-mill-signal-imagegen-smoke-review-r1.json"
OUT = ROOT / "experiments/review-packets/ch05-mill-signal-imagegen-smoke-r1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    cards: list[tuple[str, Path]] = []
    for candidate in review["candidates"]:
        record = json.loads((ROOT / candidate["record"]).read_text(encoding="utf-8"))
        cards.append((candidate["development_panel_id"], ROOT / record["output"]["path"]))
    width, gap, border, label_height = 960, 18, 8, 38
    font = ImageFont.load_default()
    rendered: list[Image.Image] = []
    for panel_id, path in cards:
        with Image.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((width - 2 * border, 600), Image.Resampling.LANCZOS)
            card = Image.new("RGB", (width, image.height + 2 * border + label_height), "#f4f0e8")
            card.paste(image, ((width - image.width) // 2, border))
            ImageDraw.Draw(card).text((border, image.height + border + 10), f"{panel_id}  sha256:{sha256(path)[:12]}", fill="#141414", font=font)
            rendered.append(card)
    sheet = Image.new("RGB", (width, gap + sum(card.height + gap for card in rendered)), "#202020")
    y = gap
    for card in rendered:
        sheet.paste(card, (0, y))
        y += card.height + gap
    OUT.mkdir(parents=True, exist_ok=True)
    contact = OUT / "contact-sheet-r1.png"
    sheet.save(contact, optimize=True)
    lines = [
        "# CH05 Mill Signal visual-smoke review packet",
        "",
        "Status: **non-canon visual research only; pending authorized human review.**",
        "",
        "This four-panel smoke samples P001, P029, P036, and P050 from the clean 50-panel development script. It does not authorize canon promotion, rendering of the remaining panels, commercial use, or a production acceptance claim.",
        "",
        f"Contact sheet: `{contact.relative_to(ROOT).as_posix()}`",
        "",
        "Record a timed human decision and specific failure tags in a new immutable review revision. Check role binding, blocking, set legibility, wardrobe/prop continuity, storytelling, and whether these images materially support the desired series direction.",
    ]
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {contact} and {OUT / 'README.md'}")


if __name__ == "__main__":
    main()
