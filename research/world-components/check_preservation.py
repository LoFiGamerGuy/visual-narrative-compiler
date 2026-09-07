"""Verify the frozen prior-state scope; output only inside this isolated task."""
from pathlib import Path
import os,subprocess,json,hashlib,datetime,argparse,concurrent.futures
HERE=Path(__file__).resolve().parent;ROOT=Path('/mnt/c/AgentWorkspaces/anime-pipeline')
B=json.loads((HERE/'protected-initial.json').read_text());env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
def git(t,*args):
 gd=ROOT/'.git' if t==ROOT else ROOT/'.git/worktrees'/t.name
 return subprocess.check_output(['git','--git-dir='+str(gd),'--work-tree='+str(t),*args],env=env,text=True).strip()
def check(old):
 t=ROOT.parent/old['name'];return {'name':old['name'],'head_matches':git(t,'rev-parse','HEAD')==old['head'],'status_matches':git(t,'status','--porcelain=v1','--untracked-files=all','--ignored=matching')==old['status']}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,B['prior_worktrees']))
source=Path(B['source']);current={}
for ns in ['production/visual-refinement','docs/research/visual-refinement','research/visual-refinement']:
 for directory,dirs,files in os.walk(source/ns):
  dirs[:]=[d for d in dirs if d not in {'.scratch','runtime','__pycache__','local'}]
  for name in files:
   p=Path(directory)/name;s=p.stat();current[p.relative_to(source).as_posix()]={'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'mode':s.st_mode,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
changes=[k for k in set(current)|set(B['prior_visual_files']) if current.get(k)!=B['prior_visual_files'].get(k)]
refs=dict(x.split(' ',1) for x in git(ROOT,'for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes').splitlines());before=dict(x.split(' ',1) for x in B['prior_refs'].splitlines());refchanges=[k for k,v in before.items() if refs.get(k)!=v]
report={'schema':'WorldComponentsPreservationComparison/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':B['method'],'worktrees':rows,'prior_visual_files_checked':len(current),'changed_paths':changes,'changed_prior_refs':refchanges,'pass':not changes and not refchanges and all(x['head_matches'] and x['status_matches'] for x in rows)}
a=argparse.ArgumentParser();a.add_argument('--output',default=str(HERE/'protected-final.json'));args=a.parse_args();out=Path(args.output).resolve();assert out.is_relative_to(HERE)
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['method','worktrees']}));raise SystemExit(0 if report['pass'] else 1)
