"""Arrange existing package QA captures in HTML; originals are never changed."""
import asyncio
import html
import json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(__file__).resolve().parent
QA = BASE / 'Nightglass-ThreeChapters-v1-verification'
SHOTS = QA / 'phone-390'
OUT = BASE / 'Nightglass-ThreeChapters-v1-capture-review'

async def main():
    receipt = json.loads((QA / 'verification.json').read_text())
    if OUT.exists():
        raise RuntimeError('Refusing to overwrite prior capture review')
    OUT.mkdir()
    captures = sorted(SHOTS.glob('*.png'))
    if not captures:
        raise RuntimeError('No actual package screenshots found')
    groups = [(f'chapter-{i}', [SHOTS / f'chapter-{i}-{part}.png' for part in ['top','middle','end']]) for i in [1,2,3]]
    groups += [('entry-and-reviews',[SHOTS / f'{name}-top.png' for name in ['start','nightglass-review','pilot-review']])]
    for label, members in groups:
        if not all(p.is_file() for p in members):
            raise RuntimeError(f'Missing actual screenshot for {label}')
    items = [{'path':str(p), 'relative_path':'../Nightglass-ThreeChapters-v1-verification/phone-390/'+p.name} for p in captures]
    (OUT / 'capture-paths.json').write_text(json.dumps({'zip_sha256':receipt.get('zip_sha256'), 'original_captures':items},indent=2)+'\n')
    links = ''.join(f'<li><a href="{html.escape(x["relative_path"])}">{html.escape(Path(x["path"]).name)}</a></li>' for x in items)
    (OUT / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Actual ZIP capture index</title><style>body{font:18px/1.5 sans-serif;margin:2rem;max-width:70rem}a{color:#14566b}</style><h1>Actual ZIP captures</h1><p>Original screenshots from fresh file://390 package QA. They are unchanged. Chapter strips only arrange them at original390px width for review.</p><ul>'+links+'</ul>')
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width':1280,'height':1100},device_scale_factor=1)
        for label, members in groups:
            tiles=''.join(f'<div class="tile"><p>{html.escape(x.stem)}</p><img src="../Nightglass-ThreeChapters-v1-verification/phone-390/{html.escape(x.name)}"></div>' for x in members)
            doc=OUT / (label+'.html')
            doc.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#e8e5df}.strip{display:flex;gap:16px;padding:16px;width:max-content}.tile{width:390px;background:white}.tile p{font:16px/24px sans-serif;height:24px;margin:8px 12px}.tile img{display:block;width:390px;height:844px}</style><div class="strip">'+tiles+'</div>')
            await page.goto(doc.as_uri(),wait_until='load')
            await page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth)')
            await page.locator('.strip').screenshot(path=str(OUT/(label+'.png')))
        await browser.close()
    print(json.dumps({'capture_count':len(captures),'index':str(OUT/'index.html'),'strips':[str(OUT/(g[0]+'.png')) for g in groups]},indent=2))

if __name__ == '__main__':
    asyncio.run(main())
