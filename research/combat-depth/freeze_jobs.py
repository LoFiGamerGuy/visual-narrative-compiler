from pathlib import Path
import argparse,hashlib,json
R=Path(__file__).resolve().parents[2];P=R/'production/combat-depth';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((P/'plan.json').read_text());entries={e['id']:e for e in plan['entries']};lib={r['id']:r for r in plan['reference_library']}
controls_path=R/'research/combat-depth/controls/manifest.json'
controls=json.loads(controls_path.read_text())['controls'] if controls_path.exists() else []
lib.update({c['id']:c for c in controls})
a=argparse.ArgumentParser();a.add_argument('ids',nargs='+');a.add_argument('--batch',required=True);args=a.parse_args();jobs=[]
for id in args.ids:
 e=entries[id];aid=id+'-P';refs=[]
 assert 1 <= len(e['references']) <= 5, 'Built-in image tool accepts at most five reference paths'
 for key in e['references']:
  if key.startswith('@'):
   selected=json.loads((P/'selected.json').read_text())['selected'];cand={c['attempt_id']:c for c in json.loads((P/'candidates.json').read_text())['candidates']}[selected[key[1:]]]
   rr={k:cand[k] for k in ['path','sha256']};rr['role']=f'Exact recurring subject/place reference from {key[1:]}; use named identities/creature and relevant geography only, not its composition or surface noise.'
  else:
   rr={k:lib[key][k] for k in ['path','sha256']};rr['role']=(lib[key].get('role','')+' This is a spatial/control guide only: do not copy diagram rendering, colors, labels or arrows into the artwork. Translate a top-down plan into the camera requested by the scene brief; do not adopt a map camera unless this scene explicitly calls for it.' if key.startswith(('map-','guide-')) else lib[key].get('role',key.title())+' Use only the specified identity/drawing/construction traits. Make a genuinely new composition/action; no reference-sheet divider or portrait inset.')
   if key.startswith(('map-','guide-')): rr.update(control_source_path=lib[key]['source_path'],control_source_sha256=lib[key]['source_sha256'])
  assert sha(R/rr['path'])==rr['sha256'];refs.append(rr)
 framing='Portrait 1024x1536, vertical single image.' if e['scale']=='vertical-wide' else 'Landscape 1536x1024, single complete composition.'
 prompt='Use case: illustration-story.\nNew original progression-fantasy scene: '+e['title']+'. '+framing+'\nCAMERA AND ACTION PRIORITY: '+e['brief']+'\n'
 prompt+='Input images:\n'+'\n'.join(f'Image {i+1}: '+rr['role'] for i,rr in enumerate(refs))+'\n'
 prompt+='Drawing treatment: deliberate original Nightglass action-comic illustration with appealing precisely drawn adult faces, confident selective contours, designed hair locks, rich angular silhouettes and broad opaque material planes with restrained soft modeling. Let mood and light follow THIS new setting. Calm material interiors, grouped highlights, mostly unmarked stone and fabric; purposeful details prove depth and function. Not glossy 3D, blur, airbrush, flat vector shapes or a grainy texture overlay. No all-over crack networks, tiny facets, etched ornament, hundreds of equal strands, glitter reflections, fleck storm or generic aura. A large world must remain inhabited and sophisticated while its surfaces give the eye rest.\n'
 if e.get('power'):prompt+='Power context, do not letter or illustrate future levels simultaneously: '+e['power']['description']+' Limitation: '+e['power']['limitation']+'\n'
 prompt+='All combatants and visible bystanders are adults; recurring identities and complexion follow the supplied references. Create cast variety through faces, builds and fighting styles. Visceral impact comes from loaded bodies, recoil, forceful contact, expression and consequences, not visual noise.\n'
 if e.get('state'):prompt+='Persistent state for this moment: '+json.dumps(e['state'])+'. Do not heal or reset earlier damage within this fight.\n'
 prompt+='Keep the specified camera distance; a tiny figure stays small without any enlarged face insert. Recurring adults recognizable by silhouette/costume/weapon in wide shots and by distinctive face/expression in close shots. One newly composed scene only, no panels, portrait divider, collage, text, diagram arrows, HUD, logos, watermark or copied franchise design. Precise anatomy and functional grips; concentrate detail at faces and actual contacts.\n'
 rel=f'production/combat-depth/prompts/{aid}.txt';out=R/rel
 if out.exists():assert out.read_text()==prompt
 else:out.write_text(prompt)
 assert not(P/f'calls/{aid}.json').exists()
 jobs.append(dict(id=id,attempt_id=aid,phase='primary',category=e['category'],prompt_path=rel,prompt_sha256=sha(out),plan_sha256=sha(P/'plan.json'),references=refs,prompt=prompt))
out=P/(args.batch+'-jobs.json');raw=json.dumps(jobs,indent=2)+'\n'
if out.exists():assert out.read_text()==raw
else:out.write_text(raw)
print(str(out))
