"""Package the local review reader with its exact frozen artwork for offline use."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'research/aws-editorial-20260910'
packet=json.loads((AREA/'packet.json').read_text())
out=AREA/'previews/Nightglass-Chapter-1-review.zip'
out.parent.mkdir(exist_ok=True)
files=[ROOT/'docs/nightglass-longform/style.css',ROOT/'docs/nightglass-longform/comic.js']
files += sorted((AREA/'reader').glob('*'))
files += [AREA/name for name in ('revision.json','RESULTS.md','packet.json','revised-packet.json','PROTOCOL.md','LOCAL-INITIAL-READ.md')]
files += [ROOT/'scripts'/name for name in ('build_aws_review_edition.py','capture_aws_review_edition.py','package_aws_review_edition.py')]
for panel in packet['panels']:
    path=ROOT/panel['image_path']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==panel['image_sha256']
    files.append(path)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path,path.relative_to(ROOT))
    archive.writestr('START.html','<!doctype html><meta charset="utf-8"><title>Nightglass Chapter 1</title><meta http-equiv="refresh" content="0;url=research/aws-editorial-20260910/reader/index.html"><a href="research/aws-editorial-20260910/reader/index.html">Read Chapter 1</a>')
    archive.writestr('MANIFEST.json',json.dumps({str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files},indent=2)+'\n')
    archive.writestr('README.txt','Extract the entire ZIP, then open START.html. Original and edited copies are available in the reader navigation. All art is unchanged. Local review draft; owner acceptance is unset.\n')
print(out)
print('bytes',out.stat().st_size,'sha256',hashlib.sha256(out.read_bytes()).hexdigest())
