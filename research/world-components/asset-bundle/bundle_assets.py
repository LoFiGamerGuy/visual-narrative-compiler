#!/usr/bin/env python3
"""WC-20260907-01 portable share archive: frozen inputs, safe restore, offline rebuild."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIXES = ('production/world-components/', 'research/world-components/', 'docs/world-components/')
MANIFEST = 'ASSET-MANIFEST.json'
MAX_FILES, MAX_FILE, MAX_TOTAL, MAX_MANIFEST = 3000, 256*1024**2, 6*1024**3, 8*1024**2
EXCLUDED = {'.scratch', 'local', '__pycache__', '.git', 'node_modules', 'venv', '.venv', 'runtime', 'cache', 'browser-profile'}
EXTENSIONS = {'.png', '.json', '.md', '.txt', '.sha256', '.html', '.js', '.css', '.svg', '.py', '.cmd', '.mjs'}

def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)+'\n').encode()

def hashed_stream(source):
    h, size = hashlib.sha256(), 0
    for block in iter(lambda: source.read(1024*1024), b''):
        h.update(block); size += len(block)
    return size, h.hexdigest()

def hashed(path):
    with path.open('rb') as source:
        return hashed_stream(source)

def safe_path(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name or '\x00' in name:
        raise ValueError('Unsafe member path')
    p = PurePosixPath(name)
    if p.is_absolute() or str(p) != name or any(x in ('.', '..') for x in p.parts):
        raise ValueError('Unsafe member path: '+name)
    if name != 'START_HERE.cmd' and not name.startswith(PREFIXES):
        raise ValueError('Outside experiment prefixes: '+name)
    for part in p.parts:
        if part.endswith((' ', '.')) or re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', part, re.I):
            raise ValueError('Windows-unsafe member: '+name)
        if any(ord(c)<32 or c in '<>"|?*' for c in part):
            raise ValueError('Unsafe filename')
    return p

def regular(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError('Symlink source/destination rejected: '+str(part))
    if not path.is_file():
        raise ValueError('Expected regular file: '+str(path))

def validate_entries(manifest):
    entries = manifest['files']
    if not isinstance(entries, list) or not 0 < len(entries) <= MAX_FILES:
        raise ValueError('File count limit')
    names = set(); total = 0
    for e in entries:
        safe_path(e['path'])
        key = e['path'].casefold()
        if key in names:
            raise ValueError('Duplicate/case-colliding member')
        names.add(key)
        if type(e['bytes']) is not int or not 0 <= e['bytes'] <= MAX_FILE:
            raise ValueError('Member size limit')
        if not re.fullmatch('[0-9a-f]{64}', e['sha256']):
            raise ValueError('Invalid SHA256')
        total += e['bytes']
    for name in names:
        if any(str(p) in names for p in PurePosixPath(name).parents if str(p) != '.'):
            raise ValueError('File/directory member collision')
    if total > MAX_TOTAL or manifest.get('total_bytes') != total:
        raise ValueError('Total size limit/mismatch')
    return entries

def gather(root, expected_art):
    if type(expected_art) is not int or not 54 <= expected_art <= 63:
        raise ValueError('Expected final native generation count must be54–63')
    records = []
    for filename in ('candidates.json',):
        records += json.loads((root/'production/world-components'/filename).read_text())['candidates']
    if len(records) != expected_art or len({e['attempt_id'] for e in records}) != len(records):
        raise ValueError('Native candidate registry count/uniqueness differs')
    if sum(e['attempt_id'].endswith('-P') for e in records) != 54:
        raise ValueError('Expected exactly54 primary generations')
    refs = json.loads((root/'production/world-components/references.json').read_text())
    if len(refs) != 9:
        raise ValueError('Expected9 copied prior references')
    for e in records+refs:
        safe_path(e['path']); source = root/e['path']; regular(source)
        if hashed(source)[1] != e['sha256']:
            raise ValueError('Registered source hash differs: '+e['path'])
    sources = {}
    for prefix in PREFIXES:
        base = root/prefix
        for directory, folders, files in os.walk(base, followlinks=False):
            folders[:] = sorted(d for d in folders if d not in EXCLUDED and not (Path(directory)/d).is_symlink())
            for name in sorted(files):
                source = Path(directory)/name
                if source.is_relative_to(root/'research/world-components/asset-bundle'):
                    continue
                if source.suffix.lower() not in EXTENSIONS and source.name not in {'.gitignore', '.gitattributes'}:
                    continue
                regular(source)
                relative = source.relative_to(root).as_posix(); safe_path(relative)
                sources[relative] = source
    # Include the restorer and small usage docs, not its local archive/receipts.
    for name in ('bundle_assets.py', 'README.md', 'coverage-preflight.json', '.gitignore'):
        sources['research/world-components/asset-bundle/'+name] = HERE/name
    sources['START_HERE.cmd'] = HERE/'START_HERE.cmd'
    entries = []
    for name,path in sorted(sources.items()):
        size,sha = hashed(path)
        entries.append(dict(path=name, bytes=size, sha256=sha))
    manifest = dict(schema='WorldComponentPortable/1', experiment_id='WC-20260907-01', generated_native_count=len(records), primary_count=54, copied_reference_count=9, files=entries, total_bytes=sum(e['bytes'] for e in entries), exclusions='Runtime, scratch, caches, venv, prior namespaces and original tool-return locations. Current copied native assets and gallery copies retain exact paths.')
    validate_entries(manifest)
    return manifest, sources

def write_archive(path, manifest, sources):
    validate_entries(manifest)
    if path.exists():
        raise FileExistsError('Archive already exists; use a new version directory')
    for e in manifest['files']:
        regular(sources[e['path']])
        if hashed(sources[e['path']]) != (e['bytes'], e['sha256']):
            raise ValueError('Source changed before packing')
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as z:
        for name,e in [(MANIFEST,None)]+[(e['path'],e) for e in manifest['files']]:
            info = zipfile.ZipInfo(name, (1980,1,1,0,0,0))
            info.create_system = 3; info.external_attr = (stat.S_IFREG|0o644)<<16
            with z.open(info,'w',force_zip64=True) as dest:
                if e is None:
                    dest.write(encoded(manifest))
                else:
                    with sources[name].open('rb') as source:
                        for block in iter(lambda:source.read(1024*1024),b''): dest.write(block)
    size,sha = hashed(path)
    return dict(schema='WorldComponentPortableReceipt/1',archive_bytes=size,archive_sha256=sha,manifest_sha256=hashlib.sha256(encoded(manifest)).hexdigest(),file_count=len(manifest['files']))

def verify(path, receipt):
    regular(path)
    if hashed(path) != (receipt['archive_bytes'], receipt['archive_sha256']):
        raise ValueError('Archive hash/size mismatch')
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        if len(infos)>MAX_FILES+1 or len({i.filename.casefold() for i in infos}) != len(infos):
            raise ValueError('Archive duplicate/count limit')
        info = z.getinfo(MANIFEST)
        if info.file_size > MAX_MANIFEST:
            raise ValueError('Manifest size limit')
        raw = z.read(MANIFEST)
        if hashlib.sha256(raw).hexdigest() != receipt['manifest_sha256']:
            raise ValueError('Manifest hash mismatch')
        manifest = json.loads(raw); entries = validate_entries(manifest)
        if [i.filename for i in infos] != [MANIFEST]+[e['path'] for e in entries]:
            raise ValueError('Unexpected/missing archive members')
        for info in infos:
            mode = info.external_attr>>16
            if info.is_dir() or stat.S_IFMT(mode) not in (0,stat.S_IFREG) or info.flag_bits & 1:
                raise ValueError('Nonregular/encrypted archive member')
        for e in entries:
            if z.getinfo(e['path']).file_size != e['bytes']:
                raise ValueError('ZIP member declared size mismatch')
            with z.open(e['path']) as source:
                if hashed_stream(source) != (e['bytes'],e['sha256']):
                    raise ValueError('ZIP member content mismatch')
    return manifest

def restore(path, receipt, target):
    manifest = verify(path,receipt)
    for ancestor in (target,*target.parents):
        if ancestor.is_symlink(): raise ValueError('Symlink target ancestor')
    target = target.resolve(); missing = []; identical = 0
    if target.exists() and not target.is_dir(): raise FileExistsError('Target root is a file')
    for e in manifest['files']:
        rel = safe_path(e['path']); dest = target.joinpath(*rel.parts); current = target
        for index,part in enumerate(rel.parts):
            current = current/part
            if current.is_symlink(): raise ValueError('Symlink destination')
            if index<len(rel.parts)-1 and current.exists() and not current.is_dir():
                raise FileExistsError('Destination parent is a file; nothing restored')
        if dest.exists():
            if not dest.is_file() or hashed(dest)!=(e['bytes'],e['sha256']):
                raise FileExistsError('Existing file differs; nothing restored: '+str(dest))
            identical += 1
        else: missing.append(e)
    with zipfile.ZipFile(path) as z:
        for e in missing:
            dest = target/e['path']; dest.parent.mkdir(parents=True,exist_ok=True)
            with z.open(e['path']) as source,dest.open('xb') as out:
                for block in iter(lambda:source.read(1024*1024),b''):out.write(block)
            if hashed(dest)!=(e['bytes'],e['sha256']):raise ValueError('Restored content mismatch')
    return dict(verified_files=len(manifest['files']),written_files=len(missing),identical_skipped=identical)

def rebuild_check(target):
    target = target.resolve()
    docs = target/'docs/world-components'
    names = ['data.json','data.js']
    before = {name:hashed(docs/name) for name in names}
    run = subprocess.run([sys.executable,str(target/'research/world-components/reader/build_reader.py'),'--require-complete'],cwd=target,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},text=True,capture_output=True,check=True)
    if before != {name:hashed(docs/name) for name in names}:
        raise ValueError('Rebuilt gallery data differs from frozen source/display bindings')
    return dict(rebuild='pass',exact_data_files=names,builder_output=run.stdout.strip())

def create(root, out, count):
    root, out = root.resolve(), out.resolve()
    if out.exists(): raise FileExistsError('Preserve output; choose a new version directory')
    manifest,sources = gather(root,count)
    out.mkdir(parents=True)
    archive = out/'world-components-portable.zip'
    receipt = write_archive(archive,manifest,sources)
    verify(archive,receipt)
    result = restore(archive,receipt,out/'fresh-restoration')
    result.update(rebuild_check(out/'fresh-restoration'))
    for name,value in [('asset-manifest.json',manifest),('archive-receipt.json',receipt),('verification.json',result)]:
        with (out/name).open('xb') as f:f.write(encoded(value))
    print(json.dumps(dict(**receipt,verification=result),indent=2))

def self_test():
    local = HERE/'local'; local.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='security-fixtures-',dir=local))
    sources={}
    for name,body in [('a.txt',b'AAA'),('b.txt',b'BBB')]:
        p=tmp/name;p.write_bytes(body);sources['production/world-components/'+name]=p
    entries=[dict(path=name,bytes=hashed(p)[0],sha256=hashed(p)[1]) for name,p in sorted(sources.items())]
    manifest=dict(files=entries,total_bytes=6);archive=tmp/'good.zip';receipt=write_archive(archive,manifest,sources)
    checks=[]
    def rejects(label,fn,types=(ValueError,FileExistsError)):
        try:fn()
        except types:checks.append(label)
        else:raise AssertionError(label+' accepted')
    target=tmp/'restore';clash=target/'production/world-components/b.txt';clash.parent.mkdir(parents=True);clash.write_bytes(b'BAD')
    rejects('clash preflight',lambda:restore(archive,receipt,target));assert not (clash.parent/'a.txt').exists()
    clash.write_bytes(b'BBB');r=restore(archive,receipt,target);assert r['written_files']==1 and r['identical_skipped']==1
    assert restore(archive,receipt,target)['written_files']==0;checks+=['exact missing restore','identical skip/idempotence']
    for bad in ['../escape','production/world-components/../escape','other/a.png','production/world-components/AUX.txt','production\\world-components\\a','/absolute']:
        rejects('unsafe path '+bad,lambda bad=bad:safe_path(bad))
    rejects('duplicate case collision',lambda:validate_entries(dict(files=entries+[dict(entries[0],path=entries[0]['path'].replace('a.txt','A.txt'))],total_bytes=9)))
    rejects('size limit',lambda:validate_entries(dict(files=[dict(entries[0],bytes=MAX_FILE+1)],total_bytes=MAX_FILE+1)))
    rejects('archive hash mismatch',lambda:verify(archive,dict(receipt,archive_sha256='0'*64)))
    link=tmp/'symlink-target';link.symlink_to(target,target_is_directory=True)
    rejects('target symlink',lambda:restore(archive,receipt,link))
    parent=tmp/'parent-file';parent.mkdir();(parent/'production').write_bytes(b'FILE')
    rejects('parent file',lambda:restore(archive,receipt,parent))
    # Malformed ZIPs use internally consistent receipts to exercise member validation.
    for label,names,mode in [('duplicate archive',[entries[0]['path'],entries[0]['path']],None),('symlink archive',[e['path'] for e in entries],stat.S_IFLNK|0o777),('unexpected member',[e['path'] for e in entries]+['production/world-components/c.txt'],None)]:
        p=tmp/(label.replace(' ','-')+'.zip')
        with zipfile.ZipFile(p,'x') as z:
            z.writestr(MANIFEST,encoded(manifest))
            for name in names:
                info=zipfile.ZipInfo(name);info.create_system=3;info.external_attr=(mode or (stat.S_IFREG|0o644))<<16
                z.writestr(info,b'AAA' if name.endswith('a.txt') else b'BBB')
        size,sha=hashed(p);badreceipt=dict(receipt,archive_bytes=size,archive_sha256=sha)
        rejects(label,lambda p=p,badreceipt=badreceipt:verify(p,badreceipt))
    result=dict(status='pass',checks=checks,fixture_directory=str(tmp.relative_to(ROOT)),production_archive_created=False)
    (tmp/'test-receipt.json').write_bytes(encoded(result));print(json.dumps(result,indent=2))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['create','verify','restore','self-test'])
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--out',type=Path,default=HERE/'local/final-v1')
    parser.add_argument('--expected-art',type=int)
    parser.add_argument('--archive',type=Path)
    parser.add_argument('--receipt',type=Path)
    parser.add_argument('--target',type=Path)
    args=parser.parse_args()
    if args.action=='self-test':self_test();return
    if args.action=='create':create(args.root,args.out,args.expected_art);return
    if not args.archive or not args.receipt:parser.error('--archive and --receipt are required')
    receipt=json.loads(args.receipt.read_text())
    if args.action=='verify':print(json.dumps(dict(verified_files=len(verify(args.archive,receipt)['files']))));return
    if not args.target:parser.error('--target required')
    print(json.dumps(restore(args.archive,receipt,args.target)))

if __name__=='__main__':main()
