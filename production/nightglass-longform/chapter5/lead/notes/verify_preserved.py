"""Audit already preserved lead calls and selected rectangular crops; no visual claims."""
import base64,hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
b=Path(__file__).resolve().parents[5];root=b/'production/nightglass-longform/chapter5/lead'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checked=[]
for p in sorted((root/'calls').glob('*.json')):
 if 'tool-return' in p.name:continue
 r=json.loads(p.read_text());assert r['status']=='returned',r['id']
 original=Path(r['source_path']);native=Path(r['path']);raw=json.loads(Path(r['raw_return_path']).read_text());args=json.loads(Path(r['arguments_path']).read_text())
 assert args==r['args'];assert hashlib.sha256(args['prompt'].encode()).hexdigest()==r['prompt_sha256'];assert sha(original)==sha(native)==r['sha256'];assert base64.b64decode(raw['image_url'].split(',',1)[1])==native.read_bytes()
 for ref in r['references']:assert sha(b/ref['path'])==ref['sha256']
 checked.append({'id':r['id'],'sha256':r['sha256'],'dimensions':list(Image.open(native).size),'status':'PASS'})
selected=json.loads((b/'production/nightglass-longform/selected.json').read_text())['selected'];crops=[]
for name,r in selected.items():
 if not name.startswith('N5-') or '/lead/' not in r['path']:continue
 target=b/r['path'];assert sha(target)==r['sha256']
 if r.get('crop'):
  c=r['crop'];source=b/c['source_path'];assert sha(source)==c['source_sha256'];a=Image.open(source).crop(c['box_xyxy']).convert('RGBA');v=Image.open(target).convert('RGBA');assert a.size==v.size and ImageChops.difference(a,v).getbbox() is None;crops.append(name)
result={'calls':checked,'lead_calls_verified':len(checked),'selected_lead_crops_verified':crops,'checks':'Exact args/prompt hash/reference hashes/original native bytes/raw return base64/selected hash and crop pixels PASS','visual_review':'Separate actual lead and independent readings required; this audit makes no visual claim.'}
(root/'notes/INTEGRITY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'lead_calls_verified':len(checked),'selected_lead_crops_verified':crops,'passed':True}))
