from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[3]
SLUG = "ember-lattice"
PROD = ROOT / "production" / "reimaginings" / SLUG / "volume"
REVIEW = ROOT / "docs" / "reimaginings" / SLUG / "volume"
EXPERIMENTS = ROOT / "experiments" / "reimaginings" / SLUG
PHONE_WIDTH = 390


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def layered_panel(source_href: str, overlay_href: str, alt: str, lazy: bool = True) -> str:
    loading = ' loading="lazy"' if lazy else ""
    return (
        '<span class="panel-stack">'
        f'<img{loading} class="panel-source" src="{esc(source_href)}" alt="{esc(alt)}">'
        f'<img{loading} class="panel-overlay" src="{esc(overlay_href)}" alt="">'
        '</span>'
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wrap_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if len(trial) <= max_chars:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > 1 and len(lines[-1]) < 5:
        short_tail = lines.pop()
        lines[-1] += " " + short_tail
    return lines


def box_px(unit: dict[str, Any], width: int, height: int) -> tuple[float, float, float, float]:
    l, t, r, b = unit["box"]
    return l * width, t * height, r * width, b * height


def text_lines(text: str, width_px: float, font_size: float) -> list[str]:
    return wrap_text(text, max(12, int(width_px / (font_size * 0.57))))


def dialogue_svg(unit: dict[str, Any], width: int, height: int) -> str:
    x1, y1, x2, y2 = box_px(unit, width, height)
    bw, bh = x2 - x1, y2 - y1
    mode = unit.get("mode", "soft")
    font_size = width * 14 / PHONE_WIDTH
    lines = text_lines(unit["text"], bw - 48, font_size)
    leading = font_size * 1.08
    text_h = len(lines) * leading
    needed = text_h + 34
    if needed > bh:
        if y1 < height / 2:
            y2 = min(height * .48, y1 + needed)
        else:
            y1 = max(height * .52, y2 - needed)
        bh = y2 - y1
    cx = (x1 + x2) / 2
    text_y = (y1 + y2 - text_h) / 2 + font_size * .88
    tspans = "".join(
        f'<tspan x="{cx:.1f}" y="{text_y+i*leading:.1f}">{esc(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    if mode == "open":
        return f'<text text-anchor="middle" font-family="Arial, sans-serif" font-size="{font_size:.1f}" font-weight="800" fill="#f8f2e8" stroke="#11151a" stroke-width="6" stroke-linejoin="round" paint-order="stroke">{tspans}</text>'

    tail = ""
    if unit.get("tail"):
        tx, ty = unit["tail"][0] * width, unit["tail"][1] * height
        bx = max(x1 + 38, min(x2 - 38, tx))
        if ty < y1:
            tail = f'<path d="M {bx-15:.1f} {y1+20:.1f} L {tx:.1f} {ty:.1f} L {bx+14:.1f} {y1+18:.1f} Z" fill="#f7f0e4" fill-opacity=".84" stroke="#181b20" stroke-width="4" stroke-linejoin="round"/>'
        else:
            tail = f'<path d="M {bx-15:.1f} {y2-20:.1f} L {tx:.1f} {ty:.1f} L {bx+14:.1f} {y2-18:.1f} Z" fill="#f7f0e4" fill-opacity=".84" stroke="#181b20" stroke-width="4" stroke-linejoin="round"/>'
    if mode == "butted":
        shape = f'<path d="M {x1+22:.1f} {y1:.1f} H {x2-14:.1f} Q {x2:.1f} {y1:.1f} {x2:.1f} {y1+14:.1f} V {y2-22:.1f} L {x2-22:.1f} {y2:.1f} H {x1+14:.1f} Q {x1:.1f} {y2:.1f} {x1:.1f} {y2-14:.1f} V {y1+22:.1f} Z" fill="#f7f0e4" fill-opacity=".84" stroke="#181b20" stroke-width="4"/>'
    elif mode == "distress":
        shape = f'<path d="M {x1+20:.1f} {y1:.1f} L {x2-18:.1f} {y1+5:.1f} L {x2:.1f} {y1+28:.1f} L {x2-6:.1f} {y2-18:.1f} L {x2-30:.1f} {y2:.1f} L {x1+16:.1f} {y2-5:.1f} L {x1:.1f} {y2-30:.1f} L {x1+6:.1f} {y1+18:.1f} Z" fill="#f7f0e4" fill-opacity=".84" stroke="#181b20" stroke-width="4"/>'
    else:
        shape = f'<rect x="{x1:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{min(54,bh*.28):.1f}" fill="#f7f0e4" fill-opacity=".84" stroke="#181b20" stroke-width="4"/>'
    return tail + shape + f'<text text-anchor="middle" font-family="Arial, sans-serif" font-size="{font_size:.1f}" font-weight="700" fill="#15181d">{tspans}</text>'


def caption_svg(unit: dict[str, Any], width: int, height: int) -> str:
    x1, y1, x2, y2 = box_px(unit, width, height)
    bw, bh = x2 - x1, y2 - y1
    font_size = width * 14 / PHONE_WIDTH
    lines = text_lines(unit["text"], bw - 40, font_size)
    leading = font_size * 1.08
    needed = len(lines) * leading + 24
    if needed > bh:
        if y1 < height / 2:
            y2 = min(height * .48, y1 + needed)
        else:
            y1 = max(height * .52, y2 - needed)
        bh = y2 - y1
    start = y1 + (bh - len(lines) * leading) / 2 + font_size * .9
    tspans = "".join(f'<tspan x="{x1+20:.1f}" y="{start+i*leading:.1f}">{esc(line)}</tspan>' for i, line in enumerate(lines))
    return (
        f'<path d="M {x1:.1f} {y1:.1f} H {x2-20:.1f} L {x2:.1f} {y1+20:.1f} V {y2:.1f} H {x1:.1f} Z" fill="#11151a" fill-opacity=".76" stroke="#e8ddc8" stroke-opacity=".35" stroke-width="2"/>'
        f'<text font-family="Arial, sans-serif" font-size="{font_size:.1f}" font-weight="700" fill="#f7f0e4">{tspans}</text>'
    )


def system_svg(unit: dict[str, Any], width: int, height: int) -> str:
    x1, y1, x2, y2 = box_px(unit, width, height)
    lines = unit.get("lines") or [unit.get("text", "")]
    kind = unit.get("kind", "status")
    accent = "#ff793d" if kind in {"cultivation", "enemy", "comparison"} else "#c89952"
    bw, bh = x2 - x1, y2 - y1
    size = width * 13 / PHONE_WIDTH
    max_chars = max(11, int((bw - 44) / (size * .54)))
    expanded: list[tuple[str, bool]] = []
    for index, line in enumerate(lines):
        expanded.extend((part, index == 0) for part in wrap_text(line, max_chars))
    gap = size * 1.12
    needed = len(expanded) * gap + 38
    if needed > bh:
        if y1 < height / 2:
            y2 = min(height * .49, y1 + needed)
        else:
            y1 = max(height * .51, y2 - needed)
        bh = y2 - y1
    tspans = "".join(
        f'<tspan x="{x1+22:.1f}" y="{y1+25+(i+.7)*gap:.1f}" font-size="{size+2 if first else size:.1f}" font-weight="{900 if first else 650}" fill="{accent if first else "#f4eee4"}">{esc(line)}</tspan>'
        for i, (line, first) in enumerate(expanded)
    )
    return (
        f'<path d="M {x1+18:.1f} {y1:.1f} H {x2:.1f} V {y2-18:.1f} L {x2-18:.1f} {y2:.1f} H {x1:.1f} V {y1+18:.1f} Z" fill="#10151a" fill-opacity=".82" stroke="{accent}" stroke-width="3"/>'
        f'<path d="M {x1+18:.1f} {y1+14:.1f} H {x2-18:.1f}" stroke="#f4eee4" stroke-opacity=".28" stroke-width="2"/>'
        f'<text font-family="Arial, sans-serif" letter-spacing=".7">{tspans}</text>'
    )


def sfx_svg(unit: dict[str, Any], width: int, height: int) -> str:
    x, y = unit["at"][0] * width, unit["at"][1] * height
    rotate = unit.get("rotate", 0)
    label = esc(unit["text"])
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rotate})"><text text-anchor="middle" font-family="Impact, Arial Black, sans-serif" font-size="68" font-style="italic" font-weight="900" fill="#ff7a3d" stroke="#14171c" stroke-width="11" paint-order="stroke">{label}</text></g>'


