"""Retain native tool returns and build source-bound candidate metadata."""
from pathlib import Path
import hashlib,json,re,shutil,struct
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'production/world-combat'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for path in sorted((P/'calls').glob('*.json')):
    c=json.loads(path.read_text())
    if not c.get('output_hint') and not c.get('source_path'): continue
    src=Path(c.get('source_path') or re.findall(r'/home/[^\s]+\.png',c['output_hint'])[0])
    dest=P/'candidates'/(c['attempt_id']+'.png');dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists(): assert sha(dest)==sha(src), 'Refuse to replace different native image'
    else: shutil.copyfile(src,dest)
    raw=dest.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'
    width,height=struct.unpack('>II',raw[16:24])
    assert sha(ROOT/c['prompt_path'])==c['prompt_sha256']
    for ref in c['references']: assert sha(ROOT/ref['path'])==ref['sha256']
    c['source_path']=str(src)
    path.write_text(json.dumps(c,indent=2)+'\n')
    rows.append({'id':c['id'],'attempt_id':c['attempt_id'],'path':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'width':width,'height':height,'status':'reviewable-unaccepted','source_path':str(src),'prompt_path':c['prompt_path'],'prompt_sha256':c['prompt_sha256'],'owner_approval':None})
(P/'candidates.json').write_text(json.dumps({'schema':'WorldCombatCandidates/1','experiment_id':'WC-20260908-01','candidates':rows},indent=2)+'\n')
selection_path=P/'selected.json'
selected=json.loads(selection_path.read_text()) if selection_path.exists() else {'schema':'WorldCombatSelection/1','experiment_id':'WC-20260908-01','selected':{},'owner_approval':None}
for c in rows:
    if c['attempt_id'].endswith('-P'): selected['selected'].setdefault(c['id'],c['attempt_id'])
selection_path.write_text(json.dumps(selected,indent=2)+'\n')
print(json.dumps({'registered':len(rows),'displayed':len(selected['selected'])}))
