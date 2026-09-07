#!/usr/bin/env python3
"""Deterministic asset-only ZIP; verified, non-overwriting fresh-clone restoration."""
import argparse, hashlib, json, os, re, stat, sys, tempfile, zipfile
from pathlib import Path, PurePosixPath
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BINARY={'.png','.jpg','.jpeg','.webp','.exr','.blend','.blend1','.gif','.tif','.tiff'}
EXCLUDED={'runtime','.scratch','browser','browsers','__pycache__','node_modules','.git','venv','.venv','cache','caches','profiles','local'}
DEFAULT_ARCHIVE=HERE/'local/SC-20260907-01-preserved-assets.zip'
MANIFEST_NAME='ASSET-MANIFEST.json'
def digest_stream(f):
 h=hashlib.sha256();size=0
 for block in iter(lambda:f.read(1024*1024),b''):h.update(block);size+=len(block)
 return size,h.hexdigest()
def digest(p):
 with p.open('rb') as f:return digest_stream(f)
def json_bytes(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def safe_relative(name):
 p=PurePosixPath(name)
 if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or str(p)!=name:raise ValueError('Unsafe asset path: '+name)
 return p

def discover():
 found={}
 for relative in ['production/structural-pilot','research/structural-pilot','docs/research/structural-pilot']:
  for dirname,dirs,files in os.walk(ROOT/relative):
   dirs[:]=sorted(d for d in dirs if d not in EXCLUDED)
   for filename in sorted(files):
    p=Path(dirname)/filename
    if p.is_symlink():raise ValueError('Symlink assets are not included: '+str(p))
    rel=p.relative_to(ROOT).as_posix();reason=None
    if p.suffix.lower() in BINARY:reason='experiment-binary-asset'
    elif '/finishing/' in rel and p.suffix.lower() in {'.svg','.json'} and 'data:image/' in p.read_text():reason='preserved-inline-raster-source'
    if reason:found[rel]=reason
 baseline=ROOT/'docs/research/sequence-pilot/reader/review-data.json'
 for panel in json.loads(baseline.read_text())['panels']:
  if panel.get('candidate'):
   p=(baseline.parent/panel['candidate']['src']).resolve();rel=p.relative_to(ROOT).as_posix()
   if digest(p)[1]!=panel['candidate']['sha256']:raise ValueError('Baseline context hash differs: '+rel)
   found[rel]='copied-prior-context-required-by-both-readers'
 entries=[]
 for rel,reason in sorted(found.items()):
  safe_relative(rel);size,sha=digest(ROOT/rel);entries.append(dict(path=rel,bytes=size,sha256=sha,reason=reason))
 return dict(schema='PreservedExperimentAssets/1',experiment='SC-20260907-01',archive_format='ZIP_STORED; sorted members; fixed 1980-01-01 timestamps; Unix regular-file mode 0644',files=entries,file_count=len(entries),total_bytes=sum(e['bytes'] for e in entries),excluded=['runtime/.scratch/browser/cache/venv profiles and dependencies','reader code and ordinary/mutable JSON','asset-bundle/local/ outputs'],baseline_metadata_path='docs/research/sequence-pilot/reader/review-data.json',baseline_metadata_sha256=digest(baseline)[1])

def write_zip(archive,manifest):
 if archive.exists():raise FileExistsError('Refuse to replace archive: '+str(archive))
 archive.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
  for name,payload in [(MANIFEST_NAME,json_bytes(manifest))]+[(e['path'],None) for e in manifest['files']]:
   info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.create_system=3;info.external_attr=(stat.S_IFREG|0o644)<<16;info.compress_type=zipfile.ZIP_STORED
   with z.open(info,'w',force_zip64=True) as out:
    if payload is not None:out.write(payload)
    else:
     expected=next(e for e in manifest['files'] if e['path']==name);p=ROOT/name;h=hashlib.sha256();size=0
     with p.open('rb') as f:
      for block in iter(lambda:f.read(1024*1024),b''):out.write(block);h.update(block);size+=len(block)
     if (size,h.hexdigest())!=(expected['bytes'],expected['sha256']):raise ValueError('Asset changed during archive creation: '+name)

def inspect_archive(archive,receipt):
 size,sha=digest(archive)
 if (size,sha)!=(receipt['archive_bytes'],receipt['archive_sha256']):raise ValueError('Archive byte/hash mismatch')
 with zipfile.ZipFile(archive) as z:
  manifest=json.loads(z.read(MANIFEST_NAME));names=z.namelist();expected=[MANIFEST_NAME]+[e['path'] for e in manifest['files']]
  if names!=expected or len(names)!=len(set(names)):raise ValueError('Archive membership/order differs from manifest')
  if hashlib.sha256(z.read(MANIFEST_NAME)).hexdigest()!=receipt['manifest_sha256']:raise ValueError('Embedded manifest hash mismatch')
  for entry in manifest['files']:
   safe_relative(entry['path']);info=z.getinfo(entry['path'])
   if stat.S_ISLNK(info.external_attr>>16):raise ValueError('Symlink archive member')
   with z.open(entry['path']) as f:actual=digest_stream(f)
   if actual!=(entry['bytes'],entry['sha256']):raise ValueError('Member hash mismatch: '+entry['path'])
 return manifest

def restore(archive,receipt,target,dry_run=False):
 manifest=inspect_archive(archive,receipt)
 if target.is_symlink():raise ValueError('Refuse symlink target root')
 target=target.resolve();missing=[];identical=[]
 # All paths and collisions are checked before making any directory or writing any asset.
 for entry in manifest['files']:
  rel=safe_relative(entry['path']);dest=target.joinpath(*rel.parts)
  current=target
  for index,part in enumerate(rel.parts):
   current=current/part
   if current.is_symlink():raise ValueError('Refuse symlink destination: '+str(current))
   if index<len(rel.parts)-1 and current.exists() and not current.is_dir():raise FileExistsError('Destination parent is not a directory; nothing restored: '+str(current))
  if not dest.resolve().is_relative_to(target):raise ValueError('Destination escapes target')
  if dest.exists():
   if not dest.is_file() or digest(dest)!=(entry['bytes'],entry['sha256']):raise FileExistsError('Existing asset differs; nothing restored: '+str(dest))
   identical.append(entry['path'])
  else:missing.append(entry)
 if not dry_run:
  with zipfile.ZipFile(archive) as z:
   for entry in missing:
    dest=target/entry['path'];dest.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation also prevents overwriting a concurrent new file after preflight.
    with z.open(entry['path']) as source,dest.open('xb') as out:
     for block in iter(lambda:source.read(1024*1024),b''):out.write(block)
    if digest(dest)!=(entry['bytes'],entry['sha256']):raise ValueError('Restored file verification failed: '+str(dest))
 return dict(dry_run=dry_run,verified_members=len(manifest['files']),identical_existing_skipped=len(identical),missing_assets=len(missing),written_assets=0 if dry_run else len(missing))

def create(archive):
 manifest=discover();manifest_path=HERE/'asset-manifest.json';receipt_path=HERE/'archive-receipt.json'
 if manifest_path.exists() or receipt_path.exists():raise FileExistsError('Preserve existing bundle manifest/receipt; use a new packaging directory/version')
 write_zip(archive,manifest);size,sha=digest(archive);receipt=dict(schema='AssetArchiveReceipt/1',archive_name=archive.name,archive_bytes=size,archive_sha256=sha,manifest_sha256=hashlib.sha256(json_bytes(manifest)).hexdigest(),files=manifest['file_count'],asset_bytes=manifest['total_bytes'],zip_member_hashes_verified=False)
 inspect_archive(archive,receipt);receipt['zip_member_hashes_verified']=True
 manifest_path.write_bytes(json_bytes(manifest));receipt_path.write_bytes(json_bytes(receipt));print(json.dumps(receipt,indent=2))

def self_test():
 with tempfile.TemporaryDirectory(dir=HERE/'local',prefix='restore-self-test-') as tmp:
  tmp=Path(tmp);archive=tmp/'fixture.zip';entries=[dict(path='assets/a.png',bytes=3,sha256=hashlib.sha256(b'AAA').hexdigest()),dict(path='assets/b.png',bytes=3,sha256=hashlib.sha256(b'BBB').hexdigest())];manifest=dict(files=entries)
  with zipfile.ZipFile(archive,'x') as z:
   z.writestr(MANIFEST_NAME,json_bytes(manifest));z.writestr('assets/a.png',b'AAA');z.writestr('assets/b.png',b'BBB')
  size,sha=digest(archive);receipt=dict(archive_bytes=size,archive_sha256=sha,manifest_sha256=hashlib.sha256(json_bytes(manifest)).hexdigest());dest=tmp/'restore';(dest/'assets').mkdir(parents=True);(dest/'assets/b.png').write_bytes(b'BAD')
  try:restore(archive,receipt,dest)
  except FileExistsError:pass
  else:raise AssertionError('Different existing asset must reject')
  assert not (dest/'assets/a.png').exists() and (dest/'assets/b.png').read_bytes()==b'BAD'
  (dest/'assets/b.png').write_bytes(b'BBB');result=restore(archive,receipt,dest);assert result['written_assets']==1 and result['identical_existing_skipped']==1
  assert restore(archive,receipt,dest)['written_assets']==0
  blocked=tmp/'parent-collision';blocked.mkdir();(blocked/'assets').write_bytes(b'parent-file')
  try:restore(archive,receipt,blocked)
  except FileExistsError:pass
  else:raise AssertionError('Existing non-directory parent must reject')
  assert (blocked/'assets').read_bytes()==b'parent-file'
  try:safe_relative('../outside.png')
  except ValueError:pass
  else:raise AssertionError('Traversal must reject')
  try:inspect_archive(archive,{**receipt,'archive_sha256':'0'*64})
  except ValueError:pass
  else:raise AssertionError('Wrong archive hash must reject')
 print('PASS: collision preflight writes nothing; identical skip; absent restore; idempotence; parent collision; traversal and archive-hash rejection')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['create','rebuild','verify','restore','self-test']);p.add_argument('--archive',type=Path,default=DEFAULT_ARCHIVE);p.add_argument('--receipt',type=Path,default=HERE/'archive-receipt.json');p.add_argument('--target',type=Path,default=ROOT);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
 if a.action=='create':create(a.archive)
 elif a.action=='self-test':self_test()
 elif a.action=='rebuild':
  manifest=json.loads((HERE/'asset-manifest.json').read_text());receipt=json.loads(a.receipt.read_text())
  for entry in manifest['files']:
   safe_relative(entry['path'])
   if digest(ROOT/entry['path'])!=(entry['bytes'],entry['sha256']):raise ValueError('Current source differs: '+entry['path'])
  if not a.archive.exists():write_zip(a.archive,manifest)
  inspect_archive(a.archive,receipt);print(json.dumps(dict(rebuilt_archive_matches=True,archive_sha256=receipt['archive_sha256'])))
 else:
  receipt=json.loads(a.receipt.read_text())
  if a.action=='verify':m=inspect_archive(a.archive,receipt);print(json.dumps(dict(verified=True,files=len(m['files']),bytes=m.get('total_bytes'))))
  else:print(json.dumps(restore(a.archive,receipt,a.target,a.dry_run)))
if __name__=='__main__':main()
