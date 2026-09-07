"""Freeze exact phase prompts only after actual secondary references are inspected."""
from pathlib import Path
import argparse,hashlib,json
R=Path(__file__).resolve().parents[2];P=R/'production/world-components'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['places','tools-danger','people-creatures']);a=parser.parse_args()
plan=json.loads((P/'kit-plan.json').read_text());styles={s['id']:s for s in plan['styles']}
cats={'places':['E1'],'tools-danger':['E2','G1'],'people-creatures':['C1','C2','M1']}[a.phase]
framing={
 'E1':'Landscape 3:2. One complete environment, a clear entrance and usable route, three principal spatial masses, generous quiet space. No featured people or creatures. Make a lived place through its practical function, not piles of decorative objects.',
 'E2':'Landscape 3:2. One complete dangerous environment with a readable route and identifiable hazard. Distinct layout and function from the everyday location. Large deliberate shapes, no debris cloud or effect haze. No featured people or creatures.',
 'G1':'Landscape 3:2. Exactly THREE separate complete equipment objects arranged with generous gaps on a quiet pale ground. One view per item, all within frame. Large readable grips, joints and contact surfaces. No exploded parts, insets, duplicate views, extra accessories or captions. Illustrative scales may differ so every object is legible.',
 'C1':'Portrait 2:3. Exactly ONE complete adult character, head to toe with all feet and held equipment within frame and generous outer margin. Character fills most height, face large enough to see its distinctive construction. Calm pale ground with a single soft contact shadow; no landscape, creature, portrait inset or second person.',
 'C2':'Portrait 2:3. Exactly ONE complete adult character, head to toe with all feet and held equipment within frame and generous outer margin. Character fills most height, face large enough to see its distinctive construction. Calm pale ground with a single soft contact shadow; no landscape, creature, portrait inset or second person.',
 'M1':'Landscape 3:2. Exactly ONE whole creature on simple quiet ground. Entire silhouette and every specified limb within frame with generous margin. Clearly separate all feet and attachment paths. One pose only, no human comparison, inset, duplicate, swarm, scenery inventory or effects obscuring anatomy.'}
jobs=[]
for e in plan['entries']:
 if e['category_id'] not in cats:continue
 s=styles[e['style_id']];category=e['category_id'];refs=[P/'references'/(s['id']+'.png')]
 roles='Image1 is the ORIGINAL DRAWING-TREATMENT REFERENCE ONLY. Preserve its characteristic contour, shading, mark texture and material treatment, but invent the requested new subject. Do not copy its character, creature, scene or multi-part board composition.'
 if category in ['E2','G1']:
  refs.append(P/'candidates'/(s['id']+'-E1-P.png'))
  roles+=' Image2 is the newly explored everyday place: use only its material vocabulary and world logic for cohesion; do not duplicate its composition or add its setting behind isolated gear.'
 elif category in ['C1','C2']:
  refs.append(P/'candidates'/(s['id']+'-G1-P.png'))
  roles+=' Image2 is this kit\'s equipment reference. Reproduce ONLY the one requested held item with its actual grip and main structure. Do not carry every tool or copy the equipment-card layout. Image1 still governs the drawing treatment.'
 elif category=='M1':
  refs.append(P/'candidates'/(s['id']+'-E2-P.png'))
  roles+=' Image2 supplies the dangerous place\'s material/ecological context, not a background to reproduce. Draw the creature isolated; image1 still governs rendering.'
 prompt='Use case: stylized-concept\nAsset type: original story-component exploration card, '+e['id']+' '+e['title']+'.\nInput roles: '+roles+'\nComposition: '+framing[category]+'\nDrawing treatment: '+s['rendering']+'\nShared visual/material rules: '+' '.join(s['visual_rules'])+'\nWorld logic (context, not lettering): '+s['world_rule']+'\nSubject brief: '+e['brief']+'\nConstraints: Adult characters have distinct mature facial construction, body mass, posture and personality, not the original reference person in another costume. Keep coherent anatomy, actual hands gripping the named tool, clear object contact and complete framing. Organized form-specific detail and broad quiet areas. Preserve the source\'s drawing language without reproducing its crowded board. No text, lettering, labels, signature, watermark, floating symbols, decorative particle fields, gratuitous filigree or extra subjects.\n'
 if category in ['C1','C2']:
  prompt+='Actual inspected gear takes precedence over the preliminary prose wherever construction differs. Match the named item in image2; its open/closed state may change for the specified carry pose, but retain its handle, joints and overall identity. The15 pipe key has a CLOSED square-ring socket as visibly drawn. The17 triangular level frame is OPEN into its triangle as drawn, not collapsed into a bar. Do not add incidental objects from any background reference.\n'
 attempt=e['id']+'-P';pp=P/'prompts'/(attempt+'.txt')
 if pp.exists():assert pp.read_text()==prompt,'Frozen prompt differs'
 else:pp.write_text(prompt)
 jobs.append({'id':e['id'],'attempt_id':attempt,'phase':a.phase,'prompt_path':pp.relative_to(R).as_posix(),'prompt_sha256':sha(pp),'references':[{'path':ref.relative_to(R).as_posix(),'sha256':sha(ref)} for ref in refs]})
out=P/(a.phase+'-jobs.json');data={'schema':'WorldComponentJobs/1','experiment_id':plan['experiment_id'],'plan_sha256':sha(P/'kit-plan.json'),'jobs':jobs};txt=json.dumps(data,indent=2)+'\n'
if out.exists():assert out.read_text()==txt,'Frozen job set differs'
else:out.write_text(txt)
out.with_suffix('.json.sha256').write_text(sha(out)+'  '+out.relative_to(R).as_posix()+'\n')
print(json.dumps({'phase':a.phase,'jobs':len(jobs),'sha256':sha(out)}))
