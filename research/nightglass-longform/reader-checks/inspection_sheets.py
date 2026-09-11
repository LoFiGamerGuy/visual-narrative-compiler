from PIL import Image,ImageDraw
from pathlib import Path
import sys
base=Path(__file__).resolve().parent/sys.argv[1];out=base/'inspection';out.mkdir(exist_ok=True)
for folder in sorted(p for p in base.iterdir() if p.is_dir() and p.name!='inspection'):
 paths=sorted(folder.glob('read-*.png'))
 for start in range(0,len(paths),4):
  ims=[Image.open(p).convert('RGB') for p in paths[start:start+4]]
  sheet=Image.new('RGB',(sum(i.width for i in ims),max(i.height for i in ims)+24),'#ddd');d=ImageDraw.Draw(sheet);x=0
  for p,i in zip(paths[start:start+4],ims):d.text((x,3),folder.name+' '+p.name,fill='black');sheet.paste(i,(x,24));x+=i.width
  sheet.save(out/f'{folder.name}-{start//4+1}.jpg',quality=94)
