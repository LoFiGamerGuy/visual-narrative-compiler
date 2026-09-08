"""Freeze exact prompt and actual reference bindings only when dependencies exist."""
from pathlib import Path
import argparse,json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/world-combat'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(P/'world-combat-plan.json');by={e['id']:e for e in plan['entries']};anchors={e['id']:e for e in read(P/'references.json')}
rows=read(P/'candidates.json')['candidates'] if (P/'candidates.json').exists() else []
attempts={x['attempt_id']:x for x in rows};selected=read(P/'selected.json')['selected'] if (P/'selected.json').exists() else {}
styles={'01':'Original Nightglass clean action manhwa: refined intentional adult facial drawing, fine selective contours, crisp angular silhouettes, limited soft modeling, dark cool planes and selective cyan edge light. Scenes gain deep inhabited architecture, wet reflected light and large organized masses. Do not replace it with generic glossy 3D fantasy.','02':'Original Sunbreak warm outlined angular painting: lively expressive adult faces, warm dark contours, broad ochre/blue/green sunlit planes and restrained matte texture; tangible architectural depth. Do not flatten into pure cel shading or generic glossy fantasy.','06':'Original Floodline graphic brush-ink noir: enormous purposeful black and white masses, expressive adult faces, energetic broken brush edges, spatially deep concrete forms and restrained hot pink accents only. Not fine manga hatching or glossy color painting.'}
a=argparse.ArgumentParser();a.add_argument('ids',nargs='+');a.add_argument('--batch',required=True);args=a.parse_args();jobs=[]
for id in args.ids:
 e=by[id];aid=id+'-P';assert not (P/'calls'/(aid+'.json')).exists(),'Primary already called'
 refs=[{'path':anchors[e['style_id']]['path'],'sha256':anchors[e['style_id']]['sha256'],'role':'Original full drawing-treatment and integrated atmosphere reference ONLY. Never copy its character, creature, weapon or layout.'}]
 for dep in e['dependency_ids']:
  c=attempts[selected[dep]];refs.append({'path':c['path'],'sha256':c['sha256'],'role':'New recurring '+by[dep]['category']+' identity/design reference '+dep+' '+by[dep]['title']+'. Preserve recognizable design, change composition/action as requested.'+(' Equipment reference defines the object only, never its cropped display-hand pose; follow the new entry grip and stance.' if by[dep]['category']=='equipment' else '')})
 roles='\n'.join('Image '+str(i+1)+': '+r['role'] for i,r in enumerate(refs))
 layout='One complete cinematic scene or ability action composition, no divider, portrait inset, character-sheet layout or collage.' if e['category'] in ['scene','ability'] else ('One adult in TWO clean matching views: left about30% expressive head-and-shoulders portrait without weapon; right about70% complete same adult head-to-both-soles combat stance and entire signature weapon. Quiet neutral ground, generous endpoint margins, no second person.' if e['category']=='character' else 'One full subject composition, complete silhouette and every important endpoint visible. No text, divider, inset portrait or collage.')
 detail='\n'.join(k.title()+': '+str(e[k]) for k in ['age','gender','complexion','face','hair','build','costume'] if k in e)
 power=e.get('power');context=('\nPower context: '+power['name']+'. '+power['description']+' Limitation: '+power.get('limitation','')+' Future growth is copy context only; do not depict simultaneous upgrades: '+'; '.join(power.get('growth',[]))) if power else ''
 prompt='Use case: '+('illustration-story' if e['category'] in ['scene','ability'] else 'stylized-concept')+'.\nAsset: NEW original progression-fantasy '+e['category']+' image, landscape3:2, intended1536x1024.\nInput image roles:\n'+roles+'\nDrawing treatment: '+styles[e['style_id']]+'\nLayout: '+layout+'\nTitle/concept (do not letter): '+e['title']+'\n'+detail+'\nRequested visual: '+e['visual_brief']+('\nSignature combat implement: '+e['weapon_visual'] if e.get('weapon_visual') else '')+context+'\nArt priorities: magnetic original character or creature presence, purposeful composition, believable scale and contact, readable action and meaningful materials. Use organized environmental detail rather than blankness for full scenes. Low clutter must not become bland design. Match reference drawing qualities, not its old identity or exact composition. Full-scene references containing portraits do NOT authorize portrait insets in a scene. No third-party franchise copying, logos, names, captions, watermarks, HUD, stat boxes, exploded assembly diagrams or decorative particle storms.\n'
 rel='production/world-combat/prompts/'+aid+'.txt';path=R/rel
 if path.exists():assert path.read_text()==prompt,'Refuse changed prompt'
 else:path.write_text(prompt)
 jobs.append({'id':id,'attempt_id':aid,'phase':'primary','category':e['category'],'prompt_path':rel,'prompt_sha256':sha(path),'references':refs,'prompt':prompt})
out=P/(args.batch+'-jobs.json');raw=json.dumps(jobs,indent=2)+'\n'
if out.exists():assert out.read_text()==raw,'Refuse changed batch freeze'
else:out.write_text(raw)
(P/(args.batch+'-jobs.sha256')).write_text(sha(out)+'  '+out.name+'\n')
print(json.dumps({'jobs':len(jobs),'path':str(out),'sha256':sha(out)}))
