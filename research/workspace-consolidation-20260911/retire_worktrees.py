"""Retire only verified, emptied checkouts; retain every branch and commit."""
import json
import os
from pathlib import Path
import subprocess
from consolidate import read_link

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
GIT=r'C:\Program Files\Git\cmd\git.exe' if os.name=='nt' else 'git'

def run(*args):
    return subprocess.check_output([GIT,'-C',str(ROOT),*args],text=True).strip()

def leftovers(path):
    found=[]
    for parent,dirs,files in os.walk(path,followlinks=False):
        for d in dirs:
            if read_link(Path(parent)/d) is not None:
                found.append(str((Path(parent)/d).relative_to(path)))
        for name in files:
            rel=str((Path(parent)/name).relative_to(path))
            if rel!='.git':
                found.append(rel)
    return found

def main():
    verification=json.loads((HERE/'verification.json').read_text(encoding='utf-8'))
    browser=json.loads((HERE/'browser-check.json').read_text(encoding='utf-8'))
    assert verification['remaining_actions']==0 and verification['failures']==0
    assert browser['failedRoutes']==0
    workspaces=json.loads((HERE/'workspaces.json').read_text(encoding='utf-8'))
    receipt=HERE/'retired-worktrees.json'
    retired=json.loads(receipt.read_text(encoding='utf-8'))['retired'] if receipt.exists() else []
    paths=[]
    for item in workspaces:
        path=ROOT.parent/item['name']
        assert path.parent==ROOT.parent and path.name.startswith('anime-pipeline-')
        assert run('rev-parse','refs/heads/'+item['branch'])==item['head']
        run('merge-base','--is-ancestor',item['head'],'HEAD')
        if item['name'] in retired:
            assert not path.exists()
            continue
        assert not leftovers(path),str(path)
        paths.append(path)
    (HERE/'empty-worktree-preflight.json').write_text(json.dumps({'workspaces':len(workspaces),'remaining_checkouts':len(paths),'unexpected_files':{}},indent=2)+'\n')
    # Repair Windows/WSL registrations explicitly; never prune by a stale label.
    registered=[p for p in paths if (p/'.git').exists()]
    repair=run('worktree','repair',*(str(p) for p in registered)) if registered else ''
    for path in paths:
        assert not leftovers(path),str(path)
        if (path/'.git').exists():
            run('worktree','remove','--force',str(path))
        else:
            # A platform failure may remove registration before empty folders.
            # Remove only proven-empty directories; never recursively erase data.
            for parent,dirs,files in os.walk(path,topdown=False):
                assert not files
                for d in dirs:
                    (Path(parent)/d).rmdir()
            path.rmdir()
        assert not path.exists()
        retired.append(path.name)
        (HERE/'retired-worktrees.json').write_text(json.dumps({'retired':retired,'repair_output':repair,'remaining_worktrees':run('worktree','list','--porcelain')},indent=2)+'\n')
        print(f'Retired {len(retired)}/{len(workspaces)}: {path.name}',flush=True)
    for item in workspaces:
        assert run('rev-parse','refs/heads/'+item['branch'])==item['head']
    print('All original branches remain. Only the consolidated checkout is active.',flush=True)

if __name__=='__main__':
    main()
