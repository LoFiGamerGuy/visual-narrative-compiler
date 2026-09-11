#!/usr/bin/env python3
"""Build the bounded three-route reader; never write to inherited source art.

Run from the isolated checkout: python research/structural-pilot/build_reader.py
Inputs resolve relative to checkout root. See reader-input-contract.md.
"""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import struct

ROOT = Path(__file__).resolve().parents[2]
SELECTED = ['P09', 'P11', 'P13', 'P14']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'Expected existing file inside isolated checkout: {value}')
    return path


def png_size(path):
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        raise ValueError(f'Expected PNG candidate: {path}')
    return struct.unpack('>II', data[16:24])


def transcript(letters):
    return [('SFX: ' if v['kind'] == 'sfx' else f"{v['speaker']}: " if v.get('speaker') else '') + v['text'] for v in letters]


def check_layout(letters, canonical):
    if not isinstance(letters, list) or len(letters) > 100 or len({v['id'] for v in letters}) != len(letters):
        raise ValueError('Lettering must contain at most 100 unique items')
    if transcript(letters) != canonical:
        raise ValueError('Lettering must preserve exact canonical transcript in order')
    for v in letters:
        if not all(isinstance(v.get(k), (int, float)) and math.isfinite(v[k]) for k in ['x', 'y', 'w', 'h', 'font_size']):
            raise ValueError('Lettering requires numeric x/y/w/h/font_size')
        if not (0 <= v['x'] <= 1-v['w'] and 0 <= v['y'] <= 1-v['h'] and .02 <= v['w'] <= 1 and .02 <= v['h'] <= 1 and 6 <= v['font_size'] <= 96):
            raise ValueError('Lettering geometry outside supported canvas')
        if v.get('tail') is not None and not all(isinstance(v['tail'].get(k), (int, float)) and 0 <= v['tail'][k] <= 1 for k in ['x', 'y']):
            raise ValueError('Lettering tail lies outside supported canvas')


