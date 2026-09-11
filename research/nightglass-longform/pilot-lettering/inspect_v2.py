from PIL import Image,ImageDraw
from pathlib import Path
base=Path(__file__).resolve().parent/'phone-v2';out=base/'inspection';out.mkdir(exist_ok=True)
for series in ['NG','BP','ST','RC','FL']:
 for typ in ['panels','continuous']:
  paths=sorted((base/series).glob(series+'*.png' if typ=='panels' else 'read-*.png'))
  for start in range(0,len(paths),4):
   ims=[Image.open(p).convert('RGB') for p in paths[start:start+4]]
   sheet=Image.new('RGB',(sum(i.width for i in ims),max(i.height for i in ims)+24),'#ddd');d=ImageDraw.Draw(sheet);x=0
   for p,i in zip(paths[start:start+4],ims):d.text((x,3),p.name,fill='black');sheet.paste(i,(x,24));x+=i.width
   sheet.save(out/f'{series}-{typ}-{start//4+1}.jpg',quality=94)
