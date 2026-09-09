import json,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent

def freeze(name,notes,summary):
 candidates={x['attempt_id']:x for x in json.loads((ROOT/'production/anchor-return/candidates.json').read_text())['candidates']}
 controls={x['id']:x for x in json.loads((ROOT/'production/anchor-return/controls/manifest.json').read_text())['controls']}
 sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
 records=[]
 for aid,findings in notes.items():
  c=candidates[aid];ctrl=controls[c['id']];call=json.loads((ROOT/c['call_path']).read_text());control_ref=[x for x in call['references'] if x['path']==ctrl['png_path']]
  direct_control=bool(control_ref)
  if not control_ref:
   primary=candidates[c['id']+'-P']; primary_call=json.loads((ROOT/primary['call_path']).read_text())
   control_ref=[x for x in primary_call['references'] if x['path']==ctrl['png_path']]
  assert len(control_ref)==1
  assert sha(c['path'])==c['sha256']
  assert sha(ctrl['png_path'])==ctrl['png_sha256']==control_ref[0]['sha256']
  records.append({'attempt_id':aid,'image_path':c['path'],'image_sha256':c['sha256'],'native_dimensions':[c['width'],c['height']],'call_path':c['call_path'],'call_sha256':sha(c['call_path']),'control_reference':control_ref[0],'control_sent_directly_in_this_call':direct_control,'actual_call_references':call['references'],'plan_sha256':call['plan_sha256'],'native_inspected':True,'phone_inspected':False,'observations':findings,'owner_approval':None})
 payload={'schema':'AnchorReturnControlTransferReview/1','reviewer':'combat_reference_research','reviewed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual native staging/contact/state transfer; observations are reviewer judgments, not owner preferences. No generation or display changes. Controls are schematic and cannot guarantee physically solved pose.','summary':summary,'records':records}
 (OUT/name).write_text(json.dumps(payload,indent=2)+'\n')

if __name__=='__main__':
 freeze('batch-01-NG.json',{
 'NG01-P':{'transferred':['High diagonal bridge, lift left and round doorway right, separated characters, ray/city scale and no tether/damage. Weapons held with complete feet visible.'],'gaps':['Humans occupy about one quarter to one third image height versus much smaller extreme-wide staging; city still reads large. Deck contains mottled surface and bright doorway reflections.'],'priority':'No structural repair recommended from this frame alone.'},
 'NG02-P':{'transferred':['Both grounded boots and low camera; one taut cyan line visibly connects left rail ring to sword pommel. Two distinct spear grips and clear gap between opponents.'],'gaps':['Ray appears behind action although plan restricts it to opening/ending; adds repeated high contrast background focus. Rear/right arm sword ownership is readable, but rigid symmetric spread is more guarded posing than visibly resisted tension.'],'priority':'Endpoint transfer is strongest of inspected active-tether frames.'},
 'NG03-P':{'transferred':['Forward body lean, spread planted legs, extended right sword and Sera two-grip interception; low oblique full-body framing.'],'gaps':['Cyan line terminates at an extra ring on hero back/hip, not the actual sword pommel clearly visible at extended fist. Changes the power load path. Blade and shaft overlap but no strong compressed contact/consequence. Ray remains a prominent repeated background subject.'],'priority':'High: actual sword-pommel endpoint is a causal repair candidate.'},
 'NG04-P':{'transferred':['True close torso crop, Sera shaft reaches hero anatomical LEFT upper arm, torn left shoulder seam starts, face recoils. RIGHT sword held outside guard; curved slack line leaves its pommel.'],'gaps':['Rail endpoint cropped; cannot verify full slack line termination from image. No boots visible by deliberate close framing, not missing anatomy. Persistent ray adds background distraction.'],'priority':'Strong contact/state transfer; preserve rather than spend repair here.'},
 'NG06-P':{'transferred':['Low oblique camera and two visibly grounded hero boots, Sera torso leaning back; a sword visibly reaches spear shaft. LEFT shoulder tear remains.'],'gaps':['Hero has two visible sword hilts, one in rear anatomical RIGHT hand and another weapon in extended anatomical LEFT hand. Contact sword therefore held on wrong side. No taut line to right anchor is visible; planned pulling cause is absent. Contact lies near Sera grip, and body reaction lacks the planned front-knee torque/rear-heel lift.'],'priority':'Highest inspected causal break: rebuild one right-hand sword/pommel-to-right-anchor load path and contact. A texture-only edit cannot fix this.'},
 'NG07-P':{'transferred':['Both kneel and visibly catch breath, blade grounded beside boot, Sera braces palm and holds spear safely outward. Strong readable aftermath expressions.'],'gaps':['Hero tear moves to anatomical RIGHT shoulder (image left), inconsistent with NG04/06 left tear. LEFT hand crosses to protect that wrong shoulder. Sera appears to brace RIGHT palm and hold spear LEFT, reversing planned sides. No short spent line visible beyond pommel ring. Ray remains prominent.'],'priority':'State continuity gap; do not declare sequence anatomically consistent.'}
 },'Six available NG primary natives inspected. Layouts improve camera and contact readability, but NG06 loses the causal power path and duplicates the weapon; NG03 uses wrong tether endpoint. NG04 is the strongest direct contact-state transfer. NG05/08 and BP/ST encounter natives were not yet available for this bounded batch.')
