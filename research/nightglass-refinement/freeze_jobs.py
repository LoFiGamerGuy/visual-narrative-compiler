"""Freeze actual new-composition prompts and references after the texture gate."""
from pathlib import Path
import argparse, json, hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/nightglass-refinement'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(P/'refinement-plan.json');by={e['id']:e for e in plan['entries']}
gate=read(P/'texture-gate.json');assert gate['expansion_allowed'] is True
attempts={c['attempt_id']:c for c in read(P/'candidates.json')['candidates']}
selected=read(P/'selected.json')['selected']
styles={'01':'Nightglass refined action-manhwa drawing: appealing precisely drawn adult faces, confident selective contours, designed hair locks, clear angular costume shapes, broad opaque material planes with limited soft modeling, purposeful cool/warm light. Use the first reference for its calmer drawing finish only. Small crisp accents belong to eyes, mouth and functional edges; interiors of clothing, ground, water and creatures are mostly quiet. No repeated tiny facets, cracks, grain, gritty overlay, wet glitter, excessive thin folds or equal-strength edge lights. Do not turn the drawing into flat vectors, blurred airbrush or glossy 3D. Light and scenery follow this NEW brief, not the reference night city.',
'02':'Sunbreak warm outlined angular painting: expressive adult faces, warm dark contours, broad ochre/blue/green sunlit planes and clean matte materials. Preserve original drawing vitality and deep architectural space while omitting pervasive grain, scratches and repeated small texture marks. Not flat vectors or glossy 3D.',
'06':'Floodline graphic brush-ink noir: decisive enormous black/white masses, expressive adult facial construction, a few energetic broken brush edges, tiny hot-pink accent. Calm interiors instead of all-over scratch hatching or gritty texture. Keep form and clean purposeful silhouette.'}
a=argparse.ArgumentParser();a.add_argument('ids',nargs='+');a.add_argument('--batch',required=True);args=a.parse_args();jobs=[]
for id in args.ids:
 e=by[id];assert e['category']!='refinement';aid=id+'-P';assert not(P/'calls'/(aid+'.json')).exists()
 if e['style_id']=='01':
  c=attempts[gate['drawing_reference_attempt']];refs=[{'path':c['path'],'sha256':c['sha256'],'role':'Calmer DRAWING TREATMENT ONLY. Never copy this man, silver hairstyle, costume, saber, portrait layout or night city unless the new brief explicitly names Riven. New characters must have the new specified face and silhouette.'}]
 else:
  t=e['drawing_treatment_reference'];refs=[{'path':t['original_benchmark_path'],'sha256':t['original_benchmark_sha256'],'role':'Original comparison DRAWING TREATMENT ONLY, with calmer surface interiors. Never copy this reference character, creature, scenery, equipment or composition.'}]
 for d in e['design_references']:
  if d['kind']=='prior_identity_or_object': rr={k:d[k] for k in ['path','sha256','role']};rr['role']=d['id']+': '+rr['role']
  else:
   c=attempts[selected[d['id']]];rr={'path':c['path'],'sha256':c['sha256'],'role':d['id']+' '+by[d['id']]['title']+': exact newly designed subject/object reference. Preserve recognizable construction and identity in a genuinely new pose/action. Equipment reference defines object only, never copy its cropped display hands.'}
  refs.append(rr)
 assert len(refs)<=e['max_actual_references']
 for rr in refs:assert sha(R/rr['path'])==rr['sha256']
 roles='\n'.join('Image '+str(i+1)+': '+rr['role'] for i,rr in enumerate(refs))
 layout='One complete cinematic composition. NO portrait panel, divider, character-sheet layout or inset.' if e['category'] in ['scene','ability'] else ('Two matching views of ONE adult: expressive head/shoulders portrait on left, complete same adult with full weapon and boots on right. Quiet broad backdrop.' if e['category']=='character' else 'One full subject, whole silhouette and every relevant endpoint inside frame. No inset, collage or diagram.')
 v=e['visual_brief'].replace('no text, arrows, particle clouds','no text, diagram arrows, particle clouds')
 prompt='FIRST PRIORITY: draw the newly described subject with calm, largely UNMARKED surface interiors. Clean hand-drawn action-comic contours and expressive faces; broad opaque color shapes with selective shaded volume. Material detail is concentrated at a few meaningful boundaries, not distributed across every surface. Skin has no branching vein/crack pattern. Ground has broad shapes, not small chips. Water has broad reflection bands, not glitter flecks. Do not copy any reference texture carpet. Preserve sophisticated proportions, atmosphere and depth.\nNEW SUBJECT AND ACTION: '+v+'\nUse case: original progression-fantasy illustration.\nAsset: NEW '+e['category']+' composition, native1536x1024 landscape3:2.\nInput reference roles:\n'+roles+'\nDrawing: '+styles[e['style_id']]+'\nLayout: '+layout+'\nConcept (do not letter): '+e['title']+'\nVisual request: '+v
 if e.get('weapon'):prompt+='\nSignature equipment: '+e['weapon']['name']+'. '+e['weapon']['description']
 if e.get('power'):prompt+='\nPower context for design only: '+e['power']['description']+' Limitation: '+e['power']['limitation']+' Do not illustrate future upgrades simultaneously.'
 prompt+='\nPriorities: magnetic character/creature presence, deliberate composition, expressive acting, believable handling and depth, broad calm surfaces with selective sharp focal accents. Quiet texture does not mean low-detail faces, bland silhouettes, empty scenes or posterized shading. No decorative dust, texture carpet, arbitrary mechanisms, glowing aura, text, labels, logos, watermarks, HUD, franchise copying or borrowed reference layout.\n'
 rel='production/nightglass-refinement/prompts/'+aid+'.txt';path=R/rel
 if path.exists():assert path.read_text()==prompt
 else:path.write_text(prompt)
 jobs.append({'id':id,'attempt_id':aid,'phase':'primary','category':e['category'],'prompt_path':rel,'prompt_sha256':sha(path),'plan_sha256':sha(P/'refinement-plan.json'),'texture_gate_sha256':sha(P/'texture-gate.json'),'references':refs,'prompt':prompt})
 out=P/(args.batch+'-jobs.json')
raw=json.dumps(jobs,indent=2)+'\n'
if out.exists():assert out.read_text()==raw
else:out.write_text(raw)
print(json.dumps({'jobs':len(jobs),'path':str(out),'sha256':sha(out)}))
