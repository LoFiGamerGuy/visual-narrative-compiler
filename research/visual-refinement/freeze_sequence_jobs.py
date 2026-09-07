"""Freeze the shared six-panel sequence for explicitly selected provisional treatments."""
from pathlib import Path
import json,hashlib,copy
R=Path(__file__).resolve().parents[2];P=R/'production/visual-refinement'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
decision=json.loads((P/'provisional-selection.json').read_text());ids=decision['style_ids'];assert len(ids)==3 and len(set(ids))==3
comparison=json.loads((P/'comparison-plan.json').read_text());styles={s['id']:s for s in comparison['styles']}
candidates={c['attempt_id']:c for c in json.loads((P/'candidates.json').read_text())['candidates']};selected=json.loads((P/'selected.json').read_text())['selected']
story=json.loads((P/'sequence-design/panel-plan.json').read_text());controls=json.loads((P/'sequence-design/shot-controls/v5/manifest.json').read_text());control={c['panel']:c for c in controls['panels']}
plan=copy.deepcopy(story);plan['schema']='RefinementSequencePlan/1';plan['status']='Provisional technical sequence tests; owner approval remains null.'
plan['provisional_styles']=[{'id':s,'title':styles[s]['title'],'selection_basis':decision['reasons'][s]} for s in ids]
plan['control_adjustments']=['P06 open gate is visibly staged behind the adults in the gap between faces rather than far background-left; plot, gate state and exact copy unchanged. P05 guide face occlusion and edge proximity are not final-art requirements.']
plan['panels'][5]['required_visible']=[x.replace('Open gate remains behind at left;', 'Open gate remains visible behind the adults;') for x in plan['panels'][5]['required_visible']]
plan['panels'][5]['shot']=plan['panels'][5]['shot'].replace('in quiet background left','in the quiet gap behind the adults')
plan['owner_approval']=None;plan['selection_record']={'path':'production/visual-refinement/provisional-selection.json','sha256':sha(P/'provisional-selection.json')}
plan['conditioning_policy']='Same per-shot editable composition guides across treatments; each treatment uses its selected A/B boards for adult identities, creature and actual drawing. No neutral setup sheet is passed separately. These are intent controls, not calibrated geometry or proof of generated compliance.'
out=P/'sequence-plan.json';out.write_text(json.dumps(plan,indent=2)+'\n');out.with_suffix('.json.sha256').write_text(sha(out)+'  production/visual-refinement/sequence-plan.json\n')
base="""Use case: illustration-story
Asset type: ONE finished original sequential-comic panel, no lettering.
Input roles: Image1 is an editable POSE/COMPOSITION/PROP-STATE guide ONLY. Its flat schematic people, crude faces, colors and line style are NOT final artwork. Images2 and3 are the selected full artwork references for Iven and Mara respectively: use their recognizable adult identities, costume topology, shared jellyfish-turtle creature and actual drawing treatment. Do not reproduce their split portrait/scene board layout.
Render a single cohesive narrative panel. Follow image1's intended camera, actor placement, hand/prop contacts and gate state, while replacing every schematic form with convincing adult anatomy and finished drawing in images2/3's treatment. Improve perspective naturally; do not leave a technical diagram or stiff mannequin. Keep a safe margin around required feet/hands/props. Image1's silhouettes are approximate, never a reason to slim Mara or make adults childlike.
Iven: adult male27, slim dancer build, long refined oval face, delicate nose, violet eyes, wine-red hair loosely tied low, small pearl earring; ivory poet sleeves, plain plum waistcoat, slim high-waisted black trousers, black boots.
Mara: adult woman38, powerful plus-size build and broad waist, warm brown skin, broad mature face/nose, full lips, thick blue-black braid; plain ivory cropped vest, magenta loose trousers, wrapped sandals and one blue upper-arm band. Keep her mature and strong. Both adults must remain consistent with references and each other.
Place: one quiet daylight canal, one broad plain masonry arch, a single vertical sliding sluice, low dry near-bank ledge and one iron circular handwheel on a plain post. The wheel is VERTICAL, facing camera, with one wooden grip mounted on its rim. The guide governs its orientation, overriding horizontal wheels in the old comparison boards. No extra wheel, gate, crank or tools. Keep a simple credible connection between wheel post and gate jamb, without decorative machinery.
Creature if in view: same gentle large-pony jellyfish-turtle, low broad slate-blue shell and translucent lavender umbrella dome, calm round turtle face and FOUR broad flowing tentacles, no extra turtle legs, coral, fringe or bright particles. Travels only left-to-right through the gate. Water stays calm and at equal level; the action is clearance, not a flood.
Story continuity: one intact wooden grip in P01/P02; in P03 it snaps into exactly two pieces, a SHORT mounted stub and a LONG detached piece held in Iven's anatomical RIGHT hand. Stub stays on wheel; detached piece remains in his RIGHT hand for P03–P06. No extra debris. Gate closed P01–P03, partly raised P04, fully raised P05–P06.
"""
tail="""Visual priorities: acting/hand action first, physical story second, quiet environment third. Adult faces, arm origins and intended prop contacts should read at ordinary phone size. Clear silhouettes and grouped light/dark areas, no gratuitous texture, sparkles or little decorative fragments. Do not put any text, dialogue, letters, SFX, captions, labels, arrows, diagram marks, signatures, watermark, page number, inset portrait or second panel into the image. Exact dialogue will be lettered separately in the reader.
"""
jobs=[]
for sid in ids:
 s=styles[sid]
 for p in plan['panels']:
  pid=p['id'];id=sid+'-'+pid;c=control[pid];a=candidates[selected[sid+'-A']];b=candidates[selected[sid+'-B']]
  refs=[c['png'],a['path'],b['path']]
  prompt=base+'\nDRAWING TREATMENT: '+s['rendering']+'\nUse the actual selected reference images2/3 as the visual treatment anchors; do not introduce a different look.\nRequested panel aspect ratio: '+p['aspect_ratio']+'.\nShot: '+p['shot']+'\nThis panel: '+p['story']+'\nAction: '+p['action']+'\nExpression: '+p['expression']+'\nRequired visible relationships: '+'; '.join(p['required_visible'])+'.\nContinuity for this moment: '+p['continuity']+'\n'+tail
  pp=P/'prompts'/(id+'-P.txt');pp.write_text(prompt)
  jobs.append({'id':id,'attempt_id':id+'-P','phase':'sequence','style_id':sid,'panel_id':pid,'prompt_path':pp.relative_to(R).as_posix(),'prompt_sha256':sha(pp),'references':[{'path':x,'sha256':sha(R/x)} for x in refs],'requested_aspect_ratio':p['aspect_ratio'],'copy_source':{'path':'production/visual-refinement/sequence-plan.json','sha256':sha(out),'panel_id':pid}})
j=P/'sequence-jobs.json';j.write_text(json.dumps({'schema':'RefinementJobs/1','experiment_id':'VR-20260907-01','jobs':jobs},indent=2)+'\n');j.with_suffix('.json.sha256').write_text(sha(j)+'  production/visual-refinement/sequence-jobs.json\n')
print('Frozen18 sequential primary prompts and source/copy bindings.')

