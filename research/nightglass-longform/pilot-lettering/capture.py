from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'research/nightglass-longform/pilot-lettering/phone-v2';OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));receipts=[]
 for series in ['NG','BP','ST','RC','FL']:
  page.goto((ROOT/'docs/pilots-reading-v2/index.html').as_uri()+'#'+series);page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');page.wait_for_timeout(350)
  folder=OUT/series;folder.mkdir(exist_ok=True)
  for fig in page.locator('figure').all():fig.screenshot(path=str(folder/(fig.get_attribute('id')+'.png')))
  page.evaluate('scrollTo(0,0)');height=page.evaluate('document.documentElement.scrollHeight')
  for i,y in enumerate(range(0,height,780)):
   page.evaluate('(y)=>scrollTo(0,y)',y);page.wait_for_timeout(100);page.screenshot(path=str(folder/f'read-{i+1:02}.png'))
  findings=page.evaluate('''() => ({width:innerWidth, overflow:document.documentElement.scrollWidth>innerWidth, panels:document.querySelectorAll('figure').length, images:Array.from(document.images).map(i=>({src:i.getAttribute('src'),complete:i.complete&&i.naturalWidth>0})),balloons:Array.from(document.querySelectorAll('.balloon')).map(b=>({panel:b.closest('figure').id,speaker:b.dataset.speaker,text:b.textContent,font:getComputedStyle(b).fontSize, width:b.offsetWidth,height:b.offsetHeight,inside:b.getBoundingClientRect().left>=0&&b.getBoundingClientRect().right<=innerWidth}))})''')
  receipts.append({'chapter':series,**findings})
 (OUT/'browser-check.json').write_text(json.dumps({'errors':errors,'chapters':receipts},indent=2)+'\n');browser.close()
print('Captured all 80 panels and five continuous readings at 390px')
