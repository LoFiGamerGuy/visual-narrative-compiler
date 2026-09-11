from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
plan=json.loads((R/'production/pilot-chapters/plan.json').read_text())
TEST={'NG01','NG02','NG09','NG12','ST02','FL05'}
# Geometry-only replacement removes defaults that silently recreate transferred/stowed props.
EQUIP={
'aren':'One solid silver crescent-edge short sword with black straight hilt and cyan pommel ring, anatomically RIGHT-handed when drawn. One flat sealed cream dispatch wallet. Do not assume either is in his hand or on his belt: the exact current inventory below controls position and possession.',
'sera':'One simple black short spear. Keep it outside tight hand-transfer crops unless explicitly required. Do not add a handheld spear that occupies a hand required for the current action.',
'pell':'Plain body harness WORN around torso. Its separate safety tether and rail attachment follow current state. No external rig or extra pole.',
'ilyra':'One silver single-edge saber with open oval black guard, anatomically RIGHT-handed when drawn. Silver guard on LEFT forearm, small plain silver collar clasp. Current state determines sheathed versus drawn; do not duplicate the saber.',
'neris':'Plain iron door key on waist cord, not being used. The caretaker door is weight-jammed, not mechanically locked.',
'bloom':'One thick botanical root and one broad thorn foot; all current root grounding/sever state is specified below. No default intact root when the body is severed.',
'tavi':'Two rounded red gauntlets: anatomical RIGHT cream circle pressure plate; anatomical LEFT cream crescent. Cream waist belt and one detachable turquoise cloth padding strip. Current inventory controls cloth location, gauntlet damage and charge; do not default to an attached turquoise waist tail.',
'mara':'Plain rope halter and small tallybook. Any bell possession is governed by current inventory, not by her role as caravan captain.',
'ram':'One plain brass signal bell about human-head height, with a wide opening and simple strap. The exact current inventory controls whether this bell is on the horn, a fence peg, in Mara’s hand or aboard the caravan. Never duplicate it.',
'ren':'Two red combat gauntlets: RIGHT has a broad black central loading plate, LEFT has a plain smooth red back. Current state exclusively controls charge, damage and wrist mark; no initial-state assertion applies across the story.',
'vexa':'One small iron upper-ring entry key and folded spectator permit. Current state controls key ownership and whether it is visible; never retain a duplicate key after transfer.',
'corin':'One long straight iron ward-pole with a broad simple solid C-shaped head. Upper shoulder and lower curve can make two jaw countercontacts. Small plain black notebook. Current state controls hands, pole position and carried clues; no extra hook or alternate pole.',
'lio':'One small brass municipal sluice key with a simple TRIANGULAR head. Current inventory exclusively controls neck cord, transfer or absence from Lio. No duplicate neck key after transfer.'}

