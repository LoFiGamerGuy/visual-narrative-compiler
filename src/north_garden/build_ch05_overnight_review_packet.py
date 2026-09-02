"""Build deterministic local review artifacts for the CH05 overnight production batch."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "experiments/review-packets/ch05-overnight-production-r1"
REGISTRY = RUN_ROOT / "candidate-registry.json"
PLAN = ROOT / "production/comic/overnight/ch05-overnight-production-plan-r1.json"
PANEL_PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT = RUN_ROOT / "review"
PACKET = OUT / "review-packet.json"
BG = "#e9e6df"
CARD = "#faf8f2"
INK = "#16191d"
SUBTLE = "#4c535b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def load_rgb(entry: dict) -> Image.Image:
    path = ROOT / entry["output"]["path"]
    if sha256(path) != entry["output"]["sha256"]:
        raise ValueError(f"candidate hash mismatch: {entry['candidate_id']}")
    return Image.open(path).convert("RGB")


def safe_rect(entry: dict, plans: dict) -> tuple[float, float, float, float]:
    plan = plans[entry["panel_id"]]
    return tuple(plan["comic_direction"]["lettering"]["safe_zones"][0]["rect_norm"])


def overlay_safe_zone(image: Image.Image, rect_norm: tuple[float, float, float, float]) -> Image.Image:
    rgba = image.convert("RGBA")
    layer = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y, w, h = rect_norm
    rect = (
        round(x * image.width),
        round(y * image.height),
        round((x + w) * image.width),
        round((y + h) * image.height),
    )
    line = max(4, min(image.size) // 220)
    draw.rectangle(rect, fill=(18, 196, 235, 65), outline=(0, 105, 145, 255), width=line)
    draw.text((rect[0] + line * 2, rect[1] + line * 2), "LETTERING SAFE ZONE", fill=(0, 72, 96, 255), font=font(max(18, min(image.size) // 45)))
    return Image.alpha_composite(rgba, layer).convert("RGB")


def save_individual_derivatives(entries: list[dict], plans: dict) -> list[dict]:
    overlay_dir = OUT / "lettering-overlays"
    phone_dir = OUT / "phone-previews"
    overlay_dir.mkdir(parents=True, exist_ok=True)
    phone_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for entry in entries:
        source = load_rgb(entry)
        cid = entry["candidate_id"]
        overlay_path = overlay_dir / f"{cid}-lettering-overlay.png"
        phone_path = phone_dir / f"{cid}-phone-390px.png"
        overlay_safe_zone(source, safe_rect(entry, plans)).save(overlay_path, optimize=False)
        phone = ImageOps.contain(source, (390, 844), Image.Resampling.LANCZOS)
        phone_canvas = Image.new("RGB", (390, 844), "#111318")
        phone_canvas.paste(phone, ((390 - phone.width) // 2, (844 - phone.height) // 2))
        phone_canvas.save(phone_path, optimize=False)
        records.append({
            "candidate_id": cid,
            "lettering_overlay": {"path": overlay_path.relative_to(ROOT).as_posix(), "sha256": sha256(overlay_path)},
            "phone_preview": {"path": phone_path.relative_to(ROOT).as_posix(), "sha256": sha256(phone_path)},
        })
    return records


def build_grid(title: str, subtitle: str, entries: list[dict], *, columns: int, cell: tuple[int, int],
               render_mode: str, plans: dict) -> Image.Image:
    rows = (len(entries) + columns - 1) // columns
    margin, header, gap = 32, 112, 20
    width = margin * 2 + columns * cell[0] + (columns - 1) * gap
    height = header + margin + rows * cell[1] + (rows - 1) * gap
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 22), title, fill=INK, font=font(30))
    draw.text((margin, 62), subtitle, fill=SUBTLE, font=font(18))
    for index, entry in enumerate(entries):
        col, row = index % columns, index // columns
        x = margin + col * (cell[0] + gap)
        y = header + row * (cell[1] + gap)
        draw.rectangle((x, y, x + cell[0], y + cell[1]), fill=CARD, outline="#697079", width=2)
        image = load_rgb(entry)
        if render_mode == "overlay":
            image = overlay_safe_zone(image, safe_rect(entry, plans))
        elif render_mode == "phone":
            reduced = ImageOps.contain(image, (390, 844), Image.Resampling.LANCZOS)
            phone = Image.new("RGB", (390, 844), "#111318")
            phone.paste(reduced, ((390 - reduced.width) // 2, (844 - reduced.height) // 2))
            image = phone
        target_h = cell[1] - 74
        framed = ImageOps.contain(image, (cell[0] - 20, target_h - 10), Image.Resampling.LANCZOS)
        px = x + (cell[0] - framed.width) // 2
        py = y + 60 + (target_h - framed.height) // 2
        canvas.paste(framed, (px, py))
        refs = len(entry["references"])
        label = f"{entry['candidate_id']}  {entry['panel_id'].split('-')[-1].upper()}  {entry['style_id']}  refs:{refs}"
        draw.text((x + 12, y + 10), label, fill=INK, font=font(16))
        draw.text((x + 12, y + 34), f"{entry['output']['width']}x{entry['output']['height']}  {entry['execution']['elapsed_seconds']:.3f}s", fill=SUBTLE, font=font(14))
    return canvas


def artifact(path: Path, image: Image.Image) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=False)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "width": image.width, "height": image.height}


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    production = json.loads(PLAN.read_text(encoding="utf-8"))
    panel_collection = json.loads(PANEL_PLANS.read_text(encoding="utf-8"))
    entries = registry["entries"]
    if len(entries) != production["generation_target"]["planned_candidates"]:
        raise SystemExit("candidate registry is incomplete")
    plans = {item["panel_id"]: item for item in panel_collection["plans"]}
    OUT.mkdir(parents=True, exist_ok=True)
    derivatives = save_individual_derivatives(entries, plans)
    artifacts: dict[str, object] = {}
    artifacts["all_candidates"] = artifact(
        OUT / "contact-sheet-all-candidates.png",
        build_grid("CH05 OVERNIGHT PRODUCTION - ALL CANDIDATES", "20 unaccepted candidates / 14 ComicPanelPlans / compare story read before finish", entries, columns=4, cell=(500, 620), render_mode="clean", plans=plans),
    )
    artifacts["lettering_overlay"] = artifact(
        OUT / "contact-sheet-lettering-overlays.png",
        build_grid("CH05 CANONICAL LETTERING SAFE-ZONE AUDIT", "Cyan is the exact normalized zone from each approved ComicPanelPlan", entries, columns=4, cell=(500, 620), render_mode="overlay", plans=plans),
    )
    artifacts["phone_preview"] = artifact(
        OUT / "contact-sheet-phone-previews.png",
        build_grid("CH05 PHONE-SIZE READABILITY", "Each candidate is first reduced to a 390x844 phone viewport; inspect silhouette and causal read", entries, columns=5, cell=(410, 920), render_mode="phone", plans=plans),
    )
    sequence_artifacts = []
    by_id = {item["candidate_id"]: item for item in entries}
    for sequence in production["sequences"]:
        subset = [by_id[cid] for cid in sequence["candidate_ids"]]
        sequence_artifacts.append({
            "sequence_id": sequence["sequence_id"],
            **artifact(
                OUT / f"sequence-{sequence['sequence_id']}.png",
                build_grid(f"CH05 SEQUENCE - {sequence['sequence_id'].replace('_', ' ').upper()}", "ComicPanelPlan order with planned comparison variants adjacent", subset, columns=3, cell=(620, 700), render_mode="clean", plans=plans),
            ),
        })
    artifacts["sequences"] = sequence_artifacts
    comparisons = {
        "continuity": ["c001", "c019", "c004", "c005", "c006", "c007", "c011", "c012", "c013", "c020", "c017", "c018"],
        "styles": ["c005", "c006", "c008", "c018", "c011", "c012", "c013", "c020"],
        "cadence": ["c017", "c013", "c014", "c015", "c016", "c018"],
    }
    for name, ids in comparisons.items():
        artifacts[f"comparison_{name}"] = artifact(
            OUT / f"comparison-{name}.png",
            build_grid(f"CH05 {name.upper()} COMPARISON", "Unaccepted engineering comparison; no composite score or production promotion", [by_id[cid] for cid in ids], columns=4 if name != "cadence" else 3, cell=(500, 650), render_mode="clean", plans=plans),
        )
    packet = {
        "record_type": "CH05OvernightReviewPacket",
        "schema_version": "1.0",
        "record_id": "ng-ch05-overnight-review-packet-r1",
        "state": "READY_FOR_STRUCTURED_REVIEW_UNACCEPTED",
        "candidate_registry": {"path": REGISTRY.relative_to(ROOT).as_posix(), "sha256": sha256(REGISTRY)},
        "production_plan": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "panel_plan_collection": {"path": PANEL_PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PANEL_PLANS)},
        "candidate_count": len(entries),
        "distinct_panel_plans": len({item["panel_id"] for item in entries}),
        "total_elapsed_seconds": registry["total_elapsed_seconds"],
        "disclosed_spend_usd": None,
        "provider_metadata_limitations": ["model unavailable", "endpoint unavailable", "provider request ID unavailable", "usage unavailable", "cost unavailable"],
        "artifacts": artifacts,
        "candidate_derivatives": derivatives,
        "boundary": "Generated pixels remain ignored local research evidence. No candidate is accepted, commercially cleared, or an exact production base.",
    }
    PACKET.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"built review packet: {PACKET.relative_to(ROOT)} {sha256(PACKET)}")
    print(f"artifacts: {3 + len(sequence_artifacts) + len(comparisons)} consolidated / {len(derivatives) * 2} candidate derivatives")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
