import base64, datetime, hashlib, json
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[5]
folder = Path(__file__).resolve().parents[1]
def h(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

outcomes = {
    'N4-32-P': 'Superseded: cream wallet missing and service-gap landmark not identifiable; supported ordinary walk correct.',
    'N4-32-R1': 'Recommended and root inspected: wallet restored, distant open gap/right upright restored without obstructing supported public path.',
    'N4-33-34-P': 'Superseded: upper extra uncorded gold tag, missing cream wallet and healed left elbow; receipt transfer and lower relief correct.',
    'N4-33-34-R1': 'Recommended and root inspected: upper tag removed, cream wallet and small left elbow tear restored; receipt transfer and lower relief retained.',
    'N4-35-36-P': 'Superseded: duplicate closed waist wallet in35 alongside valid open tabletop wallet; paid coin action and lower36 correct.',
    'N4-35-36-R1': 'Recommended and root inspected: upper duplicate wallet removed, open tabletop wallet and lower reclosed wallet preserved.',
    'N4-37-38-P': 'Superseded: copied courier bag on Kiva and additional anatomical-left capped tubes on Aren; room introduction acting correct.',
    'N4-37-38-R1': 'Recommended and root inspected: Kiva bag and extra left tubes removed; actual right sheath37 retained, outside38 close framing.',
    'N4-39-40-P': 'Recommended and root inspected: warm supported departure, closed own ledger, right sheath/left tear, closed cream wallet mostly under glove, departed packet farther along canal; no material repair needed.'
}
checks = []
for aid, outcome in outcomes.items():
    p = folder/'calls'/f'{aid}.json'
    d = json.loads(p.read_text())
    a = json.loads((folder/'requests'/f'{aid}.json').read_text())
    n = folder/'candidates'/f'{aid}.png'
    raw = json.loads(Path(d['raw_return_path']).read_text())
    assert h(n) == d['sha256'] == h(Path(d['source_path']))
    assert base64.b64decode(raw['image_url'].split(',', 1)[1]) == n.read_bytes()
    assert a['prompt'] == (folder/'requests'/f'{aid}.txt').read_text()
    assert hashlib.sha256(a['prompt'].encode()).hexdigest() == d['prompt_sha256']
    assert len(a['referenced_image_paths']) == len(d['references'])
    for ref, actual in zip(d['references'], a['referenced_image_paths']):
        assert h(root/ref['path']) == ref['sha256']
        assert Path(actual) == root/ref['path']
    assert d['status'] == 'returned' and d['submitted_utc']
    d.update(invoked=True, actual_inspection=outcome)
    p.write_text(json.dumps(d, indent=2)+'\n')
    checks.append({'id': aid, 'status': 'PASS', 'sha256': h(n), 'actual_outcome': outcome})

records = json.loads((folder/'notes/selected-records.json').read_text())
assert set(records['selected']) == {f'N4-{i}' for i in range(32,41)}
crops = []
for panel, d in records['selected'].items():
    assert h(root/d['path']) == d['sha256']
    if 'crop' in d:
        c = d['crop']; src = root/c['source_path']
        assert h(src) == c['source_sha256']
        assert list(Image.open(src).size) == c['source_dimensions']
        assert Image.open(src).crop(c['box_xyxy']).tobytes() == Image.open(root/d['path']).tobytes()
        crops.append(panel)
for d in json.loads((folder/'references/records.json').read_text()):
    src = root/d['source_path']; dest = root/d['path']
    assert h(dest) == d['sha256'] and h(src) == d['source_sha256']
    assert list(Image.open(src).size) == d['source_dimensions']
    assert Image.open(src).crop(d['box_xyxy']).tobytes() == Image.open(dest).tobytes()
    if 'viewed_selected_tier' in d:
        t = d['viewed_selected_tier']; tier = root/t['path']
        assert h(tier) == t['sha256']
        assert Image.open(src).crop(t['native_box_xyxy']).tobytes() == Image.open(tier).tobytes()
        assert Image.open(tier).crop(t['detail_box_in_tier_xyxy']).tobytes() == Image.open(dest).tobytes()
    crops.append(d['path'])
receipt = {'status':'PASS', 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'calls_submitted':9, 'calls_returned':9, 'primaries':5, 'structural_repairs':4,
           'tool_failures':0, 'pending':0, 'finishes':0, 'calls':checks,
           'selected_hashes_verified':9, 'lossless_crops_verified':crops,
           'shared_selection_mutated':False,
           'timestamp_note':'returned_utc records local preservation time after tool completion; not provider timing telemetry.'}
(folder/'notes/integrity.json').write_text(json.dumps(receipt, indent=2)+'\n')
(folder/'candidates.json').write_text(json.dumps({'unit':'N4-32–40', 'actual_calls':9,
    'primaries':5, 'structural_repairs':4, 'tool_failures':0, 'finishes':0, 'pending':0,
    'attempts':checks, 'recommended_records':'notes/selected-records.json', 'review':'notes/REVIEW.md'}, indent=2)+'\n')
print(f'PASS:9 native/original/raw/prompt/reference chains;9 selected hashes;{len(crops)} lossless panel/reference crops.')
