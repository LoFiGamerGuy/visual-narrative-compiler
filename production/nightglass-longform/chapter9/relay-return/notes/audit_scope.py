from pathlib import Path
import json,hashlib,base64,collections
from PIL import Image
r=Path(__file__).resolve().parents[1];b=r.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[json.loads(p.read_text()) for p in sorted((r/'calls').glob('*.json')) if not p.name.endswith('-tool-return.json')]
for c in records:
 assert c['status']=='returned',c['id']
 p=Path(c['path']);assert sha(p)==c['sha256']==sha(Path(c['source_path']))
 raw=json.loads(Path(c['raw_return_path']).read_text());assert base64.b64decode(raw['image_url'].split(',',1)[1])==p.read_bytes()
 assert json.loads(Path(c['arguments_path']).read_text())==c['args']
 for ref in c['references']:assert sha(b/ref['path'])==ref['sha256']
 assert len([a for a in records if a['id']==c['id']])==1
selected=[]
for p in sorted((r/'notes').glob('N9-*-selected-records.json')):
 for c in json.loads(p.read_text()):
  im=Image.open(b/c['path']);src=b/c['crop']['source_path'];assert sha(b/c['path'])==c['sha256'];assert sha(src)==c['crop']['source_sha256']
  assert im.tobytes()==Image.open(src).crop(c['crop']['box_xyxy']).tobytes();selected.append(c)
assert len({c['panel'] for c in selected})==len(selected)
counts=dict(collections.Counter(c['phase'] for c in records));assert len(records)<=21
for unit in {c['id'].rsplit('-',1)[0] for c in records}:
 phases=[c['phase'] for c in records if c['id'].rsplit('-',1)[0]==unit];assert all(phases.count(x)<=1 for x in ['primary','repair','finish'])
print(json.dumps({'returned':len(records),'pending':0,'phase_counts':counts,'proposals':len(selected),'all_raw_default_native_args_refs_and_crop_checks':True},indent=2))
