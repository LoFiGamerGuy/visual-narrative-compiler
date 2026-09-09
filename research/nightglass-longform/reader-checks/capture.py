"""Capture actual offline reading at 390px; path argument defaults comparison."""
from pathlib import Path
import json,sys,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];mode=sys.argv[1] if len(sys.argv)>1 else 'comparison';stamp=sys.argv[2] if len(sys.argv)>2 else 'draft';OUT=ROOT/'research/nightglass-longform/reader-checks'/stamp;OUT.mkdir(exist_ok=True)
snapshot=json.loads((ROOT/'production/nightglass-longform/reader/snapshot.json').read_text());ids=[c['id'] for c in snapshot['comparisons' if mode=='comparison' else 'chapters']]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));receipts=[]
 for id in ids:
  page.goto((ROOT/'docs/nightglass-longform'/('comparison.html' if mode=='comparison' else 'index.html')).as_uri()+'#'+id);page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');page.add_style_tag(content='html{scroll-behavior:auto!important}');page.wait_for_timeout(300);folder=OUT/id;folder.mkdir(exist_ok=True)
  for f in page.locator('figure').all():f.scroll_into_view_if_needed();page.wait_for_timeout(120);f.screenshot(path=str(folder/(f.get_attribute('id')+'.png')))
  height=page.evaluate('document.documentElement.scrollHeight')
  for i,y in enumerate(range(0,height,780)):
   page.evaluate('(y)=>scrollTo(0,y)',y);page.wait_for_timeout(120);page.screenshot(path=str(folder/f'read-{i+1:02}.png'))
  receipts.append(page.evaluate('''() => ({hash:location.hash,images:document.images.length,broken:Array.from(document.images).filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),overflow:document.documentElement.scrollWidth>innerWidth,balloons:Array.from(document.querySelectorAll('.balloon')).map(b=>({panel:b.closest('figure').id,text:b.textContent,font:getComputedStyle(b).fontSize,inside:b.getBoundingClientRect().left>=0&&b.getBoundingClientRect().right<=innerWidth}))})'''))
 browser.close()
(OUT/'receipt.json').write_text(json.dumps({'mode':mode,'errors':errors,'readings':receipts,'snapshot_sha256':hashlib.sha256((ROOT/'production/nightglass-longform/reader/snapshot.json').read_bytes()).hexdigest()},indent=2)+'\n')
print('Captured',mode,ids,stamp)
