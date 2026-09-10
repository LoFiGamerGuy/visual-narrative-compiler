import base64
import datetime
import hashlib
import json
from pathlib import Path
import sys

aid, source_name, metadata_json = sys.argv[1:]
metadata = json.loads(metadata_json)
root = Path(__file__).resolve().parents[1]
source = Path(source_name)
destination = root / 'candidates' / f'{aid}.png'
raw_path = root / 'calls' / f'{aid}-tool-return.json'
record_path = root / 'calls' / f'{aid}.json'
if destination.exists() or raw_path.exists():
    raise SystemExit('Refusing to overwrite a candidate or preserved raw return')
record = json.loads(record_path.read_text())
assert record['id'] == aid and record['status'] == 'submitted'
source_bytes = source.read_bytes()
raw = {'image_url': 'data:image/png;base64,' + base64.b64encode(source_bytes).decode(),
       'output_hint': metadata['output_hint']}
assert isinstance(raw['output_hint'], str)
assert len(raw['image_url']) == metadata['image_url_length']
# Validate all input evidence before creating either immutable output.
with destination.open('xb') as stream:
    stream.write(source_bytes)
digest = hashlib.sha256(destination.read_bytes()).hexdigest()
assert digest == hashlib.sha256(source_bytes).hexdigest()
with raw_path.open('x') as stream:
    stream.write(json.dumps(raw) + '\n')
record.update(status='returned', returned_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              source_path=str(source), path=str(destination), sha256=digest, raw_return_path=str(raw_path))
record_path.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'id': aid, 'path': str(destination), 'sha256': digest}))
