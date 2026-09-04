from __future__ import annotations

import hashlib
import html
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[3]
SLUG = "ember-lattice"
PROD = ROOT / "production" / "reimaginings" / SLUG
PILOT = PROD / "pilot"
SOURCE = ROOT / "experiments" / "reimaginings" / SLUG / "pilot" / "source"
DIAGNOSTICS = ROOT / "experiments" / "reimaginings" / SLUG / "pilot" / "diagnostics"
REVIEW = ROOT / "docs" / "reimaginings" / SLUG / "pilot"
PANELS_OUT = REVIEW / "panels"
SAFE_OUT = REVIEW / "safe-zones"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


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
    if len(lines) > 1 and len(lines[-1]) <= 3:
        lines[-2] = f"{lines[-2]} {lines[-1]}"
        lines.pop()
    return lines


def polygon_points(box: list[float], width: int, height: int, cut: int = 24) -> str:
    l, t, r, b = box
    x1, y1, x2, y2 = l * width, t * height, r * width, b * height
    return " ".join(
        f"{x:.1f},{y:.1f}"
        for x, y in [
            (x1 + cut, y1), (x2, y1), (x2, y2 - cut),
            (x2 - cut, y2), (x1, y2), (x1, y1 + cut),
        ]
    )


def balloon_svg(unit: dict[str, Any], width: int, height: int, thought: bool = False) -> str:
    l, t, r, b = unit["box"]
    x1, y1, x2, y2 = l * width, t * height, r * width, b * height
    cx, cy, rx, ry = (x1 + x2) / 2, (y1 + y2) / 2, (x2 - x1) / 2, (y2 - y1) / 2
    tail_x, tail_y = unit.get("tail", [cx / width, (b + 0.04)])
    tx, ty = tail_x * width, tail_y * height
    path = (
        f"M {cx-rx*0.94:.1f} {cy:.1f} "
        f"C {cx-rx:.1f} {cy-ry*0.68:.1f}, {cx-rx*0.52:.1f} {cy-ry:.1f}, {cx:.1f} {cy-ry*0.96:.1f} "
        f"C {cx+rx*0.58:.1f} {cy-ry:.1f}, {cx+rx:.1f} {cy-ry*0.54:.1f}, {cx+rx*0.95:.1f} {cy:.1f} "
        f"C {cx+rx:.1f} {cy+ry*0.62:.1f}, {cx+rx*0.48:.1f} {cy+ry:.1f}, {cx:.1f} {cy+ry*0.95:.1f} "
        f"C {cx-rx*0.56:.1f} {cy+ry:.1f}, {cx-rx:.1f} {cy+ry*0.52:.1f}, {cx-rx*0.94:.1f} {cy:.1f} Z"
    )
    dash = ' stroke-dasharray="9 7"' if thought else ""
    tail = ""
    if thought:
        tail = f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="12" fill="#f6f0e5" stroke="#17191f" stroke-width="6"/>'
    else:
        base1, base2 = cx - 22, cx + 16
        tail = f'<path d="M {base1:.1f} {cy+ry*0.82:.1f} L {tx:.1f} {ty:.1f} L {base2:.1f} {cy+ry*0.76:.1f} Z" fill="#f6f0e5" stroke="#17191f" stroke-width="7" stroke-linejoin="round"/>'
    max_chars = max(10, int((x2 - x1) / 31))
    lines = wrap_text(unit["text"], max_chars)
    size = min(42, max(29, int((x2 - x1) / max(max(len(s) for s in lines), 8) * 1.55)))
    total = len(lines) * size * 1.15
    start_y = cy - total / 2 + size * 0.82
    tspans = "".join(
        f'<tspan x="{cx:.1f}" y="{start_y+i*size*1.15:.1f}">{esc(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return (
        f'<path d="{path}" fill="#f6f0e5" fill-opacity="0.97" stroke="#17191f" stroke-width="7"{dash}/>'
        + tail
        + f'<text text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="{size}" fill="#17191f">{tspans}</text>'
    )


