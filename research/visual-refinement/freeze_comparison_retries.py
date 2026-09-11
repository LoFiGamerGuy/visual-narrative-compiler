from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];P=R/'production/visual-refinement'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copyfile(P/'selected.json',P/'primary-selected.json')
jobs=[]
for sid in ['18','19']:
 for cid in ['A','B']:
  id=sid+'-'+cid
  treatment=('BOLD WESTERN 2D ANIMATION CARTOON. Reconstruct the forms with the changing thick contour, exaggerated adult face shape rhythm, elastic brows/mouth, big simplified hair locks, clean decisive silhouettes and broad flat cel-shadow masses in image2. The current thin, finely painted illustration in image1 is the documented failure. Redraw facial construction and all surface treatment, not just the color grade. No small mottled paint patches or realistic strands. A slender elegant male remains slender; a strong plus-size mature woman remains strong and plus-size. Match image2\'s actual cartoon language, not a generic anime face.' if sid=='18' else 'REFINED NEARLY REALISTIC FASHION ILLUSTRATION. Reconstruct facial planes and proportions with the sophisticated almost-real adult face drawing, fine razor-clean contours, smooth restrained silky tonal transitions, and elegant black/light shape design in image2. The current ordinary outlined painted-comic drawing in image1 is the documented failure. Redraw the facial rendering and surface treatment rather than only desaturating the colors. Skin should have smoothly organized form, no mottled flat paint patches. Keep the male\'s wine-red hair and the woman\'s brown skin, broad mature face and plus-size body; never substitute image2\'s pale split-haired man.')
  prompt=f"""Use case: style-transfer
Asset type: one targeted correction of a failed drawing-style transfer, landscape3:2.
Input1 is the EXACT CONTENT/IDENTITY/COMPOSITION edit target. Input2 is the DESIRED DRAWING STYLE only. Do not bring input2's characters, hair colors, costume, monster or background into the result.
Change the drawing treatment of the ENTIRE image1 to the actual rendering system visible in image2.
{treatment}
Preserve image1's same one adult character, recognizable face identity within the new stylization, age, body-type category, hair style/color, costume topology, expression, pose, two-zone composition, thin divider, same canal/arch/wheel objects and same jellyfish-turtle creature. Do not add a second human. The left portrait and right full body must still show the same adult. Preserve subject and object placement; this correction is specifically a drawing-treatment test, not a new pose or scene. Both human and creature must be rendered consistently in the new treatment.
Keep large quiet sky and stone regions, clean separation around the face and body, and detail organized around form. The original image1's fine painted texture is NOT a style reference. Image2's drawing language takes precedence. No lettering, captions, labels, symbols, signature or watermark.
"""
  pp=P/'prompts'/(id+'-R.txt');pp.write_text(prompt)
  refs=['production/visual-refinement/candidates/'+id+'-P.png','production/visual-refinement/references/'+sid+'.png']
  reason='Primary retains shared fine painted-comic construction instead of the original '+('bold western animation cartoon18' if sid=='18' else 'near-realistic refined fashion19')+' rendering. This retries the failed treatment transfer; primary geometry and framing limitations remain disclosed.'
  jobs.append({'id':id,'attempt_id':id+'-R','phase':'comparison','retry_of':id+'-P','retry_reason':reason,'prompt_path':pp.relative_to(R).as_posix(),'prompt_sha256':sha(pp),'references':[{'path':p,'sha256':sha(R/p)} for p in refs]})
plan={'schema':'RefinementRetryPlan/1','experiment_id':'VR-20260907-01','decision':'Lead selects4 style-transfer repairs18/19 A/B after all20 primary native/phone reviews. Independent primary-only recommendation02/13/15 and preferred crop repairs preserved separately. Repairing absent visual families is prioritized over framing-only edits.','mechanism_change':'Actual candidate as content target plus desired original style; remove both neutral setup reference inputs.','scope':'Drawing treatment only. Do not silently repair or accept clipped creatures,18-B missing wheel contact, wheel geometry or costume-material drift.','allowance':{'total_retry_limit':10,'this_phase':4,'remaining_after_successful_calls':6,'max_retry_per_asset':1},'jobs':jobs}
out=P/'comparison-retry-jobs.json';out.write_text(json.dumps(plan,indent=2)+'\n');out.with_suffix('.json.sha256').write_text(sha(out)+'  production/visual-refinement/comparison-retry-jobs.json\n')
print('Frozen four treatment-only retries; six retry slots remain afterward.')

