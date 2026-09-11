"""Freeze observed, separate structural or surface edit requests from a JSON spec."""
from pathlib import Path
import argparse,hashlib,json
R=Path(__file__).resolve().parents[2];P=R/'production/combat-depth';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('spec');a.add_argument('--batch',required=True);args=a.parse_args()
specpath=Path(args.spec);specpath=specpath if specpath.is_absolute() else R/specpath
specs=json.loads(specpath.read_text());candidates={c['attempt_id']:c for c in json.loads((P/'candidates.json').read_text())['candidates']};plan=json.loads((P/'plan.json').read_text());entries={e['id']:e for e in plan['entries']};jobs=[]
budget=plan['budget']
for s in specs:
 c=candidates[s['source_attempt']];id=c['id'];phase=s['phase'];assert phase in ['texture','structural'];aid=id+('-F1' if phase=='texture' else '-R1')
 assert not(P/'calls'/(aid+'.json')).exists()
 count=sum(json.loads(p.read_text()).get('phase')==phase for p in (P/'calls').glob('*.json'))
 assert count+sum(j['phase']==phase for j in jobs)<budget['texture_passes' if phase=='texture' else 'structural_repairs']
 prefix=('Use case: style-transfer. Redraw ONLY THE SURFACE FINISH of the supplied exact image. Preserve its composition, camera distance, subjects, faces, hairlines, expression, costume, anatomy, weapon construction and handling, scale, spatial relationships, action and lighting mood. Substantially reduce distracting repetitive microtexture. Replace it with broad deliberate opaque light/shadow shapes, calm material interiors and selective crisp accents at faces, functional contacts and meaningful boundaries. Retain material differences, depth, inhabited scale and sophisticated drawing. This is a drawn surface redraw, not blur, denoise, low resolution, airbrush, plastic 3D, flat vectors or removal of the world. No new details to compensate.\n' if phase=='texture' else 'Use case: precise-object-edit. Correct ONLY the specified composition or structural failure in this exact source image. Keep its drawing treatment and other content consistent; this is not a texture-finishing pass.\n')
 support=s.get('support_references',[])
 assert not support or phase=='structural', 'Texture finishing must remain source-only'
 for rr in support: assert sha(R/rr['path'])==rr['sha256']
 guidance=('\nImage1 is the exact composition to edit. Additional images are correction references ONLY for the explicitly named identity or construction: '+ '; '.join('Image'+str(i+2)+': '+rr['role'] for i,rr in enumerate(support)) if support else '\nUse this supplied actual image as the ONLY edit reference.')
 prompt=prefix+s['instruction']+guidance+' Return one new native artwork with the same aspect ratio, not a comparison, panel layout, collage, text, diagram, watermark or annotated explanation.\n'
 rel=f'production/combat-depth/prompts/{aid}.txt';out=R/rel
 if out.exists():assert out.read_text()==prompt
 else:out.write_text(prompt)
 jobs.append(dict(id=id,attempt_id=aid,phase=phase,category=entries[id]['category'],retry_of=c['attempt_id'],retry_reason=s['reason'],evidence_path=str(specpath.relative_to(R)),evidence_sha256=sha(specpath),prompt_path=rel,prompt_sha256=sha(out),plan_sha256=sha(P/'plan.json'),references=[dict(path=c['path'],sha256=c['sha256'],role='Exact edit source; preserve all content except the specified '+phase+' change')]+support,prompt=prompt))
out=P/(args.batch+'-jobs.json');raw=json.dumps(jobs,indent=2)+'\n'
if out.exists():assert out.read_text()==raw
else:out.write_text(raw)
print(str(out))
