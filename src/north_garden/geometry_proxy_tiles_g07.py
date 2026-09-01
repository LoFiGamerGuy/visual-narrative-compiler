"""Generate non-figurative G07 proxy stage tiles for renderer-facing controls."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments" / "outputs" / "geometry_proxy_g07_v1"
OUT = ROOT / "experiments" / "outputs" / "geometry_proxy_tiles_g07_v1"
RECORD = ROOT / "experiments" / "results" / "geometry_proxy_tiles_g07_v1.json"
GAUNTLET = ROOT / "research" / "authoritative" / "v2.1.1" / "bench" / "gauntlet.json"
FROZEN_SHA256 = "f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae"
LAYOUTS = {"G07a": ("ORANGE", "TEAL"), "G07b": ("TEAL", "ORANGE")}
COLORS = {"ORANGE": (230, 135, 35), "TEAL": (40, 157, 163)}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check() -> None:
    if sha(GAUNTLET) != FROZEN_SHA256:
        raise RuntimeError("frozen gauntlet hash changed")

def make(case: str) -> Path:
    check(); OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{case.lower()}-role-tiles-r1.png"
    if path.exists(): return path
    base = Image.open(SOURCE / f"{case.lower()}-geometry-base-r3.png").convert("RGB")
    draw = ImageDraw.Draw(base)
    # Two deliberately non-figurative tiles sit at the prior actor anchors. The table stays a separate foreground occluder.
    left, right = LAYOUTS[case]
    for x, role in ((310, left), (786, right)):
        draw.rounded_rectangle((x, 415, x + 120, 555), radius=10, fill=COLORS[role], outline=(42, 42, 42), width=7)
        draw.line((x + 16, 435, x + 104, 535), fill=(242, 230, 200), width=8)
    draw.polygon([(250,570),(966,570),(1090,742),(126,742)], fill=(113,74,45), outline=(71,45,29), width=8)
    draw.rectangle((410,742,485,812), fill=(78,49,30)); draw.rectangle((731,742,806,812), fill=(78,49,30))
    base.save(path); return path

if __name__ == "__main__":
    records = []
    for case in LAYOUTS:
        path = make(case)
        records.append({"case_id":case,"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path),"layout":{"left":LAYOUTS[case][0],"right":LAYOUTS[case][1]},"meaning":"non-figurative renderer-facing role tile; not identity or final art"})
    RECORD.write_text(json.dumps({"record_type":"GeometryProxyTileAssets","state":"LOCAL_FICTIONAL_PROXY_ONLY","semantic_source_sha256":FROZEN_SHA256,"assets":records,"limitations":["Tiles are non-figurative layout markers only.","They are not a canonical stage, character identity, or frozen benchmark asset."]}, indent=2)+"\n",encoding="utf-8")
    print(RECORD)
