"""Read-only bounded provenance checks; output stays in this owned notes folder."""
import base64
import datetime
import hashlib
import json
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[5]
NOTES = Path(__file__).resolve().parent
LEAD = ROOT / 'production/nightglass-longform/chapter8/lead'
IDS = ['N8-03-04-P', 'N8-03-04-R1', 'N8-05-06-P', 'N8-05-06-R1',
       'N8-07-P', 'N8-08-09-P', 'N8-10-11-P', 'N8-10-11-R1',
       'N8-12-13-P', 'N8-14-P', 'N8-14-R1']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def parse(path):
    return json.loads(path.read_text())

def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p

started = datetime.datetime.now(datetime.timezone.utc).isoformat()
frozen = {i: {'record': parse(LEAD / 'calls' / f'{i}.json'),
              'sha256': sha(LEAD / 'calls' / f'{i}.json')} for i in IDS}
selected_file = ROOT / 'production/nightglass-longform/selected.json'
selected = {p: v for p, v in parse(selected_file)['selected'].items()
            if p in {f'N8-{n:02d}' for n in range(3, 15)}}
assert len(selected) == 12
errors, calls, crops, selected_results = [], [], [], []

for ident in IDS:
    c = frozen[ident]['record']
    try:
        assert c['id'] == ident and c['status'] == 'returned' and c['invoked'] is True
        assert c['phase'] == ('primary' if ident.endswith('-P') else 'repair')
        ap = resolve(c['arguments_path']); args = parse(ap)
        prompt = (LEAD / 'requests' / f'{ident}.txt').read_text()
        assert args == c['args'] and args['prompt'] == prompt
        assert hashlib.sha256(prompt.encode()).hexdigest() == c['prompt_sha256']
        assert set(args) == {'prompt', 'referenced_image_paths'}
        native = resolve(c['path']); default = resolve(c['source_path'])
        raw_path = resolve(c['raw_return_path']); raw = parse(raw_path)
        assert set(raw) == {'image_url', 'output_hint'}
        assert raw['image_url'].startswith('data:image/png;base64,')
        decoded = base64.b64decode(raw['image_url'].split(',', 1)[1], validate=True)
        assert native.read_bytes() == default.read_bytes() == decoded
        assert sha(native) == c['sha256'] and str(default) in raw['output_hint']
        assert len(args['referenced_image_paths']) == len(c['references'])
        for path, ref in zip(args['referenced_image_paths'], c['references']):
            assert resolve(path) == ROOT / ref['path']
            assert sha(resolve(path)) == ref['sha256']
        for key in ['model_snapshot', 'seed', 'billing', 'owner_approval']:
            assert key in c and c[key] is None
        submitted = datetime.datetime.fromisoformat(c['submitted_utc'])
        returned = datetime.datetime.fromisoformat(c['returned_utc'])
        assert submitted.tzinfo and returned.tzinfo and returned >= submitted
        if c['phase'] == 'repair':
            primary = frozen[ident.rsplit('-', 1)[0] + '-P']['record']
            assert c['panels'] == primary['panels']
            assert primary['sha256'] in [r['sha256'] for r in c['references']]
            assert submitted >= datetime.datetime.fromisoformat(primary['returned_utc'])
        calls.append({'id': ident, 'status': 'PASS', 'phase': c['phase'],
                      'call_record_sha256': frozen[ident]['sha256'],
                      'request_file_sha256': sha(ap), 'prompt_sha256': c['prompt_sha256'],
                      'native_sha256': c['sha256'], 'raw_return_sha256': sha(raw_path),
                      'dimensions': list(Image.open(native).size),
                      'references': c['references'], 'submitted_utc': c['submitted_utc'],
                      'returned_utc': c['returned_utc'], 'default_native_decoded_raw_equal': True})
    except Exception as exc:
        errors.append({'id': ident, 'error': repr(exc)})