def inventory(e):
 cid=e['chapter_id'];n=e['sequence_order'];s=[]
 if cid=='NG':
  s.append('Aren sword '+('sheathed at RIGHT hip; both hands free unless handling wallet.' if n<=4 or n>=14 else 'is the ONE drawn sword in anatomical RIGHT hand. LEFT hand is the rescue/free hand; never mirror these roles.'))
  if n<=4:s.append('One sealed cream dispatch wallet belongs to Aren, on belt unless held in the specified action. Sera has no wallet yet.')
  elif n==5:s.append('The ONE sealed cream dispatch wallet is transferring from Aren to Sera. Aren’s belt pouch is empty; no second white wallet remains on him.')
  elif n<=13:s.append('The cream dispatch wallet is with Sera, stowed in her coat pocket outside action crops. Aren has NO cream wallet, envelope or white dispatch case on belt or in either hand.')
  elif n==14:s.append('Sera returns the ONE unopened cream dispatch wallet to Aren. Show this transfer; no duplicate remains with Sera.')
  else:s.append('The original sealed cream dispatch wallet is back on Aren’s belt. The separate black envelope '+('is in Pell’s hand for the offer, not already on Aren.' if n==15 else 'is in Aren’s LEFT hand. No extra black envelopes.'))
  s.append('Jacket '+('fully intact, no tears.' if n<=8 else 'has the single ragged REAR LOWER HEM tear introduced in the encounter. Preserve sleeves and shoulder seams; do not convert hem damage into a missing sleeve.'))
  if n<=5 or n>=14:s.append('No active cyan tether. Do not copy a line from later panels or anchor art.')
  elif n<=12:s.append('One taut cyan tether runs from the cyan POMMEL RING BEHIND the right sword grip to the SAME heavy bridge post above/right. It never joins blade tip, blade edge, hip, clothing or Pell. Crop an endpoint only where the assigned close framing explicitly requires it.')
  elif n==13:s.append('The same pommel line is now slack; sword remains in Aren’s right hand beside him. No new anchor.')
  if 3<=n<=10:s.append('Pell wears body harness; a separate safety tether remains clipped to lift rail. The maintenance car remains attached to its suspension cable.')
  elif n==11:s.append('Pell’s safety tether is unclipped from the rail and left hanging in the car. Harness stays WORN. Aren’s free LEFT forearm clasps Pell; right hand keeps the sword.')
  elif n>=12:s.append('Pell still wears harness but has no tether to the falling car. '+('The car is EMPTY and physically separate below; one adult forearm clasp connects Pell to Aren’s LEFT arm.' if n==12 else 'Both rescued adults are safely supported on the bridge when visible.'))
  if n==3:s.append('Pell is inside the lift but outside this beak/coupling close crop; do not insert a whole person into the mechanical insert.')
 elif cid=='BP':
  s.append('Ilyra’s one saber '+('is sheathed; do not place an additional blade in her hand.' if n<=4 or n>=14 else 'is drawn in anatomical RIGHT hand; silver guard stays LEFT.'))
  s.append('Coat '+('intact, no premature tear.' if n<=7 else 'retains one ragged REAR HEM tear; do not spread damage across both sleeves or create multiple unrelated shredded tails.'))
  if n==1:s.append('Flower is distant silhouette; do not reveal captive or detailed root outside specified crop.')
  elif n==2:s.append('Flower and Neris remain outside this close framing. The heard voice has no visible human speaker or apparition.')
  elif n==6:s.append('ONE complete root/foot visibly lifted clear of threshold; no planted stump or severing. Door opens only a finger-width as weight releases.')
  elif n<=10:s.append('ONE intact root/foot is PLANTED across room threshold, jamming it with weight. Face orientation stays fixed during each rooted commitment; do not show a separate free head rotating toward Ilyra.')
  elif n==11:s.append('Root severed with open air gap. Short stump is loose/unweighted, not still rooted to room or pinning door. Whole heavy bloom tips away.')
  elif n>=12:s.append('Severed bloom lies inert on floor, with physically separate loose stump shifted clear of door. Room door is OPEN and Neris free. Do not restore intact root or standing live bloom.')
  if n<=12:s.append('No recovered clue packet/button/slip yet in Ilyra’s hands.')
  elif n==13:s.append('Single sealed paper packet with silver broken-leaf seal is lifted by LEFT guarded hand; right saber lowered. No duplicate packet.')
  elif n==14:s.append('Opened packet contains one dark coat button and nursery slip in Ilyra’s LEFT palm. Saber sheathed. No required readable prop text; nursery identity is dialogue.')
  else:s.append('Button and nursery slip retained together in packet, stowed inside Ilyra’s coat unless explicitly shown. Hands do not acquire new clue copies.')
  if n==16:s.append('Second bloom is only a distant silhouette in a separate frosted bay. The defeated first bloom does not resurrect.')
 elif cid=='ST':
  s.append('Anatomical RIGHT glove = cream CIRCLE; anatomical LEFT glove = cream CRESCENT. Follow shoulders through elbows to wrists, not screen-left/right.')
  s.append('LEFT crescent glove '+('intact, no chip.' if n<=5 else 'has one exposed chipped outer knuckle edge; retain this same damage. RIGHT circle remains intact.'))
  if n<=7:s.append('Whole turquoise cloth strip is still tied at Tavi’s waist over cream belt. It is not already on bell/clapper.')
  elif n in [8,9]:s.append('Whole turquoise cloth strip is FULLY DETACHED from waist and held/folded in Tavi’s hand. Cream belt remains, with NO turquoise waist tail.')
  elif n==10:s.append('Detached turquoise cloth is being folded around the clapper INSIDE the large bell. No cloth connection back to Tavi’s waist; cream belt remains plain.')
  else:s.append('Turquoise cloth is now tied as padding around bell clapper, not at Tavi’s waist. No second cloth tail on her; cream belt unchanged.')
  if n<=10:s.append('The ONE brass bell hangs by its simple strap from ram’s near horn, beside its sensitive ear. There is NO bell on a fence peg, in Mara’s hand or aboard caravan yet. If ram/horn are cropped out, bell is offscreen too.')
  elif n in [11,12]:s.append('The ONE padded brass bell has been removed from horn and hangs on the fence peg. Ram’s horns are bare; Mara does not yet hold it.')
  elif n==13:s.append('The ONE padded brass bell is now held by Mara. Peg and ram horn are empty.')
  elif n in [14,15]:s.append('Padded brass bell remains with Mara/caravan, outside close action framing where necessary. Ram has no bell. Do not put bell back on fence or horn.')
  else:s.append('Padded bell is aboard caravan; no bell on ram or Tavi.')
  s.append('RIGHT charge '+('is one small contained disk, only with both boots braced.' if n in [4,11] else 'is releasing only as the short narrow puff aimed at padded bell.' if n==12 else 'is absent/spent; no aura or hidden second charge.'))
  if n==5:s.append('Airborne loss of footing dissipates the previously held charge; intact right plate is unlit.')
  if n in [6,7]:s.append('Ram stays GROUNDED and is not starting a new leap/charge behind Tavi’s landing or observation.')
  if n==2:s.append('Ram and its horn bell are OFFSCREEN in this two-shot. Mara points toward that offscreen direction, not to a nearby fence bell. No additional ram body is needed in the two-shot.')
  if n==10:s.append('Bell opening is broad enough for gauntlets; show a simple existing cloth knot/fold, not intricate finger weaving.')
 elif cid=='RC':
  s.append('One RIGHT broad black-plate gauntlet and plain LEFT red glove; do not swap symbols or attacking arm.')
  s.append('RIGHT plate '+('dark/unloaded.' if n<=4 else 'begins loading at the single physical fin contact.' if n==5 else 'holds one contained red load, no second charge.' if n<=9 else 'releases its one load through the actual RIGHT fist/jaw contact.' if n==10 else 'dark/spent, not still charging.'))
  s.append('RIGHT wrist '+('unmarked with no red debt band yet.' if n<=12 else 'now has the thin red debt band; right hand is numb. LEFT wrist stays unmarked.'))
  s.append('Ivory vest '+('intact.' if n<=5 else 'has the side-seam rip from the skid. Do not restore the intact sheet costume.'))
  if n<=11:s.append('The ONE upper-ring entry key still belongs to Vexa, held or on her cord when she is present. Ren has NO key.')
  elif n==12:s.append('The ONE entry key transfers from Vexa into Ren’s LEFT hand. No duplicate remains on Vexa’s cord.')
  else:s.append('Ren holds the earned entry key in LEFT hand. Vexa has no key on cord or in hand; no duplicate prize.')
  if n<=9:s.append('Trial shark lower jaw intact, no early dent.')
  elif n>=10:s.append('Trial shark lower jaw has one bent/dented plane from the counter when visible; no blood or extra swarm.')
  if n in [15,16]:s.append('The sea lender is only a distant dark silhouette/eye, not a second giant foreground combat shark or a humanoid debtor.')
 elif cid=='FL':
  s.append('Corin '+('wears plain black gloves on BOTH hands.' if n<=3 else 'has a BARE LEFT hand and black-gloved RIGHT. Do not put the removed left glove back on.'))
  if n<=3:s.append('Ward-pole held upright or safely aside as action permits; not already wedged in a creature. Wet work coat belongs to Ada/Lio, separate from Corin’s worn white coat.')
  elif n<=6:s.append('Single C-head ward-pole lies safely on dry ledge, not in Corin’s active pool-touching hand. LEFT bare fingertips perform memory touch. No second pole.')
  elif n<=9:s.append('One pole is retrieved/held as action specifies; C-head does not yet hold jaws apart.')
  elif n<=12:s.append('Single solid C-head at near mouth corner: upper shoulder props UPPER jaw, lower curve retains LOWER lip. Straight shaft and both Corin grips stay outside the far-side victim-exit opening. Preserve two countercontacts; no magical mouth-opening claim.')
  else:s.append('Pole has been released from eel and is free with Corin. All adults are safe on dry ledge; eel remains below in canal, no ongoing victim inside mouth.')
  if n<=13:s.append('The ONE triangular-head brass sluice key stays on Lio’s neck cord whenever his actual body is visible. Corin has no key yet. Do not invent a key in pool memory unless specifically visible.')
  elif n==14:s.append('The ONE triangular-head brass key hangs visibly at living Lio’s throat; Corin notices it but does not yet hold it.')
  elif n==15:s.append('Lio’s PARTIAL hand transfers the ONE triangular brass key to Corin’s bare LEFT palm. Lio no longer has a second key at his throat. Show only his hand/forearm at edge, not an extra full body.')
  else:s.append('Corin holds the ONE triangular brass key in bare LEFT hand and pole in RIGHT; Lio neck cord is empty. No duplicate key.')
  if n in [4,6]:s.append('The memory surface is a shallow stone-bounded puddle physically ON THE GROUND beside the canal, separate from the deep moving water. Do not depict a garment pocket, held cloth basin, lifted coat hem or coat lining. No creature, eel body, ribs, mouth or shadow is visible yet. Ada and Lio remain outside this assigned close framing; no extra people or silhouettes.')
  if n==5:s.append('Lio memory is confined to still pocket and shows him AWAKE reaching toward the sluice wheel. Remove later exhausted/unconscious acting defaults from this memory depiction. No present-day Lio body.')
  elif n==6:s.append('Water ripple has erased the entire memory; no lingering Lio reflection or ghost.')
  if n<9 and n!=5:s.append('No visible Lio body yet. Do not include him just because his clothes/key are mentioned.')
  if n in [9,10,11]:s.append('Only readable portions of Lio appear in mouth; no duplicated person on ledge. FL09 includes his wet heel touching ledge to explain the single footprint.')
  if n>=7:s.append('Wet discarded work coat stays on dry ledge away from rescue mechanics unless explicitly picked up; do not dress Lio in it or duplicate a new coat.')
 return ' '.join(s)

