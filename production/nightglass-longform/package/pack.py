#!/usr/bin/env python3
"""Versioned, exact-byte offline comic snapshots. Standard library only."""
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import unquote, urlsplit
import zipfile

READER_ROOTS = ('docs/nightglass-longform', 'docs/pilots-reading-v2', 'docs/pilot-chapters')
SEED_ROOTS = (*READER_ROOTS, 'production/nightglass-longform', 'production/pilots-reading-v2',
              'production/pilot-chapters', 'research/nightglass-longform', 'research/pilot-chapters',
              'docs/texture-refinement-kit/skill/texture-refinement')
EXTRA_FILES = ('AGENTS.md', 'research/anchor-return/PIPELINE.md', 'research/anchor-return/RESULTS.md',
               'docs/texture-refinement-kit/GUIDE.md', 'docs/texture-refinement-kit/skill/texture-refinement/SKILL.md')
EXTENSIONS = {'.html','.css','.js','.json','.md','.txt','.sha256','.png','.jpg','.jpeg','.webp','.svg','.py','.cmd','.ps1','.yaml'}
BLOCK_PARTS = {'.git','.venv','venv','node_modules','__pycache__','.cache','cache','caches','.scratch','local','tmp','tools'}
BUILD_PREFIXES = ('production/nightglass-longform/package/builds/', 'production/nightglass-longform/package/output/')
REPORT_PREFIX = 'research/nightglass-longform/assets/package/'
FIXED_ZIP_TIME = (2026,9,9,0,0,0)

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def allowed(relative):
    p=Path(relative)
    return (not relative.startswith((*BUILD_PREFIXES,REPORT_PREFIX)) and
            not any(part in BLOCK_PARTS or part.startswith('.') for part in p.parts) and
            p.suffix.lower() in EXTENSIONS and p.name.lower() not in {'credentials.json','secrets.json','tokens.json'})

def inside(root, value, base=None):
    """Return repository-relative local file path; never follow external origins."""
    if not isinstance(value,str) or len(value)>4096 or '\n' in value:
        return None
    try: parsed=urlsplit(value)
    except ValueError: return None
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    value=unquote(parsed.path)
    if value.startswith(('production/','research/','docs/')):
        path=root/value
    elif value.startswith(str(root)+'/'):
        path=Path(value)
    elif base is not None and not value.startswith('/'):
        path=base/value
    else:
        return None
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return None

class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in {'href','src'} and value:
                self.links.append(value)

def json_paths(root, value):
    if isinstance(value,dict):
        for item in value.values():
            yield from json_paths(root,item)
    elif isinstance(value,list):
        for item in value:
            yield from json_paths(root,item)
    elif isinstance(value,str):
        relative=inside(root,value)
        if relative:
            yield relative

def collect(root):
    files=set(); missing=[]; archival=[]; reader_edges=[]
    for folder in SEED_ROOTS:
        # Old deliveries/extractions are excluded from this snapshot. Prune
        # their directories before walking, rather than visiting every old
        # file and rejecting it afterward (especially costly on mounted NTFS).
        for directory, directories, names in os.walk(root/folder, followlinks=False):
            parent=Path(directory)
            directories[:]=[name for name in directories
                            if name not in BLOCK_PARTS and not name.startswith('.')
                            and not ((parent/name).relative_to(root).as_posix()+'/').startswith((*BUILD_PREFIXES,REPORT_PREFIX))]
            for name in names:
                path=parent/name;relative=path.relative_to(root).as_posix()
                if allowed(relative) and path.is_file():
                    if path.is_symlink():
                        raise RuntimeError(f'Symlink refused: {path}')
                    files.add(relative)
    for relative in EXTRA_FILES:
        if (root/relative).is_file(): files.add(relative)
    pending=list(sorted(files)); checked=set()
    while pending:
        relative=pending.pop()
        if relative in checked: continue
        checked.add(relative); path=root/relative; dependencies=[]
        is_reader=any(relative.startswith(folder+'/') for folder in READER_ROOTS)
        if path.suffix=='.json':
            try: dependencies=list(json_paths(root,json.loads(path.read_text(encoding='utf-8'))))
            except (json.JSONDecodeError,UnicodeError): continue
        elif is_reader and path.suffix=='.js' and path.name=='data.js':
            text=path.read_text(encoding='utf-8'); start=text.find('=')
            try: dependencies=list(json_paths(root,json.loads(text[start+1:].strip().rstrip(';'))))
            except json.JSONDecodeError: continue
        elif is_reader and path.suffix in {'.html','.css'}:
            text=path.read_text(encoding='utf-8')
            if path.suffix=='.html':
                parser=HTMLLinks();parser.feed(text); links=parser.links
            else: links=re.findall(r'url\([\s\"\']*([^\)\"\']+)',text)
            for link in links:
                target=inside(root,link,path.parent)
                if target:
                    dependencies.append(target);reader_edges.append({'from':relative,'to':target})
        for target in sorted(set(dependencies)):
            if not allowed(target): continue
            if (root/target).is_file():
                if (root/target).is_symlink(): raise RuntimeError(f'Symlink dependency refused: {target}')
                if target not in files: files.add(target);pending.append(target)
            else:
                record={'from':relative,'path':target}
                if is_reader or relative.startswith(('production/nightglass-longform/','production/pilots-reading-v2/')):
                    missing.append(record)
                else: archival.append(record)
    return dict(files=sorted(files),required_missing=missing,archival_missing=archival,
                reader_edges=reader_edges,total_bytes=sum((root/f).stat().st_size for f in files))

