import base64
import hashlib
import json
import shutil
import sys
from pathlib import Path

root = Path(__file__).parent
call_id, source_name = sys.argv[1:]
source = Path(source_name)
target = root / 'candidates' / (call_id + '.png')
shutil.copy2(source, target)
meta = json.loads((root / 'calls' / (call_id + '-return-metadata.json')).read_text())
raw = {'image_url': 'data:image/png;base64,' + base64.b64encode(target.read_bytes()).decode(), 'output_hint': meta['output_hint']}
assert len(raw['image_url']) == meta['image_url_length']
(root / 'calls' / (call_id + '-tool-return.json')).write_text(json.dumps(raw))
record_path = root / 'calls' / (call_id + '.json')
record = json.loads(record_path.read_text())
record.update(status='returned', native_source=str(source), native_copy=str(target), native_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
record_path.write_text(json.dumps(record, indent=2))
print(call_id, 'native bytes and semantic raw return preserved')
