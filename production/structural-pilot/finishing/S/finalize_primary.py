from pathlib import Path
import json,hashlib,datetime
from PIL import Image
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S';records=[];files=[]
for panel in ['P09','P11','P13','P14']:
 p=B/panel;r=json.loads((p/'primary-work-record.json').read_text());png=p/r['selected_for_review'];svg=p/r['editable_svg'];im=Image.open(png)
 records.append(dict(panel=panel,png=str(png.relative_to(R)),svg=str(svg.relative_to(R)),png_sha256=hashlib.sha256(png.read_bytes()).hexdigest(),svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),dimensions=list(im.size),elapsed_seconds=r['elapsed_seconds'],visible_limitations=r['visible_limitations'],accepted=False))
summary=dict(schema='RouteSPrimarySummary/1',experiment='SC-20260907-01',at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),panels=records,primary_elapsed_seconds=sum(r['elapsed_seconds'] for r in records),primary_allowance_seconds=80*60,later_correction_rounds_used=0,generation_calls_by_finishing_author=0,direct_spend_usd=0,human_artist_hours=None,fixed_control='production/structural-pilot/control/v8',acceptance='All four are reviewable bounded composition proofs; none is accepted as finished art.',raw_contract_failure='All four selected S raw sources are RGB with a painted checkerboard, not native transparent actor layers. P11/P14 contain unwanted props; P09/P13 required local pose corrections.',method='Conventional chroma-neutral matting, source-coordinate masks, affine/similarity placement, native hand crops, cloned costume texture, explicit vector local limbs, frozen mesh face projection and same-pass prop occlusion masks. No image generation or generative inpainting.')
(B/'primary-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(B/'README.md').write_text('''# Route S conventional finishing proof

Four primary compositions are reviewable; none is accepted as finished art. Fixed v8 architecture, three named threat limbs, rod geometry and shutter partition supply structural pixels. Generated adult drawings supply source faces and costume pixels. The source layer contract failed: selected raw plates contain RGB painted checkerboard, and several contain forbidden props or incorrect grip poses.

| Panel | Review PNG / editable source | Primary minutes |
|---|---|---:|
'''+''.join(f"| {r['panel']} | [{Path(r['png']).name}]({r['panel']}/{Path(r['png']).parent.name}/{Path(r['png']).name}) / [SVG]({r['panel']}/{Path(r['svg']).parent.name}/{Path(r['svg']).name}) | {r['elapsed_seconds']/60:.2f} |\n" for r in records)+f'''
Primary composition time: **{summary['primary_elapsed_seconds']/60:.2f} of 80 minutes**. No later correction round used. Finishing author made zero generation calls and spent $0. Human artist time was not measured and is not represented as zero.

Every intermediate F01 version remains. Each SVG embeds source raster layers; its spec retains ordered source paths, transforms and local vector masks. Receipts and preparation/revision scripts describe source crops, matte rules and observed failures. Browser runtime files are task-owned and excluded from the authored-file manifest.

The best result is structural repeatability in final composited pixels. The substantial remaining failure is finish coherence: actor drawing is more detailed than the architectural and mechanical drawing; several conventional sleeves/hands look stiff or patched. P14 has the clearest source faces and supported anatomical right wound, but the most conspicuous repair defects around its left staff hand, Odo's flask hand and trousers. P09 has two source fists on the exact staff, but reposed local arms remain stiff. P13 preserves shutter separation and three limbs; small hand matte specks and schematic support sleeves remain. P11 preserves the airborne gap and contact placement; the effects and architecture remain visibly diagrammatic.

Geometry checks, alpha checks, hashes and affine registration are provenance and reproducibility evidence. They do not establish reader comprehension, laterality, appeal or finished-art quality. Use actual PNG review and the lead's separate decision record.
''')
for p in sorted(B.rglob('*')):
 if not p.is_file() or 'runtime' in p.relative_to(B).parts or p.name=='primary-source-manifest.json':continue
 files.append(dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(B/'primary-source-manifest.json').write_text(json.dumps(dict(schema='AuthoredRouteSManifest/1',at_utc=summary['at_utc'],files=files,excluded=['runtime/**: task-owned mutable Chromium process files']),indent=2)+'\n')
print(json.dumps(dict(primary_minutes=summary['primary_elapsed_seconds']/60,authored_files=len(files),pngs=sum(p['path'].endswith('.png') for p in files)),indent=2))
