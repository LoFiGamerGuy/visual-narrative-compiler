"""Compare every protected file/ref against the pre-isolation baseline, read only."""
import concurrent.futures,datetime,gzip,hashlib,json,os,stat,subprocess,sys
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];BASE=OUT.parents[2];ROOT=BASE/'anime-pipeline'
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
def git(args,gd=None,wt=None):
    cmd=['git']+(['--git-dir='+str(gd),'--work-tree='+str(wt)]if gd else [])+args
    return subprocess.run(cmd,cwd=ROOT,env=ENV,capture_output=True,text=True,check=True).stdout
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def inspect(before):
    name=before['name'];root=BASE/name;gd=ROOT/'.git' if name=='anime-pipeline' else ROOT/'.git/worktrees'/name
    after={k:v for k,v in before.items()if k not in ['files','admin','bytes','content_hashed']};after.update(files={},admin={},bytes=0,content_hashed=0)
    after['head']=git(['rev-parse','HEAD'],gd,root).strip();after['status']=git(['status','--porcelain=v1','--untracked-files=all','--ignored=matching'],gd,root)
    for d,dirs,files in os.walk(root,followlinks=False):
        if Path(d)==root:dirs[:]=[x for x in dirs if x!='.git']
        for f in files:
            p=Path(d)/f;rel=str(p.relative_to(root));s=p.lstat();key=hashlib.sha256(rel.encode()).hexdigest();v=[s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode];after['bytes']+=s.st_size
            old=before['files'].get(key)
            if stat.S_ISLNK(s.st_mode):v.append(hashlib.sha256(os.readlink(p).encode()).hexdigest())
            elif old and len(old)>4:v.append(digest(p));after['content_hashed']+=1
            after['files'][key]=v
    for f in ['HEAD','index','commondir','gitdir']:
        p=gd/f
        if p.is_file():after['admin'][f]=digest(p)
    changes=[{'opaque_relative_path_sha256':k,'before':before['files'].get(k),'after':after['files'].get(k)}for k in set(before['files'])|set(after['files'])if before['files'].get(k)!=after['files'].get(k)]
    result={'name':name,'file_count':len(after['files']),'content_hash_count':after['content_hashed'],'bytes':after['bytes'],'head_unchanged':before['head']==after['head'],'status_unchanged':before['status']==after['status'],'admin_unchanged':before['admin']==after['admin'],'file_changes':changes,'pass':not changes and before['head']==after['head']and before['status']==after['status']and before['admin']==after['admin']}
    print(name,result['file_count'],'PASS'if result['pass']else'FAIL',flush=True);return after,result
def run():
    with gzip.open(OUT/'evidence/protected-state-initial.json.gz','rt')as f:initial=json.load(f)
    final={'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':initial['method'],'worktrees':[]};results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
        for a,r in pool.map(inspect,initial['worktrees']):final['worktrees'].append(a);results.append(r)
    final['refs']=git(['for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes']);old=dict(l.split(' ')for l in initial['refs'].splitlines());new=dict(l.split(' ')for l in final['refs'].splitlines())
    ref_changes={k:{'before':v,'after':new.get(k)}for k,v in old.items()if new.get(k)!=v};added={k:v for k,v in new.items()if k not in old}
    isolated=json.loads((OUT/'evidence/isolation.json').read_text())['isolated_branch'];allowed={f'refs/heads/{isolated}',f'refs/remotes/origin/{isolated}'}
    result={'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protected_worktrees':results,'protected_ref_changes':ref_changes,'new_refs':added,'unexpected_new_refs':{k:v for k,v in added.items()if k not in allowed},'pass':all(r['pass']for r in results)and not ref_changes and set(added)<=allowed,'limits':'All file metadata and preselected content hashes compared; >32MiB and excluded vendor/model/dataset/private-reference files protected by size/mtime/ctime/mode, not full-content digest. Git shared mutable objects/logs/fetch administration excluded; prior index/HEAD/commondir/gitdir explicitly hashed. Read-only checks do not preserve access timestamps.'}
    suffix=sys.argv[1] if len(sys.argv)>1 else ''
    if not suffix:
        with gzip.open(OUT/'evidence/protected-state-final.json.gz','wt')as f:json.dump(final,f,separators=(',',':'))
    (OUT/f'evidence/protected-state-comparison{suffix}.json').write_text(json.dumps(result,indent=2)+'\n');print('OVERALL',result['pass'],flush=True)
    if not result['pass']:raise SystemExit(1)
if __name__=='__main__':run()
