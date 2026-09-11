"""Copy returned native PNG bytes, remove redundant inline base64, register source-bound attempts."""
from pathlib import Path
import json,hashlib,re,shutil,struct
R=Path(__file__).resolve().parents[2];P=R/'production/visual-refinement'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
groups={'setup':[],'comparison':[],'sequence':[]}
for path in sorted((P/'calls').glob('*.json')):
 c=json.loads(path.read_text())
 if 'output_hint' not in c and 'result' not in c:continue
 hint=c.get('output_hint',c.get('result',{}).get('output_hint',''))
 src=Path(c.get('source_path') or re.findall(r'/home/[^\s]+\.png',hint)[0])
 c.pop('result',None);c['output_hint']=hint;c['source_path']=str(src)
 phase=c['phase'];aid=c.get('attempt_id',c['id']+'-P');c['attempt_id']=aid
 dest=P/('setup' if phase=='setup' else 'sequence-candidates' if phase=='sequence' else 'candidates')/(aid+'.png')
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert sha(dest)==sha(src),f'Never overwrite different asset {dest}'
 else:shutil.copyfile(src,dest)
 w,h=struct.unpack('>II',dest.read_bytes()[16:24])
 pp=R/c['prompt_path'];c['prompt_sha256']=sha(pp)
 c['references']=[{'path':str(Path(x).relative_to(R)),'sha256':sha(Path(x))} for x in c['referenced_image_paths']]
 for k in ['model','snapshot','seed','usage','billing']:c.setdefault(k,None)
 path.write_text(json.dumps(c,indent=2)+'\n')
 groups[phase].append({'id':c['id'],'attempt_id':aid,'path':dest.relative_to(R).as_posix(),'sha256':sha(dest),'width':w,'height':h,'status':'reviewable-unaccepted','source_path':str(src),'prompt_path':c['prompt_path'],'prompt_sha256':c['prompt_sha256'],'owner_approval':None})
for phase,rows in groups.items():
 if not rows:continue
 filename='setup-candidates.json' if phase=='setup' else 'sequence-candidates.json' if phase=='sequence' else 'candidates.json'
 (P/filename).write_text(json.dumps({'schema':'RefinementCandidates/1','experiment_id':'VR-20260907-01','candidates':rows},indent=2)+'\n')
 print(phase,len(rows))

