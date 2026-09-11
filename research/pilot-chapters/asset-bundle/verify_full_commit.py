#!/usr/bin/env python3
"""Export every tracked file at an exact commit, then add verified pilot-chapter assets."""
import argparse, hashlib, importlib.util, json, os, subprocess, tarfile
from pathlib import Path, PurePosixPath
p=argparse.ArgumentParser();p.add_argument('--commit',required=True);p.add_argument('--delivery',required=True);a=p.parse_args()
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'research/pilot-chapters/asset-bundle/local';OUT=Path(a.delivery).resolve()
assert OUT.is_relative_to(BASE) and OUT!=BASE and OUT.is_dir()
for ancestor in (OUT,*OUT.parents):
 assert not ancestor.is_symlink(), 'Symlink output ancestor'
assert len(a.commit)==40 and all(c in '0123456789abcdef' for c in a.commit)
git=['git','--no-optional-locks','-C',str(ROOT)]
def run(*args):return subprocess.check_output(git+list(args),env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
assert run('rev-parse','HEAD').decode().strip()==a.commit
path=ROOT/'research/pilot-chapters/asset-bundle/bundle_assets.py';spec=importlib.util.spec_from_file_location('bundle',path);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
receipt=json.loads((OUT/'archive-receipt.json').read_text());archive=OUT/'pilot-chapters-portable.zip';manifest=b.verify(archive,receipt)
target=OUT/'full-commit-restoration';tarpath=OUT/'full-commit.tar';proofpath=OUT/'full-commit-verification.json'
assert not target.exists() and not tarpath.exists() and not proofpath.exists()
rows=[]
for raw in run('ls-tree','-rlz',a.commit).split(b'\0'):
 if not raw:continue
 meta,name=raw.split(b'\t',1);mode,kind,blob,size=meta.decode().split();name=name.decode();assert kind=='blob' and mode in ('100644','100755'),(name,mode)
 rel=PurePosixPath(name);assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in name
 rows.append({'path':name,'mode':mode,'git_blob':blob,'bytes':int(size)})
assert len({x['path'].casefold() for x in rows})==len(rows)
with tarpath.open('xb') as f:subprocess.run(git+['archive','--format=tar',a.commit],stdout=f,check=True,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
expected={x['path']:x for x in rows}
with tarfile.open(tarpath,'r:') as tf:
 members=tf.getmembers();files=[m for m in members if m.isfile()];assert {m.name for m in files}==set(expected) and len(files)==len(rows)
 for m in members:
  rel=PurePosixPath(m.name);assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in m.name and (m.isdir() or m.isfile())
 target.mkdir()
 for m in files:
  assert m.size==expected[m.name]['bytes'];dest=target/m.name;dest.parent.mkdir(parents=True,exist_ok=True)
  with tf.extractfile(m) as source,dest.open('xb') as out:
   for block in iter(lambda:source.read(1024*1024),b''):out.write(block)
  dest.chmod(int(expected[m.name]['mode'][-3:],8))
def audit(label):
 for row in rows:
  f=target/row['path'];assert f.is_file() and not f.is_symlink();raw=f.read_bytes();assert len(raw)==row['bytes'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],row['path']
  digest=hashlib.sha256(raw).hexdigest()
  if 'sha256' in row:assert row['sha256']==digest,row['path']
  else:row['sha256']=digest
 return {'pass':True,'stage':label,'tracked_files':len(rows),'tracked_bytes':sum(x['bytes'] for x in rows)}
before=audit('full Git archive before additive asset restoration');restored=b.restore(archive,receipt,target);after=audit('after additive asset restoration');rebuild=b.rebuild_check(target);final=audit('after reader rebuild');inventory=b.check_inventory(target,manifest)
ledger=OUT/'full-commit-files.json';ledger.write_text(json.dumps(rows,indent=2)+'\n')
proof={'schema':'PilotChaptersFullCommitRestoration/1','pass':True,'scope':'Entire exact commit, all tracked repository files; no subtree filter. No .git directory is included in git archive.','commit':a.commit,'snapshot_root':str(target),'tar':{'path':str(tarpath),'bytes':tarpath.stat().st_size,'sha256':b.hashed(tarpath)[1]},'archive_sha256':receipt['archive_sha256'],'before':before,'restore':restored,'after_restore':after,'rebuild':rebuild,'after_rebuild':final,'asset_inventory':inventory,'tracked_inventory':{'path':str(ledger),'sha256':b.hashed(ledger)[1]},'every_original_tracked_byte_unchanged':True}
proofpath.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'pass':True,'root':str(target),'tracked_files':len(rows),'restore':restored,'urls':rebuild['local_links']['checked_local_urls'],'receipt':str(proofpath)}))
