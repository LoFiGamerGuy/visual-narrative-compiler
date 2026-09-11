#!/usr/bin/env python3
"""Bundle only finalized visual-direction PNGs; verify before collision-safe restore."""
import argparse, hashlib, json, os, stat, struct, tempfile, zipfile
from pathlib import Path, PurePosixPath
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CANDIDATES=Path('production/visual-directions/candidates')
ARCHIVE=HERE/'local/visual-directions-artwork.zip'
MANIFEST='ASSET-MANIFEST.json'
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
def hash_stream(source):
 h=hashlib.sha256();size=0
 for block in iter(lambda:source.read(1024*1024),b''):h.update(block);size+=len(block)
 return size,h.hexdigest()
def hashed(path):
 with path.open('rb') as source:return hash_stream(source)
def safe_path(name):
 path=PurePosixPath(name)
 if not name or path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name or str(path)!=name:raise ValueError('Unsafe asset path: '+name)
 return path

def selection(count,overviews):
 if count is None or not 20<=count<=26:raise ValueError('Final expected candidate count must be 20 through 26')
 candidates=sorted((ROOT/CANDIDATES).glob('*.png'))
 if len(candidates)!=count:raise ValueError(f'Expected exactly {count} finalized PNG candidates; found {len(candidates)}')
 selected={p:'new-direction-candidate' for p in candidates}
 for name in overviews:
  safe_path(name);path=ROOT/name
  if not any(path.is_relative_to(ROOT/prefix) for prefix in ['production/visual-directions','docs/research/visual-directions','research/visual-directions']):raise ValueError('Overview must belong to this visual-directions experiment')
  if path.is_relative_to(HERE) or path.suffix.lower()!='.png':raise ValueError('Overview must be an explicit gallery PNG outside asset-bundle/')
  if path in selected:raise ValueError('Overview duplicates a candidate')
  selected[path]='final-gallery-overview'
 entries=[]
 for path,kind in sorted(selected.items()):
  if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):raise ValueError('Expected ordinary local PNG: '+str(path))
  with path.open('rb') as source:header=source.read(24)
  if len(header)!=24 or header[:8]!=b'\x89PNG\r\n\x1a\n' or header[12:16]!=b'IHDR':raise ValueError('Invalid PNG header: '+str(path))
  width,height=struct.unpack('>II',header[16:24])
  if not width or not height:raise ValueError('Invalid PNG dimensions')
  size,sha=hashed(path);entries.append(dict(path=path.relative_to(ROOT).as_posix(),bytes=size,sha256=sha,width=width,height=height,kind=kind))
 return dict(schema='VisualDirectionArtwork/1',candidate_count=count,overview_count=len(overviews),file_count=len(entries),total_bytes=sum(e['bytes'] for e in entries),files=entries,excludes='Prior artwork, prompts, metadata, HTML/code, runtime profiles and caches',zip_format='Sorted ZIP_STORED members; fixed 1980 timestamp; Unix regular-file mode 0644')

def write_archive(path,manifest):
 if path.exists():raise FileExistsError('Preserve existing archive: '+str(path))
 # Validate every source before starting the new ZIP.
 for entry in manifest['files']:
  safe_path(entry['path'])
  if hashed(ROOT/entry['path'])!=(entry['bytes'],entry['sha256']):raise ValueError('Source changed: '+entry['path'])
 path.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_STORED,allowZip64=True) as archive:
  for name,entry in [(MANIFEST,None)]+[(e['path'],e) for e in manifest['files']]:
   info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.create_system=3;info.external_attr=(stat.S_IFREG|0o644)<<16;info.compress_type=zipfile.ZIP_STORED
   with archive.open(info,'w',force_zip64=True) as dest:
    if entry is None:dest.write(encoded(manifest))
    else:
     with (ROOT/name).open('rb') as source:
      h=hashlib.sha256();size=0
      for block in iter(lambda:source.read(1024*1024),b''):dest.write(block);h.update(block);size+=len(block)
     if (size,h.hexdigest())!=(entry['bytes'],entry['sha256']):raise ValueError('Source changed while packing: '+name)

def verify(path,receipt):
 if hashed(path)!=(receipt['archive_bytes'],receipt['archive_sha256']):raise ValueError('Archive bytes/hash differ from receipt')
 with zipfile.ZipFile(path) as archive:
  raw=archive.read(MANIFEST)
  if hashlib.sha256(raw).hexdigest()!=receipt['manifest_sha256']:raise ValueError('Embedded manifest hash differs')
  manifest=json.loads(raw);names=archive.namelist();expected=[MANIFEST]+[e['path'] for e in manifest['files']]
  if names!=expected or len(set(names))!=len(names):raise ValueError('Archive member list differs')
  for entry in manifest['files']:
   safe_path(entry['path'])
   if stat.S_ISLNK(archive.getinfo(entry['path']).external_attr>>16):raise ValueError('Symlink member rejected')
   with archive.open(entry['path']) as source:actual=hash_stream(source)
   if actual!=(entry['bytes'],entry['sha256']):raise ValueError('Asset hash differs: '+entry['path'])
 return manifest

