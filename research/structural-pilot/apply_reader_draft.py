#!/usr/bin/env python3
"""Check/apply a hash-bound browser layout in the new structural reader only.

python research/structural-pilot/apply_reader_draft.py check DRAFT --correction
python research/structural-pilot/apply_reader_draft.py apply DRAFT --correction
No backend attempt, semantic review, or production-acceptance records are written.
"""
import argparse
import copy
import contextlib
from datetime import datetime, timezone
import hashlib
import json
import io
import math
import os
from pathlib import Path
import tempfile

import build_reader as reader

ROOT = reader.ROOT
NAMESPACE = ROOT / 'production/structural-pilot'
SELECTED = set(reader.SELECTED)
PANEL_IDS = [f'P{i:02d}' for i in range(1, 15)]
LETTER_FIELDS = {'id', 'text', 'kind', 'speaker', 'shape', 'x', 'y', 'w', 'h', 'font_size', 'tail'}
REGION_FIELDS = {'id', 'label', 'x', 'y', 'w', 'h'}
NOTE_FIELDS = {'id', 'flag', 'text', 'reviewer', 'reviewer_kind', 'created_at', 'candidate_id', 'image_sha256', 'plan_sha256', 'source_checks'}
FLAGS = {'note', 'wrong_event', 'cast_identity', 'geography', 'contact_force', 'continuity_state', 'lettering', 'delivery', 'positive_evidence'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def decode(data):
    if len(data) > 12_000_000:
        raise ValueError('Draft/input exceeds 12 MB limit')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=lambda v: (_ for _ in ()).throw(ValueError(f'Nonfinite JSON: {v}')))


def task_file(value, input_file=False):
    given = ROOT / value
    path = given.resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError('Existing file inside this isolated checkout required')
    if input_file and not path.is_relative_to(NAMESPACE):
        raise ValueError('Selected input must stay in production/structural-pilot')
    if input_file and (path.is_relative_to(NAMESPACE/'layout-history') or not path.name.endswith('reader-input.json')):
        raise ValueError('Only selected reader-input.json files are mutable; history/drafts are protected')
    for part in [given, *given.parents]:
        if part == ROOT.parent:
            break
        if part.is_symlink():
            raise ValueError('Symlink inputs are not supported')
    return path


def fields(value, allowed, label):
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError(f'{label}: unsupported fields (including approval/identity assertions)')


def string(value, size, label, empty=True):
    if not isinstance(value, str) or len(value) > size or (not empty and not value):
        raise ValueError(f'{label}: bounded text required')


def number(value, low, high, label):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{label}: finite number in {low}..{high} required')


def shapes(items, letters, canonical=None):
    if not isinstance(items, list) or len(items) > 100:
        raise ValueError('At most 100 lettering/region items permitted')
    ids = set()
    for item in items:
        fields(item, LETTER_FIELDS if letters else REGION_FIELDS, 'Lettering' if letters else 'Region')
        string(item.get('id'), 120, 'Item ID', False)
        if item['id'] in ids:
            raise ValueError('Duplicate lettering/region ID')
        ids.add(item['id'])
        for k in ['x', 'y']:
            number(item.get(k), 0, 1, k)
        for k in ['w', 'h']:
            number(item.get(k), .02, 1, k)
        if item['x'] + item['w'] > 1 + 1e-9 or item['y'] + item['h'] > 1 + 1e-9:
            raise ValueError('Shape extends outside normalized canvas')
        if letters:
            string(item.get('text'), 4000, 'Lettering text')
            string(item.get('speaker', ''), 100, 'Speaker')
            if item.get('kind') not in ['dialogue', 'ui', 'sfx'] or item.get('shape') not in ['rounded', 'ellipse']:
                raise ValueError('Unsupported lettering kind/shape')
            number(item.get('font_size'), {'dialogue': 14, 'ui': 12, 'sfx': 6}[item['kind']], 96, 'Font size at canonical390px')
            tail = item.get('tail')
            if tail is not None:
                fields(tail, {'x', 'y'}, 'Tail')
                for k in ['x', 'y']:
                    number(tail.get(k), 0, 1, 'Tail coordinate')
        else:
            string(item.get('label'), 160, 'Region label', False)
    if letters:
        reader.check_layout(items, canonical)


def verify_source(entry):
    path = task_file(entry['path'])
    if reader.sha(path) != entry['sha256']:
        raise ValueError(f'Changed source art: {entry["path"]}')
    reader.png_size(path)
    for link in entry.get('source_links', []):
        target = task_file(link['path'])
        if link.get('sha256') and reader.sha(target) != link['sha256']:
            raise ValueError(f'Changed editable source: {link["path"]}')


