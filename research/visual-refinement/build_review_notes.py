"""Create brief source-bound observations for the owner reader; never owner votes."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/visual-refinement'
C={c['attempt_id']:c for c in json.loads((P/'candidates.json').read_text())['candidates']};S=json.loads((P/'selected.json').read_text())['selected']
style={
'01':'Recognizable clean illustration, but much fine painted construction carries over from the common setup; Nightglass transfer is partial.',
'02':'Warm outlined painting is visible and holds together at phone size. Facial construction still overlaps the neutral/01 group.',
'05':'Matte paint transfer is visible. Rough dark grain reduces body/wheel/background separation at phone size.',
'06':'Brush-ink masses are distinct, but broken water/paving marks add noise. The creature does not fully obey the limited-palette treatment.',
'13':'Precise tapered form hatching is distinct from06 brushwork and reads clearly in broad white groups. Palette limits are not fully followed.',
'15':'Curved and crossed engraving lines actually model forms. At phone width fine craft becomes warm tone and loses some small-scale separation; the result is more colored than the intended ink/parchment treatment.',
'17':'Broad clear fields are calm at phone size. Faces remain only modestly differentiated from the shared neutral illustration.',
'18':'The repair creates materially bolder contours, grouped hair and cartoon facial shapes. The creature remains more mottled than the cast. This used revised conditioning, not identical inputs.',
'19':'The repair adds smoother face/material modeling closer to the original fashion reference. It is still a partial transfer, with darker small-scale separation. This used revised conditioning, not identical inputs.'}
entries={}
for id,aid in S.items():
 c=C[aid];obs=[]
 if id.startswith('X'):
  obs=([ 'Retains the older keeper character in a quieter warm clear-line/canal mixture; broad adult face and sturdy build remain readable.','The creature/world and rendering also change, so this exploratory mix cannot rank the nine controlled directions.','This is a proposed component combination, not owner approval or a new production cast.' ] if id=='X1' else [ 'Retains the lavender-haired tailor character with more restrained coat shapes, quiet canal space and a single orchid creature.','The result is an exploratory19/01 mixture, not a controlled test of one rendering variable.','Character identity, costume simplification and creature detail still need owner judgment; no new owner preference is assumed.' ])
 else:
  sid,cid=id.split('-')
  obs.append('Iven remains recognizable by his refined long face, tied wine hair and slender build.' if cid=='A' else 'Mara remains a recognizable mature broad-faced adult with strong limbs; the torso is more fitted than the original16 reference, and the vest reads more like cloth than ceramic.')
  obs.append(style[sid])
  obs.append('The creature is cropped at the right edge; a complete silhouette and exact four-tentacle anatomy are not established. Wheel design, scale and landing placement also drift between boards.')
  if id=='18-B':obs.append('Required hand-on-wheel contact fails: the wheel-side hand remains at the hip, including in the style-only repair.')
  obs.append('Large portraits read at phone size. Tiny scene faces and finger topology need enlargement; owner visual comfort remains unknown.')
 entries[id]={'attempt_id':aid,'sha256':c['sha256'],'observations':obs}
report={'schema':'RefinementReviewNotes/1','experiment_id':'VR-20260907-01','reviewer':'Lead synthesis of actual native images and independent native/phone review; AI observations only','owner_approval':None,'entries':entries}
(P/'review-notes.json').write_text(json.dumps(report,indent=2)+'\n')
print('Bound observations to20 selected source images. No preference values written.')

