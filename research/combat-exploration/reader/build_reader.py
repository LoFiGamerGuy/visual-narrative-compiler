"""Build the isolated combat gallery. Source plans, selections and art are read-only."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'production/combat-exploration'
OUT = ROOT / 'docs/combat-exploration'
STYLES = ['01', '02', '05', '06', '13', '15', '17', '18', '19']
CHARACTERS = ['C1', 'C2']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default

def asset(value, board=False):
    path = (ROOT / value['path']).resolve()
    if not path.is_relative_to(SOURCE.resolve()):
        raise ValueError('Image path leaves the combat-exploration namespace')
    raw = path.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n' or sha(path) != value['sha256']:
        raise ValueError('Image signature or source hash mismatch')
    width, height = struct.unpack('>II', raw[16:24])
    if width < 1 or height < 1:
        raise ValueError('Invalid native dimensions')
    if any(k in value and value[k] != v for k, v in [('width', width), ('height', height)]):
        raise ValueError('Declared image dimensions do not match PNG')
    if board and abs(width / height - 1.5) > .02:
        raise ValueError('Combat boards require the frozen 3:2 landscape format')
    return {**{k: value[k] for k in ['path', 'sha256', 'attempt_id'] if k in value},
            'width': width, 'height': height, 'src': os.path.relpath(path, OUT).replace(os.sep, '/')}

def build(require_complete=False):
    plan_path = SOURCE / 'combat-plan.json'
    plan = read(plan_path)
    if not plan or plan.get('schema') != 'CombatExplorationPlan/1':
        raise ValueError('A frozen CombatExplorationPlan/1 is required')
    if not isinstance(plan.get('experiment_id'), str) or not plan['experiment_id']:
        raise ValueError('Experiment identity is required')
    if sorted(s['id'] for s in plan['styles']) != STYLES:
        raise ValueError('Exactly nine original favorite styles are required')
    entries = plan['entries']
    expected = {f'{s}-{c}' for s in STYLES for c in CHARACTERS}
    if len(entries) != 18 or {e['id'] for e in entries} != expected:
        raise ValueError('Exactly18 distinct combat character IDs are required')
    for e in entries:
        if e['id'] != f'{e["style_id"]}-{e["character_id"]}':
            raise ValueError('Character ID does not match style and alternative')
        if type(e.get('age')) is not int or e['age'] < 18:
            raise ValueError('Every character must have an explicit adult age')
        if any(not isinstance(e.get(k), str) or not e[k].strip() for k in ['title', 'caption']):
            raise ValueError('Character title and display caption are required')
        for k in ['weapon', 'power']:
            if not isinstance(e.get(k), dict) or any(not isinstance(e[k].get(f), str) or not e[k][f].strip() for f in ['name', 'description']):
                raise ValueError('Weapon and power need names and descriptions')
    references = read(SOURCE / 'references.json', [])
    if sorted(r['id'] for r in references) != STYLES:
        raise ValueError('Nine original reference anchors are required')
    references = [{'id': r['id'], **asset(r)} for r in references]
    rows = read(SOURCE / 'candidates.json', {'candidates': []})['candidates']
    attempts = {c['attempt_id']: c for c in rows}
    if len(attempts) != len(rows) or any(c['id'] not in expected for c in rows):
        raise ValueError('Duplicate attempt or unknown character')
    selections = read(SOURCE / 'selected.json', {'selected': {}})['selected']
    if set(selections) - expected:
        raise ValueError('Selected unknown character')
    selected = {}
    for id, attempt in selections.items():
        raw = attempts.get(attempt)
        if not raw or raw['id'] != id or raw.get('status') != 'reviewable-unaccepted':
            raise ValueError('Selected character, attempt or status mismatch')
        selected[id] = asset(raw, board=True)
    cards = []
    for entry in entries:
        history = []
        for raw in rows:
            if raw['id'] != entry['id']:
                continue
            item = asset(raw, board=True)
            call_path = SOURCE / 'calls' / f'{raw["attempt_id"]}.json'
            call = read(call_path, {})
            if call:
                if call.get('id', raw['id']) != raw['id'] or call.get('attempt_id', raw['attempt_id']) != raw['attempt_id']:
                    raise ValueError('Call record belongs to another image')
                item.update(call_path=call_path.relative_to(ROOT).as_posix(), call_sha256=sha(call_path))
            for field in ['retry_of', 'retry_reason']:
                if raw.get(field) and call.get(field) and raw[field] != call[field]:
                    raise ValueError('Conflicting retry provenance')
            retry_of = call.get('retry_of') or raw.get('retry_of')
            reason = call.get('retry_reason') or raw.get('retry_reason')
            if retry_of or re.search(r'-R\d*$', raw['attempt_id']):
                before = attempts.get(retry_of)
                if not before or before['id'] != entry['id'] or not isinstance(reason, str) or not reason.strip() or not call:
                    raise ValueError('Retry needs a retained source attempt and correction call record')
                item.update(retry_of=retry_of, retry_reason=reason)
            history.append(item)
        cards.append({**entry, 'candidate': selected.get(entry['id']), 'history': history})
    notes_path = SOURCE / 'review-notes.json'
    notes = read(notes_path)
    if notes:
        if notes.get('schema') != 'CombatExplorationReviewNotes/1' or notes.get('experiment_id') != plan['experiment_id']:
            raise ValueError('Technical notes belong to another experiment')
        for id, note in notes.get('entries', {}).items():
            c = selected.get(id)
            if not c or note.get('attempt_id') != c['attempt_id'] or note.get('sha256') != c['sha256']:
                raise ValueError('Stale technical note source')
            if not isinstance(note.get('observations'), list) or any(not isinstance(t, str) for t in note['observations']):
                raise ValueError('Technical observations must be plain strings')
    cards = [{**e, 'ai_observations': (notes or {}).get('entries', {}).get(e['id'], {}).get('observations', [])} for e in cards]
    if require_complete and len(selected) != 18:
        raise ValueError('Final reader requires all18 actual selected character boards')
    bindings = [{'id': e['id'], 'attempt_id': e['candidate']['attempt_id'] if e['candidate'] else None,
                 'sha256': e['candidate']['sha256'] if e['candidate'] else None} for e in cards]
    identity = {'experiment_id': plan['experiment_id'], 'plan_sha256': sha(plan_path), 'source_bindings': bindings}
    data = {'schema': 'CombatExplorationReader/1', **identity,
            'dataset_sha256': hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'styles': plan['styles'], 'entries': cards, 'references': references,
            'available_count': len(selected), 'total_count': 18, 'owner_approval': None,
            'review_notes_sha256': sha(notes_path) if notes else None,
            'report_links': [{'label': label, 'path': f'../../research/combat-exploration/{name}'}
                             for name, label in [('START_HERE.md', 'Study details'), ('RESULTS.md', 'Results & observations')]
                             if (ROOT / f'research/combat-exploration/{name}').exists()]}
    OUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False)
    (OUT / 'data.json').write_text(text + '\n')
    (OUT / 'data.js').write_text('window.COMBAT_EXPLORATION_DATA = ' + text + ';\n')
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    data = build(args.require_complete)
    print(json.dumps({'available': data['available_count'], 'total': 18, 'dataset_sha256': data['dataset_sha256']}))
