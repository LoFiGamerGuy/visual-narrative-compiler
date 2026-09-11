from PIL import Image,ImageDraw
from pathlib import Path
import json
root=Path(__file__).resolve().parents[3]
base=Path('/mnt/c/AgentWorkspaces/anime-pipeline-pilot-chapters-20260909-1310')
out=root/'research/nightglass-longform/pilot-lettering/baseline-inspection';out.mkdir(parents=True,exist_ok=True)
sel=json.load(open(base/'production/pilot-chapters/selected.json'))['selected']
for series in ['NG','BP','ST','RC','FL']:
 for typ in ['readthrough','native']:
  paths=sorted((base/f'research/pilot-chapters/reader/phone-captures/final-v1/{series}-readthrough').glob('*.png')) if typ=='readthrough' else [base/f'production/pilot-chapters/candidates/{sel[series+str(i).zfill(2)]}.png' for i in range(1,17)]
  for start in range(0,len(paths),4):
   ims=[Image.open(p).convert('RGB') for p in paths[start:start+4]]
   if typ=='native':
    for i in ims:i.thumbnail((390,590))
   sheet=Image.new('RGB',(sum(i.width for i in ims),max(i.height for i in ims)+25),'#ddd');x=0;d=ImageDraw.Draw(sheet)
   for p,i in zip(paths[start:start+4],ims):d.text((x,3),series+' '+p.name,fill='black');sheet.paste(i,(x,25));x+=i.width
   sheet.save(out/f'{series}-{typ}-{start//4+1}.jpg',quality=94)
