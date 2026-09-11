from pathlib import Path
import json,hashlib,sys,re
R=Path(__file__).resolve().parents[2];P=R/'production/encounter-lab';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((P/'plan.json').read_text());lib={x['id']:x for x in plan['reference_library']};seq={x['id']:x for x in plan['sequences']}
candidates={x['attempt_id']:x for x in json.loads((P/'candidates.json').read_text())['candidates']};selected=json.loads((P/'selected.json').read_text())['selected']
jobs=[]
for ident in sys.argv[1:]:
 e=next(x for x in plan['entries'] if x['id']==ident);refs=[]
 for dep in e['continuation_dependencies']:
  if ident.startswith('ST') and dep=='ST01':continue # Actual early ring-side defect retained; later continuity uses correct-side ST02.
  c=candidates[selected[dep]];refs.append(dict(path=c['path'],sha256=c['sha256'],role='Actual earlier new encounter frame '+dep+'; preserve identity, equipment, creature construction, geography and persistent state. New action and camera.'))
 for rid in e['references']:
  c=lib[rid];refs.append(dict(path=c['path'],sha256=c['sha256'],role=c['role']))
 assert len(refs)<=5
 contract=seq[e['sequence_id']]['contract'] if e['sequence_id'] else seq[e['paired_ids'][0][:2]]['contract']
 contract=' '.join(z for z in re.split(r'(?<=[.!?]) +',contract) if not re.search(r'beat\s*[1234]|in[1234]/|inbeat|Final Tavi|In beat|Beat[1234]|in3|in4|beat2|beat3',z,re.I))
 prompt='Use case: illustration-story. Create ONE newly composed original narrative illustration, not a collage, not a sheet, no inset portrait or lettering.\nDrawing direction: '+e['drawing_direction']+'.\nInput images: '+ '\n'.join('Image '+str(i+1)+': '+r['role'] for i,r in enumerate(refs))+'\nCurrent subject, place and power constraints: '+contract+'\nRequested image: '+e['id']+' '+e['title']+'; '+e['beat']+'. Camera: '+e['scale']+'.\n'+e['brief']+'\nArt direction: beautiful memorable adult faces, decisive gesture and readable body mechanics. Preserve the original reference drawing treatment and recent quiet surfaces. Clear force, contact, body response and purposeful negative space. Dry ground in broad matte light/shadow planes; no reflective floor, tiny tile tessellation, all-over scratches, grain, crack webs, microfacets or sparkle. Selective detail belongs at faces, grips, joints and decisive contact. Keep material differences and intentional broad brushwork. Restrained effects with a clear direction; no generic aura, particle storm or rubble carpet. Continuous intact weapon construction with understandable grips. Draw only physically plausible limbs, deliberate occlusion, no floating props. No text, labels, watermark, speech balloons, split panels or franchise copies. Aspect ratio: '+('portrait 2:3' if 'portrait' in e['scale'] or ident in ['NG02','BP02','BP04','IO02','ST02','ST04','SB02','X02','X03'] else 'landscape 3:2')+'.'
 pp=P/'prompts'/(ident+'-P.txt');assert not pp.exists();pp.write_text(prompt+'\n')
 j=dict(id=ident,attempt_id=ident+'-P',phase='primary',category=e['category'],prompt=prompt+'\n',prompt_path=str(pp.relative_to(R)),prompt_sha256=sha(pp),plan_sha256=sha(P/'plan.json'),references=refs)
 jp=P/'jobs'/(ident+'-P.json');assert not jp.exists();jp.write_text(json.dumps(j,indent=2)+'\n');jobs.append(j)
print(json.dumps(jobs))
