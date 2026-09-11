from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[3]
VOLUME = ROOT / "production" / "reimaginings" / "ember-lattice" / "volume"
OUT = ROOT / "experiments" / "reimaginings" / "ember-lattice" / "volume" / "qa"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = []
    for chapter in range(1, 11):
        chapter_id = f"ch{chapter:02d}"
        plans = json.loads((VOLUME / "chapters" / chapter_id / "comic-panel-plans.json").read_text(encoding="utf-8"))["panels"]
        tile_w, tile_h, label_h, columns = 220, 330, 26, 4
        sheet = Image.new("RGB", (tile_w * columns, (tile_h + label_h) * 6), "#0d1115")
        draw = ImageDraw.Draw(sheet)
        for index, panel in enumerate(plans):
            source = ROOT / panel["source_path"]
            if not source.exists():
                raise SystemExit(f"missing QA source: {source}")
            with Image.open(source) as image:
                tile = ImageOps.fit(image.convert("RGB"), (tile_w, tile_h), Image.Resampling.LANCZOS)
            x, y = (index % columns) * tile_w, (index // columns) * (tile_h + label_h)
            sheet.paste(tile, (x, y))
            label = f'P{panel["order"]:03d} {panel["density"].upper()} {"ACTION" if panel["action"] else "STORY"}'
            draw.text((x + 6, y + tile_h + 6), label, fill="#f2eee5")
        target = OUT / f"{chapter_id}-source-contact.jpg"
        sheet.save(target, quality=91)
        outputs.append(str(target))
    print(json.dumps({"status": "PASS", "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
