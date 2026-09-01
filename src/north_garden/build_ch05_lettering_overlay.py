"""Build a non-destructive lettering-field review sheet for CH05 visual-smoke art."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "experiments/reviews/ch05-mill-signal-lettering-layout-review-r1.json"
OUT_DIR = ROOT / "experiments/review-packets/ch05-mill-signal-imagegen-smoke-r1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_treatment(review: dict, treatment: str) -> Path:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    font = ImageFont.load_default()
    width, gap, border, label_height = 960, 18, 8, 54
    cards: list[Image.Image] = []
    for panel in review["panels"]:
        path = ROOT / panel["source_image"]
        assert path.exists() and sha256(path) == panel["source_sha256"]
        with Image.open(path) as source:
            image = source.convert("RGBA")
            image.thumbnail((width - 2 * border, 600), Image.Resampling.LANCZOS)
        choice = panel["treatments"][treatment]
        x, y, w, h = choice["rect_norm"]
        box = (round(x * image.width), round(y * image.height), round((x + w) * image.width), round((y + h) * image.height))
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        if treatment == "balloon":
            draw.rounded_rectangle(box, radius=22, fill=(248, 248, 238, 190), outline=(35, 35, 35, 255), width=4)
            draw.text((box[0] + 8, box[1] + 8), "BALLOON OPTION", fill=(20, 20, 20, 255), font=font)
        else:
            draw.rounded_rectangle(box, radius=8, fill=(15, 35, 40, 105), outline=(84, 220, 235, 255), width=3)
            draw.text((box[0] + 6, box[1] + 6), "DIRECT TEXT OPTION", fill=(220, 255, 255, 255), font=font)
        rendered = Image.alpha_composite(image, overlay).convert("RGB")
        card = Image.new("RGB", (width, rendered.height + 2 * border + label_height), "#f4f0e8")
        card.paste(rendered, ((width - rendered.width) // 2, border))
        label = f"{panel['development_panel_id']} | {panel['suitability']}"
        ImageDraw.Draw(card).text((border, rendered.height + border + 8), label, fill="#141414", font=font)
        ImageDraw.Draw(card).text((border, rendered.height + border + 25), choice["note"], fill="#303030", font=font)
        cards.append(card)
    sheet = Image.new("RGB", (width, gap + sum(card.height + gap for card in cards)), "#202020")
    y = gap
    for card in cards:
        sheet.paste(card, (0, y))
        y += card.height + gap
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"lettering-{treatment}-overlay-r1.png"
    sheet.save(out, optimize=True)
    return out


def main() -> None:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    for treatment in ("balloon", "direct_text"):
        out = build_treatment(review, treatment)
        print(f"Wrote {out} sha256:{sha256(out)}")


if __name__ == "__main__":
    main()
