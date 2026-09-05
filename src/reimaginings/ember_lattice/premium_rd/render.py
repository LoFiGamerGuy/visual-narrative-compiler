from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from .core import esc, read_json, rel_href, resolve_under, sha256_file, write_json, write_text
from .model import rubric_summary


CSS = """\
:root{color-scheme:dark;--ink:#0b0e13;--paper:#f6f0e4;--ember:#ff7447;--gold:#d7aa5b;--teal:#56d7c4;--muted:#a7adba;--card:#151b23;--line:#303846}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 50% -20%,#25303c 0,#0b0e13 36rem);color:var(--paper);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;overflow-x:hidden}a{color:#8ae7da}a:focus-visible{outline:3px solid var(--ember);outline-offset:3px}.shell{max-width:1240px;margin:auto;padding:24px}.hero{padding:52px 0 28px}.eyebrow,.tag{color:var(--gold);text-transform:uppercase;letter-spacing:.12em;font-size:.76rem;font-weight:800}h1{font-size:clamp(2.1rem,7vw,5.2rem);line-height:.92;margin:.18em 0}h2{line-height:1.12}.lede{max-width:74ch;color:#ccd0d8}.nav{position:sticky;top:0;z-index:20;background:#0b0e13f2;border-bottom:1px solid var(--line);padding:12px;display:flex;gap:10px;overflow:auto;scrollbar-width:none}.nav::-webkit-scrollbar{display:none}.nav a{white-space:nowrap;padding:7px 12px;border:1px solid var(--line);border-radius:999px;text-decoration:none}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}.card{background:linear-gradient(145deg,#18202a,#12171e);border:1px solid var(--line);padding:18px;border-radius:14px;overflow:hidden}.card img{max-width:100%;height:auto}.score{font-size:2rem;font-weight:900;color:var(--gold)}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px;border-bottom:1px solid var(--line);vertical-align:top}.reader{margin:auto;display:grid;gap:clamp(26px,6vw,84px)}.reader.phone{max-width:390px}.reader.full{max-width:1024px}.reader.action{max-width:720px}.panel{margin:0;position:relative}.panel.deep-gutter{margin-bottom:clamp(72px,14vw,180px)}.art-stack{position:relative;background:#07090d}.art-stack img{display:block;width:100%;height:auto}.art-stack .overlay{position:absolute;inset:0}.art-stack .grayscale{filter:grayscale(1)}.panel figcaption{font-size:.78rem;color:var(--muted);padding:.45rem 0}.compact-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}.compact-grid figure{margin:0}.comparison{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}.comparison img{width:100%}.pill{display:inline-block;border:1px solid var(--line);padding:.25em .65em;border-radius:999px;margin:.15em}.pass{color:#74e4a5}.warn{color:#ffd36f}.fail{color:#ff7b69}.metric{font:800 .78rem/1.2 ui-monospace,Consolas,monospace;color:#ffd36f}.concept{aspect-ratio:31/26;object-fit:cover;background:#0e1218;border:1px solid var(--line);border-radius:10px}.footer{margin-top:60px;padding:30px 0;border-top:1px solid var(--line);color:var(--muted)}code{word-break:break-all}.skip{position:absolute;left:-10000px}.skip:focus{left:12px;top:12px;z-index:100;background:white;color:black;padding:8px}@media(max-width:600px){.shell{padding:14px}.comparison{grid-template-columns:1fr}.nav{font-size:.86rem}th,td{padding:7px 4px;font-size:.83rem}.hero{padding-top:34px}.reader.phone{gap:34px}}
"""


