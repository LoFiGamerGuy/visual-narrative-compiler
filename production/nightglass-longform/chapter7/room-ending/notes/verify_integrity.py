import base64,datetime,hashlib,json
from pathlib import Path
from PIL import Image
r=Path(__file__).resolve().parents[5];f=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
g=json.loads((r/'research/nightglass-longform/CHAPTER7-PRODUCTION-GATE.json').read_text());assert g['scope_ceilings']['room-ending']==6 and not g['retry_caps_reset'] and not g['new_tranche']
records=json.loads((f/'notes/selected-records.json').read_text())['selected'];assert set(records)=={'N7-38','N7-39','N7-40'}
checks=[]
for aid in ['N7-38-P','N7-39-40-P']:
 p=f/'calls'/f'{aid}.json';d=json.loads(p.read_text());a=json.loads((f/'requests'/f'{aid}.json').read_text());n=f/'candidates'/f'{aid}.png';raw=json.loads(Path(d['raw_return_path']).read_text())
 assert h(n)==d['sha256']==h(Path(d['source_path'])) and set(raw)=={'image_url','output_hint'}
 assert base64.b64decode(raw['image_url'].split(',',1)[1])==n.read_bytes()
 assert a==d['args'] and a['prompt']==(f/'requests'/f'{aid}.txt').read_text() and hashlib.sha256(a['prompt'].encode()).hexdigest()==d['prompt_sha256']
 for ref,actual in zip(d['references'],a['referenced_image_paths']):assert h(r/ref['path'])==ref['sha256'] and Path(actual)==r/ref['path']
 assert d['status']=='returned' and d['invoked'] and d['submitted_utc'] and d['phase']=='primary'
 assert all(d.get(k) is None for k in ['model_snapshot','seed','billing','owner_approval'])
 assert d['before_art_dependency']['script_sha256']==g['script_sha256']
 outcomes=[x['selection_note'] for x in records.values() if x['attempt_id']==aid];d['actual_inspection']=outcomes;p.write_text(json.dumps(d,indent=2)+'\n');checks.append({'id':aid,'status':'PASS','sha256':h(n),'dimensions':list(Image.open(n).size),'actual_inspection':outcomes})
assert {p.stem for p in (f/'candidates').glob('*.png')}=={x['id'] for x in checks}
crops=[]
for panel,d in records.items():
 p=r/d['path'];assert h(p)==d['sha256']
 if 'crop' in d:
  c=d['crop'];s=r/c['source_path'];assert h(s)==c['source_sha256'] and list(Image.open(s).size)==c['source_dimensions'];assert Image.open(s).crop(c['box_xyxy']).tobytes()==Image.open(p).tobytes();crops.append(panel)
 else:assert list(Image.open(p).size)==d['dimensions']
for c in json.loads((f/'references/records.json').read_text()):
 s=r/c['source_path'];p=r/c['path'];assert h(s)==c['source_sha256'] and h(p)==c['sha256'];assert Image.open(s).crop(c['box_xyxy']).tobytes()==Image.open(p).tobytes();crops.append(c['path'])
receipt={'status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_calls':2,'primaries':2,'repairs':0,'finishes':0,'support_calls':0,'failures':0,'pending':0,'scope_total_ceiling':6,'new_tranche':False,'caps_reset':False,'calls':checks,'selected_hashes_verified':3,'lossless_crops_verified':crops,'unknown_metadata_preserved':True,'shared_selection_mutated':False,'timing_note':'submitted_utc is local immediately before tool invocation; returned_utc is local preservation time, not provider telemetry.'}
(f/'notes/integrity.json').write_text(json.dumps(receipt,indent=2)+'\n');(f/'candidates.json').write_text(json.dumps({'scope':'N7-38-40','actual_calls':2,'primaries':2,'repairs':0,'finishes':0,'pending':0,'attempts':checks,'recommended_records':'notes/selected-records.json'},indent=2)+'\n');print('PASS:2 native/default-original/raw/args/ref chains;3 selected hashes;3 lossless panel/reference crops;2 primaries, no other calls.')
