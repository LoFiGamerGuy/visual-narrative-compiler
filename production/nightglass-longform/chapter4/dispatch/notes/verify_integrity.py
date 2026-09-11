import base64,datetime,hashlib,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[5];folder=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
outcomes={'N4-15-P':'recommended; actual native passed, root native and390 passed','N4-16-P':'superseded: invented chest medal and no distinct uncovered recipient-area ruling','N4-16-R1':'recommended; actual native and details passed critical custody; root qualifies adjacent brass rectangles as minor hardware ambiguity','N4-17-18-P':'recommended; actual whole native/two crops and Mern/quay details passed; bag body occluded in17'}
checks=[]
for aid,outcome in outcomes.items():
 p=folder/'calls'/f'{aid}.json';d=json.loads(p.read_text());a=json.loads((folder/'requests'/f'{aid}.json').read_text());n=folder/'candidates'/f'{aid}.png';raw=json.loads(Path(d['raw_return_path']).read_text())
 assert h(n)==d['sha256']==h(Path(d['source_path']))
 assert base64.b64decode(raw['image_url'].split(',',1)[1])==n.read_bytes()
 assert a['prompt']==(folder/'requests'/f'{aid}.txt').read_text()
 assert hashlib.sha256(a['prompt'].encode()).hexdigest()==d['prompt_sha256']
 assert len(a['referenced_image_paths'])==len(d['references'])
 for ref,actual in zip(d['references'],a['referenced_image_paths']):assert h(root/ref['path'])==ref['sha256'] and Path(actual)==root/ref['path']
 d.update(invoked=True,actual_inspection=outcome);p.write_text(json.dumps(d,indent=2)+'\n');checks.append({'id':aid,'status':'PASS','sha256':h(n),'actual_outcome':outcome})
records=json.loads((folder/'notes/selected-records.json').read_text());records['selected']['N4-16']['selection_note']+=' Root actual critical-custody PASS; adjacent brass rectangles at waist/bag edge leave badge-versus-fitting ambiguous, minor hardware drift qualified; no perfect one-tag claim.'
(folder/'notes/selected-records.json').write_text(json.dumps(records,indent=2)+'\n')
crops=[]
for panel,d in records['selected'].items():
 assert h(root/d['path'])==d['sha256']
 if 'crop' in d:
  c=d['crop'];src=root/c['source_path'];assert h(src)==c['source_sha256'];assert Image.open(src).crop(c['box_xyxy']).tobytes()==Image.open(root/d['path']).tobytes();crops.append(panel)
for d in json.loads((folder/'references/records.json').read_text()):
 assert h(root/d['path'])==d['sha256'] and h(root/d['source_path'])==d['source_sha256'];assert Image.open(root/d['source_path']).crop(d['box_xyxy']).tobytes()==Image.open(root/d['path']).tobytes();crops.append(d['path'])
receipt={'status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'calls_submitted':4,'calls_returned':4,'primaries':3,'structural_repairs':1,'tool_failures':0,'pending':0,'finishes':0,'calls':checks,'lossless_crops_verified':crops,'shared_selection_mutated':False}
(folder/'notes/integrity.json').write_text(json.dumps(receipt,indent=2)+'\n');(folder/'candidates.json').write_text(json.dumps({'unit':'N4-15–18','actual_calls':4,'primaries':3,'structural_repairs':1,'tool_failures':0,'finishes':0,'pending':0,'attempts':checks,'recommended_records':'notes/selected-records.json','review':'notes/REVIEW.md'},indent=2)+'\n');print('PASS4 native/original/raw/prompt/actual-reference chains;4 selected hashes;7 lossless panel/reference crops.')