def prepare(draft_path, input_path, correction=False):
    before = input_path.read_bytes()
    draft_bytes = draft_path.read_bytes()
    spec, draft = decode(before), decode(draft_bytes)
    fields(draft, {'schema', 'title', 'plan_sha256', 'exported_at', 'status', 'experiment_id', 'route_id', 'reader_input_sha256', 'reviewer_labels_verified', 'production_eligible', 'panels'}, 'Draft')
    if draft.get('schema') != 'SequenceReviewDraft/1' or draft.get('status') != 'draft-unaccepted':
        raise ValueError('Expected draft-unaccepted SequenceReviewDraft/1')
    if draft.get('reviewer_labels_verified') is not False or draft.get('production_eligible', False) is not False:
        raise ValueError('Draft cannot assert acceptance or verified identity')
    if draft.get('experiment_id') != spec.get('experiment_id'):
        raise ValueError('Different experiment ID')
    if draft.get('reader_input_sha256') != digest(before):
        raise ValueError('Stale selected-input hash; reload current reader and export again')
    if spec['selected_panels'] != reader.SELECTED:
        raise ValueError('Unsupported experiment panel scope')
    if correction != (spec['experiment_id'] == 'CF-20260907-02'):
        raise ValueError('Correction flag and selected experiment disagree')
    plan = task_file(spec['plan_path'])
    if draft.get('plan_sha256') != reader.sha(plan):
        raise ValueError('Stale or different frozen plan')
    receipt = plan.with_suffix('.sha256')
    if receipt.exists() and receipt.read_text().split()[0] != reader.sha(plan):
        raise ValueError('Frozen plan receipt mismatch')
    route = next((v for v in spec['routes'] if v['id'] == draft.get('route_id')), None)
    if route is None:
        raise ValueError('Unknown editable route; preserved baseline B cannot be changed')
    baseline_path = task_file(spec.get('baseline_path', 'docs/research/sequence-pilot/reader/review-data.json'))
    baseline = decode(baseline_path.read_bytes())
    if [p['id'] for p in baseline['panels']] != PANEL_IDS:
        raise ValueError('Expected all fourteen preserved baseline context panels')
    # Preflight every build input before any snapshot/input mutation.
    for r in spec['routes']:
        for entry in r.get('panels', {}).values():
            verify_source(entry)
    for p in baseline['panels']:
        candidate = p['candidate']
        source = (baseline_path.parent / candidate['src']).resolve()
        if not source.is_relative_to(ROOT) or reader.sha(source) != candidate['sha256']:
            raise ValueError('Preserved context source changed')
    incoming = draft.get('panels')
    if not isinstance(incoming, list) or len(incoming) != 14 or {p.get('id') for p in incoming if isinstance(p, dict)} != set(PANEL_IDS):
        raise ValueError('Draft must contain every context panel exactly once')
    projected = copy.deepcopy(spec)
    target = next(v for v in projected['routes'] if v['id'] == route['id'])
    changes, note_count = [], 0
    for planned in baseline['panels']:
        pid = planned['id']
        panel = next(v for v in incoming if v['id'] == pid)
        fields(panel, {'id', 'candidate_id', 'candidate_sha256', 'lettering', 'protected_regions', 'observations'}, pid)
        if pid in SELECTED:
            expected = route.get('panels', {}).get(pid)
            if not expected:
                raise ValueError(f'{pid}: route artwork is missing; layout application requires all four screen candidates')
            expected_id, expected_sha = expected['candidate_id'], expected['sha256']
            old_letters, old_regions = expected['lettering'], expected.get('protected_regions', [])
        else:
            expected_id, expected_sha = planned['candidate']['id'], planned['candidate']['sha256']
            old_letters, old_regions = planned['lettering'], planned.get('protected_regions', [])
        if panel.get('candidate_id') != expected_id or panel.get('candidate_sha256') != expected_sha:
            raise ValueError(f'{pid}: stale or tampered candidate ID/hash')
        letters, regions = panel.get('lettering'), panel.get('protected_regions')
        shapes(letters, True, planned['copy'])
        shapes(regions, False)
        if pid not in SELECTED and (letters != old_letters or regions != old_regions):
            raise ValueError(f'{pid}: surrounding context layout is protected')
        if correction and route['id'] == 'CF' and pid == 'P14' and regions != old_regions:
            raise ValueError('CF P14 is unchanged generated reference; only lettering may change')
        notes = panel.get('observations', [])
        if not isinstance(notes, list) or len(notes) > 500:
            raise ValueError('At most 500 browser notes per panel')
        for note in notes:
            fields(note, NOTE_FIELDS, 'Browser note')
            string(note.get('text', ''), 12000, 'Unverified browser note')
            string(note.get('reviewer', ''), 300, 'Unverified reviewer label')
            if note.get('source_checks', False) is not False or note.get('flag', 'note') not in FLAGS or note.get('reviewer_kind', 'unspecified') not in ['unspecified', 'agent', 'human']:
                raise ValueError('Browser notes cannot assert backend checks or verified reviewers')
            for key, value in [('candidate_id', expected_id), ('image_sha256', expected_sha), ('plan_sha256', reader.sha(plan))]:
                if note.get(key, value) != value:
                    raise ValueError('Browser note has stale evidence bindings')
            note_count += 1
        if pid in SELECTED and (letters != old_letters or regions != old_regions):
            changes.append({'panel': pid, 'candidate_id': expected_id, 'candidate_sha256': expected_sha, 'before_lettering': old_letters, 'after_lettering': letters, 'before_protected_regions': old_regions, 'after_protected_regions': regions})
            target['panels'][pid]['lettering'] = copy.deepcopy(letters)
            if not (correction and route['id'] == 'CF' and pid == 'P14'):
                target['panels'][pid]['protected_regions'] = copy.deepcopy(regions)
    patch = {'schema': 'StructuralReaderLayoutPatch/1', 'experiment_id': spec['experiment_id'], 'route_id': route['id'], 'input_path': str(input_path.relative_to(ROOT)), 'input_sha256_before': digest(before), 'draft_sha256': digest(draft_bytes), 'plan_sha256': reader.sha(plan), 'changes': changes, 'browser_notes_preserved_only': note_count, 'notes_policy': 'Retained in immutable draft snapshot only; never applied as semantic checks, identity verification or acceptance.', 'context_unchanged': True, 'status': 'draft-unaccepted', 'production_eligible': False}
    return patch, before, draft_bytes, (json.dumps(projected, indent=2) + '\n').encode()


