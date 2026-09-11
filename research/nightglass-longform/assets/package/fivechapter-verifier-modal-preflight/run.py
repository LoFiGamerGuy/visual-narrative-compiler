"""Browser-only regression of changed modal path on the immutable four-chapter extraction."""
import asyncio, importlib.util, json
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[4]
verifier = root/'production/nightglass-longform/package/verify_package.py'
spec = importlib.util.spec_from_file_location('verify_package',verifier)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
prior = out.parent/'Nightglass-FourChapters-v1-verification/verification.json'
old = json.loads(prior.read_text())
extraction = Path(old['extracted_root'])
assert m.digest(extraction/'PACKAGE-MANIFEST.json')==old['manifest_sha256']
receipt = {'scope':'UI-only changed verifier preflight against existing FOUR-chapter extraction; not five-chapter portability',
           'prior_verification':str(prior),'prior_verification_sha256':m.digest(prior),
           'bound_zip_sha256':old['zip_sha256'],'extracted_root':str(extraction),
           'verifier_sha256':m.digest(verifier),'artifact_mutations':False}
try:
    current = asyncio.run(m.browse(extraction,out,Path('/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome')))
    receipt['browser_verification'] = current
    previous = {r['route']:r for r in old['browser_verification']['routes'] if not r['route'].startswith('historical-options') and not r['route'].startswith('historical-anchors')}
    ordinary = {r['route']:r for r in current['routes'] if r['route'] in previous}
    receipt['regular_route_data_unchanged'] = previous==ordinary
    receipt['regular_route_count_compared'] = len(previous)
    receipt['modal_routes'] = [r for r in current['routes'] if 'modal_captures' in r]
    assert current['passed'] and receipt['regular_route_data_unchanged']
finally:
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'passed':current['passed'],'routes':len(current['routes']),
                  'unchanged_regular_routes':len(previous),
                  'modal_counts':[r['images'] for r in receipt['modal_routes']],
                  'modal_scroll_offsets':[[c['scrollTop'] for c in r['modal_captures']] for r in receipt['modal_routes']]},indent=2))