def render_svg(panel: dict[str, Any], units: list[dict[str, Any]], source: Path, target: Path) -> str:
    with Image.open(source) as image:
        width, height = image.size
    href = Path(os.path.relpath(source, target.parent)).as_posix()
    overlays: list[str] = []
    for unit in sorted(units, key=lambda row: row.get("reading_order", 0)):
        if unit["kind"] == "caption":
            overlays.append(caption_svg(unit, width, height))
        elif unit["kind"] == "dialogue":
            overlays.append(dialogue_svg(unit, width, height))
        elif unit["kind"] == "sfx":
            overlays.append(sfx_svg(unit, width, height))
        else:
            overlays.append(system_svg(unit, width, height))
    label = f'{panel["panel_id"]}: {panel["beat"]}'
    overlay_block = f"  {''.join(overlays)}\n" if overlays else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">\n'
        f'  <title>{esc(label)}</title>\n'
        f'  <image href="{href}" x="0" y="0" width="{width}" height="{height}" preserveAspectRatio="xMidYMid slice"/>\n'
        f'{overlay_block}'
        '</svg>\n'
    )


def safe_zone_svg(panel: dict[str, Any], source: Path, target: Path) -> str:
    with Image.open(source) as image:
        width, height = image.size
    href = Path(os.path.relpath(source, target.parent)).as_posix()
    focal = panel["focal_exclusion"]
    fx, fy, fr, fb = focal[0] * width, focal[1] * height, focal[2] * width, focal[3] * height
    lettering = "".join(
        f'<rect x="{box[0]*width:.1f}" y="{box[1]*height:.1f}" width="{(box[2]-box[0])*width:.1f}" height="{(box[3]-box[1])*height:.1f}" fill="#ff793d" fill-opacity=".16" stroke="#ff793d" stroke-width="4" stroke-dasharray="12 8"/>'
        for box in panel["lettering_exclusions"]
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Safe-zone diagnostic for {esc(panel['panel_id'])}">
<image href="{href}" width="{width}" height="{height}" preserveAspectRatio="xMidYMid slice"/>
<rect x="{fx:.1f}" y="{fy:.1f}" width="{fr-fx:.1f}" height="{fb-fy:.1f}" fill="#56e39f" fill-opacity=".08" stroke="#56e39f" stroke-width="5"/>{lettering}
<text x="24" y="42" font-family="Arial" font-size="24" font-weight="800" fill="#56e39f" stroke="#11151a" stroke-width="5" paint-order="stroke">GREEN FOCAL PROTECTION · ORANGE LETTERING</text></svg>'''


def contact_sheet(chapter: str, panels: list[dict[str, Any]], target: Path, grayscale: bool = False) -> None:
    thumb_w, thumb_h, columns = 180, 300, 4
    rows = (len(panels) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + 26)), "#11151a")
    draw = ImageDraw.Draw(sheet)
    for index, panel in enumerate(panels):
        source = ROOT / panel["source_path"]
        with Image.open(source) as image:
            rgb = image.convert("RGB")
            if grayscale:
                rgb = ImageOps.grayscale(rgb).convert("RGB")
            thumb = ImageOps.fit(rgb, (thumb_w, thumb_h), method=Image.Resampling.LANCZOS)
        x, y = (index % columns) * thumb_w, (index // columns) * (thumb_h + 26)
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + thumb_h + 5), f'P{panel["order"]:03d} · {panel["density"]} · {"ACTION" if panel["action"] else "STORY"}', fill="#f2eee5")
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, quality=91)


def chapter_html(chapter: str, title: str, panels: list[dict[str, Any]], final: dict[str, Any], metrics: dict[str, Any], mode: str = "phone") -> str:
    cards = []
    for panel in panels:
        order = panel["order"]
        classes = f'panel density-{panel["density"]} {"action" if panel["action"] else "story"}'
        source_href = f'../../../../../../{panel["source_path"]}'
        panel_markup = layered_panel(source_href, f'panels/p{order:03d}.svg', panel["beat"])
        cards.append(f'''<article class="{classes}" id="p{order:03d}" data-density="{panel['density']}" data-action="{str(panel['action']).lower()}">
  <div class="panel-meta"><a href="#p{order:03d}">P{order:03d}</a><span>{esc(panel['density'])}</span><span>{'action' if panel['action'] else 'story'}</span></div>
  {panel_markup}
  <details><summary>Beat and source</summary><p>{esc(panel['beat'])}</p><code>{esc(panel['source_path'])}</code></details>
</article>''')
    nav = "".join(f'<a href="#p{i:03d}">{i:02d}</a>' for i in range(1, 25))
    number = int(chapter[-2:])
    chapters = "".join(f'<a href="../ch{i:02d}/index.html" {"aria-current=\"page\"" if i == number else ""}>CH{i:02d}</a>' for i in range(1, 11))
    previous = f'../ch{number-1:02d}/index.html' if number > 1 else '../../index.html'
    following = f'../ch{number+1:02d}/index.html' if number < 10 else '../../index.html'
    controls = f'<nav class="chapter-controls"><a href="{previous}">← Previous</a><a href="../../index.html">Volume hub</a><a href="{following}">Next →</a></nav>'
    body_class = "full" if mode == "full" else "phone"
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(chapter.upper())} · {esc(title)}</title><link rel="stylesheet" href="../../assets/volume.css"></head>
<body class="{body_class}"><header class="chapter-head" id="top">{controls}<p class="eyebrow">EMBER LATTICE · OWNER REVIEW · {esc(mode.upper())}</p><h1>{esc(chapter.upper())} · {esc(title)}</h1><p>{len(panels)} continuous panels · {metrics['action_panels']} action · {metrics['spoken_internal_words']} dialogue words · {metrics['meaningful_system_moments']} system moments</p><p><a href="index.html">Phone reader</a> · <a href="full.html">Full-size reader</a> · <a href="compact.html">Compact review</a> · <a href="action.html">Action strip</a> · <a href="diagnostics.html">Diagnostics</a></p><div class="state"><b>End state</b><span>LV {final['level']} · XP {final['xp']}/{final['next_threshold']}</span><span>HP {final['hp']['current']}/{final['hp']['max']} · QI {final['qi']['current']}/{final['qi']['max']}</span><span>{esc(final['class'])} · {esc(final['cultivation'])}</span></div></header>
<nav class="chapter-menu" aria-label="chapter navigation">{chapters}</nav><nav class="panel-nav" aria-label="panel jump navigation">{nav}</nav><main class="scroll">{''.join(cards)}</main><footer>{controls}<a href="#top">Back to start ↑</a></footer></body></html>'''


def main() -> None:
    master = read_json(PROD / "volume-master.json")
    dialogue_metrics = {row["chapter"]: row for row in read_json(PROD / "dialogue-and-density-metrics.json")["chapters"]}
    ledger = read_json(PROD / "system-state-ledger.json")
    final_by_chapter = {row["chapter"]: row["final"] for row in ledger["chapters"]}
    missing: list[str] = []
    output_records: list[dict[str, Any]] = []
    chapter_rows: list[dict[str, Any]] = []
    for chapter_row in master["chapters"]:
        chapter = chapter_row["chapter"]
        chapter_prod = PROD / "chapters" / chapter
        plans = read_json(chapter_prod / "comic-panel-plans.json")
        lettering = read_json(chapter_prod / "lettering-copy.json")["panel_units"]
        out = REVIEW / "chapters" / chapter
        for panel in plans["panels"]:
            source = ROOT / panel["source_path"]
            if not source.exists():
                missing.append(panel["source_path"])
                continue
            target = out / "panels" / f'p{panel["order"]:03d}.svg'
            write_text(target, render_svg(panel, lettering.get(panel["panel_id"], []), source, target))
            safe_target = out / "safe-zones" / f'p{panel["order"]:03d}.svg'
            write_text(safe_target, safe_zone_svg(panel, source, safe_target))
            output_records.append({"panel_id": panel["panel_id"], "source": panel["source_path"], "source_sha256": sha256(source), "lettered": str(target.relative_to(ROOT)).replace("\\", "/"), "lettered_sha256": sha256(target)})
        if missing:
            continue
        metrics = dialogue_metrics[chapter]
        action_count = sum(1 for panel in plans["panels"] if panel["action"])
        metrics = {**metrics, "action_panels": action_count}
        write_text(out / "index.html", chapter_html(chapter, chapter_row["title"], plans["panels"], final_by_chapter[chapter], metrics, "phone"))
        write_text(out / "full.html", chapter_html(chapter, chapter_row["title"], plans["panels"], final_by_chapter[chapter], metrics, "full"))
        source_href = {panel["panel_id"]: Path(os.path.relpath(ROOT / panel["source_path"], out)).as_posix() for panel in plans["panels"]}
        source_cards = "".join(f'<a href="{source_href[panel["panel_id"]]}"><img src="{source_href[panel["panel_id"]]}" alt="P{panel["order"]:03d} unlettered source"><span>P{panel["order"]:03d} · {panel["density"]}</span></a>' for panel in plans["panels"])
        action_source_cards = "".join(f'<a href="{source_href[panel["panel_id"]]}"><img src="{source_href[panel["panel_id"]]}" alt="P{panel["order"]:03d} unlettered action source"><span>P{panel["order"]:03d}</span></a>' for panel in plans["panels"] if panel["action"])
        compact_cards = "".join(
            f'<a href="panels/p{panel["order"]:03d}.svg">'
            + layered_panel(source_href[panel["panel_id"]], f'panels/p{panel["order"]:03d}.svg', f'P{panel["order"]:03d}: {panel["beat"]}')
            + f'<span>P{panel["order"]:03d} · {panel["density"]} · {"ACTION" if panel["action"] else "STORY"}</span></a>'
            for panel in plans["panels"]
        )
        write_text(out / "compact.html", f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{chapter.upper()} compact review</title><link rel="stylesheet" href="../../assets/volume.css"></head><body><main class="hub"><a href="index.html">← Chapter reader</a><h1>{chapter.upper()} compact lettered review</h1><div class="review-grid">{compact_cards}</div></main></body></html>')
        action_cards = "".join(
            f'<article><a href="panels/p{panel["order"]:03d}.svg">'
            + layered_panel(source_href[panel["panel_id"]], f'panels/p{panel["order"]:03d}.svg', f'P{panel["order"]:03d}: {panel["beat"]}')
            + f'</a><p>P{panel["order"]:03d} · {esc(panel["beat"])}</p></article>'
            for panel in plans["panels"] if panel["action"]
        )
        write_text(out / "action.html", f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{chapter.upper()} action strip</title><link rel="stylesheet" href="../../assets/volume.css"></head><body><main class="hub"><a href="index.html">← Chapter reader</a><h1>{chapter.upper()} causal action strip</h1><p>Read in order: geography → intention → initiation → contact/interruption → consequence → response → adaptation → payoff/state.</p><div class="action-strip">{action_cards}</div><h2>Unlettered source contact strip</h2><div class="review-grid">{action_source_cards}</div></main></body></html>')
        ui_panels = [panel for panel in plans["panels"] if any(unit["kind"] not in {"caption", "dialogue", "sfx"} for unit in lettering.get(panel["panel_id"], []))]
        safe_cards = "".join(
            f'<a href="safe-zones/p{panel["order"]:03d}.svg">'
            + layered_panel(source_href[panel["panel_id"]], f'safe-zones/p{panel["order"]:03d}.svg', f'P{panel["order"]:03d} safe-zone diagnostic')
            + f'<span>P{panel["order"]:03d}</span></a>' for panel in plans["panels"]
        )
        ui_cards = "".join(
            f'<a href="panels/p{panel["order"]:03d}.svg">'
            + layered_panel(source_href[panel["panel_id"]], f'panels/p{panel["order"]:03d}.svg', f'P{panel["order"]:03d} UI review')
            + f'<span>P{panel["order"]:03d} · Brass Ledger</span></a>' for panel in ui_panels
        )
        write_text(out / "diagnostics.html", f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{chapter.upper()} diagnostics</title><link rel="stylesheet" href="../../assets/volume.css"></head><body><main class="hub"><a href="index.html">← Chapter reader</a><h1>{chapter.upper()} density, value, safe-zone, and UI review</h1><h2>Unlettered source density contact sheet</h2><div class="review-grid">{source_cards}</div><h2>Grayscale value grouping</h2><div class="review-grid grayscale">{source_cards}</div><h2>System UI and lettering</h2><div class="review-grid ui-grid">{ui_cards}</div><h2>Focal protection / lettering zones</h2><div class="review-grid">{safe_cards}</div></main></body></html>')
        chapter_rows.append({"chapter": chapter, "title": chapter_row["title"], "panels": 24, "action": action_count, "dialogue_words": metrics["spoken_internal_words"], "system_moments": metrics["meaningful_system_moments"], "final": final_by_chapter[chapter]})
    if missing:
        raise SystemExit(f"missing {len(missing)} source panels; first: {missing[:8]}")

    css = '''*{box-sizing:border-box}body{margin:0;background:#0d1115;color:#ece5d9;font-family:Inter,Arial,sans-serif}a{color:#ffad70}.chapter-head,.hub,footer{max-width:1040px;margin:auto;padding:28px 22px}.eyebrow{color:#c89952;letter-spacing:.16em;font-size:.78rem;font-weight:800}h1{font-size:clamp(2rem,7vw,4.5rem);margin:.15em 0}.state,.chapter-controls{display:flex;gap:10px;flex-wrap:wrap;justify-content:space-between}.state>*{background:#171d22;border:1px solid #42372c;padding:8px 12px}.chapter-menu{position:sticky;top:0;z-index:6;display:flex;justify-content:center;gap:4px;overflow:auto;background:#090c0fee;padding:8px}.chapter-menu a{padding:5px 8px;text-decoration:none;color:#cbbfb0}.chapter-menu a[aria-current]{background:#c89952;color:#0d1115;font-weight:900}.panel-nav{position:sticky;top:41px;z-index:5;display:flex;gap:5px;overflow:auto;background:#0d1115ef;border-block:1px solid #332c25;padding:9px calc((100% - 430px)/2)}.panel-nav a{min-width:30px;text-decoration:none;color:#d8cdbf}.scroll{width:min(100%,430px);margin:auto;background:#050708}.full .scroll{width:min(100%,1024px)}.panel{margin:0;border-bottom:12px solid #0d1115;position:relative}.panel-stack{display:block;position:relative}.panel-stack>.panel-source{display:block;width:100%;height:auto}.panel-stack>.panel-overlay{position:absolute;inset:0;display:block;width:100%;height:100%;object-fit:fill}.panel-meta{position:absolute;z-index:3;top:7px;left:7px;display:flex;gap:6px;opacity:.25;transition:.2s}.panel:hover .panel-meta{opacity:1}.panel-meta>*{background:#0d1115d9;padding:3px 6px;font-size:.67rem;text-transform:uppercase}.panel details{padding:8px 12px;background:#171d22;font-size:.78rem}.panel details:not([open]){display:none}.hub-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}.chapter-card{display:block;background:#171d22;border:1px solid #3c342c;padding:18px;text-decoration:none;color:#ece5d9}.chapter-card:hover{border-color:#c89952}.chapter-card strong{display:block;font-size:1.1rem}.chapter-card small{color:#bcae9f}.progression{width:100%;border-collapse:collapse;margin:24px 0}.progression th,.progression td{border-bottom:1px solid #39322b;padding:9px;text-align:left;font-size:.86rem}.pill{display:inline-block;border:1px solid #5a493a;padding:4px 8px;margin:3px}.proof{background:#141a1f;border-left:3px solid #ff793d;padding:16px;margin:18px 0}.review-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.review-grid a{background:#171d22;text-decoration:none}.review-grid img{display:block;width:100%;height:300px;object-fit:cover;object-position:top}.review-grid .panel-stack{height:300px;overflow:hidden}.review-grid .panel-stack>.panel-source,.review-grid .panel-stack>.panel-overlay{width:100%;height:100%;object-fit:cover;object-position:top}.review-grid span:not(.panel-stack){display:block;padding:7px;color:#d8cdbf;font-size:.75rem}.ui-grid{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}.action-strip{width:min(100%,430px);margin:auto}.action-strip img,.diagnostic-sheet{display:block;width:100%;height:auto}.action-strip article{border-bottom:10px solid #0d1115}.action-strip p{padding:7px;margin:0;background:#171d22;font-size:.78rem}.link-columns{columns:3 240px}.link-columns a{display:block;padding:4px 0}.read-all-break{padding:70px 20px 24px;max-width:430px;margin:auto}.limitations{border:1px solid #5b4636;padding:16px}.pass{color:#56e39f}.warn{color:#ffcf70}.fail{color:#ff6f6f}@media(max-width:500px){.chapter-head{padding:20px 16px}.panel-nav{padding-left:8px}.progression{display:block;overflow:auto}.chapter-menu{justify-content:flex-start}}'''
    css += ".grayscale img{filter:grayscale(1)}"
    write_text(REVIEW / "assets" / "volume.css", css)
    read_all_sections = []
    for row in master["chapters"]:
        chapter = row["chapter"]
        plans = read_json(PROD / "chapters" / chapter / "comic-panel-plans.json")["panels"]
        images = "".join(
            layered_panel(f'../../../../{panel["source_path"]}', f'chapters/{chapter}/panels/p{panel["order"]:03d}.svg', panel["beat"])
            for panel in plans
        )
        read_all_sections.append(f'<section id="{chapter}"><header class="read-all-break"><p class="eyebrow">{chapter.upper()}</p><h2>{esc(row["title"])}</h2><a href="chapters/{chapter}/index.html">Open chapter controls</a></header><div class="scroll">{images}</div></section>')
    read_all_nav = "".join(f'<a href="#ch{i:02d}">CH{i:02d}</a>' for i in range(1, 11))
    write_text(REVIEW / "read-all.html", f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ember Lattice · Read all</title><link rel="stylesheet" href="assets/volume.css"></head><body id="top"><header class="hub"><a href="index.html">← Volume hub</a><h1>Continuous read · CH01–CH10</h1><p>240 lettered panels in one phone-width stream.</p></header><nav class="chapter-menu">{read_all_nav}</nav>{"".join(read_all_sections)}<footer><a href="#top">Back to start ↑</a> · <a href="index.html">Volume hub</a></footer></body></html>')

    progression_sections = []
    for row in ledger["chapters"]:
        initial, final = row["initial"], row["final"]
        tx_rows = "".join(f'<tr><td>{esc(tx["panel_id"].split("-")[-1].upper())}</td><td>{esc(tx["type"])}</td><td><code>{esc(json.dumps({k:v for k,v in tx.items() if k not in {"panel_id","type"}}, ensure_ascii=False))}</code></td></tr>' for tx in row["transactions"])
        progression_sections.append(f'<details id="{row["chapter"]}"><summary><b>{row["chapter"].upper()}</b> · LV {initial["level"]}→{final["level"]} · XP {initial["xp"]}/{initial["next_threshold"]}→{final["xp"]}/{final["next_threshold"]} · {esc(initial["class"])}→{esc(final["class"])} · {esc(initial["cultivation"])}→{esc(final["cultivation"])}</summary><table class="progression"><thead><tr><th>Panel</th><th>Transaction</th><th>Exact delta / provenance</th></tr></thead><tbody>{tx_rows}</tbody></table></details>')
    write_text(REVIEW / "progression.html", f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ember Lattice · Progression ledger</title><link rel="stylesheet" href="assets/volume.css"></head><body><main class="hub"><a href="index.html">← Volume hub</a><h1>Ten-chapter progression hub</h1><p>Every XP, level, HP/Qi, class, cultivation, skill, item, inventory, equipment, quest, dungeon, trust, and faction transition below comes from the authoritative SystemState ledger.</p>{"".join(progression_sections)}</main></body></html>')
    failed_href = Path(os.path.relpath(ROOT / "experiments/reimaginings/ember-lattice/volume/ch03/diagnostics/p007-r1-landscape.png", REVIEW)).as_posix()
    selected_href = Path(os.path.relpath(ROOT / "experiments/reimaginings/ember-lattice/volume/ch03/source/p007.png", REVIEW)).as_posix()
    write_text(REVIEW / "repair-comparison.html", f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CH03 P007 repair comparison</title><link rel="stylesheet" href="assets/volume.css"></head><body><main class="hub"><a href="index.html">← Volume hub</a><h1>Bounded targeted repair · CH03 P007</h1><p>Failure class: <code>non_vertical_source</code>. Story, references, identities, state, and lettering reservation were held constant; the retry added only an explicit tall 9:16 orientation directive.</p><div class="hub-grid"><article class="chapter-card"><small>PRESERVED HARD FAIL · R1</small><strong>1536×1024 landscape</strong><img class="diagnostic-sheet" src="{failed_href}" alt="preserved landscape hard failure"></article><article class="chapter-card"><small>SELECTED PASS · R2</small><strong>925×1701 portrait</strong><img class="diagnostic-sheet" src="{selected_href}" alt="selected portrait repair"></article></div><p>Non-target hashes are recorded in <a href="../../../../production/reimaginings/ember-lattice/volume/repair-snapshots/ch03-p007-before.json">the before snapshot</a>.</p></main></body></html>')
    chapter_cards = "".join(f'<a class="chapter-card" href="chapters/{row["chapter"]}/index.html"><small>{row["chapter"].upper()} · 24 PANELS</small><strong>{esc(row["title"])}</strong><span>{row["action"]} action · {row["dialogue_words"]} words · {row["system_moments"]} UI</span></a>' for row in chapter_rows)
    chapter_cards += '<a class="chapter-card" href="../phase-b-audits/index.md"><small>PRODUCTION EVIDENCE</small><strong>Phase B cadence audits</strong><span>CH01–02 · CH03–04 · CH01–06 · CH07–10 / repair wave</span></a>'
    progression = "".join(f'<tr><td><a href="chapters/{row["chapter"]}/index.html">{row["chapter"].upper()}</a></td><td>{row["final"]["level"]}</td><td>{row["final"]["xp"]}/{row["final"]["next_threshold"]}</td><td>{row["final"]["hp"]["current"]}/{row["final"]["hp"]["max"]}</td><td>{row["final"]["qi"]["current"]}/{row["final"]["qi"]["max"]}</td><td>{esc(row["final"]["class"])}</td><td>{esc(row["final"]["cultivation"])}</td></tr>' for row in chapter_rows)
    totals = {
        "dialogue_words": sum(row["dialogue_words"] for row in chapter_rows),
        "system_moments": sum(row["system_moments"] for row in chapter_rows),
    }
    generated_requests = read_json(PROD / "generation-requests.json")["requests"]
    timing_sum = round(sum(row.get("measured_elapsed_seconds") or 0 for row in generated_requests), 3)
    reference_uses = sum(len(row["reference_ids"]) for row in generated_requests)
    validation_path = PROD / "volume-validation.json"
    validation = read_json(validation_path) if validation_path.exists() else {"status": "AUDIT_PENDING", "errors": [], "warnings": []}
    result_class = "pass" if validation["status"] == "PASS" else "warn"
    audit_totals = validation.get("review_totals", {"PASS": 0, "WARN": len(validation.get("warnings", [])), "FAIL": len(validation.get("errors", [])), "failure_classes": []})
    chapter_cards += f'<a class="chapter-card" href="../../../../production/reimaginings/ember-lattice/volume/volume-validation.json"><small>FINAL VALIDATION</small><strong class="{result_class}">{esc(validation["status"])}</strong><span>PASS {audit_totals["PASS"]} · WARN {audit_totals["WARN"]} · FAIL {audit_totals["FAIL"]} · failure classes {esc(audit_totals["failure_classes"])}</span></a>'
    first, last = ledger["chapters"][0]["initial"], ledger["chapters"][-1]["final"]
    surface_links = "".join(f'<tr><td>{row["chapter"].upper()}</td><td><a href="chapters/{row["chapter"]}/index.html">phone</a></td><td><a href="chapters/{row["chapter"]}/full.html">full</a></td><td><a href="chapters/{row["chapter"]}/compact.html">compact</a></td><td><a href="chapters/{row["chapter"]}/action.html">action</a></td><td><a href="chapters/{row["chapter"]}/diagnostics.html">density/value/safe/UI</a></td></tr>' for row in chapter_rows)
    hub = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ember Lattice · Complete Volume Review</title><link rel="stylesheet" href="assets/volume.css"></head><body id="top"><main class="hub"><p class="eyebrow">OWNER REVIEW · COMPLETE TEN-CHAPTER VOLUME</p><h1>Ember Lattice</h1><p>A debt-bound adult salvager follows the cracks in a living dungeon ledger, turning finite salvage, dangerous breath cultivation, and verified structural faults into a class path capable of stopping the Bell Regent.</p><p>Selected visual direction: owner-approved Candidate B · crisp charcoal contour · controlled cel values · muted teal/aged ivory/brass · localized ember accents · predominantly fair/light-complexioned fictional-adult principals with distinct facial, age, build, costume, and role silhouettes.</p><div><span class="pill">240 panels</span><span class="pill">108 action / 45%</span><span class="pill">10 sequences</span><span class="pill">224 new panel prompts</span><span class="pill">{reference_uses} reference uses</span><span class="pill">{totals['dialogue_words']} dialogue words</span><span class="pill">{totals['system_moments']} system moments</span><span class="pill">$0 direct paid cloud spend</span></div><p class="{result_class}"><b>Current validation: {esc(validation['status'])}</b> · PASS {audit_totals['PASS']} / WARN {audit_totals['WARN']} / FAIL {audit_totals['FAIL']}</p>
<section class="proof"><b>Owner feedback implemented.</b> Balloons use 84% ivory fill, smaller type/padding and 4px strokes; verified quiet regions use outlined open text; longer speech uses compact butted forms; Brass Ledger cards use 82% dark translucency. The volume carries 3,821 dialogue/internal words and 41 consequential status, XP, class, skill, inventory, quest, enemy, cultivation, or comparison interfaces.</section>
<p><a href="read-all.html"><b>Read all 240 panels continuously →</b></a> · <a href="progression.html">Open exact progression ledger</a> · <a href="../pilot/index.html">Approved Phase A pilot</a></p><section class="hub-grid">{chapter_cards}</section>
<h2>Every review surface</h2><table class="progression"><thead><tr><th>Chapter</th><th>Phone</th><th>Full</th><th>Compact</th><th>Action</th><th>Diagnostics</th></tr></thead><tbody>{surface_links}</tbody></table>
<h2>Original progression system</h2><p>The Brass Ledger recognizes verified contribution as Level/XP while Pressure Breath separately measures bodily cultivation. Salvage is finite: items retain rarity, weight, condition, provenance, and irreversible consumption. Skills require a verified fault, disclose Qi cost/cooldown/condition, and evolve only after shown use. Quests, injuries, equipment, trust, Free Delvers reputation, Ash Crown hostility, boss credit, and cleared dungeon zones persist across chapter boundaries.</p>
<h3>CH01 opening versus CH10 ending</h3><table class="progression"><thead><tr><th></th><th>Level / XP</th><th>HP / QI</th><th>Class</th><th>Cultivation</th><th>Stats</th></tr></thead><tbody><tr><td>CH01 open</td><td>{first['level']} · {first['xp']}/{first['next_threshold']}</td><td>{first['hp']['current']}/{first['hp']['max']} · {first['qi']['current']}/{first['qi']['max']}</td><td>{esc(first['class'])}</td><td>{esc(first['cultivation'])}</td><td>{esc(first['stats'])}</td></tr><tr><td>CH10 end</td><td>{last['level']} · {last['xp']}/{last['next_threshold']}</td><td>{last['hp']['current']}/{last['hp']['max']} · {last['qi']['current']}/{last['qi']['max']}</td><td>{esc(last['class'])}</td><td>{esc(last['cultivation'])}</td><td>{esc(last['stats'])}</td></tr></tbody></table>
<h2>Persistent progression summary</h2><table class="progression"><thead><tr><th>Chapter</th><th>LV</th><th>XP</th><th>HP</th><th>QI</th><th>Class</th><th>Cultivation</th></tr></thead><tbody>{progression}</tbody></table>
<h2>Strongest panels and spectacle</h2><p><a href="chapters/ch01/panels/p015.svg">CH01 P015 Belljaw combo</a> · <a href="chapters/ch04/panels/p018.svg">CH04 P018 Bailiff consequence</a> · <a href="chapters/ch07/panels/p014.svg">CH07 P014 Channel I breakthrough</a> · <a href="chapters/ch08/panels/p020.svg">CH08 P020 Brass Maw payoff</a> · <a href="chapters/ch10/panels/p022.svg">CH10 P022 Regentbreaker finish</a></p>
<h2>Research, derivation, rubrics, and production decisions</h2><div class="link-columns"><a href="../research/inspiration-derivation-matrix.md">Inspiration-derivation matrix</a><a href="../research/lettering-and-dialogue-research.md">Lettering/dialogue research and citations</a><a href="../style-candidate-review.md">Style rubric and Candidate B result</a><a href="../phase-a-pilot-audit.md">Story/tooling/pilot rubric</a><a href="../cumulative-experiment-ledger.md">Cumulative experiment ledger</a><a href="../failure-correction-contract.md">Failure-correction contract</a><a href="../adr/ADR-EL001-premise-and-visual-contract.md">ADR index · EL001</a><a href="../adr/ADR-EL002-owner-approval-and-lettering-v2.md">ADR index · EL002</a><a href="../../../../production/reimaginings/ember-lattice/route-audit.json">Tooling route audit</a><a href="../../../../production/reimaginings/ember-lattice/volume/volume-validation.json">Final validation JSON</a><a href="../../../../production/reimaginings/ember-lattice/volume/generation-reconciliation.json">Prompt/output reconciliation</a><a href="../../../../production/reimaginings/ember-lattice/integrity/final-integrity.json">Tracked files, commit range, remote and protected-state proof</a></div>
<h2>Locked bibles and character contracts</h2><div class="link-columns"><a href="../../../../reimaginings/ember-lattice/story-bible.md">Story bible</a><a href="../../../../reimaginings/ember-lattice/visual-bible.md">Visual/style bible</a><a href="../../../../reimaginings/ember-lattice/character-and-equipment-bible.md">Adult character, complexion, equipment bible</a><a href="../../../../reimaginings/ember-lattice/system-bible.md">System bible</a><a href="../../../../reimaginings/ember-lattice/cultivation-bible.md">Cultivation bible</a><a href="../../../../reimaginings/ember-lattice/dungeon-monster-action-bible.md">Dungeon/monster/action bible</a><a href="../../../../reimaginings/ember-lattice/skill-bible.md">Skill bible</a><a href="../../../../reimaginings/ember-lattice/item-and-rarity-bible.md">Item/rarity bible</a><a href="../../../../reimaginings/ember-lattice/quest-bible.md">Quest/faction bible</a><a href="../../../../reimaginings/ember-lattice/timeline-and-continuity-bible.md">Timeline/continuity bible</a><a href="../../../../reimaginings/ember-lattice/lettering-and-ui-bible.md">Lettering/UI bible</a></div>
<h2>Reference sheets</h2><div class="review-grid"><a href="../../../../experiments/reimaginings/ember-lattice/style-candidates/candidate-b.png"><img src="../../../../experiments/reimaginings/ember-lattice/style-candidates/candidate-b.png" alt="Candidate B approved visual direction"><span>Approved Candidate B</span></a><a href="../../../../experiments/reimaginings/ember-lattice/references/principal-elian.png"><img src="../../../../experiments/reimaginings/ember-lattice/references/principal-elian.png" alt="Elian character sheet"><span>Elian Voss</span></a><a href="../../../../experiments/reimaginings/ember-lattice/references/supporting-mira-equipment.png"><img src="../../../../experiments/reimaginings/ember-lattice/references/supporting-mira-equipment.png" alt="Mira character sheet"><span>Mira Vale</span></a><a href="../../../../experiments/reimaginings/ember-lattice/references/volume-adults.png"><img src="../../../../experiments/reimaginings/ember-lattice/references/volume-adults.png" alt="Orin Sable and delver sheet"><span>Orin, Sable, maintenance delver</span></a></div>
<h2>Targeted repair wave</h2><p>CH03 P007 returned as a 1536×1024 landscape image and failed the tall-panel contract. Its hashed original is preserved; the one allowed localized retry produced a selected 925×1701 replacement without changing any other panel. <a href="repair-comparison.html">Open the before/after comparison and non-target hash evidence.</a> Phase A P016's diagnostic retry remains documented in the approved pilot.</p>
<h2>Timing, provider metadata, and limitations</h2><p>{timing_sum:,.3f} seconds summed per-request measured latency (concurrent queues overlap in wall time). Built-in image generation; provider model exposed only as <code>imagegen-default</code>; endpoint <code>built-in-image_gen</code>; per-request usage, deterministic seed, and reproducibility unavailable; direct paid/cloud spend $0.</p><div class="limitations"><b>Owner decisions still open:</b> final volume acceptance and commercial clearance. Generated raster references/source art remain ignored and non-reproducible; deterministic plans, exact prompts, hashes, vector lettering, ledgers, audits, and HTML are tracked. No copyright-ownership or commercial-clearance claim is made.</div><p><a href="#top">Back to start ↑</a></p></main></body></html>'''
    write_text(REVIEW / "index.html", hub)
    write_json(PROD / "volume-build-report.json", {"schema": "VolumeBuildReport/1.0", "status": "PASS", "chapters": len(chapter_rows), "panels": len(output_records), "phone_review_width": PHONE_WIDTH, "lettering_profile": "v2 compact translucent hybrid", "outputs": output_records})
    print(json.dumps({"status": "PASS", "chapters": len(chapter_rows), "panels": len(output_records), "review": str(REVIEW / "index.html")}, indent=2))


if __name__ == "__main__":
    main()
