"""Source-bound offline comparison and sequential reader for VR-20260907-01."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'production/visual-refinement'
OUT = ROOT / 'docs/research/visual-refinement'
STARS = ['01', '02', '05', '06', '13', '15', '17', '18', '19']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path, fallback=None):
    return json.loads(path.read_text()) if path.exists() else fallback


def normalize_candidate(candidate):
    path = (ROOT / candidate['path']).resolve()
    if not path.is_relative_to(SOURCE.resolve()) or path.suffix.lower() != '.png':
        raise ValueError('Candidate must be a PNG in the new production namespace')
    raw = path.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n' or raw[12:16] != b'IHDR':
        raise ValueError('Invalid PNG')
    width, height = struct.unpack('>II', raw[16:24])
    if (width, height) != (candidate['width'], candidate['height']) or sha(path) != candidate['sha256']:
        raise ValueError(f'Source hash/dimension mismatch: {candidate["attempt_id"]}')
    value = {k: candidate[k] for k in ['attempt_id', 'path', 'sha256', 'width', 'height']}
    value['src'] = os.path.relpath(path, OUT).replace(os.sep, '/')
    if 'lettering' in candidate:
        value['lettering'] = candidate['lettering']
    return value


def candidate_map(prefix=''):
    manifest = read_json(SOURCE / f'{prefix}candidates.json', {'candidates': []})
    chosen = read_json(SOURCE / f'{prefix}selected.json', {'selected': {}})['selected']
    attempts = {}
    for candidate in manifest['candidates']:
        if candidate['attempt_id'] in attempts:
            raise ValueError('Duplicate attempt ID')
        attempts[candidate['attempt_id']] = candidate
    result = {}
    for key, attempt in chosen.items():
        if attempt not in attempts:
            raise ValueError(f'Selected attempt absent: {attempt}')
        c = attempts[attempt]
        if c['id'] != key or c['status'] != 'reviewable-unaccepted':
            raise ValueError('Selected candidate ID/status mismatch')
        result[key] = normalize_candidate(c)
    return result


def add_repairs(cards, prefix=''):
    manifest_path = SOURCE / f'{prefix}candidates.json'
    manifest = read_json(manifest_path, {'candidates': []})
    attempts = {c['attempt_id']: c for c in manifest['candidates']}
    for card in cards:
        selected = card['candidate']
        if not selected:
            continue
        raw = attempts[selected['attempt_id']]
        if not raw.get('retry_of') and not re.search(r'-R\d*$', selected['attempt_id']):
            continue
        call_path = SOURCE / 'calls' / f'{selected["attempt_id"]}.json'
        call = read_json(call_path, {})
        for field in ('retry_of', 'retry_reason'):
            if raw.get(field) and call.get(field) and raw[field] != call[field]:
                raise ValueError('Repair candidate and call record disagree')
        before_id = raw.get('retry_of') or call.get('retry_of')
        reason = raw.get('retry_reason') or call.get('retry_reason')
        before = attempts.get(before_id)
        if not before or before['id'] != card['id'] or not isinstance(reason, str) or not reason.strip():
            raise ValueError(f'Repair {selected["attempt_id"]} requires its retained primary and a stated hard-failure reason')
        if call.get('retry_of') and call.get('retry_reason'):
            record = call_path
        elif raw.get('retry_of') and raw.get('retry_reason'):
            record = manifest_path
        else:
            raise ValueError('One repair source record must contain both retry_of and retry_reason')
        card['repair'] = {'before': normalize_candidate(before), 'after': selected, 'reason': reason,
                          'conditioning_notice': 'The repair uses revised reference conditioning. This is not an identical-input experiment.',
                          'record_path': record.relative_to(ROOT).as_posix(), 'record_sha256': sha(record)}
    return cards


def emit(mode, plan, plan_path, entries, **extra):
    bindings = [{'id': e['id'], 'attempt_id': e['candidate']['attempt_id'] if e['candidate'] else None,
                 'sha256': e['candidate']['sha256'] if e['candidate'] else None} for e in entries]
    identity = {'experiment_id': plan['experiment_id'], 'mode': mode,
                'plan_sha256': sha(plan_path), 'source_bindings': bindings}
    data = {'schema': 'VisualRefinementReader/1', **identity, **extra, 'entries': entries,
            'plan_path': plan_path.relative_to(ROOT).as_posix(),
            'dataset_sha256': hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'available_count': sum(e['candidate'] is not None for e in entries), 'total_count': 18 if mode == 'sequence' else len(entries),
            'owner_approval': None, 'production_accepted': False,
            'study_details_available': (ROOT / 'research/visual-refinement/START_HERE.md').exists(),
            'results_available': (ROOT / 'research/visual-refinement/RESULTS.md').exists()}
    OUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False)
    (OUT / f'{mode}-data.json').write_text(text + '\n')
    (OUT / f'{mode}-data.js').write_text(f'window.VR_{mode.upper()}_DATA = ' + text + ';\n')
    return data


def build_comparison(require_complete=False):
    path = SOURCE / 'comparison-plan.json'
    plan = read_json(path)
    if not plan:
        raise ValueError('Comparison plan has not been supplied')
    styles = plan['styles']
    if sorted(s['id'] for s in styles) != STARS or sorted(c['id'] for c in plan['characters']) != ['A', 'B']:
        raise ValueError('Controlled styles/cast differ from frozen scope')
    for style in styles:
        reference = style.get('reference')
        if reference:
            ref_path = (ROOT / reference['path']).resolve()
            if not ref_path.is_relative_to(SOURCE.resolve()) or sha(ref_path) != reference['sha256']:
                raise ValueError('Style reference source/hash mismatch')
            raw = ref_path.read_bytes()
            if raw[:8] != b'\x89PNG\r\n\x1a\n':
                raise ValueError('Style reference must be PNG')
            reference['width'], reference['height'] = struct.unpack('>II', raw[16:24])
            reference['src'] = os.path.relpath(ref_path, OUT).replace(os.sep, '/')
    entries = plan['entries']
    expected = {f'{style}-{character}' for style in STARS for character in ['A', 'B']}
    controlled = [e for e in entries if e['kind'] == 'controlled']
    if len(controlled) != 18 or {e['id'] for e in controlled} != expected:
        raise ValueError('Controlled comparison requires both characters in all nine styles')
    for e in controlled:
        if e['id'] != f'{e["style_id"]}-{e["character_id"]}':
            raise ValueError('Controlled ID does not match style/cast')
    if len(entries) != 20 or {e['id'] for e in entries if e['kind'] == 'exploratory'} != {'X1', 'X2'}:
        raise ValueError('Two separate exploratory mixes are required')
    candidates = candidate_map()
    if set(candidates) - {e['id'] for e in entries}:
        raise ValueError('Unknown selected comparison ID')
    cards = add_repairs([{**e, 'candidate': candidates.get(e['id'])} for e in entries])
    review_path = SOURCE / 'review-notes.json'
    review = read_json(review_path)
    if review:
        if review.get('schema') != 'RefinementReviewNotes/1' or review.get('experiment_id') != plan['experiment_id']:
            raise ValueError('Review notes refer to the wrong experiment')
        for key, note in review['entries'].items():
            candidate = candidates.get(key)
            if not candidate or note['attempt_id'] != candidate['attempt_id'] or note['sha256'] != candidate['sha256']:
                raise ValueError(f'Stale AI observations for {key}')
            if not isinstance(note['observations'], list) or any(not isinstance(n, str) for n in note['observations']):
                raise ValueError('AI observations must be plain text')
        cards = [{**e, 'ai_observations': review['entries'].get(e['id'], {}).get('observations', [])} for e in cards]
    if require_complete and any(e['candidate'] is None for e in cards):
        raise ValueError('Final comparison requires all 20 selected actual images')
    return emit('comparison', plan, path, cards, styles=styles, characters=plan['characters'], prior_star_ids=STARS,
                review_notes_sha256=sha(review_path) if review else None)


def build_sequence(require_complete=False):
    path = SOURCE / 'sequence-plan.json'
    if not path.exists() and not require_complete:
        fallback = SOURCE / 'sequence-design/panel-plan.json'
        if fallback.exists():
            path = fallback
    plan = read_json(path)
    if not plan:
        if require_complete:
            raise ValueError('Sequence plan has not been supplied')
        data = {'schema': 'VisualRefinementReader/1', 'mode': 'sequence', 'experiment_id': 'VR-20260907-01',
                'plan_pending': True, 'entries': [], 'styles': [], 'panels': [], 'available_count': 0,
                'total_count': 18, 'owner_approval': None, 'production_accepted': False}
        OUT.mkdir(parents=True, exist_ok=True)
        text = json.dumps(data, indent=2)
        (OUT / 'sequence-data.json').write_text(text + '\n')
        (OUT / 'sequence-data.js').write_text('window.VR_SEQUENCE_DATA = ' + text + ';\n')
        return data
    panels, styles = plan['panels'], plan['provisional_styles']
    if [p['id'] for p in panels] != [f'P{i:02}' for i in range(1, 7)] or len(styles) not in (0, 3):
        raise ValueError('Sequence requires six panels and zero or three provisional styles')
    if len({s['id'] for s in styles}) != len(styles) or set(s['id'] for s in styles) - set(STARS):
        raise ValueError('Provisional styles must be distinct members of the nine-style shortlist')
    for p in panels:
        copy_ids = [c['id'] for c in p.get('copy', [])]
        if len(copy_ids) != len(set(copy_ids)) or any(not isinstance(c['text'], str) for c in p.get('copy', [])):
            raise ValueError('Invalid exact sequence copy')
    candidates = candidate_map('sequence-')
    entries = [{'id': f'{s["id"]}-{p["id"]}', 'kind': 'sequence', 'style_id': s['id'], 'panel_id': p['id'],
                'candidate': candidates.get(f'{s["id"]}-{p["id"]}')} for s in styles for p in panels]
    if set(candidates) - {e['id'] for e in entries}:
        raise ValueError('Unknown selected sequence ID')
    if require_complete and (len(entries) != 18 or any(e['candidate'] is None for e in entries)):
        raise ValueError('Final sequence requires 18 actual selected panels')
    entries = add_repairs(entries, 'sequence-')
    review_path = SOURCE / 'sequence-review-notes.json'
    review = read_json(review_path)
    routes = []
    if review:
        if review.get('schema') != 'RefinementReviewNotes/1' or review.get('experiment_id') != plan['experiment_id']:
            raise ValueError('Sequence review notes refer to the wrong experiment')
        def valid_observations(value):
            if not isinstance(value, list) or any(not isinstance(n, str) for n in value):
                raise ValueError('AI observations must be plain text')
        for key, note in review.get('entries', {}).items():
            candidate = candidates.get(key)
            if not candidate or note['attempt_id'] != candidate['attempt_id'] or note['sha256'] != candidate['sha256']:
                raise ValueError(f'Stale AI observations for {key}')
            valid_observations(note['observations'])
        seen = set()
        for route in review.get('routes', []):
            style = route['style_id']
            if style not in {s['id'] for s in styles} or style in seen:
                raise ValueError('Unknown or duplicate sequence observation route')
            seen.add(style)
            expected = {e['id']: {'attempt_id': e['candidate']['attempt_id'], 'sha256': e['candidate']['sha256']} for e in entries if e['style_id'] == style and e['candidate']}
            if len(expected) != 6 or route['source_bindings'] != expected:
                raise ValueError('Stale or incomplete route observation sources')
            valid_observations(route['observations'])
            routes.append(route)
        entries = [{**e, 'ai_observations': review.get('entries', {}).get(e['id'], {}).get('observations', [])} for e in entries]
    return emit('sequence', plan, path, entries, styles=styles, panels=panels, route_observations=routes,
                review_notes_sha256=sha(review_path) if review else None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-comparison', action='store_true')
    parser.add_argument('--require-sequence', action='store_true')
    args = parser.parse_args()
    for data in [build_comparison(args.require_comparison), build_sequence(args.require_sequence)]:
        print(json.dumps({'mode': data['mode'], 'available': data['available_count'], 'total': data['total_count'], 'dataset_sha256': data.get('dataset_sha256')}))
