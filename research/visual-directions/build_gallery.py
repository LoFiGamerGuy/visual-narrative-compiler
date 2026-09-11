"""Build the bounded 20-direction gallery; never fabricate pending artwork."""
from pathlib import Path
import argparse
import hashlib
import html
import json
import os
import struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'production/visual-directions'
OUT = ROOT / 'docs/research/visual-directions'
FAMILIES = {
    'Ink & comics': ['01', '02', '06', '09', '11', '13', '15', '17'],
    'Paint & wash': ['03', '04', '05', '08', '10', '16'],
    'Animation & graphic': ['07', '18'],
    'Fashion & luminous': ['14', '19'],
    'Craft & pixels': ['12', '20'],
}
# Observed display labels only; frozen concept briefs and prompts remain intact.
DISPLAY_STYLE = {'02': 'Color adventure comic', '05': 'Painted industrial adventure',
                 '07': 'Geometric graphic illustration', '11': 'Monochrome brush ink',
                 '12': 'Stop-motion look', '20': 'Pixel / voxel-inspired fantasy'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overview(cards):
    sheets = []
    for start in (0, 10):
        end = start + 10
        cells = []
        for card in cards[start:end]:
            title = html.escape(card['title'])
            label = html.escape(card['style'])
            c = card['candidate']
            image = f'<img src="{html.escape(c["src"])}" alt="{card["id"]} {title}, complete concept board" width="{c["width"]}" height="{c["height"]}">' if c else '<span class="pending">Image pending</span>'
            cells.append(f'<a class="cell" href="index.html#direction-{card["id"]}">{image}<div class="caption"><strong>{card["id"]} · {title}</strong><span>{label}</span></div></a>')
        sheets.append(f'<section class="sheet" id="sheet-{start+1:02}-{end:02}"><header><div><p>Original visual exploration</p><h1>Twenty possible worlds.</h1></div><span>{start+1:02}—{end:02}</span></header><div class="boards">'+''.join(cells)+'</div><footer>Explore freely; your favorites can mix across directions.</footer></section>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>All twenty directions · Overview</title><style>
*{box-sizing:border-box}body{margin:0;background:#f4f1e9;color:#252f32;font:14px/1.4 system-ui,sans-serif}a{color:inherit}nav{max-width:1280px;margin:20px auto;padding:0 20px;display:flex;gap:20px;flex-wrap:wrap}nav a{color:#245b4e}.sheet{max-width:1280px;padding:24px;margin:0 auto 30px;background:#f4f1e9}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}header p{margin:0 0 6px;font-size:10px;letter-spacing:.14em;text-transform:uppercase}h1{font-size:30px;letter-spacing:-.04em;line-height:1.1;margin:0}header>span{font-size:20px;color:#245b4e}.boards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.cell{text-decoration:none;min-width:0;background:#fffef9;border:1px solid #d4d6ce;border-radius:8px;overflow:hidden}.cell img{display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:contain}.caption{padding:10px 12px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;font-size:13px}.caption span{font-size:11px;color:#687174}footer{font-size:10px;color:#687174;padding-top:18px}.pending{aspect-ratio:3/2;display:grid;place-items:center;background:#e7e7de;color:#687174}@media(max-width:600px){nav{font-size:12px;padding:0 12px}.sheet{padding:12px}h1{font-size:22px}header>span{font-size:16px}.boards{gap:10px}.caption{padding:8px;font-size:12px;gap:4px}.caption span{font-size:10px}}@media print{@page{size:A3 portrait;margin:8mm}nav{display:none}.sheet{break-after:page;padding:0;margin:0 auto;width:740px;max-width:100%}.sheet:last-child{break-after:auto}.boards{gap:8px}.caption{font-size:12px;padding:6px}.cell{break-inside:avoid}header{margin-bottom:12px}body{print-color-adjust:exact;-webkit-print-color-adjust:exact}}
</style><nav><a href="index.html">← Open the selection gallery</a><a href="#sheet-01-10">01—10</a><a href="#sheet-11-20">11—20</a><span>Tap a board to visit its gallery card. Print for a two-page overview.</span></nav>'''+''.join(sheets)+'</html>\n'


def build(require_complete=False):
    concepts_path = SOURCE / 'concepts.json'
    experiment_path = SOURCE / 'experiment.json'
    concepts = json.loads(concepts_path.read_text())
    experiment = json.loads(experiment_path.read_text())
    assert concepts['experiment_id'] == experiment['experiment_id']
    items = concepts['concepts']
    assert [c['id'] for c in items] == [f'{n:02}' for n in range(1, 21)]
    candidate_path = SOURCE / 'candidates.json'
    selected_path = SOURCE / 'selected.json'
    candidates = json.loads(candidate_path.read_text())['candidates'] if candidate_path.exists() else []
    selected = json.loads(selected_path.read_text())['selected'] if selected_path.exists() else {}
    if set(selected) - {c['id'] for c in items}:
        raise ValueError('Unknown selected direction')
    attempts = {}
    for candidate in candidates:
        if candidate['attempt_id'] in attempts:
            raise ValueError('Duplicate attempt ID')
        attempts[candidate['attempt_id']] = candidate
    cards = []
    for concept in items:
        card = {k: concept[k] for k in ('id', 'title', 'style', 'character', 'costume', 'environment', 'monster', 'rendering', 'palette')}
        card['family'] = next(f for f, ids in FAMILIES.items() if card['id'] in ids)
        card['style_brief'] = card['style']
        card['style'] = DISPLAY_STYLE.get(card['id'], card['style'])
        card['candidate'] = None
        attempt = selected.get(card['id'])
        if attempt:
            if attempt not in attempts:
                raise ValueError(f'Selected attempt absent: {attempt}')
            c = attempts[attempt]
            if c['id'] != card['id'] or c['status'] != 'reviewable-unaccepted':
                raise ValueError(f'Wrong ID/status: {attempt}')
            path = (ROOT / c['path']).resolve()
            if not path.is_relative_to(SOURCE.resolve()) or path.suffix.lower() != '.png':
                raise ValueError('Candidate must be a local visual-directions PNG')
            raw = path.read_bytes()
            if raw[:8] != b'\x89PNG\r\n\x1a\n' or raw[12:16] != b'IHDR':
                raise ValueError('Invalid PNG signature')
            width, height = struct.unpack('>II', raw[16:24])
            if (width, height) != (c['width'], c['height']) or sha(path) != c['sha256']:
                raise ValueError(f'Candidate source/hash/dimension mismatch: {attempt}')
            card['candidate'] = {k: c[k] for k in ('attempt_id', 'path', 'sha256', 'width', 'height')}
            card['candidate']['src'] = os.path.relpath(path, OUT).replace(os.sep, '/')
        cards.append(card)
    ready = sum(c['candidate'] is not None for c in cards)
    if require_complete and ready != 20:
        raise ValueError(f'Final gallery requires 20 actual candidates; only {ready} selected')
    bindings = [{'id': c['id'], 'attempt_id': c['candidate']['attempt_id'] if c['candidate'] else None,
                 'sha256': c['candidate']['sha256'] if c['candidate'] else None} for c in cards]
    identity = {'experiment_id': experiment['experiment_id'], 'concepts_sha256': sha(concepts_path),
                'experiment_sha256': sha(experiment_path), 'source_bindings': bindings}
    data = {'schema': 'VisualDirectionsGallery/1', **identity,
            'dataset_sha256': hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'available_count': ready, 'total_count': 20, 'cards': cards, 'production_accepted': False}
    OUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    (OUT / 'gallery-data.json').write_text(text)
    (OUT / 'gallery-data.js').write_text('window.VISUAL_DIRECTIONS_DATA = ' + text.rstrip() + ';\n')
    (OUT / 'overview.html').write_text(overview(cards))
    print(json.dumps({'available': ready, 'total': 20, 'dataset_sha256': data['dataset_sha256'], 'output': str(OUT / 'index.html')}))
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-complete', action='store_true')
    build(parser.parse_args().require_complete)
