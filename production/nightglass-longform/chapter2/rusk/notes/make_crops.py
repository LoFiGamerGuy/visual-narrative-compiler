import hashlib,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[5]; folder=Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
source=folder/'candidates/N2-17-19-R1.png'; im=Image.open(source)
records=[]
for panel,box in [('N2-17',(0,0,1024,543)),('N2-18',(0,545,1024,1005)),('N2-19',(0,1007,1024,1536))]:
 target=folder/'crops'/f'{panel}.png';assert not target.exists();im.crop(box).save(target)
 records.append({'id':panel,'path':target.relative_to(root).as_posix(),'sha256':digest(target),'width':box[2]-box[0],'height':box[3]-box[1],'attempt_id':'N2-17-19-R1','source_path':source.relative_to(root).as_posix(),'source_sha256':digest(source),'xyxy':box,'derivative':'native pixel crop, right/bottom exclusive; no repair or resizing'})
ref=folder/'references/rusk-character-from-N2-18.png';box=(560,548,973,1004);assert not ref.exists();im.crop(box).save(ref)
character={'path':ref.relative_to(root).as_posix(),'sha256':digest(ref),'source_path':source.relative_to(root).as_posix(),'source_sha256':digest(source),'xyxy':box,'width':413,'height':456,'identity':'Rusk: middle-aged olive-brown man, short dark curls silvered at temples, salt-and-pepper square beard, thick brows, ochre rolled-sleeve work shirt, blue canvas apron with brass rivets and breast pocket. No eyewear.','derivative':'Unaltered native pixel crop; right/bottom exclusive.'}
(folder/'references/rusk-character.json').write_text(json.dumps(character,indent=2)+'\n')
native16=folder/'candidates/N2-16-R1.png'
records.insert(0,{'id':'N2-16','path':native16.relative_to(root).as_posix(),'sha256':digest(native16),'width':1536,'height':1024,'attempt_id':'N2-16-R1','derivative':None})
(folder/'notes/recommended-crops.json').write_text(json.dumps({'panels':records,'character_reference':character},indent=2)+'\n')
print(json.dumps({'panels':records,'character_reference':character},indent=2))
