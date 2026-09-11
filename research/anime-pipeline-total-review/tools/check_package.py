"""Check parseability, local links/fragments, asset references and offline dependencies."""
import datetime,json,re
from pathlib import Path
from urllib.parse import urlsplit,unquote
import markdown
from bs4 import BeautifulSoup
OUT=Path(__file__).resolve().parents[1];WT=OUT.parents[1];DOC=WT/'docs/research/anime-pipeline-total-review'
errors=[];links=0;external=set();cache={};jsons=[];local_targets=set()
files=[*OUT.glob('*.md'),*(OUT/'evidence').glob('*.md'),*DOC.rglob('*.html')]
def soup(p):
 if p not in cache:
  s=p.read_text();cache[p]=BeautifulSoup(markdown.markdown(s,extensions=['tables','fenced_code','toc']) if p.suffix=='.md' else s,'html.parser')
 return cache[p]
for p in OUT.rglob('*.json'):
 if '.scratch' in p.parts:continue
 try:json.loads(p.read_text());jsons.append(str(p.relative_to(WT)))
 except Exception as e:errors.append({'file':str(p),'error':str(e)})
for f in files:
 doc=soup(f)
 for node in doc.select('[href],[src]'):
  attr='href' if node.has_attr('href') else 'src';url=node[attr];parts=urlsplit(url)
  if parts.scheme in ['http','https']:
   external.add(url)
   if node.name!='a':errors.append({'file':str(f),'error':'external runtime dependency','url':url})
   continue
  if parts.scheme in ['data','mailto','javascript']:continue
  raw=re.sub(r':\d+$','',unquote(parts.path));p=Path(raw) if raw.startswith('/') else (f.parent/raw).resolve() if raw else f
  links+=1;local_targets.add(str(p))
  if not p.exists():errors.append({'file':str(f.relative_to(WT)),'error':'missing local path','url':url});continue
  if parts.fragment and p.suffix in ['.html','.md']:
   target=soup(p);frag=unquote(parts.fragment)
   if not target.find(id=frag) and not target.find(attrs={'name':frag}):errors.append({'file':str(f.relative_to(WT)),'error':'missing fragment','url':url})
result={'schema':'PackageChecks/1','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'documents':len(files),'json_parse_count':len(jsons),'local_references_checked':links,'unique_local_targets':len(local_targets),'external_citation_targets':len(external),'external_targets_are_not_revalidated_by_this_local_check':True,'errors':errors,'pass':not errors}
(OUT/'evidence/package-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
raise SystemExit(bool(errors))