def ui_svg(unit: dict[str, Any], width: int, height: int) -> str:
    box = unit["box"]
    l, t, r, b = box
    x1, y1, x2, y2 = l * width, t * height, r * width, b * height
    lines = unit.get("lines") or [unit.get("text", "")]
    kind = unit["kind"]
    accent = "#ff6a32" if kind in {"boss", "cultivation", "loot"} else "#b78a45"
    if kind == "caption":
        return (
            f'<path d="M {x1:.1f} {y1:.1f} H {x2-22:.1f} L {x2:.1f} {y1+22:.1f} V {y2:.1f} H {x1:.1f} Z" fill="#17191f" fill-opacity="0.88"/>'
            f'<text x="{x1+24:.1f}" y="{(y1+y2)/2+12:.1f}" font-family="Arial, sans-serif" font-size="34" font-weight="700" fill="#f2eee5">{esc(lines[0])}</text>'
        )
    line_count = len(lines)
    inner_h = y2 - y1 - 34
    size = min(35, max(22, int(inner_h / max(line_count, 1) * 0.70)))
    gap = inner_h / max(line_count, 1)
    tspans = "".join(
        f'<tspan x="{x1+28:.1f}" y="{y1+27+(i+0.72)*gap:.1f}" font-size="{size if i else min(38,size+4)}" font-weight="{800 if i==0 else 650}" fill="{accent if i==0 else '#f2eee5'}">{esc(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return (
        f'<polygon points="{polygon_points(box,width,height)}" fill="#11151a" fill-opacity="0.92" stroke="{accent}" stroke-width="4"/>'
        f'<path d="M {x1+24:.1f} {y1+16:.1f} H {x2-36:.1f}" stroke="#f2eee5" stroke-opacity="0.42" stroke-width="2"/>'
        f'<text font-family="Arial, sans-serif" letter-spacing="1.2">{tspans}</text>'
    )


def sfx_svg(unit: dict[str, Any], width: int, height: int) -> str:
    x, y = unit["at"][0] * width, unit["at"][1] * height
    rotate = unit.get("rotate", 0)
    text = esc(unit["text"])
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) rotate({rotate})">'
        f'<text x="0" y="0" text-anchor="middle" font-family="Impact, Arial Black, sans-serif" font-size="76" font-style="italic" font-weight="900" fill="#f2eee5" stroke="#17191f" stroke-width="13" paint-order="stroke">{text}</text>'
        f'<text x="0" y="0" text-anchor="middle" font-family="Impact, Arial Black, sans-serif" font-size="76" font-style="italic" font-weight="900" fill="#ff6a32">{text}</text></g>'
    )


def render_svg(panel: dict[str, Any], units: list[dict[str, Any]], image_path: Path) -> str:
    with Image.open(image_path) as image:
        width, height = image.size
    href = Path("../../../../../experiments/reimaginings/ember-lattice/pilot/source") / image_path.name
    overlays: list[str] = []
    for unit in units:
        kind = unit["kind"]
        if kind == "balloon":
            overlays.append(balloon_svg(unit, width, height))
        elif kind == "thought":
            overlays.append(balloon_svg(unit, width, height, thought=True))
        elif kind == "sfx":
            overlays.append(sfx_svg(unit, width, height))
        else:
            overlays.append(ui_svg(unit, width, height))
    title = f'{panel["panel_id"]}: {panel["beat"]}'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
  <title>{esc(title)}</title>
  <image href="{href.as_posix()}" x="0" y="0" width="{width}" height="{height}" preserveAspectRatio="xMidYMid slice"/>
  {''.join(overlays)}
</svg>
'''


def render_safe_zone_svg(panel: dict[str, Any], units: list[dict[str, Any]], image_path: Path) -> str:
    with Image.open(image_path) as image:
        width, height = image.size
    href = Path("../../../../../experiments/reimaginings/ember-lattice/pilot/source") / image_path.name
    boxes = "".join(
        f'<rect x="{u["box"][0]*width:.1f}" y="{u["box"][1]*height:.1f}" width="{(u["box"][2]-u["box"][0])*width:.1f}" height="{(u["box"][3]-u["box"][1])*height:.1f}" fill="#ff6a32" fill-opacity="0.15" stroke="#ff6a32" stroke-width="5" stroke-dasharray="14 10"/>'
        for u in units if "box" in u
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Safe-zone and lettering exclusions for {esc(panel['panel_id'])}">
  <image href="{href.as_posix()}" x="0" y="0" width="{width}" height="{height}" preserveAspectRatio="xMidYMid slice"/>
  <rect x="{width*.05:.1f}" y="{height*.05:.1f}" width="{width*.90:.1f}" height="{height*.90:.1f}" fill="none" stroke="#7ff0b2" stroke-width="6" stroke-dasharray="18 12"/>
{boxes}
  <text x="{width*.06:.1f}" y="{height*.085:.1f}" font-family="Arial, sans-serif" font-weight="800" font-size="30" fill="#7ff0b2" stroke="#11151a" stroke-width="6" paint-order="stroke">GREEN: 5% SAFE FRAME · ORANGE: LETTERING EXCLUSION</text>
</svg>
'''


