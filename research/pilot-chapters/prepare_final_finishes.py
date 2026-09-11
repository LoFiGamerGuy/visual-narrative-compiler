from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];r=R/'research/pilot-chapters';p=R/'production/pilot-chapters'
proposal=r/'independent-review/bounded-finish-proposal-02.json';entries=json.loads(proposal.read_text())['entries'];cs={e['attempt_id']:e for e in json.loads((p/'candidates.json').read_text())['candidates']}
assert len(entries)==34 and sum(a.endswith('-F1') for a in cs)==6
assert len({e['id'] for e in entries})==34
master=json.loads((r/'first-texture-spec.json').read_text())[0]['prompt'].split('Especially preserve:')[0]
focus_overrides={'NG08':'Fine repeated ray facets, cyan speckles, mesh roof microcontrast, city/window and foliage glints. Preserve translucent glass planes, selective lit windows and distance.','RC01':'Pervasive floor/bridge scratches, tiny shark scratches, cloud-edge flecks and sea foam. Retain intentional directional nib drawing and strong black/white masses.','ST16':'Chalk chips, grass/flower flecks, cart/fence wood grain, valley foliage subdivisions and small island facets. Retain broad opaque paint, cloud volume and soft wool.','FL11':'High contrast concrete scratch fields, waterfall speckles, white/magenta reflection fragments and minor coat splatter. Retain broad expressive black brushwork, mature facial lines, ribs and depth.'}
spec=[]
for e in entries:
 aid=e['source_attempt_id'];ident=e['id'];assert e['native_viewed'] and e['phone_viewed'];assert cs[aid]['sha256']==e['source_sha256'];assert not (p/'jobs'/(ident+'-F1.json')).exists()
 focus=focus_overrides.get(ident,'; '.join(e['observed_competing_surfaces']))
 prompt=master+'Especially preserve: '+e['protected_features']+'. Preserve every actual current hand, contact, object, costume and damage state as drawn. This pass must not repair or reinterpret a story inconsistency.\nFocus the simplification on: '+focus+'\nKeep selective expressive strokes and material distinctions; group repetitive marks within the existing forms.\n\nReturn one edited artwork, not a before/after composite. Do not add subjects, objects, text, labels or watermarks. Do not redesign the image.\n'
 spec.append({'source_attempt_id':aid,'attempt_id':ident+'-F1','phase':'texture','reason':'Root actual native inspection and independent native+phone-qualified bounded-finish-proposal-02.json SHA '+hashlib.sha256(proposal.read_bytes()).hexdigest()+': '+focus,'prompt':prompt})
(r/'final-texture-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
print('Prepared34 evidence-bound source-only finish specs; no tool calls.')
