from pathlib import Path
from PIL import Image
import json, hashlib, base64, datetime
b=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
results=[]
for p in sorted((b/'requests').glob('*.json')):
 a=json.loads(p.read_text());r=json.loads((b/'calls'/p.name).read_text());raw=json.loads((b/'calls'/(p.stem+'-tool-return.json')).read_text());meta=json.loads((b/'calls'/(p.stem+'-return-metadata.json')).read_text())
 assert a==r['args'] and r['status']=='returned'
 assert all(sha(x['path'])==x['sha256'] for x in r['references'])
 assert Path(r['native_source']).read_bytes()==Path(r['native_copy']).read_bytes()==base64.b64decode(raw['image_url'].split(',',1)[1])
 assert sha(r['native_copy'])==r['native_sha256'] and len(raw['image_url'])==meta['image_url_length'] and raw['output_hint']==meta['output_hint']
 results.append({'attempt_id':p.stem,'kind':r['kind'],'sha256':r['native_sha256'],'pass':True})
 selected=json.loads((b/'selected-records.json').read_text())
assert len(selected)==7
for r in selected:
 assert sha(r['path'])==r['sha256'];c=r['crop'];assert sha(c['source_path'])==c['source_sha256'];im=Image.open(c['source_path']);assert list(im.size)==c['source_dimensions'];assert im.crop(c['box_xyxy']).tobytes()==Image.open(r['path']).tobytes()
for r in json.loads((b/'references/records.json').read_text()):
 assert sha(r['path'])==r['sha256'] and sha(r['source_path'])==r['source_sha256'];im=Image.open(r['source_path']);assert list(im.size)==r['source_dimensions'];assert im.crop(r['box_xyxy']).tobytes()==Image.open(r['path']).tobytes()
out={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_calls_returned':len(results),'primary':sum(x['kind']=='primary' for x in results),'structural_repairs':sum(x['kind'] in ('structural_repair','structural-repair') for x in results),'finish':0,'attempts':results,'seven_selected_full_native_tiers_verified':True,'all_reference_derivatives_verified':True,'raw_return_note':'Semantic tool-return objects preserve exact image_url bytes/output_hint; no model/seed/billing fabricated.'}
(b/'notes/FINAL-VERIFICATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
