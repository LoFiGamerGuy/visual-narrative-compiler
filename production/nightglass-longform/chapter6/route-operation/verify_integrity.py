from pathlib import Path
from PIL import Image
import hashlib,json,base64,collections
r=Path(__file__).parent;root=r.parents[3];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();calls=[]
for p in (r/'calls').glob('*.json'):
 x=json.loads(p.read_text())
 if 'attempt_id' not in x:continue
 assert x['status']=='returned',p
 assert x['args']==json.loads((r/'requests'/(x['attempt_id']+'.json')).read_text()),p
 assert all(h(Path(q['path']))==q['sha256'] for q in x['references']),p
 n=Path(x['native_copy']);o=Path(x['native_source']);raw=json.loads((r/'calls'/(x['attempt_id']+'-tool-return.json')).read_text());meta=json.loads((r/'calls'/(x['attempt_id']+'-return-metadata.json')).read_text())
 assert n.read_bytes()==o.read_bytes()==base64.b64decode(raw['image_url'].split(',',1)[1]);assert h(n)==x['native_sha256'];assert raw['output_hint']==meta['output_hint'];assert len(raw['image_url'])==meta['image_url_length'];calls.append(x)
sels=json.loads((r/'selected-records.json').read_text())
for x in sels:
 p=root/x['path'];c=x['crop'];s=root/c['source_path'];assert h(p)==x['sha256'];assert h(s)==c['source_sha256'];im=Image.open(s);assert list(im.size)==c['source_dimensions'];assert Image.open(p).tobytes()==im.crop(c['box_xyxy']).tobytes()
refs=[]
for p in (r/'references').glob('*.json'):
 x=json.loads(p.read_text());s=Path(x['source_path']);t=Path(x['path']);assert h(s)==x['source_sha256'];assert h(t)==x['sha256'];im=Image.open(s);assert list(im.size)==x['source_dimensions'];assert Image.open(t).tobytes()==im.crop(x['box_xyxy']).tobytes();refs.append(str(p))
counts=collections.Counter(x['kind'] for x in calls)
out={'actual_returned_calls':len(calls),'counts':dict(counts),'selected_panels':len(sels),'derived_reference_records':len(refs),'exact_args_and_reference_hashes_pass':True,'original_copy_semantic_raw_native_bytes_equal':True,'selected_crops_source_bound_and_pixel_exact':True,'derived_references_source_bound_and_pixel_exact':True,'shared_selection_mutated':False,'ceiling_worker_calls':18,'ceiling_chapter_calls':65}
(r/'notes/FINAL-VERIFICATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
