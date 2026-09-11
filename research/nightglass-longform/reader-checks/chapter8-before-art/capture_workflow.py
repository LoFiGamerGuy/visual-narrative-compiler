from pathlib import Path
import json,hashlib,math
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright
R=Path('/mnt/c/AgentWorkspaces/anime-pipeline-nightglass-longform-20260909-2110');O=R/'research/nightglass-longform/reader-checks/chapter8-workflow-reviewed';O.mkdir(exist_ok=True)
snap=R/'production/nightglass-longform/reader/snapshot.json';(O/'reading-snapshot.json').write_bytes(snap.read_bytes());rec={'snapshot_sha256':hashlib.sha256(snap.read_bytes()).hexdigest(),'viewport':[390,844],'individuals':[],'segments':{},'errors':[]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1);page.on('pageerror',lambda e:rec['errors'].append(str(e)));page.goto((R/'docs/nightglass-longform/index.html').as_uri()+'#chapter-8');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');page.add_style_tag(content='html{scroll-behavior:auto!important}');page.wait_for_timeout(200)
 for n in [5,6,7]:
  id=f'N8-{n:02}';f=page.locator(f'figure[id="{id}"]');f.scroll_into_view_if_needed();page.wait_for_timeout(100);f.screenshot(path=str(O/(id+'.png')));rec['individuals'].append(id)
 for name,first,last in [('workflow-04-07','N8-04','N8-07')]:
  out=O/name;out.mkdir(exist_ok=True);bounds=page.evaluate('([a,b])=>({start:document.getElementById(a).getBoundingClientRect().top+scrollY,end:document.getElementById(b).getBoundingClientRect().bottom+scrollY})',[first,last]);start=math.floor(bounds['start']);end=math.floor(bounds['end']);last_y=max(0,end-844);ys=sorted(set(list(range(start,max(start+1,last_y),780))+[last_y])) if end-start>844 else [last_y];frames=[]
  for i,y in enumerate(ys,1):
   page.evaluate('(y)=>scrollTo(0,y)',y);page.wait_for_timeout(100);f=f'read-{i:02}.png';page.screenshot(path=str(out/f));frames.append({'file':f,'requested_y':y,'actual_y':page.evaluate('scrollY')})
  rec['segments'][name]={'first':first,'last':last,'bounds':bounds,'frames':frames}
  for k in range(0,len(frames),4):
   subset=frames[k:k+4];sheet=Image.new('RGB',(390*len(subset),868),'#e9e5db');d=ImageDraw.Draw(sheet)
   for j,fr in enumerate(subset):d.text((j*390+8,5),name+' / '+fr['file'],fill='black');sheet.paste(Image.open(out/fr['file']).convert('RGB'),(j*390,24))
   sheet.save(out/f'inspection-{k//4+1}.jpg',quality=95,subsampling=0)
 rec['broken']=page.evaluate('Array.from(document.images).filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)');rec['overflow']=page.evaluate('document.documentElement.scrollWidth>innerWidth');rec['balloons']=page.evaluate('Array.from(document.querySelectorAll(".balloon")).map(e=>({text:e.textContent,font:getComputedStyle(e).fontSize,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right}))');rec['body_status']=page.locator('body').inner_text()[:600];b.close()
(O/'receipt.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in rec.items() if k!='balloons'},ensure_ascii=False,indent=2))
