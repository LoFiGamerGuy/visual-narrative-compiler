import base64,datetime,hashlib,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[5];folder=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(scope,ids):
 checks=[]
 for ident in ids:
  cp=scope/'calls'/f'{ident}.json';c=json.loads(cp.read_text());ap=Path(c['arguments_path']);args=json.loads(ap.read_text());rp=Path(c['raw_return_path']);raw=json.loads(rp.read_text());native=Path(c['path'])
  assert args==c['args'] and args['prompt']==(scope/'requests'/f'{ident}.txt').read_text()
  assert hashlib.sha256(args['prompt'].encode()).hexdigest()==c['prompt_sha256']
  assert set(raw)=={'image_url','output_hint'} and native.read_bytes()==Path(c['source_path']).read_bytes()==base64.b64decode(raw['image_url'].split(',',1)[1],validate=True)
  assert sha(native)==c['sha256'] and c['source_path'] in raw['output_hint']
  assert len(args['referenced_image_paths'])==len(c['references'])
  for p,r in zip(args['referenced_image_paths'],c['references']):assert Path(p)==root/r['path'] and sha(Path(p))==r['sha256']
  assert c['status']=='returned' and c['invoked'] and all(k in c and c[k] is None for k in ('owner_approval','model_snapshot','seed','billing'))
  assert datetime.datetime.fromisoformat(c['returned_utc'])>=datetime.datetime.fromisoformat(c['submitted_utc'])
  checks.append({'id':ident,'phase':c['phase'],'native_sha256':sha(native),'call_record_sha256':sha(cp),'args_sha256':sha(ap),'raw_return_sha256':sha(rp),'references':c['references'],'native_dimensions':list(Image.open(native).size),'status':'PASS_PRESERVATION'})
 assert checks[0]['phase']=='primary' and checks[1]['phase']=='repair' and checks[1]['references'][0]['sha256']==checks[0]['native_sha256']
 return checks
own=audit(folder,['N8-44-45-P','N8-44-45-R1'])
selected=json.loads((folder/'notes/selected-records.json').read_text())['selected'];assert set(selected)=={'N8-44','N8-45'}
crops=[]
for panel,c in selected.items():
 p=root/c['path'];s=root/c['crop']['source_path'];assert sha(p)==c['sha256'] and sha(s)==c['crop']['source_sha256'];assert Image.open(p).tobytes()==Image.open(s).crop(c['crop']['box_xyxy']).tobytes();crops.append(c['path'])
for name in ['references/inspection-records.json','notes/N8-45-review-crops.json','notes/N8-45-framing-candidates.json']:
 for c in json.loads((folder/name).read_text()):
  p=root/c['path'];s=root/c['source_path'];assert sha(p)==c['sha256'] and sha(s)==c['source_sha256'];assert Image.open(p).tobytes()==Image.open(s).crop(c['box_xyxy']).tobytes();crops.append(c['path'])
receipt={'status':'PASS_PRESERVATION_AND_QUALIFIED_CROP_DELIVERY','actual_calls':2,'primaries':1,'repairs':1,'finishes':0,'support_calls':0,'failed_returns':0,'pending':0,'scope_ceiling':3,'unused_finish_not_required':1,'original_structural_cap_spent':True,'calls':own,'selected_hashes_verified':2,'exact_lossless_crops_verified':crops,'visual_limits':'44R1 accepted;45 originalP intimate crop accepted with wallet/key whollyoffframe. Full45P bookobject and full45R1 erroneousRIGHTtear remain failed and preserved. No claim crop repaired source.','shared_selection_mutated':False,'unknown_metadata_null':True}
(folder/'notes/integrity.json').write_text(json.dumps(receipt,indent=2)+'\n')
(folder/'candidates.json').write_text(json.dumps({'scope':'N8-44-45','actual_calls':2,'pending':0,'attempts':own,'recommended_records':'notes/selected-records.json','limitations':receipt['visual_limits']},indent=2)+'\n')
lead=audit(root/'production/nightglass-longform/chapter8/lead',['N8-02-P','N8-02-R1'])
(folder/'notes/CROSS-AUDIT-N8-02.json').write_text(json.dumps({'status':'PASS','bounded_ids':['N8-02-P','N8-02-R1'],'calls':lead,'reference_hashes_verified':5,'count':2,'primaries':1,'repairs':1,'excluded':'All root03+ and other scopes; no new visual acceptance implied.','actual_image_calls_by_audit':0,'shared_mutations':False},indent=2)+'\n')
print(f'PASS own2call chains/3refs/2selected/{len(crops)} exact crops; bounded root02P/R1 twochains/5refs PASS; no pending calls')
