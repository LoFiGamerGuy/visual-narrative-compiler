"""Resume browser-only QA from preserved, already hash-verified ZIP extraction."""
import asyncio, importlib.util,json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('verify_package',root/'production/nightglass-longform/package/verify_package.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
previous=root/'research/nightglass-longform/assets/package/Nightglass-Chapter1-v1-verification/verification.json'
old=json.loads(previous.read_text())
archive=Path(old['zip']); extraction=Path(old['extracted_root'])
assert m.digest(archive)==old['zip_sha256']
assert m.digest(extraction/'PACKAGE-MANIFEST.json')==old['manifest_sha256']
out=root/'research/nightglass-longform/assets/package/Nightglass-Chapter1-v1-browser-r2'
out.mkdir()
receipt={k:v for k,v in old.items() if k!='browser_verification'}
receipt['prior_hash_verification_receipt']=str(previous)
receipt['retry_reason']='Verifier first attempted hidden historical archive button in reading mode; correct flow clicks Panel gallery first. Delivery bytes unchanged.'
receipt['verifier_path']='production/nightglass-longform/package/verify_package.py'
receipt['verifier_sha256']=m.digest(root/receipt['verifier_path'])
try:
 receipt['browser_verification']=asyncio.run(m.browse(extraction,out,Path('/home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome')))
finally:
 (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt['browser_verification'],indent=2))
assert receipt['browser_verification']['passed']