def build(input_path, output, correction=False):
    spec = json.loads(input_path.read_text())
    if spec['selected_panels'] != SELECTED:
        raise ValueError('This reader is scoped to P09/P11/P13/P14 only')
    plan = local(spec['plan_path'])
    plan_data = json.loads(plan.read_text())
    plan_receipt = plan.with_suffix('.sha256')
    if plan_receipt.exists() and plan_receipt.read_text().split()[0] != sha(plan):
        raise ValueError('Frozen plan SHA receipt does not match plan bytes')
    baseline_path = local(spec.get('baseline_path', 'docs/research/sequence-pilot/reader/review-data.json'))
    baseline = json.loads(baseline_path.read_text())
    if [p['id'] for p in baseline['panels']] != [f'P{i:02d}' for i in range(1, 15)]:
        raise ValueError('Baseline must contain the preserved 14-panel sequence')
    if correction:
        if spec['experiment_id'] != 'CF-20260907-02' or plan_data['experiment_id'] != spec['experiment_id']:
            raise ValueError('Correction reader requires frozen CF-20260907-02 experiment')
        for pid, exact in plan_data['exact_copy'].items():
            if next(p for p in baseline['panels'] if p['id'] == pid)['copy'] != exact:
                raise ValueError('Correction copy must match preserved baseline')
        routes = spec['routes']
        if [r['id'] for r in routes] != ['G', 'CF']:
            raise ValueError('Separate correction reader requires G and CF only')
        for pid in SELECTED:
            generated = routes[0]['panels'].get(pid)
            if not generated or generated['sha256'] != plan_data['sources'][pid]['sha256']:
                raise ValueError('G comparison image must match frozen correction source')
        carried = routes[1]['panels'].get('P14')
        if not carried or carried['sha256'] != plan_data['sources']['P14']['sha256']:
            raise ValueError('P14 must be carried unchanged as generated reference only')
        for pid, entry in routes[1]['panels'].items():
            if pid != 'P14' and entry.get('source_candidate_sha256') != plan_data['sources'][pid]['sha256']:
                raise ValueError('Each conventional correction must bind its frozen generated source')
    else:
        for frozen in plan_data['panels']:
            p = next(v for v in baseline['panels'] if v['panel'] == frozen['panel'])
            if p['panel'] != frozen['panel'] or p['copy'] != frozen['copy'] or p['target_css_height_at390'] != frozen['target_css_height_at390']:
                raise ValueError('Experiment must preserve all baseline panel numbers, copy and canvas heights')
        routes = [{'id': 'B', 'label_provenance': 'Preserved baseline', 'panels': {}}] + spec['routes']
        if [r['id'] for r in routes] != ['B', 'S', 'G']:
            raise ValueError('Expected routes S and G, in that order; baseline B is automatic')
    output.mkdir(parents=True, exist_ok=True)
    assets = output / 'assets'
    assets.mkdir(exist_ok=True)
    labels = {'G': 'source', 'CF': 'proof'} if correction else {rid: label for rid, label in zip(sorted(['B', 'S', 'G'], key=lambda x: hashlib.sha256((spec['experiment_id']+x).encode()).hexdigest()), ['X', 'Y', 'Z'])}
    manifest = {'schema': 'StructuralReader/1', 'experiment_id': spec['experiment_id'], 'plan_sha256': sha(plan), 'baseline_data_sha256': sha(baseline_path), 'input_sha256': sha(input_path), 'selected_panels': SELECTED, 'routes': [], 'datasets': {}, 'production_eligible': False}
    if correction:
        manifest.update(mode='conventional-correction', neutral_labels=False, reference_only_panels=['P14'], default_route='CF')
    bindings = []

    def candidate(path, expected, cid):
        actual = sha(path)
        if expected != actual:
            raise ValueError(f'Candidate hash mismatch: {path}')
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,120}', cid):
            raise ValueError(f'Unsafe candidate ID: {cid}')
        dest = assets / f'{actual}.png'
        if dest.exists() and sha(dest) != actual:
            raise ValueError(f'Existing asset corrupted: {dest}')
        if not dest.exists():
            shutil.copyfile(path, dest)
        w, h = png_size(dest)
        bindings.append({'source': str(path.relative_to(ROOT)), 'sha256': actual, 'display': str(dest.relative_to(ROOT))})
        return {'id': cid, 'sha256': actual, 'src': f'assets/{actual}.png', 'width': w, 'height': h, 'status': 'draft-unaccepted'}

    for route in routes:
        rid = route['id']
        replacements = route.get('panels', {})
        if set(replacements) - set(SELECTED):
            raise ValueError('Only selected screen panels may be replaced')
        dataset = copy.deepcopy(baseline)
        dataset['plan_sha256'] = manifest['plan_sha256']
        dataset['title'] = baseline['title']
        dataset['status'] = {'production_eligible': False, 'blockers': ['All candidates are draft-unaccepted. Human comprehension, owner preference and commercial clearance remain unresolved.']}
        source_links = {}
        for p in dataset['panels']:
            p['observations'] = []  # Prior checks are not rebound to this experiment.
            entry = replacements.get(p['id'])
            if rid != 'B' and p['id'] in SELECTED:
                p['candidate'] = None
                p['lettering'] = []
                p['protected_regions'] = []
                if entry:
                    path = local(entry['path'])
                    p['candidate'] = candidate(path, entry['sha256'], entry['candidate_id'])
                    p['lettering'] = copy.deepcopy(entry['lettering'])
                    check_layout(p['lettering'], p['copy'])
                    p['protected_regions'] = copy.deepcopy(entry.get('protected_regions', []))
                    links = []
                    for link in entry.get('source_links', []):
                        target = local(link['path'])
                        actual = sha(target)
                        if link.get('sha256', actual) != actual:
                            raise ValueError(f'Editable source hash mismatch: {target}')
                        links.append({'label': link['label'], 'href': os.path.relpath(target, output), 'sha256': actual})
                    source_links[p['id']] = links
            elif p['candidate']:
                old = p['candidate']
                path = local(str((baseline_path.parent / old['src']).relative_to(ROOT)))
                p['candidate'] = candidate(path, old['sha256'], old['id'])
        manifest['routes'].append({'id': rid, 'label_neutral': labels[rid], 'label_provenance': route['label_provenance'], 'source_links': source_links, 'missing': [p['id'] for p in dataset['panels'] if not p['candidate']]})
        manifest['datasets'][rid] = dataset
    if not correction:
        manifest['routes'].sort(key=lambda r: r['label_neutral'])
    for rid, dataset in manifest['datasets'].items():
        (output / f'route-{rid}.json').write_text(json.dumps(dataset, indent=2) + '\n')
    (output / 'routes.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (output / 'review-data.js').write_text('window.STRUCTURAL_ROUTES = ' + json.dumps(manifest) + ';\nwindow.SEQUENCE_REVIEW_DATA = window.STRUCTURAL_ROUTES.datasets[window.STRUCTURAL_ROUTES.default_route || window.STRUCTURAL_ROUTES.routes[0].id];\n')
    record = {'schema': 'StructuralReaderBuild/1', 'experiment_id': spec['experiment_id'], 'plan_sha256': manifest['plan_sha256'], 'input_sha256': sha(input_path), 'baseline_data_sha256': sha(baseline_path), 'bindings': list({(v['source'], v['sha256']): v for v in bindings}.values()), 'route_labels': labels, 'missing': {r['id']: r['missing'] for r in manifest['routes']}, 'production_eligible': False}
    (output / 'source-bindings.json').write_text(json.dumps(record, indent=2) + '\n')
    if correction:
        frontend = ROOT / 'docs/research/structural-pilot/reader'
        for name in ['app.js', 'style.css']:
            shutil.copyfile(frontend / name, output / name)
        html = (frontend / 'index.html').read_text()
        html = html.replace('STRUCTURAL PILOT / WORKING READER', 'CF-20260907-02 / CONVENTIONAL CORRECTION PROOF')
        html = html.replace('<p class="neutral-note">', '<p class="neutral-note" hidden>')
        html = html.replace('<div class="toolbar" aria-label="Workspace controls">', '<p class="proof-note">CF-20260907-02 · Agent-authored conventional correction proof · No new generation. P14 is the unchanged generated reference. Ten surrounding panels preserve baseline context; this is unaccepted experimental work.</p><div class="toolbar" aria-label="Workspace controls">')
        html = html.replace('>Matched comparison</button>', '>Correction comparison</button>')
        (output / 'index.html').write_text(html)
    print(json.dumps({'reader': str(output.relative_to(ROOT) / 'index.html'), 'missing': record['missing'], 'bindings': len(record['bindings'])}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default='production/structural-pilot/reader-input.json')
    parser.add_argument('--correction', action='store_true', help='Build separate CF reader from an explicit correction input')
    args = parser.parse_args()
    build(local(args.input), ROOT / 'docs/research/structural-pilot' / ('correction-reader' if args.correction else 'reader'), args.correction)
