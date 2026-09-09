from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'production/anchor-return'
master=Path('/home/gosnerp/.codex/skills/texture-refinement/references/master-prompt.txt').read_text()
cs={x['attempt_id']:x for x in json.loads((P/'candidates.json').read_text())['candidates']}
notes={
'NG01':'Preserve the two intact characters, city scale, bridge diagonals and clear sky-ray silhouette.',
'NG02':'Preserve the taut line from the held sword pommel to the left post, both planted boots and weapon ownership.',
'NG04':'Preserve the exact spear-shaft contact at the left upper arm, torn white shoulder seam, face expression and slack curved tether.',
'NG05':'Preserve the sliding silhouette, missed spear gap, right-post tether connected to sword pommel, torn left shoulder seam and all limbs.',
'NG07':'Preserve both kneeling recovery poses, sword and spear ownership and the actual visible wound and garment tear; do not relocate injury in this surface pass.',
'NG08':'Preserve the rear-view pose, hand at injured shoulder, actual injury side, sword, separated departing rival and huge sky creature.',
'BP01':'Preserve the clear air gap underneath the floating thorn root-foot, intact tailored coat and fine expressive face.',
'BP02':'Preserve the exact blade-to-petal contact, single sword, current hand ownership, intact root and all character anatomy.',
'BP03':'Preserve the planted single root and thorn foot contact, intact coat and anticipatory pose.',
'BP04':'Preserve the torn coat-tail holes and contact with sweeping petal, crouch, guarded hand near head, single sword and expressive face.',
'BP05':'Preserve the high camera, planted single root, flanking pose, planted palm and coat damage.',
'BP06':'Preserve the approaching blade and exact root relationship, intact root, all current coat holes, sword grip and bracing feet.',
'BP07':'Preserve the crucial clean air gap between severed hanging root and separate planted stump, cut surfaces and sword follow-through.',
'BP08':'Preserve the collapsed flower resting on the ground, separate severed stump, kneeling exhausted character, damaged coat and single sword.'}
out=[]
for ident,keep in notes.items():
 c=cs[ident+'-P']
 if ident.startswith('NG'):
  focus='Quiet the grainy scratched floor and competing reflections into broad matte blue-gray planes with only necessary seams and cast shadows. Group balcony foliage into calm leaf masses and distant windows into deliberate sparse light groups. Simplify microfacets and speckles on the ray, keeping its translucent navy silhouette and purposeful cyan lights. Preserve fine economical anime ink and soft face shading; do not make broad black cartoon outlines.'
  reason='Root native inspection: mottled reflective deck, many equally bright window/leaf speckles and fine ray facets compete with faces and contact; calmer source-preserving finish warranted.'
 else:
  focus='Turn the dense burgundy moss carpet into broad velvety maroon shadow masses with only selective leaf edges, especially beneath the figures and root. Reduce all-over petal vein webs and tiny bright pinpricks to sparse structural veins while retaining translucent overlapping charcoal petals, oval pale void, elegant tapered contours and delicate soft facial rendering. Group background vines; retain glasshouse ribs and pale atmospheric depth. Preserve this source’s refined illustrative treatment, never coarse cel shading or glossy 3D.'
  reason='Root native inspection: dense high-frequency maroon moss, petal veins, pinprick highlights and background vines overwhelm otherwise strong tailored character and flower silhouette.'
 prompt=master.replace('[name the features you love and must keep]',keep).replace('[name the specific surfaces or effects that feel too busy]',focus)
 prompt+='\nPreserve existing anatomy, handedness, damage and exact action even where imperfect. This pass only redraws surfaces, not structure or story state.\n'
 out.append(dict(source_attempt_id=c['attempt_id'],source_sha256=c['sha256'],attempt_id=ident+'-F1',phase='texture',reason=reason,prompt=prompt))
p=R/'research/anchor-return/encounter-finish-evidence-01.json';p.write_text(json.dumps(out,indent=2)+'\n');print(p)
