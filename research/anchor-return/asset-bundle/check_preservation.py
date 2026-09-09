#!/usr/bin/env python3
"""Read-only AR baseline audit; write one fresh receipt in asset-bundle/local only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASELINE=ROOT/'research/anchor-return/protected-initial.json'
ACTIVE_REF='refs/heads/autonomous/anchor-return-20260909-1030'
REMOTE_REF='refs/remotes/origin/autonomous/anchor-return-20260909-1030'
EXEMPT_REFS={ACTIVE_REF,REMOTE_REF}
# The new baseline records this exact argv; enforce it before any audit.
STATUS_ARGS=['status','--porcelain=v1','--untracked-files=all','--ignored=matching']
STATUS_NORMALIZATION='raw-stdout'


def sha(data):return hashlib.sha256(data).hexdigest()

def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def git(path,args):
    # Disables optional index refresh writes and external fsmonitor hooks. No fetch,
    # checkout, clean, update-ref, protected-file writes or shell invocation.
    path=Path(path).resolve();pointer=path/'.git'
    if pointer.is_file():
        text=pointer.read_text().strip()
        if not text.startswith('gitdir: '):raise ValueError('Unsupported Git pointer')
        value=text[len('gitdir: '):].replace(chr(92),'/')
        if re.match(r'^[A-Za-z]:/',value):value='/mnt/'+value[0].lower()+'/'+value[3:]
        directory=Path(value)
        if not directory.is_absolute():directory=path/directory
    elif pointer.is_dir():directory=pointer
    else:raise ValueError('Missing worktree Git pointer')
    result=subprocess.run(['git','--git-dir='+str(directory.resolve()),'--work-tree='+str(path),'--no-optional-locks','-c','core.fsmonitor=false',*args],cwd=path,
        env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'},capture_output=True,timeout=240)
    if result.returncode:raise RuntimeError('git '+args[0]+' failed: '+result.stderr.decode('utf-8','replace')[:1500])
    return result.stdout

def parse_refs(text):
    result={}
    for line in text.splitlines():
        if not line:continue
        ref,digest=line.split(' ',1)
        if ref in result:raise ValueError('Duplicate baseline/current ref')
        result[ref]=digest.strip()
    return result

def parse_worktrees(text):
    result={}
    for block in text.strip().split('\n\n'):
        if not block:continue
        lines=block.splitlines()
        if not lines[0].startswith('worktree '):raise ValueError('Malformed worktree porcelain')
        path=lines[0][len('worktree '):]
        if path in result:raise ValueError('Duplicate worktree')
        result[path]=lines[1:]
    return result

def compare_refs(old,new):
    old={k:v for k,v in old.items() if k not in EXEMPT_REFS}
    new={k:v for k,v in new.items() if k not in EXEMPT_REFS}
    changed=[{'ref':k,'before':old.get(k),'after':new.get(k)} for k in sorted(set(old)|set(new)) if old.get(k)!=new.get(k)]
    return {'pass':not changed,'protected_ref_count':len(old),'changes':changed,'exempt_refs':sorted(EXEMPT_REFS)}

def check_tree(record):
    p=Path(record['path'])
    try:
        head=git(p,['rev-parse','HEAD']).decode().strip()
        status=git(p,STATUS_ARGS)
        digest=sha(status)
        return {'path':str(p),'head_before':record['head'],'head_now':head,'head_matches':head==record['head'],
                'status_sha256_before':record['status_sha256'],'status_sha256_now':digest,'status_matches':digest==record['status_sha256'],
                'status_bytes':len(status),'pass':head==record['head'] and digest==record['status_sha256']}
    except Exception as error:return {'path':str(p),'pass':False,'error_type':type(error).__name__,'error':str(error)}

def check_source(record):
    p=Path(record['source_path'])
    try:
        digest=file_sha(p)
        return {'source_path':str(p),'expected_sha256':record['sha256'],'actual_sha256':digest,'bytes':p.stat().st_size,'pass':digest==record['sha256']}
    except Exception as error:return {'source_path':str(p),'pass':False,'error_type':type(error).__name__,'error':str(error)}

def compare_topology(old,new):
    active=str(ROOT)
    if active in old:raise ValueError('Precreation baseline unexpectedly contains active worktree')
    if active not in new or 'branch '+ACTIVE_REF not in new[active]:raise ValueError('Expected new active worktree/branch missing')
    if len(new)!=len(old)+1:raise ValueError('Exactly one added active worktree permitted')
    flags=new[active]
    if len(flags)!=2 or not any(re.fullmatch(r'HEAD [0-9a-f]{40}',x) for x in flags):raise ValueError('Unexpected active topology flags')
    prior={k:v for k,v in new.items() if k!=active}
    changes=[{'path':k,'before':old.get(k),'after':prior.get(k)} for k in sorted(set(old)|set(prior)) if old.get(k)!=prior.get(k)]
    return {'pass':not changes,'total_worktrees_before':len(old),'total_worktrees_now':len(new),'changes':changes,'allowed_added_worktree':active,'active_head_exempt':True}

def expand_sources(baseline):
    sources=[];definitions=[]
    for spec in baseline['source_definitions']:
        path=Path(spec['path'])
        if file_sha(path)!=spec['sha256']:raise ValueError('Protected source definition changed')
        rows=json.loads(path.read_text())[spec['field']]
        for row in rows:
            if spec['field']=='source_files':sources.append({'source_path':row['source_path'],'sha256':row['sha256']})
            elif spec['field']=='files':
                name=row['path'];relative=Path(name)
                if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe baseline manifest path')
                target=spec.get('aliases',{}).get(name,str(Path(spec['root'])/relative))
                sources.append({'source_path':target,'sha256':row['sha256']})
            else:raise ValueError('Unknown baseline source definition field')
        definitions.append({'path':str(path),'sha256':spec['sha256'],'expanded_files':len(rows),'pass':True})
    if len(sources)!=baseline['source_count'] or len(sources)!=738:raise ValueError('Protected source expansion count differs')
    return sources,definitions

def audit():
    baseline=json.loads(BASELINE.read_text())
    source_rows,source_definitions=expand_sources(baseline)
    if len(baseline['worktrees'])!=23:raise ValueError('Unexpected baseline coverage')
    paths=[x['path'] for x in baseline['worktrees']]
    if len(set(paths))!=23 or str(ROOT) in paths:raise ValueError('Protected list must contain23 unique prior worktrees and exclude active root')
    if baseline.get('schema')!='AnchorReturnProtectedBaseline/1' or baseline.get('status_args')!=STATUS_ARGS:raise ValueError('Baseline schema or recorded status command differs')
    started=datetime.now(timezone.utc).isoformat()
    with ThreadPoolExecutor(max_workers=4) as pool:
        trees=list(pool.map(check_tree,baseline['worktrees']))
        sources=list(pool.map(check_source,source_rows))
    aggregate=hashlib.sha256(json.dumps([[x['source_path'],x.get('actual_sha256')] for x in sources],separators=(',',':')).encode()).hexdigest()
    aggregate_check={'expected_sha256':baseline['source_aggregate_sha256'],'actual_sha256':aggregate,'pass':aggregate==baseline['source_aggregate_sha256'],'serialization':"SHA256(json.dumps([[actualpath,actualhash],...],separators=(',',':')).encode()), definition iteration order"}
    refs=compare_refs(parse_refs(baseline['refs']),parse_refs(git(ROOT,['for-each-ref','--format=%(refname) %(objectname)']).decode()))
    old=parse_worktrees(baseline['worktrees_porcelain']);new=parse_worktrees(git(ROOT,['worktree','list','--porcelain']).decode())
    topology=compare_topology(old,new)
    return {'schema':'AnchorReturnPreservationAudit/1','experiment_id':'AR-20260909-01','started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
        'baseline_path':str(BASELINE.relative_to(ROOT)),'baseline_sha256':file_sha(BASELINE),'checker_sha256':file_sha(Path(__file__)),
        'status_contract':{'args':STATUS_ARGS,'normalization':STATUS_NORMALIZATION,'historical_argv_recorded':True,'equivalence_claim':'Exact recorded baseline argv and raw stdout SHA equality; Git-dir/work-tree explicitly normalized for Windows pointers.','read_only_controls':['git --no-optional-locks','GIT_OPTIONAL_LOCKS=0','core.fsmonitor=false']},
        'source_aggregate_check':aggregate_check,'source_definition_checks':source_definitions,'recorded_source_aggregate_sha256':baseline['source_aggregate_sha256'],'worktrees':trees,'original_source_files':sources,'refs':refs,'worktree_topology':topology,
        'pass':all(x['pass'] for x in trees+sources) and refs['pass'] and topology['pass'] and aggregate_check['pass'],
        'limits':['Status digest includes ignored paths exactly as Git reports them; it does not byte-hash ignored/cache file contents or every tracked/untracked file.',
                  'Only 738 saved original source files have content SHA verification. Existing modified files can retain the same Git status while their bytes change.',
                  'Snapshot contains status hashes, not original status text, so a mismatch cannot be expanded into a filename diff against that baseline.',
                  'Local Git refs are audited; this does not query the network remote. Root separately verifies pushed remote parity.',
                  'Read-only observations occur over an interval, not an atomic filesystem snapshot; run after concurrent delivery mutations settle.',
                  'Baseline precedes active worktree creation. Exactly one active worktree addition is allowed with fixed branch/path; its HEAD may advance. Only its local and origin tracking refs are exempt. All other topology and ref changes fail.']}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    output=args.output.absolute()
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):raise ValueError('Receipt symlink path rejected')
    output=output.resolve();local=HERE/'local'
    if not output.is_relative_to(local) or output.suffix!='.json':raise ValueError('--output must be a new .json below asset-bundle/local')
    if output.exists():raise FileExistsError('Preserve existing receipt; choose a fresh path')
    result=audit();output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'pass':result['pass'],'receipt':str(output),'worktrees':len(result['worktrees']),'original_sources':len(result['original_source_files']),'protected_refs':result['refs']['protected_ref_count'],'failing_worktrees':[x['path'] for x in result['worktrees'] if not x['pass']]},indent=2))
    return 0 if result['pass'] else 1

if __name__=='__main__':sys.exit(main())
