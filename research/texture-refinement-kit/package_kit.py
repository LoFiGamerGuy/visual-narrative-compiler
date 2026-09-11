from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[2]
KIT=ROOT/'docs/texture-refinement-kit'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for p in KIT.rglob('*') if p.is_file() and p.name!='MANIFEST.json']
manifest={str(p.relative_to(KIT)):sha(p) for p in sorted(files)}
(KIT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
out=ROOT/'docs/texture-refinement-kit-share.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(KIT.rglob('*')):
        if p.is_file(): z.write(p,'texture-refinement-kit/'+str(p.relative_to(KIT)))
extract=Path(tempfile.mkdtemp(prefix='texture-kit-extracted-'))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    z.extractall(extract)
restored=extract/'texture-refinement-kit'
for path,digest in manifest.items(): assert sha(restored/path)==digest,path
class Links(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['href','src'] and v and not v.startswith('#'):
                assert '://' not in v, f'External dependency: {v}'
                assert (restored/v).is_file(),v
Links().feed((restored/'index.html').read_text())
for record in json.loads((ROOT/'research/texture-refinement-kit/source-baseline.json').read_text()):
    assert sha(Path(record['source']))==record['sha256']
local=Path.home()/'.codex/skills/texture-refinement'
for p in (KIT/'skill/texture-refinement').rglob('*'):
    if p.is_file(): assert sha(p)==sha(local/p.relative_to(KIT/'skill/texture-refinement'))
receipt=dict(zip=str(out),sha256=sha(out),bytes=out.stat().st_size,files=len(manifest)+1,extracted=str(restored),all_extracted_hashes_match=True,local_links_exist=True,source_files_unchanged=True,installed_skill_matches=True)
(ROOT/'research/texture-refinement-kit/package-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
