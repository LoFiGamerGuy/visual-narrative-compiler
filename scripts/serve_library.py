#!/usr/bin/env python3
"""Browse the consolidated library and exact historical workspaces on localhost."""
import argparse
from contextlib import closing
from functools import partial
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
import sqlite3
from urllib.parse import unquote, urlsplit
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'research/workspace-consolidation-20260911/inventory.sqlite3'
ALLOWED = {'.html','.css','.js','.mjs','.json','.png','.jpg','.jpeg','.svg','.webp',
           '.gif','.ico','.md','.txt','.pdf','.zip','.gz','.csv','.woff','.woff2','.ttf'}
OLD_ROOT = re.compile(r'(?:file://)?(?:/mnt/c/|/?[Cc]:[/\\])[Aa]gent[Ww]orkspaces[/\\](anime-pipeline(?:-[^/\\\s"\'<>]+)?)[/\\]([^"\'<>\s]*)')

def remap_links(text):
    """Remap browser URLs in the response; preserve historical files on disk."""
    def replace(match):
        name,rest = match.groups()
        rest = rest.replace('\\','/')
        return ('/' if name == 'anime-pipeline' else '/workspaces/'+name+'/') + rest
    return OLD_ROOT.sub(replace,text)

class Library:
    def __init__(self,root=ROOT,inventory=INVENTORY):
        self.root = Path(root).resolve()
        self.inventory = Path(inventory)
        self.mapping = None
        exported = self.inventory.with_name('preservation-map.jsonl.gz')
        if exported.exists():
            with gzip.open(exported,'rt',encoding='utf-8') as stream:
                self.mapping = {(r['workspace'],r['path']):r['destination']
                                for r in map(json.loads,stream)}

    @staticmethod
    def safe(parts):
        return not any(p in ('.','..') or p.startswith('.') for p in parts)

    def resolve(self,url):
        route = unquote(urlsplit(url).path).replace('\\','/').lstrip('/')
        parts = route.split('/')
        if not self.safe(parts):
            return None
        # Old relative sibling links remain useful without sibling directories.
        if parts[0].startswith('anime-pipeline-'):
            parts.insert(0,'workspaces')
        elif parts[0] == 'anime-pipeline':
            parts = parts[1:] or ['']
            route = '/'.join(parts)
        if parts[0] == 'workspaces':
            if len(parts)<3 or (self.mapping is None and not self.inventory.exists()):
                return None
            workspace,rel = parts[1],'/'.join(parts[2:])
            if not rel or rel.endswith('/'):
                rel += 'index.html'
            if self.mapping is not None:
                destination = self.mapping.get((workspace,rel))
            else:
                with closing(sqlite3.connect(f'{self.inventory.as_uri()}?mode=ro',uri=True)) as db:
                    row = db.execute('SELECT destination FROM actions WHERE workspace=? AND path=?',(workspace,rel)).fetchone()
                destination = row[0] if row else None
            if not destination:
                return None
            dest = self.root / destination
        else:
            dest = self.root / route
            if dest.is_dir():
                dest /= 'START-HERE.html' if dest == self.root else 'index.html'
        resolved = dest.resolve()
        if not resolved.is_relative_to(self.root) or resolved.suffix.lower() not in ALLOWED or not resolved.is_file():
            return None
        if not self.safe(resolved.relative_to(self.root).parts):
            return None
        return resolved

class Handler(BaseHTTPRequestHandler):
    def __init__(self,*args,library,**kwargs):
        self.library = library
        super().__init__(*args,**kwargs)

    def do_HEAD(self):
        self.respond(False)

    def do_GET(self):
        self.respond(True)

    def respond(self,body):
        path = self.library.resolve(self.path)
        if path is None:
            self.send_error(404,'Not in the readable library')
            return
        mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        payload = None
        if path.suffix.lower() in ('.html','.js','.mjs'):
            payload = remap_links(path.read_text(encoding='utf-8',errors='replace')).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type',mime + ('; charset=utf-8' if payload is not None else ''))
        self.send_header('Content-Length',str(len(payload) if payload is not None else path.stat().st_size))
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        if body:
            try:
                if payload is not None:
                    self.wfile.write(payload)
                else:
                    with path.open('rb') as source:
                        while chunk := source.read(1024*1024):
                            self.wfile.write(chunk)
            except (BrokenPipeError,ConnectionResetError):
                pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--open',action='store_true',dest='open_browser')
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,library=Library()))
    url = f'http://127.0.0.1:{server.server_port}/START-HERE.html'
    print(f'Library: {url}\nPress Ctrl+C to stop.',flush=True)
    if args.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
