from pathlib import Path
import hashlib,json,re,shutil,struct
R=Path(__file__).resolve().parents[2];P=R/'production/encounter-lab';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for path in sorted((P/'calls').glob('*.json')):
 c=json.loads(path.read_text())
 if not c.get('output_hint') and not c.get('source_path'):continue
 src=Path(c.get('source_path') or re.findall(r'/home/[^\s]+\.png',c['output_hint'])[0]);dest=P/'candidates'/(c['attempt_id']+'.png')
 if dest.exists():assert sha(dest)==sha(src)
 else:shutil.copyfile(src,dest)
 raw=dest.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';width,height=struct.unpack('>II',raw[16:24])
 assert sha(R/c['prompt_path'])==c['prompt_sha256']
 for ref in c['references']:assert sha(R/ref['path'])==ref['sha256']
 rows.append(dict(id=c['id'],attempt_id=c['attempt_id'],path=str(dest.relative_to(R)),sha256=sha(dest),width=width,height=height,status='reviewable-unaccepted',source_path=str(src),prompt_path=c['prompt_path'],prompt_sha256=c['prompt_sha256'],call_path=str(path.relative_to(R)),call_sha256=sha(path),owner_approval=None))
(P/'candidates.json').write_text(json.dumps(dict(schema='EncounterLabCandidates/1',experiment_id='EN-20260909-01',candidates=rows),indent=2)+'\n')
sel=P/'selected.json';s=json.loads(sel.read_text()) if sel.exists() else dict(schema='EncounterLabDisplaySelection/1',experiment_id='EN-20260909-01',selected={},owner_approval=None)
for c in rows:
 if c['attempt_id'].endswith('-P'):s['selected'].setdefault(c['id'],c['attempt_id'])
sel.write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({'attempts':len(rows),'selected':len(s['selected'])}))