def exclusive(path, data):
    with path.open('xb') as f:
        f.write(data)
    path.chmod(0o444)


def atomic_input(path, data):
    fd, name = tempfile.mkstemp(prefix='.reader-layout-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def apply(draft_path, input_path, correction=False):
    lock = NAMESPACE / '.reader-layout.lock'
    with lock.open('x'):
        try:
            patch, before, draft_bytes, after = prepare(draft_path, input_path, correction)
            if not patch['changes']:
                return {**patch, 'applied': False, 'reason': 'No selected layout changes; no input mutation'}
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
            history = NAMESPACE / 'layout-history' / f'{stamp}-{digest(before)[:12]}-{digest(draft_bytes)[:12]}'
            history.mkdir(parents=True, exist_ok=False)
            for name, data in [('input-before.json', before), ('input-after.json', after), ('browser-draft.json', draft_bytes), ('patch.json', (json.dumps(patch, indent=2)+'\n').encode())]:
                exclusive(history / name, data)
            if input_path.read_bytes() != before:
                raise ValueError('Selected input changed during validation; no mutation applied')
            output = ROOT / 'docs/research/structural-pilot' / ('correction-reader' if correction else 'reader')
            atomic_input(input_path, after)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    reader.build(input_path, output, correction)
            except Exception as error:
                # Restore exact prior selection and reader when a build cannot finish.
                atomic_input(input_path, before)
                with contextlib.redirect_stdout(io.StringIO()):
                    reader.build(input_path, output, correction)
                exclusive(history/'failed.json', (json.dumps({'error':str(error),'restored_input_sha256':digest(before),'status':'build-failed-input-restored'},indent=2)+'\n').encode())
                raise
            result = {**patch, 'applied': True, 'input_sha256_after': digest(after), 'snapshot_path': str(history.relative_to(ROOT)), 'reader': str((output/'index.html').relative_to(ROOT)), 'reader_data_sha256': reader.sha(output/'review-data.js'), 'rebuild_completed': True}
            exclusive(history/'result.json', (json.dumps(result,indent=2)+'\n').encode())
            return result
        finally:
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'apply'])
    parser.add_argument('draft')
    parser.add_argument('--correction', action='store_true')
    parser.add_argument('--input', help='Selected input inside production/structural-pilot')
    args = parser.parse_args()
    default = 'production/structural-pilot/reader-patches/CF-reader-input.json' if args.correction else 'production/structural-pilot/reader-input.json'
    input_path = task_file(args.input or default, input_file=True)
    draft_path = task_file(args.draft)
    result = apply(draft_path, input_path, args.correction) if args.action == 'apply' else prepare(draft_path,input_path,args.correction)[0]
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit(f'Reader draft rejected: {error}')
