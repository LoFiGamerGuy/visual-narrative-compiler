"""Verify the closed study's frozen briefs, exact prompts, originals and display choices."""
from pathlib import Path
import datetime, hashlib, json, struct

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / 'production/visual-directions'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    return json.loads(path.read_text())

frozen = {}
for name in ('experiment.json', 'concepts.json'):
    actual = digest(P / name)
    assert actual == (P / (name + '.sha256')).read_text().strip(), name
    frozen[name] = actual
candidates = read(P / 'candidates.json')['candidates']
selected = read(P / 'selected.json')['selected']
assert len(candidates) == 21 and len(selected) == 20
assert set(selected) == {f'{i:02}' for i in range(1, 21)}
assert len({c['attempt_id'] for c in candidates}) == 21
assert len({c['sha256'] for c in candidates}) == 21
bindings = []
for c in candidates:
    suffix = 'retry' if c['attempt_id'].endswith('-R') else 'primary'
    reservation = read(P / 'calls' / f"{c['id']}-{suffix}.json")
    returned_name = f"{c['id']}-retry-returned.json" if suffix == 'retry' else f"{c['id']}-returned.json"
    returned = read(P / 'calls' / returned_name)
    assert returned['attempt_id'] == reservation['attempt_id'] == c['attempt_id']
    assert digest(ROOT / reservation['prompt_path']) == reservation['prompt_sha256']
    native = ROOT / c['path']
    assert digest(native) == digest(Path(returned['source_path'])) == c['sha256']
    data = native.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', data[16:24]) == (c['width'], c['height']) == (1536, 1024)
    assert len(data) == c['bytes']
    assert all(c[k] is None and reservation[k] is None for k in ('provider','model','seed','usage','billing_allocation'))
    assert c['direct_paid_usd'] == reservation['direct_paid_usd'] == 0
    for reference in reservation['references']:
        assert digest(ROOT / reference['path']) == reference['sha256']
    bindings.append({'id':c['id'], 'attempt_id':c['attempt_id'], 'path':c['path'], 'sha256':c['sha256'], 'displayed':selected[c['id']] == c['attempt_id']})
assert sum(b['displayed'] for b in bindings) == 20
assert selected['19'] == 'VD19-R'
assert len(list((P / 'calls').glob('*-returned.json'))) == 21
result = {
    'schema':'DirectionStudyResults/1',
    'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'experiment_id':'VD-20260907-01',
    'frozen_inputs':frozen,
    'concepts':20, 'primary_calls':20, 'targeted_retry_calls':1,
    'total_tool_calls':21, 'returned_native_images':21, 'displayed_options':20,
    'native_dimensions':[1536,1024], 'tool_originals_retained_and_hash_verified':21,
    'correction':{'direction':'19','primary':'VD19-P','displayed':'VD19-R','reason':'Generated signature-like artifact','method':'Built-in generative image edit; primary retained; not a claim of exact pixels unchanged elsewhere'},
    'generation_closed':True, 'unused_retry_allowance':5,
    'direct_paid_usd':0, 'provider':None, 'raster_model':None, 'seed':None, 'usage':None, 'billing_allocation':None,
    'owner_favorites':None, 'production_accepted':False,
    'art_scope':'Twenty independent visual concepts with varied characters, settings and monsters; shared medium families remain. Not sequence-consistency evidence.',
    'bindings':bindings, 'artifact_verification_pass':True,
}
(ROOT / 'research/visual-directions/results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','frozen_inputs')}))
