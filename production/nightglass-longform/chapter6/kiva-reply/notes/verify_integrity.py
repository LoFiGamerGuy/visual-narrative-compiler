import base64,datetime,hashlib,json
from pathlib import Path
from PIL import Image
r=Path(__file__).resolve().parents[5];f=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
outcomes={
'N6-30-P':'Actual whole+envelope detail root/worker PASS; first BLUE-GRAY/COPPER shared-edge OssaRIGHT-to-ArenLEFT, RIGHTrim/empty counterbag/bare shoulders. One closed wallet now vertical at LEFT waist; incidental fitting loops qualified.',
'N6-31-P':'Actual whole root/worker PASS: ordinary blue-awning approach, closed wornbag/emptyhands/current kit. Walking feet overlap, not two-flat-sole proof.',
'N6-32-P':'Actual whole root/worker PASS before opened33: same envelope ArenLEFT-to-KivaRIGHT, offbackbag/RIGHTrim/bare shoulders; older records remain bench.',
'N6-33-34-P':'Upper33 actual full/native/crop PASS and retained ORIGINAL. Lower34 rejected only for duplicate horizontal cream wallet beside retained vertical wallet. Actual Kiva sheet heldRIGHT in34 is hand-neutral.',
'N6-33-34-R1':'Actual whole/full34 crop PASS: removes only extra horizontal wallet; one vertical cream wallet remains, all paper custody/acting/kit intact. Upper33 intentionally remains originalP.',
'N6-35-P':'Actual whole native PASS recommendation: ordinary empty-handed departure/current one verticalwallet and bag; Kiva resumes supported hinge/pin work, new buyer papers staybench. Creamcurtain detail/old smallslips partially occluded; walking feet overlap.'}
checks=[]
for aid,outcome in outcomes.items():
 p=f/'calls'/f'{aid}.json';d=json.loads(p.read_text());a=json.loads((f/'requests'/f'{aid}.json').read_text());n=f/'candidates'/f'{aid}.png';raw=json.loads(Path(d['raw_return_path']).read_text())
 assert h(n)==d['sha256']==h(Path(d['source_path']))
 assert base64.b64decode(raw['image_url'].split(',',1)[1])==n.read_bytes()
 assert a['prompt']==(f/'requests'/f'{aid}.txt').read_text() and hashlib.sha256(a['prompt'].encode()).hexdigest()==d['prompt_sha256']
 assert len(a['referenced_image_paths'])==len(d['references'])
 for ref,actual in zip(d['references'],a['referenced_image_paths']):assert h(r/ref['path'])==ref['sha256'] and Path(actual)==r/ref['path']
 assert d['status']=='returned' and d['invoked'] and d['submitted_utc']
 assert all(d.get(k) is None for k in ['model_snapshot','seed','billing'])
 d['actual_inspection']=outcome;p.write_text(json.dumps(d,indent=2)+'\n');checks.append({'id':aid,'status':'PASS','sha256':h(n),'actual_outcome':outcome})
assert {p.stem for p in (f/'candidates').glob('*.png')}==set(outcomes)
repair=json.loads((f/'calls/N6-33-34-R1.json').read_text());assert len(repair['references'])==1 and repair['references'][0]['sha256']==h(f/'candidates/N6-33-34-P.png')
records=json.loads((f/'notes/selected-records.json').read_text());assert set(records['selected'])=={f'N6-{i}' for i in range(30,36)}
crops=[]
for panel,d in records['selected'].items():
 assert h(r/d['path'])==d['sha256']
 if 'crop' in d:
  c=d['crop'];s=r/c['source_path'];assert h(s)==c['source_sha256'] and list(Image.open(s).size)==c['source_dimensions']
  assert Image.open(s).crop(c['box_xyxy']).tobytes()==Image.open(r/d['path']).tobytes();crops.append(panel)
assert records['selected']['N6-33']['attempt_id']=='N6-33-34-P' and records['selected']['N6-34']['attempt_id']=='N6-33-34-R1'
for d in json.loads((f/'references/records.json').read_text()):
 s=r/d['source_path'];p=r/d['path'];assert h(s)==d['source_sha256'] and h(p)==d['sha256'] and list(Image.open(s).size)==d['source_dimensions']
 assert Image.open(s).crop(d['box_xyxy']).tobytes()==Image.open(p).tobytes();crops.append(d['path'])
receipt={'status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'calls_submitted':6,'calls_returned':6,'primaries':5,'structural_repairs':1,'finishes':0,'tool_failures':0,'pending':0,'per_unit_caps_obeyed':True,'scope_ceiling':10,'new_tranche':False,'calls':checks,'selected_hashes_verified':6,'lossless_crops_verified':crops,'shared_selection_mutated':False,'unknown_model_seed_billing_preserved':True,'timestamp_note':'submitted_utc is the local immediately-before-tool invocation record; returned_utc is local preservation time after completion, not provider telemetry.'}
(f/'notes/integrity.json').write_text(json.dumps(receipt,indent=2)+'\n');(f/'candidates.json').write_text(json.dumps({'unit':'N6-30-35','actual_calls':6,'primaries':5,'structural_repairs':1,'finishes':0,'tool_failures':0,'pending':0,'attempts':checks,'recommended_records':'notes/selected-records.json','review':'notes/REVIEW.md'},indent=2)+'\n')
print(f'PASS:6 native/original/raw/prompt/reference chains;6 selected hashes;{len(crops)} exact lossless panel/reference crops. Five primaries and sole34 wallet repair, no cap reset.')
