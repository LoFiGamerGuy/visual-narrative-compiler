"""Isolated local provenance fixtures only: no image tools or real calls."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'lead-setup/record_return.py'
OUT=HERE/'helper-fixture-v1';OUT.mkdir(exist_ok=False)
# A fixed 1x1 PNG test byte string, not production artwork.
png=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a10sAAAAASUVORK5CYII=')
meta={'output_hint':'isolated fixture only','image_url_length':len('data:image/png;base64,'+base64.b64encode(png).decode())}
results=[]
def make(name,record=None):
 r=OUT/name
 for sub in ['notes','candidates','calls']:(r/sub).mkdir(parents=True,exist_ok=True)
 (r/'notes/record_return.py').write_bytes(SOURCE.read_bytes());(r/'native.png').write_bytes(png)
 (r/'calls/N8-02-P.json').write_text(json.dumps(record or {'id':'N8-02-P','status':'submitted','phase':'primary','fixture_only':True})+'\n')
 return r
def run(r,m=meta):
 return subprocess.run([sys.executable,str(r/'notes/record_return.py'),'N8-02-P',str(r/'native.png'),json.dumps(m)],capture_output=True,text=True)
def files(r):return {str(p.relative_to(r)):p.read_bytes() for p in r.rglob('*') if p.is_file()}
def fail_unchanged(name,record=None,m=meta,orphan=False,candidate=False):
 r=make(name,record)
 if orphan:(r/'calls/N8-02-P-tool-return.json').write_bytes(b'preserved orphan raw bytes\n')
 if candidate:(r/'candidates/N8-02-P.png').write_bytes(b'preserved native bytes\n')
 before=files(r);p=run(r,m);assert p.returncode!=0 and files(r)==before
 results.append({'case':name,'pass':True,'exit_code':p.returncode,'all_fixture_files_unchanged':True,'candidate_exists':(r/'candidates/N8-02-P.png').exists(),'raw_exists':(r/'calls/N8-02-P-tool-return.json').exists()})
fail_unchanged('orphan-raw',orphan=True)
fail_unchanged('bad-metadata-length',m={**meta,'image_url_length':1})
fail_unchanged('bad-output-hint-type',m={**meta,'output_hint':7})
fail_unchanged('wrong-call-id',record={'id':'N8-03-P','status':'submitted'})
fail_unchanged('wrong-call-status',record={'id':'N8-02-P','status':'returned'})
fail_unchanged('candidate-only',candidate=True)
r=make('ordinary-return');p=run(r);assert p.returncode==0;candidate=r/'candidates/N8-02-P.png';raw=json.loads((r/'calls/N8-02-P-tool-return.json').read_text());call=json.loads((r/'calls/N8-02-P.json').read_text());assert candidate.read_bytes()==png and (r/'native.png').read_bytes()==png;assert base64.b64decode(raw['image_url'].split(',',1)[1])==png and raw['output_hint']==meta['output_hint'];assert call['status']=='returned' and call['sha256']==hashlib.sha256(png).hexdigest() and call['id']=='N8-02-P' and call['fixture_only']
results.append({'case':'ordinary-return','pass':True,'exit_code':0,'candidate_source_raw_bytes_exact':True,'call_status':'returned','native_sha256':call['sha256']})
before=files(r);p=run(r);assert p.returncode!=0 and files(r)==before;results.append({'case':'repeat-return','pass':True,'exit_code':p.returncode,'all_fixture_files_unchanged':True})
receipt={'fixture_only':True,'real_art_or_call_records_touched':False,'helper_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'results':results}
(HERE/'CHAPTER8-HELPER-FIXTURE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
