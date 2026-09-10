import base64, datetime, hashlib, json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[5]
f=Path(__file__).resolve().parents[1]
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
outcomes={
'N6-19-P':'Root+worker actual native PASS; original bindery/dusk/three cast/current kit. Boot bottoms near crop edge not complete sole proof.',
'N6-20-P':'Root+worker actual native PASS before21; authoritative supported exterior stone landing/stair/rail/dark door/brass lock and Venn-held inserted key. Bow occluded.',
'N6-21-P':'Root+worker actual native PASS before22-24; authoritative modest room layout/furnishings and visitors. FarLEFT tear occluded, nearRIGHT intact sleeve/sheath; dark bag shading qualified.',
'N6-22-24-P':'Root+worker actual whole native and full crops PASS with minor variations:22 tan buckled tail and warmer wooden stair glimpse,24 additional gray front roll and script-neutral RIGHT hand on sill. No material repair requested;20/21 remain future spatial/bag authority.'}
checks=[]
for aid,outcome in outcomes.items():
 p=f/'calls'/f'{aid}.json';d=json.loads(p.read_text());a=json.loads((f/'requests'/f'{aid}.json').read_text());n=f/'candidates'/f'{aid}.png';raw=json.loads(Path(d['raw_return_path']).read_text())
 assert h(n)==d['sha256']==h(Path(d['source_path']))
 assert base64.b64decode(raw['image_url'].split(',',1)[1])==n.read_bytes()
 assert a['prompt']==(f/'requests'/f'{aid}.txt').read_text()
 assert hashlib.sha256(a['prompt'].encode()).hexdigest()==d['prompt_sha256']
 assert len(a['referenced_image_paths'])==len(d['references'])
 for ref,actual in zip(d['references'],a['referenced_image_paths']):
  assert h(root/ref['path'])==ref['sha256'] and Path(actual)==root/ref['path']
 assert d['status']=='returned' and d['invoked'] and d['submitted_utc']
 assert all(d.get(k) is None for k in ['model_snapshot','seed','billing'])
 d['actual_inspection']=outcome;p.write_text(json.dumps(d,indent=2)+'\n')
 checks.append({'id':aid,'status':'PASS','sha256':h(n),'actual_outcome':outcome})
assert {p.stem for p in (f/'candidates').glob('*.png')}==set(outcomes)
unused=json.loads((f/'calls/N6-22-24-R1.json').read_text());uargs=json.loads((f/'requests/N6-22-24-R1.json').read_text())
assert unused['status']=='not_submitted' and unused['invoked'] is False and not (f/'candidates/N6-22-24-R1.png').exists()
assert not (f/'calls/N6-22-24-R1-tool-return.json').exists()
assert hashlib.sha256(uargs['prompt'].encode()).hexdigest()==unused['prompt_sha256']
assert uargs['prompt']==(f/'requests/N6-22-24-R1.txt').read_text()
for ref in unused['references']: assert h(root/ref['path'])==ref['sha256']
records=json.loads((f/'notes/selected-records.json').read_text())
assert set(records['selected'])=={f'N6-{i}' for i in range(19,25)}
crops=[]
for panel,d in records['selected'].items():
 assert h(root/d['path'])==d['sha256']
 if 'crop' in d:
  c=d['crop'];src=root/c['source_path'];assert h(src)==c['source_sha256'] and list(Image.open(src).size)==c['source_dimensions']
  assert Image.open(src).crop(c['box_xyxy']).tobytes()==Image.open(root/d['path']).tobytes();crops.append(panel)
for listing in ['references/records.json','notes/primary-detail-crops.json']:
 for d in json.loads((f/listing).read_text()):
  src=root/d['source_path'];dest=root/d['path'];assert h(dest)==d['sha256'] and h(src)==d['source_sha256']
  assert list(Image.open(src).size)==d['source_dimensions']
  assert Image.open(src).crop(d['box_xyxy']).tobytes()==Image.open(dest).tobytes();crops.append(d['path'])
receipt={'status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'calls_submitted':4,'calls_returned':4,'primaries':4,'structural_repairs':0,'finishes':0,'tool_failures':0,'pending':0,'unused_prepared_repair':{'id':'N6-22-24-R1','invoked':False,'reason':unused['cancellation_reason']},'calls':checks,'selected_hashes_verified':6,'lossless_crops_verified':crops,'shared_selection_mutated':False,'unknown_model_seed_billing_preserved':True,'timestamp_note':'submitted_utc is local immediately-before-tool invocation record; returned_utc is local preservation time, not provider timing telemetry.'}
(f/'notes/integrity.json').write_text(json.dumps(receipt,indent=2)+'\n')
(f/'candidates.json').write_text(json.dumps({'unit':'N6-19-24','actual_calls':4,'primaries':4,'structural_repairs':0,'finishes':0,'tool_failures':0,'pending':0,'attempts':checks,'unused_prepared_repair':'N6-22-24-R1 (never invoked)','recommended_records':'notes/selected-records.json','review':'notes/REVIEW.md'},indent=2)+'\n')
print(f'PASS: 4 native/original/raw/prompt/reference chains;6 selected hashes;{len(crops)} lossless panel/reference/inspection crops. One prepared repair explicitly unsubmitted.')