SAFE_TWO_SHOTS={'NG05','NG14','NG15','BP14','BP15','ST13','ST15','RC02','RC03','RC07','RC12','RC14','FL02','FL14'}
records=[]
for e in plan['entries']:
 if e['id'] in TEST:continue
 jp=R/f"production/pilot-chapters/jobs/{e['id']}-P.json"; pp=R/f"production/pilot-chapters/prompts/{e['id']}-P.txt"
 call=R/f"production/pilot-chapters/calls/{e['id']}-P.json"
 assert not call.exists(),e['id']+' called during audit; do not amend'
 stable={k:EQUIP[k] for k in e['cast_in_frame'] if k in EQUIP}
 two=e['copy'];rec='Do not change action geometry merely to fit speaker order; identify each balloon after actual art using short attribution and deliberate tail routing. Offscreen voices stay offscreen.'
 if e['id'] in SAFE_TWO_SHOTS and len(two)==2 and two[0]['speaker']!=two[1]['speaker']:
  rec=f"Where the two-shot has no forced contact geography, place {two[0]['speaker']} toward image LEFT and {two[1]['speaker']} toward image RIGHT to follow frozen reading order. Keep both faces below reserved lettering. Do not mirror anatomical equipment or power sides."
 records.append({'id':e['id'],'original_job_exists':jp.exists(),'original_job_sha256':hashlib.sha256(jp.read_bytes()).hexdigest() if jp.exists() else None,'original_prompt_sha256':hashlib.sha256(pp.read_bytes()).hexdigest() if pp.exists() else None,'replace_visible_equipment_prose':stable,'append_authoritative_current_inventory':inventory(e),'speaker_blocking_recommendation':rec,'do_not_change':['frozen plan','scripts','exact copy','panel IDs','story outcomes'],'review_basis':'All frozen panel/script states and actual existing uncalled prompt templates examined; later nonexistent jobs covered prospectively.'})
assert len(records)==74
obj={'schema':'PilotUncalledPromptStateAmendments/1','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':hashlib.sha256((R/'production/pilot-chapters/plan.json').read_bytes()).hexdigest(),'excluded_already_called_test_ids':sorted(TEST),'total_uncalled_ids':74,'actual_existing_uncalled_jobs':sum(x['original_job_exists'] for x in records),'scope':'Editorial suggestions only. Root must version uncalled prompts/jobs and preserve v1. No production files, frozen plan, scripts or copy changed by this agent. Stable equipment replacement must supersede rather than coexist with conflicting baseline equipment sentences.','amendments':records}
(OUT/'uncalled-state-amendments.json').write_text(json.dumps(obj,indent=2)+'\n')
print('ids',len(records),'existing_jobs',obj['actual_existing_uncalled_jobs'],'sha',hashlib.sha256((OUT/'uncalled-state-amendments.json').read_bytes()).hexdigest())