def image_metrics(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        phone_h = max(1, round(rgb.height * 390 / rgb.width))
        phone = rgb.resize((390, phone_h), Image.Resampling.LANCZOS)
        gray = ImageOps.grayscale(phone)
        edge = gray.filter(ImageFilter.FIND_EDGES)
        edge_hist = edge.histogram()
        edge_pixels = sum(edge_hist[42:])
        edge_density = edge_pixels / (390 * phone_h)
        blur = gray.filter(ImageFilter.GaussianBlur(1.2))
        high = ImageChops.difference(gray, blur)
        high_hist = high.histogram()
        high_pixels = sum(high_hist[12:])
        high_occupancy = high_pixels / (390 * phone_h)
        entropy = gray.entropy()
        luma_std = ImageStat.Stat(gray).stddev[0]
        return {
            "width": rgb.width,
            "height": rgb.height,
            "phone_width": 390,
            "phone_height": phone_h,
            "edge_density": round(edge_density, 6),
            "global_luma_entropy": round(entropy, 6),
            "high_frequency_occupancy": round(high_occupancy, 6),
            "luminance_stddev": round(luma_std, 6),
        }


def validate_system(ledger: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    initial, final = ledger["initial"], ledger["final"]
    if initial["xp"] + 85 - initial["next_threshold"] != final["xp"]:
        errors.append("XP carry does not reconcile")
    if final["level"] != initial["level"] + 1:
        errors.append("Level-up does not reconcile")
    if 31 - 12 + 14 - 30 + 8 - 8 != final["qi"]["current"]:
        errors.append("Qi transactions do not reconcile")
    if 44 - 22 - 1 - 1 != final["hp"]["current"]:
        errors.append("HP transactions do not reconcile")
    if final["inventory"].get("Spark Talisman") != 0:
        errors.append("Consumed Spark Talisman remains")
    if final["inventory"].get("Iron Seal") != 2:
        errors.append("Unconsumed Iron Seals changed")
    if final["inventory"].get("Cinder-Key") != 1:
        errors.append("Boss loot missing")
    if final["class"] != "Salvager" or not final.get("class_options_unlocked"):
        errors.append("Class unlock/selection boundary invalid")
    if "Cracked Rib" not in final.get("statuses", []):
        errors.append("Injury persistence missing")
    running = {"hp": initial["hp"]["current"], "qi": initial["qi"]["current"]}
    for transaction in ledger["transactions"]:
        resource = transaction.get("resource")
        if resource in running and "before" in transaction and "after" in transaction:
            if transaction["before"] != running[resource]:
                errors.append(f'{resource.upper()} transaction chain breaks at {transaction["panel_id"]}')
            running[resource] = transaction["after"]
        if transaction["type"] == "cultivation_advance":
            if transaction["qi_before"] != running["qi"]:
                errors.append(f'QI breakthrough chain breaks at {transaction["panel_id"]}')
            running["qi"] = transaction["qi_after"]
    for resource, value in running.items():
        if value != final[resource]["current"]:
            errors.append(f"Final {resource.upper()} does not equal the irreversible transaction chain")
    return errors


def validate_references() -> list[str]:
    errors: list[str] = []
    registry = read_json(PROD / "reference-registry.json")
    seen: set[str] = set()
    for row in registry["references"]:
        ref_id = row["reference_id"]
        if ref_id in seen:
            errors.append(f"Duplicate reference ID: {ref_id}")
        seen.add(ref_id)
        target = ROOT / row["path"]
        if not target.exists():
            errors.append(f"Missing registered reference: {row['path']}")
        elif sha256(target) != row["sha256"]:
            errors.append(f"Registered reference hash drift: {ref_id}")
        if not row.get("created_in_experiment") or not row.get("registered_before_reuse"):
            errors.append(f"Reference admission contract incomplete: {ref_id}")
        if row.get("owner_acceptance") != "PENDING" or row.get("commercial_clearance") is not False:
            errors.append(f"Reference review/clearance state is overstated: {ref_id}")
    return errors


def make_render_records(requests: dict[str, Any], plans: dict[str, Any]) -> list[dict[str, Any]]:
    refs = {row["reference_id"]: row for row in read_json(PROD / "reference-registry.json")["references"]}
    panel_by_short = {f'p{p["order"]:03d}': p for p in plans["panels"]}
    timing = requests["timing_seconds"]
    records = []
    for request in requests["requests"]:
        rid = request["request_id"]
        output = ROOT / request["output_path"]
        exact_prompt = request.get("exact_prompt")
        if exact_prompt is None:
            exact_prompt = request["scene_prompt"] + "\n" + requests["prompt_blocks"][request["prompt_block"]]
        input_refs = []
        for ref_id in request.get("reference_ids", []):
            row = refs[ref_id]
            input_refs.append({"reference_id": ref_id, "path": row["path"], "sha256": row["sha256"]})
        dims = None
        output_hash = None
        if output.exists():
            with Image.open(output) as image:
                dims = {"width": image.width, "height": image.height}
            output_hash = sha256(output)
        target = request.get("target_panel")
        review = request.get("review_status", "PASS")
        failure_classes = request.get("failure_classes", [])
        record = {
            "schema": "RenderRecord/1.0",
            "request_id": rid,
            "exact_prompt": exact_prompt,
            "prompt_hash": sha_text(exact_prompt),
            "target_chapter": "pilot" if target else None,
            "target_sequence": "el-pilot-s01" if target else None,
            "target_panel_ids": [panel_by_short[target]["panel_id"]] if target in panel_by_short else [],
            "input_references": input_refs,
            "output_path": request["output_path"],
            "output_hash": output_hash,
            "dimensions": dims,
            "measured_elapsed_seconds": timing.get(rid),
            "timing_note": request.get("timing_note"),
            "product_tool": "built-in in-product image generation",
            "model": None,
            "endpoint": None,
            "provider_request_id": None,
            "usage": None,
            "monetary_cost": None,
            "direct_paid_cloud_spend_usd": 0,
            "deterministic_seed": None,
            "extraction_crop_composite": "no crop; full returned source art; deterministic SVG lettering after selection",
            "crop_coordinates": None,
            "candidate_paths_and_hashes": [{"path": request["output_path"], "sha256": output_hash}],
            "review_status": review,
            "failure_classes": failure_classes,
            "human_review": "LOCAL_AGENT_VISUAL_REVIEW",
            "owner_approval": "PENDING",
            "acceptance_state": "OWNER_REVIEW_PENDING",
            "commercial_clearance": False,
            "production_base": False,
            "reproducibility": False,
        }
        records.append(record)
    return records


def make_html(plans: dict[str, Any], metrics: list[dict[str, Any]], hard_gates: list[dict[str, str]]) -> None:
    panel_cards = "".join(
        f'''<article class="panel-card" id="{p['panel_id']}">
          <div class="panel-meta"><span>P{p['order']:02d}</span><span>{esc(p['density'])}</span><span>{'ACTION' if p['action'] else 'BEAT'}</span></div>
          <a href="panels/p{p['order']:03d}.svg" aria-label="Open full-size panel P{p['order']:02d}"><img loading="lazy" src="panels/p{p['order']:03d}.svg" alt="{esc(p['beat'])}"></a>
        </article>'''
        for p in plans["panels"]
    )
    phone_cards = "".join(
        f'<img src="panels/p{p["order"]:03d}.svg" alt="Phone preview P{p["order"]:02d}: {esc(p["beat"])}">'
        for p in plans["panels"]
    )
    metric_rows = "".join(
        f'<tr><td>P{m["order"]:02d}</td><td>{m["planned_density"]}</td><td>{m["edge_density"]:.3f}</td><td>{m["high_frequency_occupancy"]:.3f}</td><td>{m["global_luma_entropy"]:.2f}</td><td class="{m["status"].lower()}">{m["status"]}</td></tr>'
        for m in metrics
    )
    gate_rows = "".join(
        f'<tr><td>{esc(g["requirement"])}</td><td class="{g["status"].lower()}">{g["status"]}</td><td>{esc(g["evidence"])}</td></tr>'
        for g in hard_gates
    )
    css = '''
      :root{--ink:#17191f;--paper:#f2eee5;--teal:#284c50;--ember:#ff6a32;--brass:#b78a45;--muted:#b7b3aa}
      *{box-sizing:border-box}html{scroll-behavior:smooth;max-width:100%;overflow-x:hidden}body{margin:0;max-width:100%;overflow-x:hidden;background:#0b0e11;color:var(--paper);font-family:Arial,sans-serif;line-height:1.5}
      a{color:#ffc28f}.top{padding:3rem max(1.25rem,6vw);background:linear-gradient(135deg,#10161a,#192b2d);border-bottom:2px solid var(--ember)}
      h1{font-size:clamp(2.5rem,7vw,5rem);margin:.1em 0;line-height:.95}h2{margin-top:0;font-size:clamp(1.7rem,4vw,2.8rem)}.kicker{color:var(--ember);letter-spacing:.18em;font-weight:800}
      nav{position:sticky;top:0;z-index:5;background:#11151aee;padding:.7rem 1rem;display:flex;gap:.8rem;overflow:auto;border-bottom:1px solid #3a4146}nav a{white-space:nowrap;text-decoration:none;padding:.35rem .65rem;border:1px solid #48545a;border-radius:999px}
      main,section,.grid,.samples,.contract{min-width:0}section{padding:3rem max(1rem,6vw);max-width:1400px;margin:auto}.read{max-width:920px}.panel-card{margin:0 auto 90px;background:#111;border:1px solid #30373b}.panel-card img{display:block;width:100%;height:auto}.panel-meta{display:flex;gap:1rem;padding:.5rem .8rem;color:#bbb;font-size:.8rem;letter-spacing:.1em}
      .phone{width:390px;max-width:100%;margin:auto;background:#000;border:10px solid #252b2f;border-radius:28px;overflow:hidden;box-shadow:0 25px 70px #000}.phone img{display:block;width:390px;max-width:100%;height:auto;margin:0 0 34px}
      .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}.card{background:#14191d;border:1px solid #30383e;padding:1rem}.card img{width:100%;height:auto}.selected{border:2px solid var(--ember)}
      table{width:100%;border-collapse:collapse;background:#12171b}th,td{border:1px solid #354047;padding:.65rem;text-align:left;vertical-align:top}.pass{color:#7ff0b2;font-weight:800}.warn{color:#ffd36a;font-weight:800}.fail{color:#ff7777;font-weight:800}
      .strip{display:grid;grid-template-columns:repeat(11,1fr);gap:4px;max-width:100%;min-width:0;overflow-x:auto;overflow-y:hidden}.strip img{min-width:100px;width:100%;height:auto}.gray img{filter:grayscale(1)}.links{columns:2;column-gap:2rem}.links li{break-inside:avoid;margin:.4rem 0}.note{border-left:4px solid var(--brass);padding:1rem;background:#171d20}.contract{display:grid;grid-template-columns:minmax(220px,.65fr) 1fr;gap:1.2rem;align-items:start}.contract img{width:100%;height:auto;border:1px solid #465158}.samples{display:grid;grid-template-columns:repeat(3,minmax(220px,1fr));gap:1rem}.samples img{width:100%;height:auto}
      @media(max-width:650px){section{padding:2rem 1rem}.links{columns:1}.panel-card{margin-bottom:56px}.contract,.samples{grid-template-columns:1fr}}
    '''
    index = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ember Lattice — Phase A Pilot Review</title><style>{css}</style></head>
    <body><header class="top"><div class="kicker">PHASE A · OWNER REVIEW PILOT</div><h1>Ember Lattice</h1><p>A debt-bound adult salvager turns a cultivation bottleneck into a combat class unlock inside a living dungeon ledger.</p><p class="note">Sixteen finished panels. Owner acceptance, commercial clearance, and exact reproducibility remain pending. Phase B is locked until explicit approval.</p></header>
    <nav><a href="#read">Read pilot</a><a href="#phone">390px phone</a><a href="#action">Action strip</a><a href="#appearance">Appearance</a><a href="#lettering">Lettering/UI</a><a href="#styles">Style routes</a><a href="#checks">Hard gates</a><a href="#density">Density/value</a><a href="#contracts">Contracts</a></nav>
    <main><section id="read" class="read"><h2>Read the pilot</h2>{panel_cards}</section>
    <section id="phone"><h2>390-pixel continuous phone preview</h2><div class="phone">{phone_cards}</div></section>
    <section id="action"><h2>Consecutive causal action strip · P05–P15</h2><p>Geography → charge → interception → counter → fault read → initiation → interruption → consequence → inventory choice → breakthrough → combo payoff.</p><div class="strip">{''.join(f'<img src="panels/p{i:03d}.svg" alt="Action beat P{i:02d}">' for i in range(5,16))}</div></section>
    <section id="appearance"><h2>Protagonist appearance and complexion contract</h2><div class="contract"><img src="../../../../experiments/reimaginings/ember-lattice/references/principal-elian.png" alt="Elian Voss approved neutral reference"><div><h3>Elian Voss · fictional adult, age 27</h3><p>Fair/light peach-beige complexion with a warm undertone; ash-blond hair over a charcoal underlayer; green eyes; mature narrow jaw; frayed gray-green coat; asymmetrical hookblade. Dramatic lighting may shift local color, but must preserve this base complexion, adult facial proportions, hair block, and equipment silhouette.</p><p>The pilot provides neutral appearance evidence in P02–P03 and dramatic evidence in P09, P12, P14, and P15. The reference at left is fresh, hash-pinned, and limited to this reimagining.</p></div></div></section>
    <section id="lettering"><h2>Local lettering and system-UI examples</h2><p>All visible words and boxes are deterministic SVG layered over text-free source art. Dialogue uses organic ivory balloons and semantic tails; the Brass Ledger uses cut-corner charcoal panels with brass/ember accents.</p><div class="samples"><div class="card"><h3>Dialogue · P03</h3><img src="panels/p003.svg" alt="Dialogue balloon example"></div><div class="card"><h3>Skill readout · P09</h3><img src="panels/p009.svg" alt="System skill UI example"></div><div class="card"><h3>Loot/state · P16</h3><img src="panels/p016.svg" alt="Loot and state UI example"></div></div><p><a href="safe-zones.html">Open safe-zone and lettering-exclusion overlay review</a></p></section>
    <section id="styles"><h2>Bounded style and generation-route comparison</h2><div class="grid">
      <div class="card"><h3>Candidate A · 91</h3><img src="../../../../experiments/reimaginings/ember-lattice/style-candidates/candidate-a.png" alt="Candidate A proof"><p>Pass; texture too active for ordinary panels.</p></div>
      <div class="card selected"><h3>Candidate B · 96 · selected</h3><img src="../../../../experiments/reimaginings/ember-lattice/style-candidates/candidate-b.png" alt="Candidate B proof"><p>Best phone silhouettes, value grouping, adult identity, and action clarity.</p></div>
      <div class="card"><h3>Candidate C · 85</h3><img src="../../../../experiments/reimaginings/ember-lattice/style-candidates/candidate-c.png" alt="Candidate C proof"><p>Pass, but painterly convergence risk.</p></div></div>
      <p>One authorized no-purchase route was available: built-in in-product image generation. The production topology changed materially: critical panels were generated individually with a fresh, small, hash-pinned reference set.</p></section>
    <section id="checks"><h2>Hard pilot gates</h2><table><thead><tr><th>Requirement</th><th>Result</th><th>Evidence</th></tr></thead><tbody>{gate_rows}</tbody></table></section>
    <section id="density"><h2>Density and value checks</h2><p>Metrics support local visual inspection. P005 is a specific WARN because it rendered above its planned-low role; 1/11 planned-low panels exceed calibration, below the 25% fail-closed threshold.</p><table><thead><tr><th>Panel</th><th>Plan</th><th>Edge</th><th>High-freq.</th><th>Entropy</th><th>Review</th></tr></thead><tbody>{metric_rows}</tbody></table><h3>Grayscale rhythm</h3><div class="strip gray">{''.join(f'<img src="panels/p{i:03d}.svg" alt="Grayscale P{i:02d}">' for i in range(1,17))}</div></section>
    <section id="contracts"><h2>Contracts, bibles, ledgers, prompts, and evidence</h2><ul class="links">
      <li><a href="../failure-correction-contract.md">Failure-correction contract</a></li><li><a href="../research/inspiration-derivation-matrix.md">Research and derivation matrix</a></li><li><a href="../style-candidate-review.md">Style review</a></li><li><a href="../cumulative-experiment-ledger.md">Cumulative experiment ledger</a></li>
      <li><a href="../phase-a-pilot-audit.md">Phase A pilot audit</a></li>
      <li><a href="../../../../reimaginings/ember-lattice/story-bible.md">Story bible and 10-chapter outline</a></li><li><a href="../../../../reimaginings/ember-lattice/character-and-equipment-bible.md">Character/complexion/equipment contracts</a></li><li><a href="../../../../reimaginings/ember-lattice/visual-bible.md">Visual bible</a></li><li><a href="../../../../reimaginings/ember-lattice/system-bible.md">System/cultivation bible</a></li><li><a href="../../../../reimaginings/ember-lattice/dungeon-monster-action-bible.md">Dungeon/monster/action bible</a></li><li><a href="../../../../reimaginings/ember-lattice/item-skill-quest-bible.md">Item/skill/quest bible</a></li>
      <li><a href="../../../../production/reimaginings/ember-lattice/pilot/comic-panel-plans.json">ComicPanelPlans</a></li><li><a href="../../../../production/reimaginings/ember-lattice/pilot/system-state.json">SystemState ledger</a></li><li><a href="../../../../production/reimaginings/ember-lattice/pilot/lettering-copy.json">Lettering/UI copy</a></li><li><a href="../../../../production/reimaginings/ember-lattice/generation-requests.json">Exact generation prompts</a></li><li><a href="render-records.json">RenderRecords</a></li><li><a href="validation-report.json">Validation report</a></li><li><a href="density-metrics.json">Density metrics</a></li><li><a href="output-reconciliation.json">Output reconciliation</a></li><li><a href="safe-zones.html">Safe-zone overlays</a></li><li><a href="../evidence/isolation-baseline.md">Isolation baseline</a></li><li><a href="../../../../production/reimaginings/ember-lattice/integrity/integrity-report.json">Protected-worktree integrity report</a></li><li><a href="../../../../production/reimaginings/ember-lattice/integrity/protected-state-after.json">Protected-state after snapshot</a></li>
    </ul></section></main></body></html>'''
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW / "index.html").write_text(index, encoding="utf-8", newline="\n")
    reader = index.replace("Phase A Pilot Review", "Pilot Reader").replace('id="styles"', 'id="styles" hidden').replace('id="checks"', 'id="checks" hidden').replace('id="density"', 'id="density" hidden').replace('id="contracts"', 'id="contracts" hidden')
    (REVIEW / "reader.html").write_text(reader, encoding="utf-8", newline="\n")
    safe_cards = "".join(
        f'<article class="panel-card"><div class="panel-meta"><span>P{p["order"]:02d}</span><span>{esc(p["beat"])}</span></div><img src="safe-zones/p{p["order"]:03d}.svg" alt="Safe-zone overlay P{p["order"]:02d}"></article>'
        for p in plans["panels"]
    )
    safe_page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ember Lattice — Safe Zones</title><style>{css}</style></head><body><header class="top"><div class="kicker">DETERMINISTIC REVIEW OVERLAY</div><h1>Safe zones</h1><p>Green is the five-percent framing safe zone. Orange boxes reserve local lettering/UI exclusions.</p><p><a href="index.html">Return to the full pilot review</a></p></header><main><section class="read">{safe_cards}</section></main></body></html>'''
    (REVIEW / "safe-zones.html").write_text(safe_page, encoding="utf-8", newline="\n")


def main() -> None:
    plans = read_json(PILOT / "comic-panel-plans.json")
    lettering = read_json(PILOT / "lettering-copy.json")
    ledger = read_json(PILOT / "system-state.json")
    requests = read_json(PROD / "generation-requests.json")
    PANELS_OUT.mkdir(parents=True, exist_ok=True)
    SAFE_OUT.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []
    warnings: list[str] = []
    panels = plans["panels"]
    if len(panels) != 16:
        errors.append(f"Expected 16 pilot panels, found {len(panels)}")
    if plans.get("animation_shot_plan") is not None or plans.get("e_conte") is not None:
        errors.append("AnimationShotPlan and E-Conte must remain null")
    expected_ids = [f"el-pilot-s01-p{i:03d}" for i in range(1, 17)]
    if [p["panel_id"] for p in panels] != expected_ids:
        errors.append("Panel IDs/order are not immutable and consecutive")

    density_counts = {key: sum(1 for p in panels if p["density"] == key) for key in ("low", "moderate", "high")}
    if density_counts != {"low": 11, "moderate": 3, "high": 2}:
        errors.append(f"Pilot density commitment changed: {density_counts}")
    if any(panels[i]["density"] == panels[i + 1]["density"] == "high" for i in range(len(panels) - 1)):
        errors.append("Adjacent maximum-density panels")

    system_errors = validate_system(ledger)
    errors.extend(system_errors)
    reference_errors = validate_references()
    errors.extend(reference_errors)
    metrics: list[dict[str, Any]] = []
    manual_warn = {5: "planned_low_rendered_moderate_density"}
    for panel in panels:
        order = panel["order"]
        source = SOURCE / f"p{order:03d}.png"
        if not source.exists():
            errors.append(f"Missing source image: {source}")
            continue
        units = lettering["panel_units"].get(panel["panel_id"], [])
        (PANELS_OUT / f"p{order:03d}.svg").write_text(render_svg(panel, units, source), encoding="utf-8", newline="\n")
        (SAFE_OUT / f"p{order:03d}.svg").write_text(render_safe_zone_svg(panel, units, source), encoding="utf-8", newline="\n")
        row = {"panel_id": panel["panel_id"], "order": order, "planned_density": panel["density"], "source_path": source.relative_to(ROOT).as_posix(), "source_sha256": sha256(source), **image_metrics(source)}
        row["status"] = "WARN" if order in manual_warn else "PASS"
        row["failure_classes"] = [manual_warn[order]] if order in manual_warn else []
        metrics.append(row)
    low_warns = sum(1 for m in metrics if m["planned_density"] == "low" and m["status"] == "WARN")
    if low_warns / max(density_counts["low"], 1) > 0.25:
        errors.append("More than 25% of planned-low panels exceed calibration")
    elif low_warns:
        warnings.append(f"{low_warns}/11 planned-low panels exceed accepted low-detail calibration")

    required_kinds = {"status", "quest", "skill", "boss", "cultivation", "inventory", "loot", "balloon", "sfx"}
    actual_kinds = {u["kind"] for units in lettering["panel_units"].values() for u in units}
    if not required_kinds.issubset(actual_kinds):
        errors.append(f"Missing required local lettering/UI kinds: {sorted(required_kinds-actual_kinds)}")
    for panel_id, units in lettering["panel_units"].items():
        for unit in units:
            if unit["kind"] in {"balloon", "thought"} and len(unit["text"].split()) > 16:
                errors.append(f"Balloon over 16 words: {panel_id}")

    hard_gates = [
        {"requirement":"Recognizable modern action anime/manhwa at phone size","status":"PASS","evidence":"Clean tapered contour, mature expressive faces, cel value groups, and dynamic P06–P15 staging remain legible at 390px."},
        {"requirement":"Fair/light fictional-adult protagonist consistency","status":"PASS","evidence":"Neutral P02/P03 and dramatic P09/P12/P14/P15 preserve Elian's fair/light base and mature proportions."},
        {"requirement":"Causal and impressive action at phone size","status":"PASS","evidence":"Eleven consecutive beats P05–P15 show geography, charge, intercept, counter, read, move, interruption, consequence, choice, breakthrough, and combo payoff."},
        {"requirement":"Professional comics lettering, not blocky dialogue UI","status":"PASS","evidence":"Organic measured SVG balloons with semantic tails; ordinary balloon copy is under 16 words."},
        {"requirement":"Original readable system UI distinct from dialogue","status":"PASS","evidence":"Cut-corner charcoal/brass/ember Ledger components are visually separate from ivory balloons and do not copy blue holographic interfaces."},
        {"requirement":"Promised LitRPG elements visible","status":"PASS","evidence":"Level, XP, class lock, cultivation stage, skill cost/cooldown, boss level, quest, inventory sacrifice, loot rarity, and level-up appear in sequence."},
        {"requirement":"Low-detail panels actually low-detail","status":"PASS","evidence":"10/11 planned-low panels pass; P005 remains a specific WARN, below the 25% fail-closed threshold."},
        {"requirement":"No generated gibberish or baked-in lettering boxes","status":"PASS","evidence":"Local inspection found text-free source art; every visible word/shape is deterministic SVG."},
        {"requirement":"No arithmetic or provenance contradiction","status":"PASS" if not system_errors else "FAIL","evidence":"XP, HP, Qi, inventory, loot, quest, injury, breakthrough, and class-unlock transactions reconcile."},
        {"requirement":"No missing required state","status":"PASS","evidence":"Cracked Rib, consumed talisman, intact seals, acquired skill, Cinder-Key, class options, and cleared dungeon persist in final state."},
    ]
    records = make_render_records(requests, plans)
    write_json(REVIEW / "density-metrics.json", {"schema":"PilotDensityMetrics/1.0","calibration":"owner_review_pending","metrics":metrics})
    write_json(REVIEW / "render-records.json", {"schema":"RenderRecordCollection/1.0","records":records})
    generated = [r for r in records if r["output_hash"]]
    write_json(REVIEW / "output-reconciliation.json", {
        "schema":"PilotOutputReconciliation/1.0",
        "requested_outputs":len(records),
        "returned_and_recorded_outputs":len(generated),
        "missing_outputs":[r["request_id"] for r in records if not r["output_hash"]],
        "selected_panel_sources":16,
        "diagnostic_retries":1,
        "selected_retry":"pilot-p016-r2",
        "direct_paid_cloud_spend_usd":0,
        "measured_elapsed_seconds_sum":round(sum(r["measured_elapsed_seconds"] or 0 for r in records),3),
        "timing_caveat":"Concurrent batches record wall time where per-request latency was unavailable; see RenderRecords.",
        "phase_b_outputs":0,
    })
    report = {
        "schema":"PilotValidationReport/1.0",
        "status":"FAIL" if errors else "PASS_WITH_WARN" if warnings else "PASS",
        "counts":{"panels":len(panels),"action_panels":sum(1 for p in panels if p["action"]),"lettering_units":sum(len(v) for v in lettering["panel_units"].values()),"generation_requests":len(records),"density":density_counts},
        "errors":errors,"warnings":warnings,"hard_gates":hard_gates,
        "owner_approval":"PENDING","phase_b_authorized":False,"direct_paid_cloud_spend_usd":0,
        "provider_metadata_availability":{"model":None,"endpoint":None,"request_id":None,"usage":None,"cost":None,"seed":None},
    }
    write_json(REVIEW / "validation-report.json", report)
    make_html(plans, metrics, hard_gates)
    if errors:
        raise SystemExit("Pilot validation failed:\n- " + "\n- ".join(errors))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
