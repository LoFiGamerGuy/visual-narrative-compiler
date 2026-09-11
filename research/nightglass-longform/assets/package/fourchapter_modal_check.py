"""UI-only supplement for the already hash-verified four-chapter ZIP extraction."""
import asyncio, hashlib, json
from pathlib import Path
from playwright.async_api import async_playwright

base = Path(__file__).resolve().parent
prior = base/'Nightglass-FourChapters-v1-verification/verification.json'
verification = json.loads(prior.read_text())
root = Path(verification['extracted_root'])
out = base/'Nightglass-FourChapters-v1-asset-modal-checks'
out.mkdir(exist_ok=False)
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

async def main():
    errors, network, captures, closes = [], [], [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome', headless=True, args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
        page.on('pageerror', lambda e:errors.append(str(e)))
        page.on('request', lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
        for label, expected in [('options',78),('anchors',9)]:
            await page.goto((root/'docs/pilot-chapters/index.html').as_uri(),wait_until='load')
            await page.locator('#mode-all').click()
            await page.locator('#open-'+label).click()
            modal = page.locator('dialog[open]')
            await modal.evaluate('(d)=>d.querySelectorAll("img").forEach(i=>i.loading="eager")')
            await page.wait_for_function('Array.from(document.querySelectorAll("dialog[open] img")).every(i=>i.complete)',timeout=60000)
            for stage, fraction in [('top',0),('middle',.5),('end',1)]:
                await modal.evaluate('(d,f)=>d.scrollTop=(d.scrollHeight-d.clientHeight)*f', fraction)
                await page.wait_for_timeout(150)
                data = await modal.evaluate('(d)=>({id:d.id,scrollTop:d.scrollTop,scrollHeight:d.scrollHeight,clientHeight:d.clientHeight,images:d.querySelectorAll("img").length,broken:Array.from(d.querySelectorAll("img")).filter(i=>!i.naturalWidth).map(i=>i.src),horizontalOverflow:d.scrollWidth>d.clientWidth+1})')
                filename = f'{label}-{stage}.png'
                await page.screenshot(path=str(out/filename))
                captures.append({'file':filename,'sha256':digest(out/filename),'dialog':data})
                assert data['images']==expected and not data['broken'] and not data['horizontalOverflow']
                if stage != 'top': assert data['scrollTop']>0
            await modal.locator('[data-close]').first.click()
            closed = await page.locator('dialog[open]').count()==0
            closes.append({'dialog':label,'close_worked':closed})
            assert closed
        await browser.close()
    receipt = {'transport':'file:// from actual fresh four-chapter ZIP extraction; UI-only scrolling',
               'extracted_root':str(root),'bound_prior_verification':str(prior),
               'prior_verification_sha256':digest(prior),'zip_sha256':verification['zip_sha256'],
               'viewport':[390,844],'errors':errors,'network_requests':network,
               'captures':captures,'close_checks':closes,'passed':not errors and not network and all(c['close_worked'] for c in closes),
               'artifact_mutations':False}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    assert receipt['passed']
    print('PASS:78 options images and9 anchors;6 true internal-scroll captures;both close controls;zero errors/network/broken/overflow.')

asyncio.run(main())
