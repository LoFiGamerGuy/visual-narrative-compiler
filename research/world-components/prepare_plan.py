"""Adapt reviewed exploration briefs into the reader and prompt contract."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/world-components'
draft=R/'research/world-components/world-design/prompt-draft-v2.json'
d=json.loads(draft.read_text());kits=json.loads((draft.parent/'kits-draft-v2.json').read_text());byid={k['id']:k for k in kits['kits']}
styles=[];entries=[]
categories=[{'id':id,'title':title,'description':desc} for id,title,desc in [
 ('C1','Character A','One possible adult lead or supporting character.'),('C2','Character B','An independent alternative, not an automatically paired cast member.'),('E1','Everyday place','A place where life and work happen.'),('E2','Dangerous place','A different location with a clear source of danger.'),('M1','Creature','A new species with a role in its world.'),('G1','Gear','Three tools with clear uses; item captions remain outside the image.')]]
for s in d['styles']:
 k=byid[s['id']]
 styles.append({'id':s['id'],'title':s['source_title'],'display_style':k['rendering_label'].split(' (')[0],'rendering':s['rendering'],'world_title':s['title'],'world_rule':s['world_rule'],'visual_rules':k['visual_rules'],'possible_conflict':s['possible_conflict'],'crossmix_note':s['crossmix_note'],'owner_rank':None})
 for c in categories:
  e=s['entries'][c['id']]
  entries.append({'id':s['id']+'-'+c['id'],'style_id':s['id'],'category_id':c['id'],**e})
plan={'schema':'WorldComponentPlan/1','experiment_id':'WC-20260907-01','status':'frozen-exploration-briefs-not-canon','draft_path':draft.relative_to(R).as_posix(),'draft_sha256':hashlib.sha256(draft.read_bytes()).hexdigest(),'styles':styles,'categories':categories,'entries':entries,'owner_approval':None,'mixing_rule':d['mixing_rule']}
out=P/'kit-plan.json';txt=json.dumps(plan,indent=2,ensure_ascii=False)+'\n'
if out.exists():assert out.read_text()==txt,'Refuse to overwrite a changed frozen plan'
else:out.write_text(txt)
out.with_suffix('.json.sha256').write_text(hashlib.sha256(out.read_bytes()).hexdigest()+'  production/world-components/kit-plan.json\n')
print('Frozen9 styles and54 component briefs.')