def _wrap(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    for authored_line in text.splitlines() or [""]:
        words = authored_line.split()
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
    return lines or [""]


def _text_tspans(text: str, x: float, y: float, width: float, size: float, leading: float | None = None) -> tuple[str, int]:
    lines = _wrap(text, max(8, int(width / (size * .56))))
    step = leading or size * 1.12
    spans = "".join(f'<tspan x="{x:.1f}" y="{y + index * step:.1f}">{esc(line)}</tspan>' for index, line in enumerate(lines))
    return spans, len(lines)


def _box_px(box: list[float], width: int, height: int) -> tuple[float, float, float, float]:
    return box[0] * width, box[1] * height, box[2] * width, box[3] * height


def _leaf_art_path(asset_path: Path) -> Path:
    """Resolve the raster under a lightweight SVG asset wrapper."""
    current = asset_path.resolve()
    seen: set[Path] = set()
    while current.suffix.lower() == ".svg":
        if current in seen:
            raise ValueError(f"cyclic SVG asset reference: {current}")
        seen.add(current)
        match = re.search(r'<image\b[^>]*\bhref="([^"]+)"', current.read_text(encoding="utf-8"))
        if not match:
            return current
        href = match.group(1)
        if href.startswith(("data:", "http://", "https://", "#")):
            raise ValueError(f"SVG asset wrapper must reference a local file: {current}")
        current = (current.parent / href).resolve()
    if not current.is_file():
        raise FileNotFoundError(current)
    return current


def _art_stack(art_href: str, overlay_href: str, alt: str, grayscale: bool = False) -> str:
    art_class = "art grayscale" if grayscale else "art"
    return f'<div class="art-stack"><img class="{art_class}" loading="lazy" src="{esc(art_href)}" alt="{esc(alt)}"><img class="overlay" loading="lazy" src="{esc(overlay_href)}" alt="" aria-hidden="true"></div>'


def _lettering(unit: dict[str, Any], width: int, height: int) -> str:
    kind = unit["kind"]
    style = unit.get("style", kind)
    if kind == "sfx":
        at = unit.get("at", [.5, .5])
        x, y = at[0] * width, at[1] * height
        rotate = float(unit.get("rotate", -8))
        size = width * float(unit.get("font_scale", .07))
        return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rotate:.1f})"><text text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-size="{size:.1f}" font-style="italic" font-weight="900" letter-spacing="1" fill="#ff7447" stroke="#11151b" stroke-width="{size*.18:.1f}" paint-order="stroke" stroke-linejoin="round">{esc(unit["text"])}</text></g>'
    x1, y1, x2, y2 = _box_px(unit["box"], width, height)
    bw, bh = x2 - x1, y2 - y1
    size = width * float(unit.get("font_scale", .034))
    if kind == "open":
        spans, count = _text_tspans(unit["text"], (x1 + x2) / 2, (y1 + y2) / 2 - size * .56, bw, size)
        color = "#ffb06f" if style == "ledger_delta" else "#fff9ed"
        return f'<text text-anchor="middle" font-family="Arial,sans-serif" font-size="{size:.1f}" font-weight="900" fill="{color}" stroke="#11151b" stroke-width="{size*.24:.1f}" paint-order="stroke" stroke-linejoin="round">{spans}</text>'
    if kind == "caption":
        spans, count = _text_tspans(unit["text"], x1 + size, y1 + size * 1.55, bw - size * 2, size)
        return f'<path d="M{x1:.1f},{y1:.1f} H{x2-size:.1f} L{x2:.1f},{y1+size:.1f} V{y2:.1f} H{x1:.1f}Z" fill="#12161c" fill-opacity=".88" stroke="#d7aa5b" stroke-width="2"/><text font-family="Arial,sans-serif" font-size="{size:.1f}" font-weight="700" fill="#f6f0e4">{spans}</text>'
    if kind == "ui":
        spans, count = _text_tspans(unit["text"], x1 + size * 1.15, y1 + size * 1.75, bw - size * 2.3, size)
        accent = unit.get("accent", "#ff7447")
        return f'<path d="M{x1+size:.1f},{y1:.1f} H{x2:.1f} V{y2-size:.1f} L{x2-size:.1f},{y2:.1f} H{x1:.1f} V{y1+size:.1f}Z" fill="#10151c" fill-opacity=".9" stroke="{esc(accent)}" stroke-width="3"/><path d="M{x1+size:.1f},{y1+size*.55:.1f} H{x2-size:.1f}" stroke="#f6f0e4" stroke-opacity=".26"/><text font-family="Arial,sans-serif" font-size="{size:.1f}" font-weight="750" letter-spacing=".4" fill="#f6f0e4">{spans}</text>'
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    line_count = len(_wrap(unit["text"], max(8, int((bw - size * 2) / (size * .56)))))
    spans, _ = _text_tspans(unit["text"], cx, cy - (line_count - 1) * size * .56, bw - size * 2, size)
    # Reading order perturbs the contour slightly, avoiding repetitive pill geometry.
    wobble = (int(unit.get("reading_order", 1)) % 3 - 1) * size * .12
    path = f'M{x1+size*.7:.1f},{y1:.1f} C{x1+wobble:.1f},{y1+bh*.12:.1f} {x1-wobble:.1f},{y2-bh*.18:.1f} {x1+size*.55:.1f},{y2:.1f} C{x1+bw*.35:.1f},{y2+size*.18:.1f} {x2-size*.3:.1f},{y2-wobble:.1f} {x2:.1f},{y2-bh*.25:.1f} C{x2+size*.12:.1f},{y1+bh*.2:.1f} {x2-size*.5:.1f},{y1+wobble:.1f} {x1+size*.7:.1f},{y1:.1f}Z'
    tail = ""
    if isinstance(unit.get("tail"), list) and len(unit["tail"]) == 2:
        tx, ty = unit["tail"][0] * width, unit["tail"][1] * height
        anchor_y = y2 if ty >= cy else y1
        anchor_x = min(max(tx, x1 + size), x2 - size)
        tail = f'<path d="M{anchor_x-size*.65:.1f},{anchor_y:.1f} Q{tx:.1f},{ty:.1f} {anchor_x+size*.45:.1f},{anchor_y-size*.1:.1f}Z" fill="#f6f0e4" fill-opacity=".92" stroke="#11151b" stroke-width="3" stroke-linejoin="round"/>'
    dash = ' stroke-dasharray="8 6"' if style == "whisper" else ""
    fill = "#edf6f3" if style == "off_panel" else "#f6f0e4"
    opacity = ".88" if style == "whisper" else ".94"
    weight = "600" if style == "whisper" else "720"
    if style == "thought":
        tail = f'<circle cx="{x1+size*.7:.1f}" cy="{y2+size*.35:.1f}" r="{size*.22:.1f}" fill="{fill}" stroke="#11151b" stroke-width="3"/>'
    if style == "belljaw":
        fill, opacity, dash, weight = "#171a1e", ".94", "", "800"
        text_fill = "#f2dfc0"
    else:
        text_fill = "#12151a"
    return f'<path d="{path}" fill="{fill}" fill-opacity="{opacity}" stroke="#11151b" stroke-width="3"{dash}/>{tail}<text text-anchor="middle" font-family="Arial,sans-serif" font-size="{size:.1f}" font-weight="{weight}" fill="{text_fill}">{spans}</text>'


