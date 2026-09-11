"""Fast final head/status/ref recheck; supplements, not replaces, the full file comparison."""
from pathlib import Path
import gzip,json,os,subprocess,datetime
HERE=Path(__file__).resolve().parent.parent
ROOT=Path('/mnt/c/AgentWorkspaces/anime-pipeline')
b=json.loads(gzip.decompress((HERE/'evidence/protected-initial.json.gz').read_bytes()))
def git(tree,*args):
    gd=ROOT/'.git' if tree==ROOT else ROOT/'.git/worktrees'/tree.name
    return subprocess.check_output(['git','--git-dir='+str(gd),'--work-tree='+str(tree),*args],env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),text=True).strip()
rows=[]
for old in b['worktrees']:
    tree=ROOT.parent/old['name']
    rows.append({'name':old['name'],'head_unchanged':git(tree,'rev-parse','HEAD')==old['head'],'status_unchanged':git(tree,'status','--porcelain=v1','--untracked-files=all','--ignored=matching')==old['status'].strip()})
before=dict(x.split(' ',1) for x in b['refs'].strip().splitlines())
after=dict(x.split(' ',1) for x in git(ROOT,'for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes').splitlines())
changes=[k for k,v in before.items() if after.get(k)!=v]
r={'schema':'FinalProtectedRefsStatus/1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'full_file_comparison':'protected-comparison.json','worktrees':rows,'protected_ref_changes':changes,'pass':not changes and all(x['head_unchanged'] and x['status_unchanged'] for x in rows)}
(HERE/'evidence/final-protected-status.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
raise SystemExit(0 if r['pass'] else 1)
