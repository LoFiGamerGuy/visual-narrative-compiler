"""Resolve comic-plan spatial assignments into adapter-neutral stage input."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PLANS=ROOT/'production/comic/ch01-sc01-panel-plans-v1.json'
STAGE=ROOT/'production/stages/kitchen-table-spatial-contract-v1.json'
OUT=ROOT/'production/stages/resolved/ch01-sc01-kitchen-spatial-inputs-v1.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 plans=json.loads(PLANS.read_text()); stage=json.loads(STAGE.read_text())
 anchors=stage['anchor_contract']; result=[]
 for p in plans['plans']:
  if p['spatial_mode']!='grounded': continue
  assert p['spatial_stage_contract_id']==stage['record_id']
  placed=[]
  for a in p['spatial_assignments']:
   if 'anchor' in a:
    q=anchors[a['anchor']]; x=sum(q['x_range'])/2; depth=sum(q['depth_range'])/2
    placed.append({'role':a['role'],'anchor':a['anchor'],'x_normalized':x,'depth_normalized':depth})
   else: placed.append({'role':a['role'],'world_xyz_m':a['world_xyz_m'],'posture':a['posture']})
  result.append({'panel_id':p['panel_id'],'spatial_mode':'grounded','camera_profile':stage['camera_profiles'][0]['camera_id'],'occluders':[x['occluder_id'] for x in stage['occluders']],'placements':placed,'adapter_limitations':stage['limitations']})
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps({'record_type':'ResolvedComicSpatialInputs','state':'INTENT_DERIVED_NOT_RENDER_PROVENANCE','plans_source_sha256':sha(PLANS),'stage_source_sha256':sha(STAGE),'medium':'comic','animation_shot_plan':None,'resolved':result},indent=2)+'\n')
 print(OUT)
if __name__=='__main__': main()
