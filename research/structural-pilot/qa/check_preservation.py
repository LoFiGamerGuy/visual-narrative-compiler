"""Read-only preservation comparison against the pre-implementation fixed tree list."""
from pathlib import Path
import os,stat,json,gzip,hashlib,subprocess,datetime
HERE=Path(__file__).resolve().parent.parent
ROOT=Path('/mnt/c/AgentWorkspaces/anime-pipeline')
baseline=json.loads(gzip.decompress((HERE/'evidence/protected-initial.json.gz').read_bytes()))
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
def git(tree,*args):
 gd=ROOT/'.git' if tree==ROOT else ROOT/'.git/worktrees'/tree.name
 return subprocess.check_output(['git','--git-dir='+str(gd),'--work-tree='+str(tree),*args],env=env,text=True).strip()
results=[]
for old in baseline['worktrees']:
 tree=ROOT.parent/old['name'];entries={};known=old['files']
 for directory,dirs,files in os.walk(tree,followlinks=False):
  dirs[:]=[d for d in dirs if d!='.git' and not (d=='.scratch' and ('total-review' in tree.name or 'sequence-pilot' in tree.name))]
  for name in files:
   p=Path(directory)/name;rel=p.relative_to(tree).as_posix()
   key=hashlib.sha256(rel.encode()).hexdigest();st=p.lstat()
   row=[st.st_size,st.st_mtime_ns,st.st_ctime_ns,st.st_mode]
   if key in known and len(known[key])>4:
    data=os.readlink(p).encode() if stat.S_ISLNK(st.st_mode) else p.read_bytes()
    row.append(hashlib.sha256(data).hexdigest())
   entries[key]=row
 changes=[{'opaque_path':k,'before':known.get(k),'after':entries.get(k)} for k in sorted(set(known)|set(entries)) if known.get(k)!=entries.get(k)]
 head=git(tree,'rev-parse','HEAD')
 status=git(tree,'status','--porcelain=v1','--untracked-files=all','--ignored=matching')
 row={'name':old['name'],'head':head,'head_unchanged':head==old['head'],'status_unchanged':status.strip()==old['status'].strip(),'files_before':len(known),'files_after':len(entries),'changes':changes,'content_hashes_checked':sum(len(v)>4 for v in entries.values())}
 row['pass']=row['head_unchanged'] and row['status_unchanged'] and not changes
 results.append(row);print(json.dumps({k:v for k,v in row.items() if k!='changes'}),flush=True)
refs=git(ROOT,'for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes')
before=dict(x.split(' ',1) for x in baseline['refs'].strip().splitlines())
after=dict(x.split(' ',1) for x in refs.strip().splitlines())
ref_changes=[{'ref':k,'before':v,'after':after.get(k)} for k,v in before.items() if after.get(k)!=v]
result={'schema':'ProtectedComparison/1','started_from_snapshot_utc':baseline['captured_utc'],'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':baseline['method'],'worktrees':results,'protected_ref_changes':ref_changes,'new_task_refs':[k for k in after if k not in before],'pass':all(x['pass'] for x in results) and not ref_changes}
(HERE/'evidence/protected-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'pass':result['pass'],'protected_trees':len(results),'ref_changes':len(ref_changes)}),flush=True)
