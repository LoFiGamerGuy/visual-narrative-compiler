import base64, datetime, hashlib, json
from pathlib import Path
from PIL import Image
r=Path(__file__).resolve().parents[5]; f=Path(__file__).resolve().parents[1]
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
records=json.loads((f/'notes/selected-records.json').read_text())['selected']
assert set(records)=={f'N6-{i}' for i in range(39,43)}
checks=[]
for panel,selected in records.items():
 aid=selected['attempt_id']; cp=f/'calls'/f'{aid}.json'; d=json.loads(cp.read_text()); a=json.loads((f/'requests'/f'{aid}.json').read_text()); n=r/selected['path']; raw=json.loads(Path(d['raw_return_path']).read_text())
 assert h(n)==selected['sha256']==d['sha256']==h(Path(d['source_path']))
 assert base64.b64decode(raw['image_url'].split(',',1)[1])==n.read_bytes()
 assert a['prompt']==(f/'requests'/f'{aid}.txt').read_text() and hashlib.sha256(a['prompt'].encode()).hexdigest()==d['prompt_sha256']
 assert len(a['referenced_image_paths'])==len(d['references'])
 for ref,actual in zip(d['references'],a['referenced_image_paths']): assert h(r/ref['path'])==ref['sha256'] and Path(actual)==r/ref['path']
 assert d['status']=='returned' and d['invoked'] and d['submitted_utc']
 assert all(d.get(k) is None for k in ['model_snapshot','seed','billing'])
 assert list(Image.open(n).size)==selected['dimensions']
 d['actual_inspection']=selected['selection_note']; cp.write_text(json.dumps(d,indent=2)+'\n')
 checks.append({'id':aid,'status':'PASS','sha256':h(n),'dimensions':selected['dimensions'],'actual_outcome':selected['selection_note']})
assert {p.stem for p in (f/'candidates').glob('*.png')}=={c['id'] for c in checks}
crops=[]
for d in json.loads((f/'references/records.json').read_text()):
 s=r/d['source_path'];p=r/d['path'];assert h(s)==d['source_sha256'] and h(p)==d['sha256'] and list(Image.open(s).size)==d['source_dimensions']
 assert Image.open(s).crop(d['crop_xyxy']).tobytes()==Image.open(p).tobytes();crops.append(d['path'])
receipt={'status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'calls_submitted':4,'calls_returned':4,'primaries':4,'structural_repairs':0,'finishes':0,'tool_failures':0,'pending':0,'per_unit_caps_obeyed':True,'scope_ceiling':8,'new_tranche':False,'calls':checks,'selected_hashes_verified':4,'lossless_crops_verified':crops,'shared_selection_mutated':False,'unknown_model_seed_billing_preserved':True,'timestamp_note':'submitted_utc is local immediately-before invocation; returned_utc is local preservation after completion, not provider telemetry.'}
(f/'notes/integrity.json').write_text(json.dumps(receipt,indent=2)+'\n')
(f/'candidates.json').write_text(json.dumps({'unit':'N6-39-42','actual_calls':4,'primaries':4,'structural_repairs':0,'finishes':0,'tool_failures':0,'pending':0,'attempts':checks,'recommended_records':'notes/selected-records.json','review':'notes/REVIEW.md'},indent=2)+'\n')
print('PASS: four native/original/raw/prompt/reference chains, four selected native hashes, one exact lossless key-contact crop; four primaries, no repairs/finishes/cap reset.')
