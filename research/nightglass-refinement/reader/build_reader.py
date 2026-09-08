"""Build the isolated nightglass-refinement gallery. Source plans, selections and art are read-only."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'production/nightglass-refinement'
OUT = ROOT / 'docs/nightglass-refinement'
STYLES = ['01', '02', '05', '06', '13', '15', '17', '18', '19']
CATEGORY_IDS = {'refinement':[f'T{i:02}' for i in range(1,5)], 'scene':[f'S{i:02}' for i in range(1,7)], 'character':[f'C{i:02}' for i in range(1,5)], 'equipment':[f'G{i:02}' for i in range(1,4)], 'wildlife':['W01'], 'monster':['M01','M02'], 'ability':[f'A{i:02}' for i in range(1,5)]}
BEFORE_IDS = {'T01':'S01','T02':'S06','T03':'C01','T04':'M01'}
DIMENSIONS = {'refinement':['overall','drawing','texture','component_preservation'], 'scene':['overall','drawing','character','setting','creature','action','texture'], 'character':['overall','drawing','character','weapon','power','texture'], 'equipment':['overall','drawing','design','function','texture'], 'wildlife':['overall','drawing','creature','setting','texture'], 'monster':['overall','drawing','creature','threat','texture'], 'ability':['overall','drawing','power','action','texture']}
LABELS = {'refinement':'Texture pairs','scene':'Full scenes','character':'Characters','equipment':'Equipment','wildlife':'Wildlife','monster':'Monsters','ability':'Abilities'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default

def asset(value, board=False):
    path = (ROOT / value['path']).resolve()
    if not path.is_relative_to(SOURCE.resolve()):
        raise ValueError('Image path leaves the nightglass-refinement namespace')
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

def previous():
    folder = SOURCE / 'previous'
    manifest_path = folder / 'manifest.json'
    manifest = read(manifest_path)
    if not manifest or manifest.get('schema') != 'WorldCombatPreviousSources/1':
        raise ValueError('Preserved previous source manifest is required')
    selection_path = (ROOT / manifest['selection_path']).resolve()
    if not selection_path.is_relative_to(folder.resolve()):
        raise ValueError('Previous choice file leaves preserved namespace')
    selection = read(selection_path)
    data_path = folder / 'data.json'
    old = read(data_path)
    validation = read(ROOT / 'research/nightglass-refinement/previous-validation.json')
    if not validation or validation.get('schema') != 'WorldCombatPreviousValidation/1' or validation.get('export_sha256') != sha(selection_path) or validation.get('data_sha256') != sha(data_path) or validation.get('plan_sha256') != sha(folder / 'plan.json') or selection.get('plan_sha256') != sha(folder / 'plan.json'):
        raise ValueError('Preserved export, data or plan differs from validated original bytes')
    if selection.get('schema') != 'CombatExplorationChoices/1' or old.get('schema') != 'CombatExplorationReader/1':
        raise ValueError('Unexpected preserved previous schemas')
    for key in ['experiment_id','dataset_sha256','plan_sha256','source_bindings']:
        if selection.get(key) != old.get(key):
            raise ValueError('Previous choices no longer match their original dataset')
    old_entries = {e['id']:e for e in old['entries']}
    bindings = {b['id']:b for b in selection['source_bindings']}
    sources = manifest['sources']
    if len(sources) != 18 or len({s['id'] for s in sources}) != 18 or set(s['id'] for s in sources) != set(old_entries) or set(selection['choices']) != set(old_entries) or set(bindings) != set(old_entries):
        raise ValueError('All18 exact previous sources and choices are required')
    cards = []
    for source in sources:
        id = source['id']; bound = bindings[id]; entry = old_entries[id]; choice = selection['choices'][id]
        if any(source.get(k) != bound.get(k) or entry['candidate'].get(k) != bound.get(k) for k in ['attempt_id','sha256']):
            raise ValueError('Previous source identity has changed')
        if set(choice) != {'character','style','weapon','power','comfort','note','shortlist'} or any(choice[k] not in [None,'like','dislike','unsure'] for k in ['character','style','weapon','power']) or choice['comfort'] not in [None,'yes','no','unsure'] or not isinstance(choice['note'],str) or type(choice['shortlist']) is not bool:
            raise ValueError('Malformed preserved previous response')
        path = (ROOT / source['path']).resolve()
        if not path.is_relative_to(folder.resolve()):
            raise ValueError('Previous image leaves preserved namespace')
        cards.append({'id':id,'title':entry['title'],'style_id':entry['style_id'],'candidate':asset(source),'choices':choice})
    return {'schema':'NightglassRefinementPreviousView/1','experiment_id':selection['experiment_id'],
            'dataset_sha256':selection['dataset_sha256'],'manifest_sha256':sha(manifest_path),'data_sha256':sha(data_path),
            'selection_path':selection_path.relative_to(ROOT).as_posix(),'selection_sha256':sha(selection_path),
            'download_src':os.path.relpath(selection_path, OUT).replace(os.sep,'/'),'styles':old['styles'],'entries':cards}

def previous_world():
    folder = SOURCE / 'previous-world'; manifest_path = folder / 'manifest.json'
    manifest = read(manifest_path); data_path = folder / 'data.json'; old = read(data_path)
    if not manifest or manifest.get('schema') != 'NightglassRefinementPreviousWorld/1' or not old or old.get('schema') != 'WorldCombatReader/1':
        raise ValueError('Preserved world-combat manifest and data are required')
    if manifest.get('data_sha256') != sha(data_path) or manifest.get('dataset_sha256') != old.get('dataset_sha256') or manifest.get('experiment_id') != old.get('experiment_id') or manifest.get('owner_choices_export') is not None:
        raise ValueError('Previous world source binding changed or unprovided ratings were added')
    entries = {e['id']:e for e in old['entries']}; sources = manifest['sources']
    if len(entries) != 24 or len(sources) != 24 or len({s['id'] for s in sources}) != 24 or set(s['id'] for s in sources) != set(entries):
        raise ValueError('All24 previous world images are required')
    cards = []
    for source in sources:
        e = entries[source['id']]
        if any(source[k] != e['candidate'][k] for k in ['attempt_id','sha256']):
            raise ValueError('Previous world image identity changed')
        if not (ROOT / source['path']).resolve().is_relative_to(folder.resolve()):
            raise ValueError('Previous world image leaves its preserved namespace')
        cards.append({'id':e['id'],'title':e['title'],'category':e['category'],'style_id':e['style_id'],'caption':e['caption'],'candidate':asset(source)})
    feedback_path = SOURCE / 'owner-feedback.json'; feedback = read(feedback_path)
    if not feedback or feedback.get('schema') != 'NightglassRefinementOwnerFeedback/1' or not isinstance(feedback.get('verbatim'),str) or feedback.get('new_round_choices') is not None:
        raise ValueError('Global owner feedback must remain distinct from new choices')
    return {'schema':'NightglassRefinementPreviousWorldView/1','experiment_id':old['experiment_id'],'dataset_sha256':old['dataset_sha256'],'data_sha256':sha(data_path),'manifest_sha256':sha(manifest_path),'entries':cards,'owner_feedback':feedback['verbatim'],'feedback_sha256':sha(feedback_path),'per_image_choices':None}

def build(require_complete=False):
    plan_path = SOURCE / 'refinement-plan.json'
    plan = read(plan_path)
    if not plan or plan.get('schema') != 'NightglassRefinementPlan/1':
        raise ValueError('A frozen NightglassRefinementPlan/1 is required')
    if not isinstance(plan.get('experiment_id'), str) or not plan['experiment_id']:
        raise ValueError('Experiment identity is required')
    if not plan.get('styles') or len({s['id'] for s in plan['styles']}) != len(plan['styles']) or set(s['id'] for s in plan['styles']) - set(STYLES):
        raise ValueError('Plan styles must be distinct original anchor IDs')
    world = previous_world()
    world_entries = {e['id']:e for e in world['entries']}
    entries = plan['entries']
    expected = {id for ids in CATEGORY_IDS.values() for id in ids}
    if len(entries) != 24 or {e['id'] for e in entries} != expected:
        raise ValueError('Exactly24 frozen nightglass-refinement IDs are required')
    for e in entries:
        if e.get('before_id') != BEFORE_IDS.get(e['id']):
            raise ValueError('Paired before ID differs from frozen four-study mapping')
        if e.get('category') not in CATEGORY_IDS or e['id'] not in CATEGORY_IDS[e['category']]:
            raise ValueError('Entry ID does not match its category')
        if e['style_id'] not in {s['id'] for s in plan['styles']}:
            raise ValueError('Entry style is not declared by the plan')
        if 'age' in e and (type(e['age']) is not int or e['age'] < 18):
            raise ValueError('An explicit character age must be adult')
        if any(not isinstance(e.get(k), str) or not e[k].strip() for k in ['title', 'caption']):
            raise ValueError('Title and visible caption are required')
        for k in ['weapon', 'power']:
            if k in e and (not isinstance(e[k], dict) or any(not isinstance(e[k].get(f), str) or not e[k][f].strip() for f in ['name','description'])):
                raise ValueError('Optional weapon and power need names and descriptions')
        if 'power' in e:
            if 'limitation' in e['power'] and not isinstance(e['power']['limitation'], str):
                raise ValueError('Power limitation must be plain text')
            if not isinstance(e['power'].get('growth', []), list) or any(not isinstance(t,str) for t in e['power'].get('growth',[])):
                raise ValueError('Power growth must be a plain text list')
        if not isinstance(e.get('related_ids',[]),list) or set(e.get('related_ids',[]))-expected:
            raise ValueError('Related links must refer to this round only')
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
        cards.append({**entry, 'candidate': selected.get(entry['id']), 'history': history, 'before':world_entries[entry['before_id']]['candidate'] if entry.get('before_id') else None})
    notes_path = SOURCE / 'review-notes.json'
    notes = read(notes_path)
    if notes:
        if notes.get('schema') != 'NightglassRefinementReviewNotes/1' or notes.get('experiment_id') != plan['experiment_id']:
            raise ValueError('Technical notes belong to another experiment')
        for id, note in notes.get('entries', {}).items():
            c = selected.get(id)
            if not c or note.get('attempt_id') != c['attempt_id'] or note.get('sha256') != c['sha256']:
                raise ValueError('Stale technical note source')
            if not isinstance(note.get('observations'), list) or any(not isinstance(t, str) for t in note['observations']):
                raise ValueError('Technical observations must be plain strings')
    cards = [{**e, 'ai_observations': (notes or {}).get('entries', {}).get(e['id'], {}).get('observations', [])} for e in cards]
    if require_complete and len(selected) != 24:
        raise ValueError('Final reader requires all24 actual selected nightglass-refinement images')
    bindings = [{'id': e['id'], 'attempt_id': e['candidate']['attempt_id'] if e['candidate'] else None,
                 'sha256': e['candidate']['sha256'] if e['candidate'] else None, 'before_id':e.get('before_id'), 'before_attempt_id':e['before']['attempt_id'] if e['before'] else None, 'before_sha256':e['before']['sha256'] if e['before'] else None} for e in cards]
    identity = {'experiment_id': plan['experiment_id'], 'plan_sha256': sha(plan_path), 'source_bindings': bindings}
    data = {'schema': 'NightglassRefinementReader/1', **identity,
            'dataset_sha256': hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'styles': plan['styles'], 'categories':[{'id':k,'title':LABELS[k],'dimensions':v} for k,v in DIMENSIONS.items()], 'entries':cards, 'references':references, 'previous':previous(), 'previous_world':world,
            'available_count': len(selected), 'total_count': 24, 'owner_approval': None,
            'review_notes_sha256': sha(notes_path) if notes else None,
            'report_links': [{'label': label, 'path': f'../../research/nightglass-refinement/{name}'}
                             for name, label in [('START_HERE.md', 'Study details'), ('RESULTS.md', 'Results & observations')]
                             if (ROOT / f'research/nightglass-refinement/{name}').exists()]}
    OUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False)
    (OUT / 'data.json').write_text(text + '\n')
    (OUT / 'data.js').write_text('window.NIGHTGLASS_REFINEMENT_DATA = ' + text + ';\n')
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    data = build(args.require_complete)
    print(json.dumps({'available': data['available_count'], 'total': 24, 'dataset_sha256': data['dataset_sha256']}))
