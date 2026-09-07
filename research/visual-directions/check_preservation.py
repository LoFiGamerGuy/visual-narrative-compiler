"""Compare the declared prior-state scope without writing in any protected tree."""
from pathlib import Path
import os,subprocess,json,hashlib,datetime,argparse
HERE=Path(__file__).resolve().parent;ROOT=Path('/mnt/c/AgentWorkspaces/anime-pipeline');B=json.loads((HERE/'protected-initial.json').read_text());env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
def git(tree,*args):
 gd=ROOT/'.git' if tree==ROOT else ROOT/'.git/worktrees'/tree.name
 return subprocess.check_output(['git','--git-dir='+str(gd),'--work-tree='+str(tree),*args],env=env,text=True).strip()
rows=[]
for old in B['prior_worktrees']:
 tree=ROOT.parent/old['name'];rows.append({'name':old['name'],'head_matches':git(tree,'rev-parse','HEAD')==old['head'],'status_matches':git(tree,'status','--porcelain=v1','--untracked-files=all','--ignored=matching')==old['status']})
prior=ROOT.parent/'anime-pipeline-structural-20260907-054652';current={}
for ns in ['production/structural-pilot','docs/research/structural-pilot','research/structural-pilot']:
 for directory,dirs,files in os.walk(prior/ns):
  dirs[:]=[d for d in dirs if d not in {'.scratch','runtime','__pycache__','local'}]
  for name in files:
   p=Path(directory)/name;st=p.stat();key=hashlib.sha256(p.relative_to(prior).as_posix().encode()).hexdigest();current[key]={'size':st.st_size,'mtime_ns':st.st_mtime_ns,'ctime_ns':st.st_ctime_ns,'mode':st.st_mode,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
changes=[k for k in set(current)|set(B['prior_structural_files']) if current.get(k)!=B['prior_structural_files'].get(k)];refs=dict(x.split(' ',1) for x in git(ROOT,'for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes').splitlines());before=dict(x.split(' ',1) for x in B['prior_refs'].splitlines());refchanges=[k for k,v in before.items() if refs.get(k)!=v]
r={'schema':'DirectionStudyPreservationComparison/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':B['method'],'worktrees':rows,'prior_structural_files_checked':len(current),'changed_opaque_paths':changes,'changed_prior_refs':refchanges,'pass':not changes and not refchanges and all(x['head_matches'] and x['status_matches'] for x in rows)}
p=argparse.ArgumentParser();p.add_argument('--output',default=str(HERE/'protected-final.json'));args=p.parse_args();out=Path(args.output).resolve();assert out.is_relative_to(HERE);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['method','worktrees']}));raise SystemExit(0 if r['pass'] else 1)
