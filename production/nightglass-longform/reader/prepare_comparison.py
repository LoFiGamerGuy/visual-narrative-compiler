from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
script=ROOT/'production/nightglass-longform/scripts/chapter-1.json';frozen=HERE/'comparison-script.json'
if not frozen.exists():
 d=json.loads(script.read_text());frozen.write_text(json.dumps({'schema':'NightglassFrozenComparisonCopy/1','source_path':str(script.relative_to(ROOT)),'source_sha256':sha(script),'panels':[p for p in d['panels'] if p['id'] in [f'N1-{n}' for n in range(31,37)]]},ensure_ascii=False,indent=2)+'\n')
manifest_path=HERE/'comparison-sources.json';m=json.loads(manifest_path.read_text());methods=m['methods'];crops=HERE/'crops';crops.mkdir(exist_ok=True)
for name,start,boxes in [('C-page-1-R1',31,[(0,0,1024,518),(0,526,1024,1002),(0,1010,1024,1536)]),('C-page-2-P',34,[(0,0,1024,458),(0,466,1024,980),(0,989,1024,1536)])]:
 source=ROOT/f'production/nightglass-longform/comparison/C/candidates/{name}.png'
 if not source.exists():continue
 with Image.open(source) as im:
  for i,box in enumerate(boxes):
   target=crops/f'{name}-N1-{start+i}.png';im.crop(box).save(target)
   methods.setdefault('C',{})[f'N1-{start+i}']={'path':str(target.relative_to(ROOT)),'sha256':sha(target),'attempt_id':f'{name}-tier-{i+1}','crop':{'source_path':str(source.relative_to(ROOT)),'source_sha256':sha(source),'source_dimensions':list(im.size),'box_xyxy':list(box),'operation':'lossless rectangular PNG crop; no scaling, retouching or generated pixels'},'selection_note':'Integrator selected C-page-1-R1 plus C-page-2-P for completed comparison; original pages and primary remain preserved.'}
for method,n,filename in [('B',34,'B34-R1.png'),('A',34,'A-N1-34-R1.png')]:
 p=ROOT/f'production/nightglass-longform/comparison/{method}/candidates/{filename}'
 if p.exists():methods.setdefault(method,{})[f'N1-{n}']={'path':str(p.relative_to(ROOT)),'sha256':sha(p),'attempt_id':p.stem,'selection_note':'Integrator selected structural repair for comparison.'}
manifest_path.write_text(json.dumps(m,indent=2)+'\n')
