from pathlib import Path
import json,hashlib,subprocess,os,datetime,concurrent.futures,argparse
HERE=Path(__file__).resolve().parent;ROOT=Path('/mnt/c/AgentWorkspaces/anime-pipeline');B=json.loads((HERE/'protected-initial.json').read_text());env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
def sha(b):return hashlib.sha256(b).hexdigest()
def git(p,*args):
 gd=ROOT/'.git' if p==ROOT else ROOT/'.git/worktrees'/p.name
 return subprocess.check_output(['git','--git-dir='+str(gd),'--work-tree='+str(p),*args],env=env)
def tree(x):
 p=Path(x['path']);return {'path':str(p),'head_matches':git(p,'rev-parse','HEAD').decode().strip()==x['head'],'status_matches':sha(git(p,'status','--porcelain=v1','--untracked-files=all','--ignored=matching'))==x['status_sha256']}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:trees=list(pool.map(tree,B['worktrees']))
changed=[]
for name,old in B['files'].items():
 p=Path(name)
 if not p.is_file():changed.append(name);continue
 s=p.stat();now={'sha256':sha(p.read_bytes()),'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}
 if now!=old:changed.append(name)
refs=dict(x.split(' ',1) for x in git(ROOT,'for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes').decode().splitlines());before=dict(x.split(' ',1) for x in B['refs'].splitlines());refchanges=[k for k,v in before.items() if refs.get(k)!=v]
r={'schema':'NightglassRefinementPreservationCheck/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worktrees':trees,'files_checked':len(B['files']),'changed_paths':changed,'changed_prior_refs':refchanges,'scope':B['scope'],'pass':not changed and not refchanges and all(x['head_matches'] and x['status_matches'] for x in trees)}
a=argparse.ArgumentParser();a.add_argument('--output',default=str(HERE/'protected-final.json'));args=a.parse_args();out=Path(args.output).resolve();assert out.is_relative_to(HERE);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['worktrees','scope']}));raise SystemExit(0 if r['pass'] else 1)