def _panel_svg(panel: dict[str, Any], asset_path: Path, target: Path, width: int, height: int, mode: str = "normal") -> str:
    # The art stays as a direct HTML image and this file remains a transparent,
    # deterministic overlay. Browsers intentionally suppress external resources
    # nested inside SVGs used as images, so layering is the portable path.
    del asset_path, target
    overlays: list[str] = []
    if mode in {"normal", "dialogue-density"}:
        overlays.extend(_lettering(unit, width, height) for unit in sorted(panel.get("lettering_units", []), key=lambda row: row["reading_order"]))
    if mode == "safe-zone":
        colors={"primary_action_silhouette":"#56d7c4","face_eyes":"#f084ae","expressive_hands_weapon_contact":"#ffd36f","equipment_injury_evidence":"#9aa8ff"}
        for zone in panel.get("protected_zones", []):
            box=zone["box"]; color=colors.get(zone["type"],"#56d7c4")
            x1, y1, x2, y2 = _box_px(box, width, height)
            overlays.append(f'<rect x="{x1:.1f}" y="{y1:.1f}" width="{x2-x1:.1f}" height="{y2-y1:.1f}" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-width="5"/><text x="{x1+8:.1f}" y="{y1+26:.1f}" font-family="Arial" font-size="18" font-weight="800" fill="{color}" stroke="#11151b" stroke-width="5" paint-order="stroke">{esc(zone["type"].upper())}</text>')
        for box in panel.get("negative_space_regions", []):
            x1, y1, x2, y2 = _box_px(box, width, height)
            overlays.append(f'<rect x="{x1:.1f}" y="{y1:.1f}" width="{x2-x1:.1f}" height="{y2-y1:.1f}" fill="#ff7447" fill-opacity=".10" stroke="#ff7447" stroke-width="5" stroke-dasharray="12 8"/><text x="{x1+8:.1f}" y="{y1+28:.1f}" font-family="Arial" font-size="18" font-weight="800" fill="#ff9b78" stroke="#11151b" stroke-width="5" paint-order="stroke">NEGATIVE SPACE</text>')
    if mode in {"dialogue-density", "lettering-collision"}:
        units = panel.get("lettering_units", [])
        area = sum((u["box"][2]-u["box"][0])*(u["box"][3]-u["box"][1]) for u in units if u.get("kind") != "sfx" and isinstance(u.get("box"), list))
        for unit in units:
            if not isinstance(unit.get("box"), list):
                continue
            x1, y1, x2, y2 = _box_px(unit["box"], width, height)
            phone_px=float(unit.get("font_scale",.034))*390
            overlays.append(f'<rect x="{x1:.1f}" y="{y1:.1f}" width="{x2-x1:.1f}" height="{y2-y1:.1f}" fill="#ff7447" fill-opacity=".10" stroke="#ffd36f" stroke-width="4"/><circle cx="{x1+18:.1f}" cy="{y1+18:.1f}" r="16" fill="#11151b" stroke="#ffd36f" stroke-width="3"/><text x="{x1+18:.1f}" y="{y1+25:.1f}" text-anchor="middle" font-family="Arial" font-size="19" font-weight="900" fill="#ffd36f">{unit["reading_order"]}</text><text x="{x1+8:.1f}" y="{y2-8:.1f}" font-family="Arial" font-size="17" font-weight="800" fill="#fff" stroke="#11151b" stroke-width="4" paint-order="stroke">{phone_px:.1f}px PHONE</text>')
        spoken=sum(len(u.get("text","").split()) for u in units if u.get("kind")=="dialogue")
        overlays.append(f'<rect x="12" y="12" width="430" height="54" rx="8" fill="#11151b" fill-opacity=".94"/><text x="26" y="46" font-family="Arial" font-size="21" font-weight="800" fill="#ffd36f">AREA {area*100:.1f}% · SPOKEN {spoken} WORDS</text>')
    if mode == "noise":
        clean=panel.get("clean_art",{}); status=clean.get("status","UNRECORDED"); metric=clean.get("result_metrics",{}).get("median_delta",0)
        color="#74e4a5" if status in {"REPAIRED","PASS_NO_REPAIR"} else "#ff7b69"
        overlays.append(f'<rect x="12" y="12" width="520" height="54" rx="8" fill="#11151b" fill-opacity=".94"/><text x="26" y="46" font-family="Arial" font-size="21" font-weight="800" fill="{color}">CLEAN ART {esc(status)} · HF {metric}</text>')
    label = f'{panel["panel_id"]}: {panel["beat"]}'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}"><title>{esc(label)}</title>{"".join(overlays)}</svg>\n'


