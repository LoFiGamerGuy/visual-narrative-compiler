import base64
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys

aid, source_name, metadata_json = sys.argv[1:]
metadata = json.loads(metadata_json)
root = Path(__file__).resolve().parents[1]
source = Path(source_name)
destination = root / 'candidates' / f'{aid}.png'
if destination.exists():
    raise SystemExit('Refusing to overwrite a candidate')
shutil.copyfile(source, destination)
digest = hashlib.sha256(destination.read_bytes()).hexdigest()
assert digest == hashlib.sha256(source.read_bytes()).hexdigest()
raw = {'image_url': 'data:image/png;base64,' + base64.b64encode(source.read_bytes()).decode(),
       'output_hint': metadata['output_hint']}
assert len(raw['image_url']) == metadata['image_url_length']
raw_path = root / 'calls' / f'{aid}-tool-return.json'
raw_path.write_text(json.dumps(raw) + '\n')
record_path = root / 'calls' / f'{aid}.json'
record = json.loads(record_path.read_text())
record.update(status='returned', returned_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              source_path=str(source), path=str(destination), sha256=digest, raw_return_path=str(raw_path))
record_path.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'id': aid, 'path': str(destination), 'sha256': digest}))
