#!/usr/bin/env python3
"""Verify a freshly extracted delivery ZIP; browser/receipts stay outside delivery."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
from urllib.parse import unquote, urlsplit
import zipfile


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def extract(archive, output):
    if output.exists():
        raise RuntimeError('Verification output already exists; use a new directory')
    output.mkdir(parents=True)
    extraction = output / 'extracted'
    extraction.mkdir()
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f'CRC mismatch: {bad}')
        roots = set()
        for info in z.infolist():
            p = PurePosixPath(info.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in info.filename or not p.parts:
                raise RuntimeError(f'Unsafe ZIP path: {info.filename}')
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise RuntimeError(f'Symlink ZIP entry: {info.filename}')
            roots.add(p.parts[0])
        if len(roots) != 1:
            raise RuntimeError('Expected one versioned ZIP root')
        z.extractall(extraction)
    root = extraction / roots.pop()
    manifest = json.loads((root / 'PACKAGE-MANIFEST.json').read_text())
    expected = {'PACKAGE-MANIFEST.json'}
    for record in manifest['files']:
        f = root / record['path']
        if not f.resolve().is_relative_to(root.resolve()):
            raise RuntimeError('Manifest path escaped delivery')
        if not f.is_file() or f.stat().st_size != record['bytes'] or digest(f) != record['sha256']:
            raise RuntimeError(f'Manifest mismatch: {record["path"]}')
        expected.add(record['path'])
    actual = {f.relative_to(root).as_posix() for f in root.rglob('*') if f.is_file()}
    if actual != expected:
        raise RuntimeError(f'Unexpected/missing ZIP files: {actual ^ expected}')
    return root, manifest


async def browse(root, output, chromium):
    from playwright.async_api import async_playwright
    results = []
    errors = []
    network = []
    snapshot = json.loads((root / 'production/nightglass-longform/reader/snapshot.json').read_text())
    routes = [('start', 'START-HERE.html')]
    routes += [(f'chapter-{c["number"]}', f'docs/nightglass-longform/index.html#chapter-{c["number"]}')
               for c in snapshot['chapters'] if c['available']]
    routes += [(f'pilot-{name}', f'docs/pilots-reading-v2/index.html#{name}') for name in ['NG','BP','ST','RC','FL']]
    routes += [(f'comparison-{name}', f'docs/nightglass-longform/comparison.html#{name}') for name in ['A','B','C']]
    routes += [('nightglass-review', 'docs/nightglass-longform/review.html'),
               ('pilot-review', 'docs/pilots-reading-v2/review.html'),
               ('historical-reader', 'docs/pilot-chapters/index.html')]
    expected_figures = {f'chapter-{c["number"]}':c['available'] for c in snapshot['chapters'] if c['available']}
    expected_figures.update({f'pilot-{name}':16 for name in ['NG','BP','ST','RC','FL']})
    expected_figures.update({f'comparison-{name}':6 for name in ['A','B','C']})
    shots = output / 'phone-390'
    shots.mkdir()
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=str(chromium), args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width':390,'height':844}, device_scale_factor=1)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: network.append(request.url) if request.url.startswith(('http://','https://')) else None)
        await page.route('http://**/*', lambda route: route.abort())
        await page.route('https://**/*', lambda route: route.abort())
        async def inspect(label, expected_modal_images=None):
            await page.wait_for_timeout(250)
            modal = None
            if expected_modal_images is not None:
                modal = page.locator('dialog[open]')
                await modal.wait_for(state='visible')
                await modal.evaluate("d=>d.querySelectorAll('img').forEach(i=>i.loading='eager')")
                await page.wait_for_function('Array.from(document.querySelectorAll("dialog[open] img")).every(i=>i.complete)',timeout=60000)
                data = await modal.evaluate('''d => ({title:document.title, images:d.querySelectorAll('img').length,
                  broken:Array.from(d.querySelectorAll('img')).filter(i=>!i.naturalWidth).map(i=>i.src),
                  horizontalOverflow:d.scrollWidth>d.clientWidth+1,
                  hrefs:Array.from(d.querySelectorAll('a[href]')).map(a=>a.href),
                  height:d.scrollHeight, figures:d.querySelectorAll('figure').length})''')
            else:
                # Trigger native lazy-loading throughout the actual extracted reader.
                height = await page.evaluate('document.documentElement.scrollHeight')
                for y in range(0,height,760):
                    await page.evaluate('(y)=>window.scrollTo(0,y)',y)
                    await page.wait_for_timeout(20)
                await page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
                await page.wait_for_function('Array.from(document.images).every(i=>i.complete)',timeout=60000)
                await page.evaluate('window.scrollTo(0,0)')
                data = await page.evaluate('''() => ({title:document.title, images:document.images.length,
                  broken:Array.from(document.images).filter(i=>!i.naturalWidth).map(i=>i.src),
                  horizontalOverflow:document.documentElement.scrollWidth>innerWidth,
                  hrefs:Array.from(document.querySelectorAll('a[href]')).map(a=>a.href),
                  height:document.documentElement.scrollHeight, figures:document.querySelectorAll('figure').length})''')
            missing = []
            for href in data.pop('hrefs'):
                parsed = urlsplit(href)
                if parsed.scheme == 'file':
                    path = Path(unquote(parsed.path)).resolve()
                    if not path.is_relative_to(root.resolve()) or not path.is_file():
                        missing.append(href)
                elif parsed.scheme in ('http','https'):
                    missing.append('external dependency: '+href)
            expected=expected_figures.get(label)
            data.update(route=label,missing_links=missing,expected_figures=expected,
                        wrong_panel_count=expected is not None and data['figures']!=expected)
            if modal is not None:
                captures = []
                for stage, fraction in [('top',0),('middle',.5),('end',1)]:
                    await modal.evaluate('(d,f)=>d.scrollTop=(d.scrollHeight-d.clientHeight)*f',fraction)
                    await page.wait_for_timeout(150)
                    metrics = await modal.evaluate('''d=>({id:d.id,scrollTop:d.scrollTop,
                      scrollHeight:d.scrollHeight,clientHeight:d.clientHeight,
                      images:d.querySelectorAll('img').length,
                      broken:Array.from(d.querySelectorAll('img')).filter(i=>!i.naturalWidth).map(i=>i.src),
                      horizontalOverflow:d.scrollWidth>d.clientWidth+1})''')
                    filename = label+'-'+stage+'.png'
                    await page.screenshot(path=str(shots/filename))
                    captures.append(dict(file=filename,**metrics))
                offsets = [c['scrollTop'] for c in captures]
                maximum = captures[-1]['scrollHeight']-captures[-1]['clientHeight']
                scroll_ok = offsets[0]==0 and abs(offsets[-1]-maximum)<=1
                if maximum>1:
                    scroll_ok = scroll_ok and 0<offsets[1]<offsets[2]
                await modal.locator('[data-close]').first.click()
                data.update(expected_modal_images=expected_modal_images,
                            wrong_modal_count=data['images']!=expected_modal_images,
                            modal_captures=captures,modal_scrolling_worked=scroll_ok,
                            modal_close_worked=await page.locator('dialog[open]').count()==0)
            else:
                await page.screenshot(path=str(shots/(label+'-top.png')))
                if data['height']>1688:
                    await page.evaluate('(y)=>window.scrollTo(0,y)',data['height']//2)
                    await page.screenshot(path=str(shots/(label+'-middle.png')))
                    await page.evaluate('(y)=>window.scrollTo(0,y)',data['height'])
                    await page.screenshot(path=str(shots/(label+'-end.png')))
            results.append(data)
        for label, relative in routes:
            path, _, fragment = relative.partition('#')
            await page.goto((root/path).as_uri()+('#'+fragment if fragment else ''), wait_until='load')
            await inspect(label)
        # Actual historical archive UI creates its image/source links on demand.
        for selector,label,count in [('#open-options','historical-options',78),('#open-anchors','historical-anchors',9)]:
            await page.goto((root/'docs/pilot-chapters/index.html').as_uri(),wait_until='load')
            await page.locator('#mode-all').click()
            await page.locator(selector).click()
            await inspect(label,expected_modal_images=count)
        await browser.close()
    failed = bool(errors or network or any(r['broken'] or r['horizontalOverflow'] or r['missing_links'] or r['wrong_panel_count']
                  or r.get('wrong_modal_count',False) or not r.get('modal_scrolling_worked',True)
                  or not r.get('modal_close_worked',True)
                  or any(c['broken'] or c['horizontalOverflow'] or c['images']!=r['expected_modal_images']
                         for c in r.get('modal_captures',[])) for r in results))
    return {'viewport':[390,844],'transport':'file:// from newly extracted delivery ZIP',
            'image_check':'Scroll reading pages unchanged; load archive dialog images and capture actual internal top/middle/end with offsets and close checks.',
            'routes':results,'page_errors':errors,'network_requests':network,'passed':not failed}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--chromium',type=Path,default=Path('/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome'))
    args=parser.parse_args()
    archive=args.zip.resolve(); output=args.output.resolve()
    root,manifest=extract(archive,output)
    receipt={'zip':str(archive),'zip_sha256':digest(archive),'version':manifest['version'],
             'milestone':manifest['milestone'],'manifest_sha256':digest(root/'PACKAGE-MANIFEST.json'),
             'manifest_files_verified':len(manifest['files']),'extracted_root':str(root),
             'browser_verification':'pending','human_acceptance':False}
    receipt_path=output/'verification.json'
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    try:
        receipt['browser_verification']=asyncio.run(browse(root,output,args.chromium))
    except Exception as error:
        receipt['browser_verification']={'passed':False,'error':str(error)}
        receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
        raise
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'version':manifest['version'],'verified_files':len(manifest['files']),
                      'passed':receipt['browser_verification']['passed'],'receipt':str(receipt_path)},indent=2))
    if not receipt['browser_verification']['passed']:
        raise SystemExit(1)

if __name__=='__main__':
    main()
