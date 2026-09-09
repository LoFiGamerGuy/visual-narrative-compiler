"""Capture specified story panels at 390px after native loading; output folder then panel ids."""
from pathlib import Path
import sys,json,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent/sys.argv[1];out.mkdir(exist_ok=True)
ids=sys.argv[2:]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1);page.goto((ROOT/'docs/nightglass-longform/index.html').as_uri());page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)');page.add_style_tag(content='html{scroll-behavior:auto!important}');page.wait_for_timeout(200)
 for id in ids:
  f=page.locator('figure[id="'+id+'"]');f.scroll_into_view_if_needed();page.wait_for_timeout(250);f.screenshot(path=str(out/(id+'.png')))
 browser.close()
(out/'capture-record.json').write_text(json.dumps({'panels':ids,'viewport':[390,844],'snapshot_sha256':hashlib.sha256((ROOT/'production/nightglass-longform/reader/snapshot.json').read_bytes()).hexdigest()},indent=2)+'\n')
