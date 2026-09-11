from pathlib import Path
import json,hashlib
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/'research/aws-editorial-20260910/previews/revised';out.mkdir(exist_ok=True,parents=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((root/'research/aws-editorial-20260910/reader/index.html').as_uri());page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');page.add_style_tag(content='html{scroll-behavior:auto!important}')
 for f in page.locator('figure').all():f.screenshot(path=str(out/(f.get_attribute('id')+'.png')))
 receipt=page.evaluate('''() => ({images:document.images.length,overflow:document.documentElement.scrollWidth>innerWidth,balloons:Array.from(document.querySelectorAll('.balloon')).map(b=>({panel:b.closest('figure').id,text:b.textContent,font:getComputedStyle(b).fontSize,inside:b.getBoundingClientRect().left>=0&&b.getBoundingClientRect().right<=innerWidth}))})''');receipt['errors']=errors
 receipt['edition']='revised';receipt['viewport']={'width':390,'height':844}
 receipt['revised_packet_sha256']=hashlib.sha256((root/'research/aws-editorial-20260910/revised-packet.json').read_bytes()).hexdigest()
 assert receipt['images']==48 and not receipt['overflow'] and not errors
 assert all(b['inside'] for b in receipt['balloons'])
 receipt['additional_widths']=[]
 for width in (320,430,1024):
  page.set_viewport_size({'width':width,'height':844});page.wait_for_timeout(100)
  check=page.evaluate('''() => ({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,offscreen:Array.from(document.querySelectorAll('.balloon')).filter(b=>b.getBoundingClientRect().left<0||b.getBoundingClientRect().right>innerWidth).length})''')
  assert not check['overflow'] and check['offscreen']==0
  receipt['additional_widths'].append(check)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');browser.close();print('Captured',receipt['images'],'panels; overflow:',receipt['overflow'],'errors:',errors)
