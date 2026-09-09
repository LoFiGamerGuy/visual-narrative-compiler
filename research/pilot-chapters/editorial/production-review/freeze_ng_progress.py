from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((R/'production/pilot-chapters/candidates.json').read_text())['candidates']
N={
'NG07-P':('Roof/hatch geography explicit: Aren on car roof over harnessed Pell; right sword and cyan line behind grip to upper post are particularly clear.','One knee/left palm support replaces two-boot stance. Car has multiple suspension elements.','Strong transfer; no repair priority.'),
'NG08-P':('Huge wing dwarfs protagonist and skyline; clear beak threat and raised blade.','Aren now stands on broad bridge beside bridge post while car hangs separately left, contradicting his established roof position in NG07 and return to car in NG10. Line slack rather than taut; beak already at blade.','High comparative repair candidate: restore car roof/hatch beneath protagonist while preserving giant threat scale.'),
'NG10-P':('Blade/beak contact, planted legs and displaced ray support counterbeat; lower hem tear finally readable, wallet absent.','Line attaches blade tip rather than pommel; sword is much longer recurved object, body uses two-handed grip. Deflection reads more as opposition than clearly upward pull.','Disclose power/weapon inconsistency; NG08 geography is larger chapter disruption.'),
'NG11-P':('Pell grips Aren forearm; harness remains worn and loose safety strap hangs inside car. Immediate rescue preparation is legible.','Aren holds sword in anatomical left and offers right forearm, reversing contract but matching NG12 actual art. Ray persists behind but disengaged.','Clasp works; do not spend repair solely for side swap.'),
'NG13-P':('Three adults visibly safe, Sera grips Pell harness shoulder, gate closed, wallet absent from Aren; both rescue and missed opportunity supported.','Line disappears rather than visibly slack; sword held right again. Texture on floor active.','Strong immediate resolution, no structural repair priority.'),
'NG16-P':('Separate black envelope, restored cream belt wallet, torn lower jacket and descending stairs toward cyan lower door open the next route.','Envelope anatomical right rather than specified left; sheathed sword side partly obscured.','Series hook visually legible; no repair solely for hand.'),
'NG09-F1':('Quieter ray planes, jacket and architecture retain face/contact/line and removed wallet.','Guard-origin tether and unclear hem tear persist from R; surface finish is not structural repair.','Useful finish with unchanged semantic caveats.'),
'NG12-F1':('Quieter large city masses and body shapes retain rescue/car separation, clear line and no wallet.','Forward guard ring and reversed sides persist.','Useful finish with unchanged semantic caveats.'),
'ST02-F1':('Woodgrain, hair facets, clothes, vegetation simplified while expressive faces and remote bell-carrying ram remain.','Bell throat/horn ambiguity persists; distant ram scale not verified.','Useful finish; premise improvement preserved.'),
'FL05-F1':('Concrete speckles replaced by broad scraped patches; pool clue and hand remain focal, no coat-pocket or early eel regression.','Concentric ripples still coexist with sharp memory; possible wrong-hand orientation persists.','Useful medium-preserving quieting; power rule caveat unchanged.')}
rows=[]
for aid,(s,g,p) in N.items():
 c=next(x for x in r if x['attempt_id']==aid);assert sha(R/c['path'])==c['sha256'];row={'attempt_id':aid,'path':c['path'],'sha256':c['sha256'],'prompt_sha256':c['prompt_sha256'],'call_sha256':c['call_sha256'],'native_inspected':True,'phone_inspected':False,'strength':s,'gap':g,'priority':p}
 if '-F' in aid:
  src=next(x for x in r if x['attempt_id']==c['id']+'-R1');row.update(source_attempt_id=src['attempt_id'],source_sha256=src['sha256'])
 rows.append(row)
o={'schema':'PilotEditorialProgressiveNativeReview/1','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':sha(R/'production/pilot-chapters/plan.json'),'scope':'Six new NG native panels plus four source-only finishes inspected. Root geography/endpoint concerns known; corroborating author review. NG14/15 not present at review; no complete chapter acceptance.','reviews':rows}
p=O/'ng-progress-six-and-four-finishes.json';p.write_text(json.dumps(o,indent=2)+'\n');print(sha(p))