for panel, record in selected.items():
    try:
        assert record['attempt_id'] in IDS
        path = resolve(record['path']); assert sha(path) == record['sha256']
        if 'crop' in record:
            c = record['crop']; source = resolve(c['source_path'])
            assert sha(source) == c['source_sha256']
            original = Image.open(source); actual = Image.open(path)
            assert list(original.size) == c['source_dimensions']
            box = c['box_xyxy']; assert len(box) == 4 and all(type(v) is int for v in box)
            assert 0 <= box[0] < box[2] <= original.width
            assert 0 <= box[1] < box[3] <= original.height
            expected = original.crop(box)
            assert actual.mode == expected.mode and actual.size == expected.size
            assert actual.tobytes() == expected.tobytes()
            crops.append({'panel': panel, 'path': str(path.relative_to(ROOT)),
                          'sha256': record['sha256'], 'source_sha256': c['source_sha256'],
                          'box_xyxy': box, 'exact_unscaled_pixel_equivalence': True})
        else:
            assert path == resolve(frozen[record['attempt_id']]['record']['path'])
        selected_results.append({'panel': panel, 'attempt_id': record['attempt_id'],
                                 'sha256': record['sha256'], 'status': 'PASS'})
    except Exception as exc:
        errors.append({'panel': panel, 'error': repr(exc)})

# Metadata-only scope/cap reconciliation; no re-audit of previously checked02 or room.
counter = {}
for scope in ['lead', 'room-ending', 'relay-return']:
    directory = ROOT / 'production/nightglass-longform/chapter8' / scope / 'calls'
    metadata = [parse(p) for p in directory.glob('*.json') if not p.name.endswith('-tool-return.json')]
    counter[scope] = {'invoked': sum(bool(c.get('invoked')) for c in metadata),
                      'returned': sum(c.get('status') == 'returned' for c in metadata),
                      'pending': sum(c.get('invoked') and c.get('status') != 'returned' for c in metadata)}
    if scope == 'lead':
        for phase in ['primary', 'repair']:
            usage = Counter(p for c in metadata if c.get('invoked') and c.get('phase') == phase
                            for p in c.get('panels', []))
            if any(n > 1 for n in usage.values()):
                errors.append({'scope': scope, 'phase': phase, 'duplicate_panel_attempts': dict(usage)})

for ident in IDS:
    if sha(LEAD / 'calls' / f'{ident}.json') != frozen[ident]['sha256']:
        errors.append({'id': ident, 'error': 'Call metadata changed during bounded audit'})
current = parse(selected_file)['selected']
if any(current.get(p) != r for p, r in selected.items()):
    errors.append({'error': 'Audited selected projection changed during audit'})

receipt = {'status': 'PASS' if not errors else 'FAIL', 'started_utc': started,
           'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'frozen_call_ids': IDS, 'actual_new_calls_audited': len(calls),
           'primaries': 7, 'repairs': 4, 'finishes': 0, 'pending_in_frozen_set': 0,
           'references_checked': sum(len(c['references']) for c in calls),
           'calls': calls, 'selected': selected_results, 'exact_selected_crops': crops,
           'scope_metadata_counter_observation': counter, 'errors': errors,
           'request_digest_note': 'Stored prompt digests verified; exact request JSON equals submitted args. Request-file SHA256 is newly computed audit evidence, not a claimed historical whole-request digest field.',
           'timestamp_note': 'Recorded local submitted/returned timestamps are ordered; no inference of unknown backend start or model metadata.',
           'limits': 'Preservation only. No renewed actual visual/phone/story acceptance.02/room counted only, not re-audited. Relay calls excluded even if started during audit. Failed native attempts remain intact.',
           'shared_mutations': False, 'image_calls_by_audit': 0}
(NOTES / 'CROSS-AUDIT-N8-03-14.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ['status','actual_new_calls_audited','references_checked','scope_metadata_counter_observation','errors']}, indent=2))
raise SystemExit(bool(errors))