def restore(path,receipt,target,dry_run=False):
 manifest=verify(path,receipt)
 if target.is_symlink():raise ValueError('Symlink target root rejected')
 target=target.resolve();missing=[];identical=0
 # Complete collision/path preflight before creating any directories or assets.
 for entry in manifest['files']:
  rel=safe_path(entry['path']);dest=target.joinpath(*rel.parts);parent=target
  for index,part in enumerate(rel.parts):
   parent=parent/part
   if parent.is_symlink():raise ValueError('Symlink destination rejected: '+str(parent))
   if index<len(rel.parts)-1 and parent.exists() and not parent.is_dir():raise FileExistsError('Destination parent is a file; nothing restored')
  if not dest.resolve().is_relative_to(target):raise ValueError('Destination escapes target')
  if dest.exists():
   if not dest.is_file() or hashed(dest)!=(entry['bytes'],entry['sha256']):raise FileExistsError('Existing asset differs; nothing restored: '+str(dest))
   identical+=1
  else:missing.append(entry)
 if not dry_run:
  with zipfile.ZipFile(path) as archive:
   for entry in missing:
    dest=target/entry['path'];dest.parent.mkdir(parents=True,exist_ok=True)
    with archive.open(entry['path']) as source,dest.open('xb') as out:
     for block in iter(lambda:source.read(1024*1024),b''):out.write(block)
    if hashed(dest)!=(entry['bytes'],entry['sha256']):raise ValueError('Restored asset verification failed')
 return dict(verified_assets=len(manifest['files']),identical_existing_skipped=identical,missing_assets=len(missing),written_assets=0 if dry_run else len(missing),dry_run=dry_run)

def freeze(path,count,overviews):
 mp=HERE/'asset-manifest.json';rp=HERE/'archive-receipt.json'
 if mp.exists() or rp.exists():raise FileExistsError('Preserve existing final manifest/receipt; use a new bundle version')
 manifest=selection(count,overviews);write_archive(path,manifest);size,sha=hashed(path);receipt=dict(schema='VisualDirectionArchive/1',archive_name=path.name,archive_bytes=size,archive_sha256=sha,manifest_sha256=hashlib.sha256(encoded(manifest)).hexdigest(),asset_count=len(manifest['files']),asset_bytes=manifest['total_bytes'])
 verify(path,receipt);mp.write_bytes(encoded(manifest));rp.write_bytes(encoded(receipt));print(json.dumps(receipt,indent=2))

def self_test():
 (HERE/'local').mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(dir=HERE/'local',prefix='restore-test-') as temporary:
  tmp=Path(temporary);path=tmp/'test.zip';entries=[dict(path='assets/a.png',bytes=3,sha256=hashlib.sha256(b'AAA').hexdigest()),dict(path='assets/b.png',bytes=3,sha256=hashlib.sha256(b'BBB').hexdigest())];manifest=dict(files=entries)
  with zipfile.ZipFile(path,'x') as archive:
   archive.writestr(MANIFEST,encoded(manifest));archive.writestr('assets/a.png',b'AAA');archive.writestr('assets/b.png',b'BBB')
  size,sha=hashed(path);receipt=dict(archive_bytes=size,archive_sha256=sha,manifest_sha256=hashlib.sha256(encoded(manifest)).hexdigest());target=tmp/'target';(target/'assets').mkdir(parents=True);(target/'assets/b.png').write_bytes(b'BAD')
  try:restore(path,receipt,target)
  except FileExistsError:pass
  else:raise AssertionError('Differing existing file accepted')
  assert not (target/'assets/a.png').exists()
  (target/'assets/b.png').write_bytes(b'BBB');result=restore(path,receipt,target);assert result['written_assets']==1 and result['identical_existing_skipped']==1;assert restore(path,receipt,target)['written_assets']==0
  blocked=tmp/'parent-file';blocked.mkdir();(blocked/'assets').write_bytes(b'FILE')
  try:restore(path,receipt,blocked)
  except FileExistsError:pass
  else:raise AssertionError('Non-directory parent accepted')
  try:safe_path('../escape.png')
  except ValueError:pass
  else:raise AssertionError('Unsafe path accepted')
  try:verify(path,{**receipt,'archive_sha256':'0'*64})
  except ValueError:pass
  else:raise AssertionError('Wrong archive hash accepted')
 print('PASS: collision preflight, identical skip, missing restore, idempotence, parent-file rejection, path rejection, archive hash rejection')

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['create','verify','restore','rebuild','self-test']);parser.add_argument('--archive',type=Path,default=ARCHIVE);parser.add_argument('--receipt',type=Path,default=HERE/'archive-receipt.json');parser.add_argument('--target',type=Path,default=ROOT);parser.add_argument('--dry-run',action='store_true');parser.add_argument('--expected-candidates',type=int);parser.add_argument('--overview',action='append',default=[]);args=parser.parse_args()
 if args.action=='self-test':self_test();return
 if args.action=='create':freeze(args.archive,args.expected_candidates,args.overview);return
 receipt=json.loads(args.receipt.read_text())
 if args.action=='restore':print(json.dumps(restore(args.archive,receipt,args.target,args.dry_run)));return
 if args.action=='rebuild' and not args.archive.exists():write_archive(args.archive,json.loads((HERE/'asset-manifest.json').read_text()))
 manifest=verify(args.archive,receipt);print(json.dumps(dict(verified=True,assets=len(manifest['files']),archive_sha256=receipt['archive_sha256'])))
if __name__=='__main__':main()
