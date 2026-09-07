"""Validate local HTML links/assets and all new machine-readable JSON; no network requests."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,datetime,hashlib
ROOT=Path.cwd();HUB=ROOT/'docs/research/sequence-pilot'
class Page(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for key in ['href','src']:
            if key in a:self.links.append((tag,key,a[key]))
cache={}
def parse(p):
    if p not in cache:
        x=Page();x.feed(p.read_text());cache[p]=x
    return cache[p]
errors=[];pages=list(HUB.rglob('*.html'))+[ROOT/'production/sequence-pilot/boards/index.html'];links=0
for p in pages:
    x=parse(p)
    if len(set(x.ids))!=len(x.ids):errors.append(str(p.relative_to(ROOT))+': duplicate IDs')
    for tag,key,href in x.links:
        u=urlsplit(href)
        if u.scheme in ['https','http','mailto','data']:continue
        dest=Path(unquote(u.path)) if u.scheme=='file' else (p.parent/unquote(u.path)).resolve() if u.path else p
        links+=1
        if not dest.exists():errors.append(str(p.relative_to(ROOT))+': missing '+href)
        elif u.fragment and dest.suffix=='.html' and unquote(u.fragment) not in parse(dest).ids:errors.append(str(p.relative_to(ROOT))+': missing anchor '+href)
count=0
for base in ['research/sequence-pilot','production/sequence-pilot','docs/research/sequence-pilot']:
    for p in (ROOT/base).rglob('*.json'):
        if '.scratch' in p.parts:continue
        try:json.loads(p.read_text());count+=1
        except Exception as e:errors.append(str(p.relative_to(ROOT))+': '+str(e))
for name in ['index.html','app.js','style.css']:
    if (ROOT/'src/sequence_pilot/web'/name).read_bytes()!=(HUB/'reader'/name).read_bytes():errors.append('Reader frontend differs from source: '+name)
r={'schema':'LocalPackageValidation/1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'html_pages':len(pages),'local_links_checked':links,'json_files_parsed':count,'errors':errors,'pass':not errors}
(ROOT/'research/sequence-pilot/evidence/package-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(0 if r['pass'] else 1)
