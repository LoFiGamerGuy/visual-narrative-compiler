from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/visual-refinement'
plan=json.loads((P/'comparison-plan.json').read_text());styles={x['id']:x for x in plan['styles']};chars={x['id']:x for x in plan['characters']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
common="""Use case: stylized-concept
Asset type: controlled original comic character-and-scene comparison board, landscape 3:2.
Input roles: Image1 is the drawing-treatment reference ONLY: its people, costumes, creature and world must NOT enter this image. Image2 is the shared cast IDENTITY sheet ONLY, not the desired rendering style. Image3 is the shared CREATURE identity sheet ONLY, not the desired rendering style.
Re-draw the requested subject in image1's distinctive drawing treatment. Keep the same identity, costume topology, body-type category, expression, camera, pose, creature and major world objects described below. The neutral setup's rendering must not override the style reference.
Composition: exactly two image zones separated by one thin plain vertical divider at35% width. Left35% a LARGE waist-up character portrait with quiet pale background. Right65% one scene showing the SAME character complete head to toe, one creature fully within frame, the broad plain arch, one water channel, low stone ledge and a small circular iron handwheel on its plain post. No text anywhere. Leave useful breathing room around the face and silhouette. Do not crop feet or creature.
Place: quiet daytime canal landing. One straight channel, one broad plain masonry arch in middle distance, simple closed sluice within arch, one low near-bank stone ledge, one iron handwheel on a plain post with a single short wooden crank on its rim. Large quiet sky and undecorated stone planes; one or two meaningful masonry seams only, no decorative architecture or crowds. Keep the handwheel modest so it does not dominate the character.
Creature: one large-pony-scale gentle jellyfish-turtle from image3 on the far right, facing LEFT toward the character, across a visible hand-to-creature gap. Broad low slate-blue shell, translucent pale lavender umbrella dome, calm broad turtle face, FOUR broad flowing tentacles, no additional legs. Simplify internal texture to fit the rendering. This creature has no coral, glowing particles, filigree or little hanging threads.
"""
tail="""Constraints: clearly adult subject; correct coherent hands; portrait and full-body identity match. Preserve subject shape and costume rather than importing the style-reference character. Organized form-specific detail and broad quiet regions. Face first, body gesture second, creature third, background subordinate. No luminous haze, visual noise, repeated ornament, scribble fields, extra people, extra creatures, labels, lettering, speech balloons, symbols, signature or watermark.
"""
jobs=[]
for e in plan['entries']:
 id=e['id']
 if e['kind']=='controlled':
  s=styles[e['style_id']];c=chars[e['character_id']]
  prompt=common+'Subject: '+c['subject']+'\nPose and expression: '+c['pose']+'\nDrawing treatment: '+s['rendering']+'\nPalette policy: '+s['palette']+'\n'+tail
  paths=[s['reference']['path'],'production/visual-refinement/setup/SETUP_CAST-P.png','production/visual-refinement/setup/SETUP_CREATURE-P.png']
 elif id=='X1':
  prompt="""Use case: stylized-concept
Asset type: exploratory original character/style mixture, landscape3:2. This is NOT a controlled comparison.
Input roles: Image1 supplies ONLY the retained adult character11: older stocky male keeper. Image2 supplies clear-line drawing treatment17 and calm visual organization. Image3 supplies ONLY broad canal-architecture shapes and decisive dark masses06; do not reproduce its noir rendering or character.
Create a two-zone board, portrait left35%, full body and one creature right65%, one thin vertical divider. Keep the adult male52 face from image1: broad flat nose, short gray beard, heavy lids, short gray hair, stocky thick-necked body and compassionate quiet smile. Simple woven poncho over loose dark robes, rope-fastened boots, plain crooked reed staff; no dense woven pattern or multiple dangling ornaments.
Render him with image2's clean rounded adult adventure-comic contours, gentle planar shading, readable facial features and warm flat color organization. Use image3's broad concrete arch and white/black architectural planes as a very quiet canal landing setting, a single water channel and low ledge. A small simplified root-legged island turtle based on image2 stands across the water: one smooth turtle shell with one tiny tree, six broad root legs, no busy miniature city. Warm terracotta-gray, mint, cream, muted blue and black. Full feet and creature silhouette visible, portrait large and inviting, scene breathable. No rejected image1 forest, moth-deer, dry-brush texture or snow. No tiny decorative fragments, sparkles, text, labels, symbols, signatures or watermarks.
"""
  paths=['production/visual-refinement/references/'+x+'.png' for x in ['11','17','06']]
 else:
  prompt="""Use case: stylized-concept
Asset type: exploratory original character/style mixture, landscape3:2. This is NOT a controlled comparison.
Input roles: Image1 supplies ONLY retained adult female character14. Image2 supplies sophisticated nearly realistic fashion facial drawing19 and one orchid creature concept. Image3 supplies economical cel-shadow grouping01; do not import its man, city or manta.
Create a two-zone board, large waist-up portrait left35%, complete full-body woman and one creature right65%, one thin vertical divider. Preserve image1's adult woman23 identity: long narrow face, delicate nose, warm brown eyes, slender upright build, very long lavender hair and soft mischievous smile. Simplified asymmetric lavender coat with one broad ruffle at hem over fitted midnight dress, long plain boots, one long silver sewing needle held at rest. No chains, floating loops, stars or jewelry clutter.
Combine image2's refined nearly realistic adult facial proportions, razor-clean thin contours and restrained silky gradients with image3's broad precise cel-shadow grouping on coat and body. Calm elegant confident adult presence. A quiet pale stone canal landing with one distant arch and wide pale sky. ONE isolated orchid creature across the water, image2's broad translucent black petals opening around a white hollow and six spare root legs. Keep petals few and clearly separated; no dense veins or trailing root forest. Bone white, black, lavender and a small deep-crimson accent. Strong face/body/creature hierarchy, generous empty regions, whole feet and creature visible. No image1 luminous fashion world, nebula moth, ribbon fields or luminous particles. No text, labels, signature or watermark.
"""
  paths=['production/visual-refinement/references/'+x+'.png' for x in ['14','19','01']]
 pp=P/'prompts'/(id+'-P.txt');pp.write_text(prompt)
 jobs.append({'id':id,'attempt_id':id+'-P','phase':'comparison','prompt_path':pp.relative_to(R).as_posix(),'prompt_sha256':sha(pp),'references':[{'path':p,'sha256':sha(R/p)} for p in paths]})
out=P/'comparison-jobs.json';out.write_text(json.dumps({'schema':'RefinementJobs/1','experiment_id':'VR-20260907-01','jobs':jobs},indent=2)+'\n')
out.with_suffix('.json.sha256').write_text(sha(out)+'  production/visual-refinement/comparison-jobs.json\n')
print('Frozen20 exact prompts with reference SHA256s.')