def _head(title: str, css_href: str) -> str:
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><link rel="stylesheet" href="{esc(css_href)}"></head><body><a class="skip" href="#content">Skip to content</a>'


def _nav(prefix: str) -> str:
    links = [
        ("Hub", f"{prefix}index.html"), ("Phone", f"{prefix}readers/phone.html"), ("Full", f"{prefix}readers/full.html"),
        ("Compact", f"{prefix}readers/compact.html"), ("Action", f"{prefix}readers/action.html"),
        ("Grayscale", f"{prefix}diagnostics/grayscale.html"), ("Safe zones", f"{prefix}diagnostics/safe-zones.html"),
        ("Collisions", f"{prefix}diagnostics/lettering-collisions.html"), ("Density", f"{prefix}diagnostics/dialogue-density.html"),
        ("Clean art", f"{prefix}diagnostics/clean-art.html"), ("Compare", f"{prefix}comparison/index.html"),
        ("Failures", f"{prefix}failures/index.html"), ("Benchmark", f"{prefix}benchmark/index.html"),
        ("Gear", f"{prefix}gear/index.html"), ("Future cast", f"{prefix}future-cast/index.html"), ("Evidence", f"{prefix}evidence/index.html"),
    ]
    return '<nav class="nav" aria-label="Premium R&amp;D"><strong>EMBER LATTICE</strong>' + "".join(f'<a href="{href}">{label}</a>' for label, href in links) + '</nav>'


def _foot() -> str:
    return '<footer class="footer">Deterministic SVG-first premium R&amp;D review surface.</footer></main></body></html>\n'


def _reader_page(title: str, panels: list[dict[str, Any]], art_hrefs: dict[str, str], overlay_hrefs: dict[str, str], css_href: str, prefix: str, mode: str) -> str:
    if mode == "action":
        panels = [panel for panel in panels if panel["action"]]
    if mode == "compact":
        body = '<section class="compact-grid">' + "".join(f'<figure id="{esc(panel["panel_id"])}">{_art_stack(art_hrefs[panel["panel_id"]], overlay_hrefs[panel["panel_id"]], panel["beat"])}<figcaption>P{panel["order"]:03d} · {esc(panel["density"])} · {esc(panel["beat"])}</figcaption></figure>' for panel in panels) + '</section>'
    else:
        body = f'<section class="reader {mode}">' + "".join(f'<figure class="panel{" deep-gutter" if panel["order"] in {1,29,37,44,46,52} else ""}" id="{esc(panel["panel_id"])}" data-panel-order="{panel["order"]}">{_art_stack(art_hrefs[panel["panel_id"]], overlay_hrefs[panel["panel_id"]], panel["beat"])}<figcaption>P{panel["order"]:03d} · {esc(panel["density"])} · {"action" if panel["action"] else "story"}</figcaption></figure>' for panel in panels) + '</section>'
    return _head(title, css_href) + _nav(prefix) + f'<main class="shell" id="content"><header class="hero"><p class="eyebrow">CH01 premium vertical slice</p><h1>{esc(title)}</h1><p class="lede">{len(panels)} panels · source art remains separate from deterministic vector lettering and UI.</p></header>{body}' + _foot()


def _diagnostic_page(title: str, panels: list[dict[str, Any]], art_hrefs: dict[str, str], overlay_hrefs: dict[str, str], css_href: str, grayscale: bool = False) -> str:
    body = '<section class="compact-grid">' + "".join(f'<figure>{_art_stack(art_hrefs[p["panel_id"]], overlay_hrefs[p["panel_id"]], title, grayscale)}<figcaption>P{p["order"]:03d} · {esc(p["density"])}</figcaption></figure>' for p in panels) + '</section>'
    return _head(title, css_href) + _nav("../") + f'<main class="shell" id="content"><header class="hero"><p class="eyebrow">Diagnostic</p><h1>{esc(title)}</h1></header>{body}' + _foot()


