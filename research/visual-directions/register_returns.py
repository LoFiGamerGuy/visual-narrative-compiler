"""Copy builtin-tool originals without removing them; append immutable candidate records."""
from pathlib import Path
import json,hashlib,shutil,struct
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'production/visual-directions'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((P/'candidates.json').read_text());selection=json.loads((P/'selected.json').read_text());known={c['attempt_id']:c for c in manifest['candidates']};added=[]
for receipt in sorted((P/'calls').glob('*-returned.json')):
 row=json.loads(receipt.read_text());aid=row['attempt_id'];cid=row['direction_id']
 if aid in known:continue
 source=Path(row['source_path']).resolve()
 if not source.is_relative_to(Path('/home/gosnerp/.codex/generated_images')):raise ValueError('Unexpected tool original path')
 suffix='retry' if aid.endswith('-R') else 'primary';dest=P/'candidates'/f'{cid}-{suffix}.png'
 if dest.exists():raise ValueError('Candidate filename already exists; do not overwrite')
 with source.open('rb') as src, dest.open('xb') as out:shutil.copyfileobj(src,out)
 assert digest(source)==digest(dest)
 with dest.open('rb') as stream:header=stream.read(24)
 if header[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Expected PNG')
 width,height=struct.unpack('>II',header[16:24])
 candidate={'id':cid,'attempt_id':aid,'path':dest.relative_to(ROOT).as_posix(),'sha256':digest(dest),'width':width,'height':height,'bytes':dest.stat().st_size,'status':'reviewable-unaccepted','tool_original_retained':True,'provider':None,'model':None,'seed':None,'usage':None,'billing_allocation':None,'direct_paid_usd':0}
 manifest['candidates'].append(candidate);selection['selected'][cid]=aid;added.append(cid)
 (P/'calls'/f'{cid}-{suffix}-registered.json').write_text(json.dumps(candidate,indent=2)+'\n')
(P/'candidates.json').write_text(json.dumps(manifest,indent=2)+'\n');(P/'selected.json').write_text(json.dumps(selection,indent=2)+'\n')
print(json.dumps({'added':added,'total':len(manifest['candidates'])}))