def gate(root,milestone):
    snapshot=json.loads((root/'production/nightglass-longform/reader/snapshot.json').read_text())
    chapters=[{key:c.get(key) for key in ('number','title','available','total','complete')} for c in snapshot['chapters']]
    required={'trial':[], 'chapter1':[1], 'threechapters':[1,2,3], 'fourchapters':[1,2,3,4], 'fivechapters':[1,2,3,4,5], 'sixchapters':[1,2,3,4,5,6]}[milestone]
    for number in required:
        chapter=next((c for c in snapshot['chapters'] if c['number']==number),None)
        if not chapter or not chapter.get('complete') or chapter['available']!=chapter['total']:
            raise RuntimeError(f'Chapter {number} is not a complete reviewed reader snapshot')
    if snapshot.get('source_issues'): raise RuntimeError('Reader snapshot has source issues')
    edition=json.loads((root/'production/pilots-reading-v2/edition.json').read_text())
    if len(edition.get('panels',[]))!=80: raise RuntimeError('Expected all 80 revised pilot panels')
    return chapters

def starter(version,milestone,chapters):
    label={'trial':'TRIAL — moving production snapshot','chapter1':'Chapter 1 milestone; later chapters may be drafts','threechapters':'Three-chapter development delivery','fourchapters':'Four-chapter development delivery','fivechapters':'Five-chapter development delivery','sixchapters':'Six-chapter development delivery'}[milestone]
    items=''.join(f"<li>Chapter {c['number']}: {html.escape(c['title'])} — {c['available']}/{c['total']} illustrated panels; {'reviewed complete' if c['complete'] else 'incomplete preview'}</li>" for c in chapters)
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nightglass Courier — Start here</title><style>body{{margin:3rem auto;padding:0 1.2rem;max-width:42rem;background:#0b1625;color:#f7f2e8;font:18px/1.55 Georgia,serif}}a{{color:#9ee4ed}}li{{margin:.6rem 0}}small{{color:#bdc9d4}}</style><h1>Nightglass Courier</h1><p>{html.escape(label)}</p><p><a href="docs/nightglass-longform/index.html">Read Nightglass Courier →</a></p><p><a href="docs/pilots-reading-v2/index.html">Read the five revised opening stories →</a></p><ul>{items}</ul><p><a href="docs/nightglass-longform/comparison.html">Six-beat continuity comparison</a> · <a href="docs/pilot-chapters/index.html">Preserved original pilots and nine-path library</a></p><p><a href="docs/nightglass-longform/review.html">Edition notes and native sources</a> · <a href="PACKAGE-STATUS.md">Package scope</a> · <a href="PACKAGE-MANIFEST.json">Exact file inventory</a></p><small>Version {html.escape(version)}. Open locally; no server, installation or internet is needed. Extract the ZIP before reading. This development edition does not claim human acceptance or publication.</small></html>'''

def build(root,version,milestone,output):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,95}',version): raise RuntimeError('Use a plain version label')
    chapters=gate(root,milestone); plan=collect(root)
    if plan['required_missing']: raise RuntimeError('Required dependencies missing: '+json.dumps(plan['required_missing']))
    free=shutil.disk_usage(output if output.exists() else root).free
    reserve=plan['total_bytes']*4+512*1024*1024
    if free<reserve: raise RuntimeError(f'Insufficient room for staging, ZIP, and independent extraction: {free} available, {reserve} reserved')
    target=output/version; archive=output/(version+'.zip')
    if target.exists() or archive.exists(): raise RuntimeError('Version already exists; previous artifacts are never overwritten')
    output.mkdir(parents=True,exist_ok=True);target.mkdir()
    records=[]
    try:
        for relative in plan['files']:
            source=root/relative; dest=target/relative
            before=source.stat();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
            after=source.stat()
            if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns): raise RuntimeError(f'Source changed while copied: {relative}')
            copied_hash=digest(dest)
            if copied_hash!=digest(source): raise RuntimeError(f'Copy mismatch/source changed: {relative}')
            records.append({'path':relative,'bytes':dest.stat().st_size,'sha256':copied_hash})
        # Freeze every included file, even if production continued while earlier copies ran.
        for record in records:
            if digest(root/record['path'])!=record['sha256']: raise RuntimeError(f'Source changed during snapshot: {record["path"]}')
        again=collect(root)
        if again['files']!=plan['files']: raise RuntimeError('Source dependency inventory changed during snapshot')
        print(json.dumps({'event':'source-snapshot-frozen','version':version,'files':len(records),'source_bytes':plan['total_bytes'],'target':str(target)}),flush=True)
        (target/'START-HERE.html').write_text(starter(version,milestone,chapters),encoding='utf-8')
        (target/'OPEN-COMIC.cmd').write_bytes(b'@echo off\r\nstart "" "%~dp0START-HERE.html"\r\n')
        status=f'# {version}\n\nMilestone: {milestone}.\n\n'+('\n'.join(f"- Chapter {c['number']}: {c['available']}/{c['total']} panels, reviewed_complete={c['complete']}" for c in chapters))+'\n\nAll revised pilots, historical nine-path library, new attempts, editable scripts/lettering and recorded relative source dependencies are included. Absolute paths in historical tool records describe original execution locations; they are not reader links. Historical research records retain references to intermediate captures and legacy duplicate paths that were not dependencies of the preserved reader; those missing historical paths are explicitly listed in PACKAGE-MANIFEST.json. No credentials, caches, installed tools or neighboring worktrees are included. Owner acceptance and publication remain unclaimed.\n\nOpen START-HERE.html or OPEN-COMIC.cmd after extracting this ZIP. Package browser verification is recorded separately against the exact ZIP SHA-256.\n'
        (target/'PACKAGE-STATUS.md').write_text(status,encoding='utf-8')
        # Manifest includes generated entry files, excluding itself to avoid circular hashing.
        for name in ('START-HERE.html','OPEN-COMIC.cmd','PACKAGE-STATUS.md'):
            f=target/name;records.append({'path':name,'bytes':f.stat().st_size,'sha256':digest(f)})
        manifest={'schema':'NightglassOfflinePackage/1','version':version,'milestone':milestone,
                  'chapters':chapters,'files':sorted(records,key=lambda r:r['path']),
                  'required_missing':[],'archival_missing':plan['archival_missing'],
                  'native_bytes_policy':'Unchanged native tool-return PNGs plus separately marked pixel crops; regular copies only.',
                  'zip_policy':'Sorted entries, fixed timestamp, deflate level 6; unchanged inputs and label reproduce ZIP bytes.'}
        (target/'PACKAGE-MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
            for path in sorted(p for p in target.rglob('*') if p.is_file()):
                info=zipfile.ZipInfo(version+'/'+path.relative_to(target).as_posix(),FIXED_ZIP_TIME)
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                with path.open('rb') as src,z.open(info,'w',force_zip64=True) as dst: shutil.copyfileobj(src,dst)
        with zipfile.ZipFile(archive) as z:
            bad=z.testzip()
            if bad: raise RuntimeError(f'ZIP CRC failed: {bad}')
        receipt={'version':version,'milestone':milestone,'directory':str(target),'zip':str(archive),
                 'zip_sha256':digest(archive),'file_count':len(records)+1,'source_bytes':plan['total_bytes'],
                 'zip_bytes':archive.stat().st_size,'free_bytes_before_build':free,'reserved_bytes':reserve,'browser_verification':'not yet run'}
        (output/(version+'-build.json')).write_text(json.dumps(receipt,indent=2)+'\n')
        return receipt
    except Exception as error:
        (target/'BUILD-FAILED.txt').write_text(str(error)+'\nThis incomplete attempt is retained; use a new version label.\n')
        raise

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['plan','build'])
    parser.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--version');parser.add_argument('--milestone',choices=['trial','chapter1','threechapters','fourchapters','fivechapters','sixchapters'],default='trial')
    parser.add_argument('--output',type=Path);parser.add_argument('--plan-report',type=Path)
    args=parser.parse_args();root=args.source.resolve()
    if args.command=='plan':
        result=collect(root)
        if args.plan_report:
            args.plan_report.parent.mkdir(parents=True,exist_ok=True);args.plan_report.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'files':len(result['files']), 'total_bytes':result['total_bytes'], 'required_missing':result['required_missing'], 'archival_missing_count':len(result['archival_missing']), 'plan_report':str(args.plan_report) if args.plan_report else None},indent=2))
    else:
        if not args.version: parser.error('--version is required for build')
        print(json.dumps(build(root,args.version,args.milestone,(args.output or root/'production/nightglass-longform/package/output').resolve()),indent=2))

if __name__=='__main__': main()
