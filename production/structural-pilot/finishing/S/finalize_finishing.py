from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S';primary=json.loads((B/'primary-summary.json').read_text());correction=json.loads((B/'P14/correction-round-1-work-record.json').read_text());portable=json.loads((B/'portable-verification.json').read_text());now=datetime.datetime.now(datetime.timezone.utc)
checks=[]
for r in primary['panels']:
 p=R/r['png'];checks.append(dict(panel=r['panel'],original_primary_png=r['png'],unchanged=hashlib.sha256(p.read_bytes()).hexdigest()==r['png_sha256']))
selected=[]
for p,ver in [('P09','F01-v4-portable'),('P11','F01-v3'),('P13','F01-v4'),('P14','F02-v5-portable')]:
 base=B/p/ver;png=base/(p+'-'+ver+'.png');svg=png.with_suffix('.svg');selected.append(dict(panel=p,png=str(png.relative_to(R)),svg=str(svg.relative_to(R)),png_sha256=hashlib.sha256(png.read_bytes()).hexdigest(),svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),inline_rasters_in_svg='data:image/' in svg.read_text(),accepted=False))
pack_start=datetime.datetime.fromisoformat(correction['end_utc']);pack=dict(schema='FinishingPackagingWork/1',start_utc=pack_start.isoformat(),end_utc=now.isoformat(),elapsed_seconds=(now-pack_start).total_seconds(),scope='Portable external-raster copies, unchanged pixel comparison, preservation verification and final source/timing manifest; no artistic corrections.',paid_spend_usd=0,generation_calls=0);(B/'packaging-work-record.json').write_text(json.dumps(pack,indent=2)+'\n')
summary=dict(schema='RouteSFinishingSummary/1',at_utc=now.isoformat(),selected=selected,primary_seconds=primary['primary_elapsed_seconds'],primary_allowance_seconds=4800,correction_seconds=correction['elapsed_seconds'],correction_rounds={'P09':0,'P11':0,'P13':0,'P14':1},correction_cap_seconds_per_panel=1500,packaging_seconds=pack['elapsed_seconds'],total_finishing_art_minutes=(primary['primary_elapsed_seconds']+correction['elapsed_seconds'])/60,preserved_primary_checks=checks,portable_pixel_equivalence=portable['panels'],generation_calls_by_finishing_author=0,direct_spend_usd=0,human_artist_hours=None,acceptance='Unaccepted structural and conventional finishing proofs. Lead/independent review owns semantic and art decisions.',visible_P14_correction_limitations=correction['visible_limitations'])
(B/'finishing-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(B/'FINISHING-RESULT.md').write_text('''# Route S final review set

These remain unaccepted conventional composition proofs. The selected P14 correction removes the large matte holes, connects the left wrist to the held staff, and adds fixed-prop contour/material shading. Source faces and the supported right dorsal injury remain intact. Local arm stiffness, cupped hand quality and clothing clone seams remain visible.

'''+''.join(f"- {r['panel']}: [PNG]({r['panel']}/{Path(r['png']).parent.name}/{Path(r['png']).name}) · [editable SVG]({r['panel']}/{Path(r['svg']).parent.name}/{Path(r['svg']).name})\n" for r in selected)+f'''
Primary art work: {primary['primary_elapsed_seconds']/60:.2f}/80 minutes. One P14 correction: {correction['elapsed_seconds']/60:.2f}/25 minutes. Packaging/verification: {pack['elapsed_seconds']/60:.2f} minutes separately. Total finishing art work: {summary['total_finishing_art_minutes']:.2f} minutes. Zero generation calls by this finishing author and $0 direct spend. Human artist labor remains unmeasured.

All selected SVGs use external local PNG references. Portable P09/P14 renders match preserved inline originals exactly, including PNG hashes. The original four primary PNG hashes are unchanged. Earlier inline SVG/spec versions remain local preservation artifacts; the lead owns ignore rules and repository packaging.

See `finishing-summary.json`, `portable-verification.json`, per-panel work records and version receipts for exact timing, source hashes, masks, transforms and limitations. Geometry and hash checks establish provenance; they do not establish finished-art quality.
''')
files=[]
for p in sorted(B.rglob('*')):
 if not p.is_file() or 'runtime' in p.relative_to(B).parts or p.name=='finishing-source-manifest.json':continue
 files.append(dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(B/'finishing-source-manifest.json').write_text(json.dumps(dict(schema='RouteSFinalSourceManifest/1',at_utc=now.isoformat(),files=files,excluded=['runtime/** task-owned mutable browser files']),indent=2)+'\n')
print(json.dumps(dict(art_minutes=summary['total_finishing_art_minutes'],packaging_minutes=pack['elapsed_seconds']/60,files=len(files),all_original_primaries_unchanged=all(r['unchanged'] for r in checks)),indent=2))
