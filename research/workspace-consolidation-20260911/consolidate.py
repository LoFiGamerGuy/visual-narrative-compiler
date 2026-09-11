#!/usr/bin/env python3
"""One-off, resumable local consolidation; no uploads or artwork generation.

Audit hashes every sibling file, including ignored files. Plan retains one current
path and stores conflicting bytes once under archive/workspace-variants. Execute
checks source identity before each action and destination identity after moving.
Git registrations are retired separately, after verification.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DB = HERE / 'inventory.sqlite3'
GIT_EXE = r'C:\Program Files\Git\cmd\git.exe' if os.name == 'nt' else 'git'

def read_link(path, info=None):
    info = info or path.lstat()
    if stat.S_ISLNK(info.st_mode):
        return os.readlink(path)
    # Windows Python does not classify WSL's LX_SYMLINK reparse points.
    if os.name == 'nt' and getattr(info, 'st_reparse_tag', 0) == 0xA000001D:
        import ctypes
        from ctypes import wintypes
        api = ctypes.WinDLL('kernel32',use_last_error=True)
        api.CreateFileW.argtypes = [wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
        api.CreateFileW.restype = wintypes.HANDLE
        api.DeviceIoControl.argtypes = [wintypes.HANDLE,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD),ctypes.c_void_p]
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = api.CreateFileW(str(path),0,7,None,3,0x02200000,None)
        if handle == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            buffer = ctypes.create_string_buffer(16384)
            used = wintypes.DWORD()
            if not api.DeviceIoControl(handle,0x000900A8,None,0,buffer,len(buffer),ctypes.byref(used),None):
                raise ctypes.WinError(ctypes.get_last_error())
            return buffer.raw[12:used.value].decode('utf-8')
        finally:
            api.CloseHandle(handle)
    return None

def digest(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def git(*args):
    return subprocess.check_output([GIT_EXE, '-C', str(ROOT), *args], text=True).strip()

def audit():
    if (HERE/'verification.json').exists():
        raise RuntimeError('Completed preservation inventory: audit must not overwrite it')
    db = sqlite3.connect(DB)
    db.execute('CREATE TABLE IF NOT EXISTS files (workspace TEXT, path TEXT, size INTEGER, mtime INTEGER, sha TEXT, mode INTEGER, link TEXT, PRIMARY KEY(workspace,path))')
    workspaces = sorted(p for p in ROOT.parent.glob('anime-pipeline-*') if p.is_dir())
    metadata = []
    for ws in workspaces:
        gitfile = (ws / '.git').read_text().strip()
        raw = gitfile.removeprefix('gitdir: ')
        raw = raw.replace('/mnt/c/', 'C:/') if os.name == 'nt' else raw.replace('C:/', '/mnt/c/')
        gd = Path(raw)
        args = [GIT_EXE, f'--git-dir={gd}', f'--work-tree={ws}']
        run = lambda *a: subprocess.check_output(args + list(a), text=True).strip()
        metadata.append(dict(name=ws.name, head=run('rev-parse','HEAD'), branch=run('symbolic-ref','--short','HEAD'), gitfile=gitfile, status=run('status','--porcelain=v1','--untracked-files=all').splitlines()))
        existing = {r[0]:r[1:] for r in db.execute('SELECT path,size,mtime FROM files WHERE workspace=?',(ws.name,))}
        pending = []
        for parent, dirs, files in os.walk(ws, followlinks=False):
            for d in list(dirs):
                if read_link(Path(parent)/d) is not None:
                    dirs.remove(d)
                    files.append(d)
            for name in files:
                path = Path(parent)/name
                rel = path.relative_to(ws).as_posix()
                if rel == '.git':
                    continue
                s = path.lstat()
                if existing.get(rel) == (s.st_size,s.st_mtime_ns):
                    continue
                pending.append((path,rel,s))
        def measure(item):
            path,rel,s = item
            link = read_link(path,s)
            if not link and not stat.S_ISREG(s.st_mode):
                raise RuntimeError(f'Unsupported file: {path}')
            sha = hashlib.sha256(os.fsencode(link)).hexdigest() if link else digest(path)
            after = path.lstat()
            if (s.st_size,s.st_mtime_ns) != (after.st_size,after.st_mtime_ns):
                raise RuntimeError(f'Changed during audit: {path}')
            return (ws.name,rel,s.st_size,s.st_mtime_ns,sha,s.st_mode,link)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for n,row in enumerate(pool.map(measure,pending),1):
                db.execute('INSERT OR REPLACE INTO files VALUES(?,?,?,?,?,?,?)',row)
                if n % 2000 == 0:
                    db.commit()
                    print(f'hashed {ws.name}: {n}/{len(pending)}',flush=True)
        db.commit()
        count,size = db.execute('SELECT count(*),sum(size) FROM files WHERE workspace=?',(ws.name,)).fetchone()
        print(f'audited {ws.name}: {count} files, {size:,} bytes',flush=True)
    (HERE/'workspaces.json').write_text(json.dumps(metadata,indent=2)+'\n')
    db.close()

def plan():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute('CREATE TABLE IF NOT EXISTS actions (workspace TEXT,path TEXT,destination TEXT,action TEXT,sha TEXT,size INTEGER,done INTEGER DEFAULT 0,PRIMARY KEY(workspace,path))')
    if db.execute('SELECT count(*) FROM actions').fetchone()[0]:
        raise RuntimeError('Existing plan: do not overwrite execution evidence')
    canonical = {}
    by_hash = {}
    rows = list(db.execute("SELECT * FROM files ORDER BY CASE WHEN workspace LIKE '%nightglass-longform%' THEN 0 WHEN workspace LIKE '%aws-editorial%' THEN 1 ELSE 2 END, workspace DESC,path"))
    for n,r in enumerate(rows,1):
        rel,sha,link = r['path'],r['sha'],r['link']
        key = rel.casefold()
        if key not in canonical:
            target = ROOT/rel
            if os.path.lexists(target):
                current_link = read_link(target)
                if target.is_dir() and not current_link:
                    raise RuntimeError(f'File/directory collision: {rel}')
                canonical[key] = (rel,hashlib.sha256(os.fsencode(current_link)).hexdigest() if current_link else digest(target), current_link)
                by_hash.setdefault((canonical[key][1],current_link),rel)
            else:
                canonical[key] = (rel,sha,link)
                by_hash.setdefault((sha,link),rel)
                db.execute('INSERT INTO actions(workspace,path,destination,action,sha,size) VALUES(?,?,?,?,?,?)',(r['workspace'],rel,rel,'move',sha,r['size']))
                continue
        kept = canonical[key]
        if (sha,link) == (kept[1],kept[2]):
            dest,action = kept[0],'duplicate'
        elif (sha,link) in by_hash:
            dest,action = by_hash[(sha,link)],'duplicate-variant'
        else:
            dest = f'archive/workspace-variants/{sha[:2]}/{sha}/{Path(rel).name}'
            if (ROOT/dest).exists():
                raise RuntimeError(f'Unexpected existing archive: {dest}')
            action = 'preserve-variant'
            by_hash[(sha,link)] = dest
        db.execute('INSERT INTO actions(workspace,path,destination,action,sha,size) VALUES(?,?,?,?,?,?)',(r['workspace'],rel,dest,action,sha,r['size']))
        if n % 10000 == 0:
            print(f'planned {n}/{len(rows)}',flush=True)
    db.commit()
    summary = [dict(r) for r in db.execute('SELECT action,count(*) AS files,sum(size) AS bytes FROM actions GROUP BY action')]
    (HERE/'plan-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)

def identity(path,sha,link):
    if not os.path.lexists(path):
        return False
    if link is not None:
        return read_link(path) == link
    return path.is_file() and not path.is_symlink() and digest(path) == sha

def execute():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = list(db.execute('SELECT a.*,f.link FROM actions a JOIN files f USING(workspace,path) ORDER BY a.rowid'))
    log = open(HERE/'execution.jsonl','a',buffering=1)
    for n,r in enumerate(rows,1):
        if r['done']:
            continue
        source = ROOT.parent/r['workspace']/r['path']
        dest = ROOT/r['destination']
        if not os.path.lexists(source):
            if not identity(dest,r['sha'],r['link']):
                raise RuntimeError(f'Missing source and unverified target: {source}')
        else:
            if not identity(source,r['sha'],r['link']):
                raise RuntimeError(f'Source changed: {source}')
            if r['action'] in ('move','preserve-variant'):
                if os.path.lexists(dest):
                    raise RuntimeError(f'Refusing overwrite: {dest}')
                dest.parent.mkdir(parents=True,exist_ok=True)
                source.rename(dest)
                if not identity(dest,r['sha'],r['link']):
                    raise RuntimeError(f'Move verification failed: {dest}')
            else:
                if not identity(dest,r['sha'],r['link']):
                    raise RuntimeError(f'Duplicate target changed: {dest}')
                try:
                    source.unlink()
                except PermissionError:
                    info = source.lstat()
                    if os.name != 'nt' or not (getattr(info,'st_file_attributes',0) & stat.FILE_ATTRIBUTE_READONLY):
                        raise
                    # Only the already-verified redundant copy loses readonly.
                    os.chmod(source,stat.S_IWRITE)
                    source.unlink()
        log.write(json.dumps(dict(r),separators=(',',':'))+'\n')
        db.execute('UPDATE actions SET done=1 WHERE workspace=? AND path=?',(r['workspace'],r['path']))
        if n % 1000 == 0:
            db.commit()
            print(f'consolidated {n}/{len(rows)}',flush=True)
    db.commit()
    log.close()
    print('All planned files consolidated. Verify before retiring registrations.',flush=True)

def verify():
    db = sqlite3.connect(DB)
    rows = db.execute('SELECT DISTINCT a.destination,a.sha,f.link FROM actions a JOIN files f USING(workspace,path)').fetchall()
    def check(r):
        path,sha,link = r
        if not identity(ROOT/path,sha,link):
            raise RuntimeError(f'Preservation check failed: {path}')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for _ in pool.map(check,rows):
            pass
    sources = db.execute('SELECT count(*),sum(size) FROM files').fetchone()
    result = dict(verified_at=time.strftime('%Y-%m-%dT%H:%M:%S%z'),source_files=sources[0],source_bytes=sources[1],verified_destinations=len(rows),remaining_actions=db.execute('SELECT count(*) FROM actions WHERE done=0').fetchone()[0],failures=0)
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['audit','plan','execute','verify'])
    args = parser.parse_args()
    globals()[args.command]()