def build_site(manifest: dict[str, Any], rubric: dict[str, Any], content_root: Path, output_root: Path) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    width, height = manifest["project"]["canvas"]["width"], manifest["project"]["canvas"]["height"]
    assets = {row["asset_id"]: row for row in manifest["assets"]}
    summary = rubric_summary(rubric, manifest)
    selected = manifest.get("recommendation", {}).get("selected_workflow_id") or (summary["winner"] or {}).get("workflow_id")
    workflow_ids = [row["workflow_id"] for row in manifest["workflows"]]
    if selected not in workflow_ids:
        raise ValueError("recommendation.selected_workflow_id must be a registered workflow")
    generated: list[Path] = []

    def emit_text(relative: str, value: str) -> Path:
        target = output_root / relative
        write_text(target, value)
        generated.append(target)
        return target

    def emit_json(relative: str, value: Any) -> Path:
        target = output_root / relative
        write_json(target, value)
        generated.append(target)
        return target

    emit_text("assets/premium.css", CSS)
    normal_hrefs: dict[str, str] = {}
    reader_art_hrefs: dict[str, str] = {}
    diagnostic_art_hrefs: dict[str, str] = {}
    diagnostic_hrefs: dict[str, dict[str, str]] = {key: {} for key in ("grayscale", "safe-zone", "lettering-collision", "dialogue-density", "noise")}
    original_lettering_hrefs: dict[str, str] = {}
    variant_hrefs: dict[str, dict[str, str]] = {workflow_id: {} for workflow_id in workflow_ids}
    comparison_art_hrefs: dict[str, dict[str, str]] = {workflow_id: {} for workflow_id in workflow_ids}
    for panel in manifest["panels"]:
        panel_id = panel["panel_id"]
        for workflow_id in workflow_ids:
            target = output_root / "panels" / workflow_id / f"{panel_id}.svg"
            asset_path = resolve_under(content_root, assets[panel["variants"][workflow_id]]["path"], "asset.path")
            emit_text(str(target.relative_to(output_root)).replace("\\", "/"), _panel_svg(panel, asset_path, target, width, height, "normal"))
            variant_hrefs[workflow_id][panel_id] = f"../panels/{workflow_id}/{panel_id}.svg"
            comparison_art_hrefs[workflow_id][panel_id] = rel_href(_leaf_art_path(asset_path), output_root / "comparison")
        original_panel = dict(panel)
        original_panel["lettering_units"] = panel.get("original_lettering_units", [])
        original_target = output_root / "panels" / "original-lettering" / f"{panel_id}.svg"
        emit_text(str(original_target.relative_to(output_root)).replace("\\", "/"), _panel_svg(original_panel, original_target, original_target, width, height, "normal"))
        original_lettering_hrefs[panel_id] = f"../panels/original-lettering/{panel_id}.svg"
        normal_hrefs[panel_id] = f"../panels/{selected}/{panel_id}.svg"
        selected_asset = resolve_under(content_root, assets[panel["variants"][selected]]["path"], "asset.path")
        selected_art = _leaf_art_path(selected_asset)
        reader_art_hrefs[panel_id] = rel_href(selected_art, output_root / "readers")
        diagnostic_art_hrefs[panel_id] = rel_href(selected_art, output_root / "diagnostics")
        for mode, folder in (("grayscale", "grayscale"), ("safe-zone", "safe-zone"), ("lettering-collision", "lettering-collision"), ("dialogue-density", "dialogue-density"), ("noise", "noise")):
            target = output_root / "diagnostics" / folder / f"{panel_id}.svg"
            emit_text(str(target.relative_to(output_root)).replace("\\", "/"), _panel_svg(panel, selected_asset, target, width, height, mode))
            diagnostic_hrefs[mode][panel_id] = f"{folder}/{panel_id}.svg"

    for mode in ("phone", "full", "compact", "action"):
        emit_text(f"readers/{mode}.html", _reader_page(f"{mode.title()} reader", manifest["panels"], reader_art_hrefs, normal_hrefs, "../assets/premium.css", "../", mode))
    for mode, page_name, title in (("grayscale", "grayscale", "Grayscale / value review"), ("safe-zone", "safe-zones", "Negative-space and protected-subject review"), ("lettering-collision", "lettering-collisions", "Lettering collision and reading-order review"), ("dialogue-density", "dialogue-density", "Dialogue density and phone typography review"), ("noise", "clean-art", "Clean-art / high-frequency noise review")):
        emit_text(f"diagnostics/{page_name}.html", _diagnostic_page(title, manifest["panels"], diagnostic_art_hrefs, diagnostic_hrefs[mode], "../assets/premium.css", mode == "grayscale"))

    comparisons = []
    for panel in manifest["panels"]:
        panel_id=panel["panel_id"]
        art=comparison_art_hrefs[selected][panel_id]
        original=_art_stack(art, original_lettering_hrefs[panel_id], "Original lettering: "+panel["beat"])
        revised=_art_stack(art, variant_hrefs[selected][panel_id], "Revised lettering: "+panel["beat"])
        comparisons.append(f'<section class="card"><h2>P{panel["order"]:03d} · {esc(panel["beat"])}</h2><div class="comparison"><article><p class="tag">Approved prior lettering</p>{original}</article><article><p class="tag">Editorial revision</p>{revised}</article></div></section>')
    emit_text("comparison/index.html", _head("Original versus revised lettering", "../assets/premium.css") + _nav("../") + '<main class="shell" id="content"><header class="hero"><p class="eyebrow">Same art · editable overlays</p><h1>Original versus revised</h1><p class="lede">All 52 panels compare the approved prior overlay against the editorial relettering on identical selected art.</p></header>' + "".join(comparisons) + _foot())

    failure_cards = []
    for failure in manifest["failures"]:
        failed = assets[failure["failed_asset_id"]]
        failed_path = resolve_under(content_root, failed["path"], "failure.failed_asset.path")
        failed_href = rel_href(failed_path, output_root / "failures")
        repaired_html = '<p class="warn">No accepted repair yet.</p>'
        if failure.get("repaired_asset_id"):
            repaired = assets[failure["repaired_asset_id"]]
            repaired_path = resolve_under(content_root, repaired["path"], "failure.repaired_asset.path")
            repaired_leaf = _leaf_art_path(repaired_path)
            repaired_html = f'<img loading="lazy" src="{esc(rel_href(repaired_leaf, output_root / "failures"))}" alt="Repaired output">'
        failure_cards.append(f'<article class="card"><p class="tag">{esc(failure["failure_class"])} · {esc(failure["status"])}</p><h2>{esc(failure["failure_id"])}</h2><div class="comparison"><figure><img loading="lazy" src="{esc(failed_href)}" alt="Preserved failed output"><figcaption>Preserved pre-repair</figcaption></figure><figure>{repaired_html}<figcaption>Accepted repair</figcaption></figure></div><p><strong>Smallest changed instruction:</strong> {esc(failure["changed_instruction"])}</p><p><strong>Frozen:</strong> {esc(", ".join(failure["frozen_variables"]))}</p><p><strong>Review:</strong> {esc(failure.get("visual_review_result", "registered repair evidence"))}</p></article>')
    if not failure_cards:
        failure_cards.append('<article class="card"><p class="pass">No failed outputs are registered.</p></article>')
    emit_text("failures/index.html", _head("Failure and repair gallery", "../assets/premium.css") + _nav("../") + '<main class="shell" id="content"><header class="hero"><p class="eyebrow">Correction evidence</p><h1>Failure and repair gallery</h1><p class="lede">Failures remain hash-pinned and visible; repairs declare the smallest changed instruction and frozen variables.</p></header>' + "".join(failure_cards) + _foot())

    gear_path = content_root / "production/reimaginings/ember-lattice/premium-rd/gear-item-bible.json"
    cast_path = content_root / "production/reimaginings/ember-lattice/premium-rd/future-cast-bible.json"
    if gear_path.is_file():
        gear = read_json(gear_path)
        family_cards=[]
        for index,family in enumerate(gear["faction_design_families"],1):
            href=rel_href(content_root/f"production/reimaginings/ember-lattice/premium-rd/concepts/gear/family-{index:02d}.svg",output_root/"gear")
            family_cards.append(f'<article class="card"><img class="concept" loading="lazy" src="{esc(href)}" alt="Text-free {esc(family["name"])} equipment concept"><p class="tag">{esc(" · ".join(family["palette"]))}</p><h2>{esc(family["name"])}</h2><p>{esc(family["silhouette"])}</p><p><strong>Materials:</strong> {esc(", ".join(family["materials"]))}</p><p><strong>Upgrade grammar:</strong> {esc(family["upgrade_language"])}</p><p><strong>Cost:</strong> {esc(family["tradeoff"])}</p></article>')
        chain_cards=[]; item_map={i["item_id"]:i for i in gear["items"]}
        for chain in gear["evolution_chains"]:
            stages="".join(f'<li><strong>{esc(item_map[s]["name"])}</strong> — {esc(item_map[s]["mechanical_benefit"])} <span class="warn">Cost: {esc(item_map[s]["explicit_limitation_or_cost"])}</span></li>' for s in chain["stages"])
            chain_cards.append(f'<article class="card"><p class="tag">Three-stage evolution</p><h2>{esc(chain["purpose"])}</h2><ol>{stages}</ol><p>{esc(chain["branch_rule"])}</p></article>')
        item_rows="".join(f'<tr><td>{esc(i["name"])}</td><td>{esc(i["category"])} / {esc(i["slot"])}</td><td>{esc(i["mechanical_benefit"])}</td><td>{esc(i["explicit_limitation_or_cost"])}</td><td>{esc(i["introduction_window"])}</td></tr>' for i in gear["items"])
        gear_html=_head("Gear and progression bible","../assets/premium.css")+_nav("../")+f'<main class="shell" id="content"><header class="hero"><p class="eyebrow">Forward design reservoir</p><h1>Gear, items, and upgrades</h1><p class="lede">{gear["counts"]["items"]} named items · {gear["counts"]["evolution_chains"]} evolution chains · {gear["counts"]["build_archetypes"]} build archetypes · {gear["counts"]["boss_reward_families"]} boss/reward families. Function changes silhouette; glow never substitutes for design.</p></header><section><h2>Faction material languages</h2><div class="grid">{"".join(family_cards)}</div></section><section><h2>Signature evolution chains</h2><div class="grid">{"".join(chain_cards)}</div></section><section class="card"><h2>Complete item register</h2><div style="overflow:auto"><table><thead><tr><th>Item</th><th>Category / slot</th><th>Tactical benefit</th><th>Explicit cost</th><th>Window</th></tr></thead><tbody>{item_rows}</tbody></table></div></section>'+_foot()
        emit_text("gear/index.html",gear_html)
    else:
        emit_text("gear/index.html",_head("Gear bible unavailable","../assets/premium.css")+_nav("../")+'<main class="shell" id="content"><header class="hero"><h1>Gear bible unavailable</h1><p class="lede">This generic benchmark fixture does not include the Ember Lattice world-design reservoir.</p></header>'+_foot())
    if cast_path.is_file():
        cast=read_json(cast_path); cards=[]
        for index,char in enumerate(cast["characters"],1):
            href=rel_href(content_root/f"production/reimaginings/ember-lattice/premium-rd/concepts/characters/future-{index:02d}.svg",output_root/"future-cast")
            cards.append(f'<article class="card"><img class="concept" loading="lazy" src="{esc(href)}" alt="Text-free silhouette concept for {esc(char["name"])}"><p class="tag">{esc(char["faction"])} · {esc(char["introduction_window"])}</p><h2>{esc(char["name"])}</h2><p>{esc(char["narrative_role"])}</p><p><strong>Silhouette:</strong> {esc(char["silhouette"])}</p><p><strong>Signature:</strong> {esc(char["signature_gear"])}</p><p><strong>Grammar:</strong> {esc(char["combat_cultivation_grammar"])}</p><p><strong>Pressure:</strong> {esc(char["relationship_pressure"])}</p><p><strong>Avoid:</strong> {esc(char["prohibited_tropes_or_similarities"])}</p></article>')
        cast_html=_head("Future cast bible","../assets/premium.css")+_nav("../")+f'<main class="shell" id="content"><header class="hero"><p class="eyebrow">Forward reservoir · CH01 unchanged</p><h1>Future cast</h1><p class="lede">{cast["counts"]["characters"]} adult allies, rivals, mentors, craftspeople, officials, antagonists, and morally ambiguous operators. Text labels remain HTML overlays; concept SVGs contain no baked-in text.</p></header><section class="grid">{"".join(cards)}</section>'+_foot()
        emit_text("future-cast/index.html",cast_html)
    else:
        emit_text("future-cast/index.html",_head("Future cast unavailable","../assets/premium.css")+_nav("../")+'<main class="shell" id="content"><header class="hero"><h1>Future cast unavailable</h1><p class="lede">This generic benchmark fixture does not include the Ember Lattice future-cast reservoir.</p></header>'+_foot())

    score_rows = "".join(f'<tr><td>{esc(row["label"])}</td><td>{row["median_score"]:.3f}</td><td>{row["weakest_panel_score"]:.3f}</td><td>{row["mean_score"]:.3f}</td><td>{row["hard_failure_count"]}</td></tr>' for row in summary["workflows"])
    criterion_rows = "".join(f'<tr><td>{esc(row["label"])}</td><td>{esc(row["criterion_id"])}</td><td>{float(row["weight"]):.4f}</td></tr>' for row in rubric["criteria"])
    emit_text("benchmark/index.html", _head("Blind normalized benchmark", "../assets/premium.css") + _nav("../") + f'<main class="shell" id="content"><header class="hero"><p class="eyebrow">Complete-set scoring</p><h1>Blind / normalized rubric</h1><p class="lede">Winner: {esc((summary["winner"] or {}).get("label", "none eligible"))}. Median and weakest-panel scores are both exposed; hard failures disqualify a route.</p></header><section class="card"><h2>Workflow results</h2><table><thead><tr><th>Workflow</th><th>Median</th><th>Weakest</th><th>Mean</th><th>Hard failures</th></tr></thead><tbody>{score_rows}</tbody></table></section><section class="card"><h2>Locked criteria</h2><table><thead><tr><th>Criterion</th><th>ID</th><th>Weight</th></tr></thead><tbody>{criterion_rows}</tbody></table></section>' + _foot())

    elapsed = sum(float(row["measured_elapsed_seconds"]) for row in manifest["render_records"])
    known_cost = sum(float(row["monetary_cost"]) for row in manifest["render_records"] if row.get("monetary_cost") is not None)
    unknown_costs = sum(row.get("monetary_cost") is None for row in manifest["render_records"])
    record_rows = []
    for record in manifest["render_records"]:
        output = assets[record["output_asset_id"]]
        record_rows.append(f'<tr><td>{esc(record["record_id"])}</td><td>{esc(record["workflow_id"])}</td><td>{esc(record["panel_id"])}</td><td><code>{esc(record["prompt_hash"])}</code><details><summary>Exact prompt</summary><pre>{esc(record["exact_prompt"])}</pre></details></td><td><code>{esc(record["output_hash"])}</code><br>{esc(output["path"])}</td><td>{float(record["measured_elapsed_seconds"]):.3f}s</td><td>{"unknown" if record.get("monetary_cost") is None else f'{float(record["monetary_cost"]):.4f}'}</td><td>{esc(record["review_status"])}</td></tr>')
    document_cards = []
    for document in manifest.get("evidence_documents", []):
        source = resolve_under(content_root, document["path"], "evidence_document.path")
        href = rel_href(source, output_root / "evidence")
        document_cards.append(f'<a class="card" href="{esc(href)}"><span class="tag">{esc(document["category"])}</span><h3>{esc(document["title"])}</h3><code>{esc(document["sha256"])}</code></a>')
    if not document_cards:
        document_cards.append('<article class="card"><p class="warn">No supplemental evidence documents registered.</p></article>')
    recommendation = manifest.get("recommendation", {})
    evidence_html = _head("Prompt, output, cost, and evidence reconciliation", "../assets/premium.css") + _nav("../") + f'<main class="shell" id="content"><header class="hero"><p class="eyebrow">Reproducibility evidence</p><h1>Prompt / output reconciliation</h1><p class="lede">Every output hash reconciles to a registered asset. Prompt hashes are recomputed from exact UTF-8 prompt bytes.</p><p><span class="pill">elapsed {elapsed:.3f}s</span><span class="pill">known direct cost {known_cost:.4f}</span><span class="pill">unknown cost records {unknown_costs}</span></p></header><section class="card"><h2>Timing and cost records</h2><div style="overflow:auto"><table><thead><tr><th>Record</th><th>Workflow</th><th>Panel</th><th>Prompt</th><th>Output</th><th>Elapsed</th><th>Cost</th><th>Review</th></tr></thead><tbody>{"".join(record_rows)}</tbody></table></div></section><section><h2>Research, story, progression, route, and integrity evidence</h2><div class="grid">{"".join(document_cards)}</div></section><section class="card"><h2>Licensing and reproducibility</h2><p>{esc(recommendation.get("licensing_reproducibility", "Not recorded"))}</p><h2>Provider limitations</h2><p>{esc(recommendation.get("provider_limitations", "Not recorded"))}</p></section>' + _foot()
    emit_text("evidence/index.html", evidence_html)

    section_links = [
        ("Read CH01", "readers/phone.html", "Phone-first continuous reader"), ("Full size", "readers/full.html", "Full source-resolution SVG reader"),
        ("Compact review", "readers/compact.html", "Complete-sequence scanning"), ("Action strip", "readers/action.html", "Causal action beats only"),
        ("Grayscale", "diagnostics/grayscale.html", "Value hierarchy"), ("Safe zones", "diagnostics/safe-zones.html", "Faces, hands, gear, and action protection"),
        ("Lettering collisions", "diagnostics/lettering-collisions.html", "Bounds, reading order, and phone type"), ("Dialogue density", "diagnostics/dialogue-density.html", "Coverage and spoken-word load"),
        ("Clean art", "diagnostics/clean-art.html", "High-frequency noise repair status"), ("Comparison", "comparison/index.html", "Prior versus revised lettering on identical art"),
        ("Failures", "failures/index.html", "Preserved outputs and targeted correction"), ("Benchmark", "benchmark/index.html", "Median and weakest-panel evidence"),
        ("Gear and items", "gear/index.html", "60 tactical items and 12 evolution chains"), ("Future cast", "future-cast/index.html", "12 production-ready character reservoirs"),
        ("Evidence", "evidence/index.html", "Prompts, hashes, timing, cost, research, and story package"),
    ]
    if manifest["project"].get("deliverable") == "premium_ch01":
        optional_links = [
            ("24-panel bakeoff", "benchmark-suite/index.html", "Locked normalized route evaluation"),
            ("Repaired failures", "benchmark-suite/failures/index.html", "Raw failures beside minimum-change repairs"),
            ("Original volume", "../volume/index.html", "Approved baseline and complete ten-chapter release"),
            ("Progression ledger", "../volume/progression.html", "Cross-chapter stats, inventory, quests, and trust"),
        ]
        section_links.extend(row for row in optional_links if (output_root / row[1]).resolve().is_file())
    cards = "".join(f'<a class="card" href="{href}"><span class="tag">{esc(blurb)}</span><h2>{esc(label)}</h2></a>' for label, href, blurb in section_links)
    winner = summary["winner"] or {}
    hub = _head(manifest["project"]["title"], "assets/premium.css") + _nav("") + f'<main class="shell" id="content"><header class="hero"><p class="eyebrow">Premium R&amp;D · {esc(manifest["project"]["chapter"])}</p><h1>{esc(manifest["project"]["title"])}</h1><p class="lede">{esc(recommendation.get("executive_recommendation", "Complete-set evidence determines the route."))}</p><p><span class="pill">{len(manifest["panels"])} panels</span><span class="pill">{len(manifest["workflows"])} workflows</span><span class="pill">winner {esc(winner.get("label", "none"))}</span><span class="pill">weakest {winner.get("weakest_panel_score", 0):.3f}</span></p></header><section class="grid">{cards}</section><section class="card"><h2>Selected production architecture</h2><p>{esc(recommendation.get("architecture", "Not recorded"))}</p><h3>Provider limitations</h3><p>{esc(recommendation.get("provider_limitations", "Not recorded"))}</p><h3>Remaining capability gaps</h3><p>{esc(recommendation.get("remaining_gaps", "None recorded"))}</p></section>' + _foot()
    emit_text("index.html", hub)
    emit_json("rubric-summary.json", summary)

    ledger_rows = []
    for target in sorted(generated, key=lambda p: p.relative_to(output_root).as_posix()):
        ledger_rows.append({"path": target.relative_to(output_root).as_posix(), "sha256": sha256_file(target), "bytes": target.stat().st_size})
    ledger = {"schema": "PremiumBuildLedger/1.0", "build_id": manifest["project"]["build_id"], "selected_workflow_id": selected, "files": ledger_rows}
    write_json(output_root / "build-ledger.json", ledger)
    return {"status": "PASS", "output_root": str(output_root), "selected_workflow_id": selected, "file_count": len(ledger_rows) + 1, "ledger": ledger}
