import hashlib,json,sys
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[5];folder=Path(__file__).resolve().parents[1]
aid=sys.argv[1];boxes=json.loads(sys.argv[2]);source=folder/'candidates'/f'{aid}.png';im=Image.open(source)
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
records_path=folder/'notes/selected-records.json';out=json.loads(records_path.read_text()) if records_path.exists() else {'selected':{},'status':'worker recommendations for lead integration; shared selection not mutated'}
for panel,box in boxes.items():
 target=folder/'crops'/f'{panel}.png';assert not target.exists();im.crop(box).save(target)
 out['selected'][panel]={'path':target.relative_to(root).as_posix(),'sha256':h(target),'attempt_id':aid,'crop':{'source_path':source.relative_to(root).as_posix(),'source_sha256':h(source),'source_dimensions':list(im.size),'box_xyxy':box,'operation':'lossless rectangular PNG crop; no scaling or retouch'}}
records_path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
