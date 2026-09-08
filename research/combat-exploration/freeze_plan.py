"""Freeze original briefs, drawing-reference roles and exact built-in prompts before calls."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/combat-exploration';D=R/'research/combat-exploration/design'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frozen(p,body):
 if p.exists():assert p.read_text()==body,'Refuse to rewrite frozen input '+str(p)
 else:p.write_text(body)
def encoded(j):return json.dumps(j,indent=2,ensure_ascii=False)+'\n'
source=R/'research/combat-exploration/concepts-lead.json';draft=json.loads(source.read_text());refs={x['id']:x for x in json.loads((P/'references.json').read_text())}
entries=draft['entries'];assert len(entries)==18 and {e['id'] for e in entries}=={s+'-C'+str(n) for s in refs for n in [1,2]}
styles=draft['styles'];assert {s['id'] for s in styles}==set(refs);by_style={s['id']:s for s in styles}
plan={'schema':'CombatExplorationPlan/1','experiment_id':'CE-20260908-01','styles':styles,'entries':entries,'source_draft_sha256':sha(source),'owner_approval':None,'canon':None,'budget':{'primary':18,'maximum_repairs':6,'maximum_repairs_per_candidate':1,'maximum_calls':24},'presentation':'3:2 landscape two-view board; left30% expressive head/shoulders, right70% same adult complete figure and one weapon; no scenery or other characters.'}
frozen(P/'combat-plan.json',encoded(plan));frozen(P/'combat-plan.sha256',sha(P/'combat-plan.json')+'\n')
jobs=[]
for e in entries:
 assert isinstance(e['age'],int) and e['age']>=18
 s=by_style[e['style_id']];ref=refs[e['style_id']];aid=e['id']+'-P'
 subject='\n'.join(f'{k.replace("_"," ").capitalize()}: {e[k]}' for k in ['title','age','gender','complexion','face','hair','silhouette','costume','portrait_expression','pose','combat_role'] if e.get(k))
 prompt=f'''Use case: stylized-concept.
Asset: one ORIGINAL progression-fantasy combat-character design board, landscape3:2 composition, intended1536x1024. Create a new image using the supplied original board ONLY as a drawing-treatment reference.
Reference role: image1 establishes linework, rendering, shape language and material finish. DO NOT reuse its character face, hair construction, costume, weapon, creature or location. This is an entirely new adult combatant, not a reskin. No third-party character imitation.
Drawing treatment: {s.get('display_style','')}
Layout: two clean separate views on one quiet neutral ground. Left approximately30% is a large expressive head-and-shoulders portrait. Right approximately70% shows the SAME adult from head to both boot soles in a purposeful combat-ready stance, with the entire signature weapon inside frame. One person depicted in two views, matching face/hair/outfit. No additional people, creatures, character sheet poses or gear inventory. A plain subtle separator is enough. Generous clear margins around hair, boots and weapon tips. Portrait shows face and shoulders without the weapon. Portrait unobscured; complete figure and weapon silhouette do not overlap the portrait panel.
{subject}
Exactly one signature combat weapon in the full-body view: {e['weapon']['name']}. {e.get('weapon_visual',e['weapon']['description'])}
Power concept: {e['power']['name']}. {e['power']['description']}
Potential growth (concept context only, do not add extra objects or diagrams): {'; '.join(e.get('progression',[]))}
Current visible power cue: {e.get('current_power_cue','None')}.
Art direction: magnetic lead or rival presence, deliberately designed attractive and expressive adult face, memorable costume silhouette, desirable fantasy combat equipment. Communicate personality through gaze, expression and stance. Preserve the reference drawing system rather than a generic glossy fantasy render. Quiet background with a soft grounding shadow; no environment scene. Restrained material detailing, one small readable power cue at most, no particle storms or aura hiding anatomy or equipment. Render correct hands visibly wrapped around a plausible grip and clear weapon construction. Any unoccupied hand stays anatomically complete. No household tools or civilian-work props.
No text, name labels, stat boxes, logos, watermarks or faux lettering anywhere. No duplicate weapon, spare blade, scabbard, familiar or extra floating equipment. Do not turn the character into the source anchor. This is one finished new design board, not a collage of existing art.
'''
 pp=P/'prompts'/(aid+'.txt');frozen(pp,prompt)
 jobs.append({'id':e['id'],'attempt_id':aid,'phase':'primary','prompt_path':pp.relative_to(R).as_posix(),'prompt_sha256':sha(pp),'references':[{'path':ref['path'],'sha256':ref['sha256'],'role':ref['role']}],'prompt':prompt})
frozen(P/'primary-jobs.json',encoded(jobs));frozen(P/'primary-jobs.sha256',sha(P/'primary-jobs.json')+'\n');print(json.dumps({'entries':18,'plan_sha256':sha(P/'combat-plan.json'),'jobs_sha256':sha(P/'primary-jobs.json')}))
