"""Reconcile new chapter calls without counting argument/return/request duplicates."""
from pathlib import Path
import collections
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
path = HERE / 'generation-accounting.json'
data = json.loads(path.read_text())
# The 47 opening/comparison invocations were individually reconciled at delivery.
records = [r for r in data['records'] if not any(
    f'/chapter{n}/' in r['record'] for n in range(2, 10))]
for folder in sorted(HERE.glob('chapter[2-9]')):
    for record in sorted(folder.glob('*/calls/*.json')):
        if any(part in record.name for part in ('return', '.args.', '.response.')):
            continue
        canonical = record.with_name(record.name.replace('.request.', '.'))
        if '.request.' in record.name and canonical.exists():
            continue
        value = json.loads(record.read_text())
        if not (value.get('args') or value.get('arguments_path')):
            continue
        if value.get('status') in (None, 'prepared'):
            continue
        ident = value.get('id', value.get('attempt_id', record.stem.replace('.request', '')))
        phase = 'structural_repair' if ident.endswith('-R1') else 'primary'
        records.append(dict(record=str(record.relative_to(ROOT)),
            record_sha256=hashlib.sha256(record.read_bytes()).hexdigest(),
            attempt_id=ident, phase=phase, recorded_status=value['status']))
data.update(records=records, actual_invocations=len(records),
    remaining_allowance=data['invocation_ceiling'] - len(records),
    phase_counts=dict(collections.Counter(r['phase'] for r in records)),
    pending_invocations=sum(r['recorded_status'] in ('submitted', 'running') for r in records))
selected = json.loads((HERE / 'selected.json').read_text())['selected']
for n in range(2, 10):
    count = sum(k.startswith(f'N{n}-') for k in selected)
    if count:
        data['story_panels'][f'chapter{n}_selected'] = count
path.write_text(json.dumps(data, indent=2) + '\n')
print({k: data[k] for k in ('actual_invocations', 'pending_invocations', 'remaining_allowance')})
print('Pending:', [r['attempt_id'] for r in records if r['recorded_status'] in ('submitted', 'running')])
