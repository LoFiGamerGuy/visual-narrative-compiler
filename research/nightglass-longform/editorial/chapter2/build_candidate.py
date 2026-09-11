import json
from pathlib import Path

ROOT = Path(__file__).parent
panels = []


def panel(action, state, camera, *copy):
    panels.append({
        'id': f'N2-{len(panels)+1:02}',
        'action': action,
        'copy': [{'speaker': speaker, 'text': text} for speaker, text in copy],
        'camera': camera,
        'current_state': state,
        'reuse': None,
        'lettering': 'Exact copy stays editable outside art. Reserve deliberate quiet space for this panel\u2019s actual speakers; keep faces, handoffs, physical supports and clues clear. No raster words or balloons.',
    })


panel('Dawn opens the public forecourt of the Office of Route Closures. Aren joins a short queue of adult tradespeople carrying the ordinary outgoing bundle from Lower Post inside his coat. The high licensed-route gate is far above this accessible civic entrance.',
      'Continues N1-48 without reset. Aren owns brass rectangular Lower Post badge on red cord, earned pay, closed cream wallet at belt and outgoing bundle including petition. Sword sheathed anatomical RIGHT hip; no line. Existing LEFT-elbow sleeve tear and lower-hem tear persist; shoulder still sore.',
      'extreme wide, inhabited civic forecourt; Aren small among working adults')
panel('At a breakfast stall bordering the queue, Aren sets down one of his earned coins and accepts a steaming paper cup with his left hand. He studies the cup with tired, private pleasure before returning to the line.',
      'First pay is real and partly spent by choice; remaining pay retained. Bundle remains concealed in coat. Sword sheathed; no power. No new clothing damage.',
      'intimate hands and warming face; queue soft behind',
      ('Vendor', 'Sweet?'), ('Aren', 'Yes. Please.'))
panel('Sera enters the forecourt with her inspection ledger. Aren lowers the cup and shows her the edge of the outgoing petition; he asks for help directly. She stops beside him rather than ushering him out of the queue.',
      'Aren cup LEFT; petition supported against his chest by RIGHT hand, sword still sheathed. Sera carries ledger only; spear absent from this scene. No line.',
      'eye-level two-shot, candid tired expression',
      ('Aren', 'Would you help me get these received?'), ('Sera', 'Show me the receipt.'))
panel('At the public counter, clerk Maret receives the petition and the copy of his signed delivery receipt packed with the petition by Ossa. Aren sets his now-empty cup into a nearby return bin. Sera stands alongside him with her closed ledger.',
      'Petition and receipt now on Maret counter; remaining ordinary outgoing bundle still Aren\u2019s. Cup leaves inventory into bin. Sword sheathed, no line. Maret is adult woman with cropped dark curls, round glasses and moss-green vest over cream blouse.',
      'medium counter exchange, open work surface and three distinct adults',
      ('Maret', 'A reply to Lower District?'))
panel('Maret opens a large working address register to a narrow closed-route entry and traces the line with a blunt pencil. Beside it, Aren\u2019s copy of his genuine signed receipt lies flat. Her expression is concentrated rather than mocking.',
      'Maret owns register and pencil. Petition and signed receipt remain visible at counter. Register words added only as editable overlay if needed; dialogue carries the issue.',
      'over-counter close on hands, register and Aren listening',
      ('Maret', 'I cannot register a return against a closed route. There is no inspected entrance on file.'))
panel('Aren places his brass Lower Post badge beside the receipt without removing it from the red cord. He keeps one palm on the counter to steady himself and meets Maret\u2019s eyes.',
      'Badge remains attached to Aren\u2019s cord; not surrendered. Petition and receipt still clerk counter. Both old garment tears remain. Sword sheathed; no line.',
      'close face and meaningful objects, no hero pose',
      ('Aren', 'I was paid there this morning. That signature belongs to a person.'))
panel('Maret slides the receipt copy back toward Aren and places an open yellow verification folder next to the petition. She points to its two blank witness fields while explaining what can change the record.',
      'Aren recovers receipt copy with LEFT hand. Petition sits inside yellow folder on counter; folder not yet handed off. Badge stays Aren. No change to Chapter1 paid status or service-door access.',
      'medium practical explanation, readable faces and folder shape',
      ('Maret', 'The payment stands. For an office return, I need a current door register and an inspected route.'))
panel('Sera opens her own ledger beside the yellow folder, revealing two previous reports. She puts a fingertip on their separate dates, visibly choosing to add her own name to the new attempt.',
      'Sera ledger open, Maret yellow folder on counter. Aren holds receipt copy. No fabricated signatures; actual later witnesses will be gathered before certification.',
      'close angled across Sera\u2019s shoulder; her face remains visible',
      ('Sera', 'I filed these. This time I will walk it, with the residents.'))
panel('Maret hands the closed yellow folder containing the petition to Aren, who accepts it with both empty hands. She retains no duplicate of the unreceived petition. Sera closes her ledger, ready to leave with him.',
      'Yellow folder with petition now Aren. Receipt copy secured in his cream wallet; outgoing bundle inside coat. Sword sheathed; no line. Maret retains address register.',
      'medium doorwayward turn, decision becoming a job',
      ('Maret', 'Bring it back before this desk closes. I will keep the case open.'))
panel('Later that morning at Lower Post, Aren lays the yellow folder open in front of Ossa. Sera sets her ledger beside it; the warm hall is busy with ordinary adult residents, and the reopened stair entrance is visible in the distance.',
      'Yellow folder, petition and Ossa\u2019s bound door register on sorting table. Aren\u2019s outgoing bundle placed beside them for repacking. Cup gone; no new equipment. Sword sheathed. Ossa silver braid, indigo apron.',
      'wide interior work scene; recurring room recognizable',
      ('Ossa', 'Names first. Then the doors they actually use.'))
panel('Ossa reads from her worn door register while a waiting resident corrects a landing name. Ossa makes the correction openly rather than treating the book as infallible; Sera watches the conversation and records the same correction.',
      'Ossa and Sera maintain separate books. Yellow folder remains table. No magic or interfaces. Residents are adult neighbors, not a crowd of interchangeable cheering figures.',
      'intimate cluster around working table; hands point to separate books',
      ('Resident', 'Hessa moved down one landing.'), ('Ossa', 'Then that is where the post goes.'))
panel('Pell holds a simple folded route sketch against the open entrance wall and taps the regular stair. Through the doorway, its previously closed wicket stands open. Aren studies the route while Sera notes its start.',
      'Pell owns sketch; no tall harness rig or new weapon. Aren has no load harness yet. Public stair will remain the inspected route; a broken bridge will later be excluded, not silently certified.',
      'medium map-and-real-geography view, actual open passage visible',
      ('Pell', 'I will keep this latch clear. Start here. Come back here.'))
panel('Ossa packs several tied bundles of waiting ordinary post, including the outgoing bundle and held personal letters, into one modest gray canvas mail bag with a single narrow carrying strap. She places the yellow folder in its broad front sleeve, keeping it distinct from the letters. Aren signs the small collection sheet on her table.',
      'One gray canvas bag contains ordinary entrusted letters and the yellow petition folder. Bag has ONE single-shoulder strap, no load-spreader harness. Aren signs custody while bag remains table. Black Chapter1 offer remains Ossa\u2019s, not in bag.',
      'close deliberate packing and signature, warm hands',
      ('Ossa', 'This inspection is work. You will be paid for the round.'))
panel('Aren lifts the manageable but bulky bag onto his left shoulder and tests its weight with both feet on the floor. The narrow strap pulls against his old sore shoulder; he adjusts his stance instead of pretending it is effortless.',
      'Aren now carries gray bag on a single LEFT shoulder strap; yellow folder in front sleeve. Right sword sheathed. No cyan line, no harness, no new tear or injury. Existing elbow and hem damage retained.',
      'medium full stance and bag, small honest strain',
      ('Aren', 'All right. Stairs first.'))
panel('At the open wicket, Pell seats a simple keeper into the latch so it cannot swing shut behind them. Aren and Sera pass through the opening in the same frame; Pell remains to finish the entrance work.',
      'Pell left at Lower Post entrance with tools and route sketch. Aren carries bag and all its contents. Sera carries ledger. Wicket visibly held OPEN. No sword drawn, no power.',
      'wide side, distinct departure and fixed door mechanism',
      ('Pell', 'You will not have to jump the railing again.'))
panel('Aren and Sera emerge onto an inhabited lower-city terrace. Adults sweep thresholds, laundry hangs between balconies, and a tiny metalworking shop glows at the next door. Aren\u2019s bag is one solid burden against his left side.',
      'Both walking on continuous supported terrace, same single-strap bag. No ray or other fauna in this scene. Existing clothing damage persists; all letters still bag.',
      'extreme-wide horizontal world invitation, humans doing ordinary work')
panel('At the metalworker\u2019s threshold, Aren gives Rusk a held personal letter selected from the bag. Rusk, an adult man in a blue work apron, recognizes the handwriting before he touches the seal.',
      'One personal letter leaves bag into Rusk\u2019s hands. Bag set on stable threshold, yellow folder remains front sleeve. Sword sheathed; no line. Rusk receives his own letter, not petition.',
      'close letter and adult face, quiet change in expression',
      ('Rusk', 'She thinks I stopped answering.'))
panel('Rusk places his waiting reply on Aren\u2019s open hand. Aren faces him squarely, leaving room for the man\u2019s concern instead of turning the exchange into a joke.',
      'Rusk retains received personal letter. One new reply transfers into Aren\u2019s LEFT hand; Aren bag remains threshold. No envelope duplication; yellow folder untouched.',
      'eye-level two-shot with small handoff',
      ('Aren', 'I can take your answer.'))
panel('Sera watches Rusk sign the current-door sheet on a firm board against his own threshold. Behind his signing hand, the open shop contains active tools and an unfinished hinge. Aren tucks Rusk\u2019s reply into the gray bag.',
      'Witnessed current-door signature obtained at actual occupied door. Sheet returns to Sera ledger after panel. Aren holds bag open, right weapon remains sheathed. No claim that signature proves the whole district.',
      'medium occupation and evidence together',
      ('Sera', 'This is the door you collect from?'), ('Rusk', 'Every working day.'))
panel('At the next stair junction Aren follows an old arrow toward a shuttered upper doorway. Hessa calls from her open home on the landing below. He stops on a broad supported step and looks down, caught by a practical mistake.',
      'Same bag on LEFT shoulder; no power or loss of footing. Sera follows with ledger. Hessa is an adult dark-skinned woman with short twists and a rust cardigan; new home below, old shuttered door above.',
      'vertical geography, wrong sign above and actual person below',
      ('Hessa', 'Down here. The sign never moved with me.'))
panel('Sera crouches beside Hessa\u2019s real threshold to amend the door location in her ledger. Aren waits on the landing, looking back at the misleading arrow and understanding how a returned letter could be produced without anyone checking.',
      'Hessa remains at lower home; Sera corrects observed location before asking for signature. Bag Aren shoulder. Yellow folder remains bag sleeve. No blanket accusation or conspiracy proof.',
      'medium low view linking threshold, ledger and Aren\u2019s reaction',
      ('Sera', 'I will record both: the old sign and this entrance.'))
panel('Hessa signs the corrected sheet on her door shelf and passes Aren a warm wrapped roll with her free hand. Aren accepts it with an unguarded smile; the empty sleeve tear and overworked shoulder make the small kindness visible.',
      'Hessa signature witnessed by Sera. Roll transfers to Aren LEFT hand; gray bag supported on floor for exchange. No garment repair here; both prior tears remain. Sword sheathed, no line.',
      'intimate hands and warm face',
      ('Hessa', 'You missed breakfast.'), ('Aren', 'Thank you.'))
panel('The final door belongs to a night caretaker. Aren notices a sleeping household just inside the ajar entrance and uses a gentle two-knuckle tap instead of the heavy bell beside it. Sera waits back from the doorway.',
      'Roll now eaten; plain wrapping tucked in Aren\u2019s pocket, no food held. Gray bag on floor beside Aren. Dain is an adult caretaker with shaved head and charcoal house robe. No children need be shown.',
      'close hand at door, quiet domestic light beyond',
      ('Dain', 'Keep it quiet. I have only just got them to sleep.'))
panel('Dain accepts a personal envelope from Aren at the threshold and signs the witness sheet resting on a little shelf. Aren gives him a small nod; Sera records the completed handoff without speaking over the quiet household.',
      'One ordinary letter leaves gray bag to Dain. Third occupied doorstep witnessed. Current-door sheet then secured in Sera ledger. Bag yellow folder still retained. No powers or drawn blade.',
      'medium quiet exchange with signature and faces',
      ('Aren', 'I will.'))
panel('Back on the terrace, Sera compares the collected doorstep sheet with the real row of open homes. Aren settles the fuller outgoing bag at his feet and waits while she writes what she personally observed.',
      'Only these visited doors certified; no invented district population total. Sera owns signed witness sheet; Aren owns bag, yellow folder and entrusted outgoing replies. Sword sheathed.',
      'wide eye-level, inhabited doors behind concrete witnesses',
      ('Sera', 'These doors. These names. I can stand behind that.'))
panel('Their direct path to the upper office ends at a maintenance bridge with a missing tread section. Aren pauses on solid stone well before the edge. Sera lays a hand across the route sketch instead of letting urgency decide for them.',
      'Both fully supported before gap. Single-strap bag carried normally. No jump, line or attempted crossing. Broken bridge is NOT the Chapter1 reopened entrance and will not be approved for public use.',
      'wide route problem with clear safe stop and alternative stair visible',
      ('Sera', 'This span cannot go on a public return route.'))
panel('Aren turns away from the tempting short bridge and heads toward the long, intact stair climbing around its outer wall. He lifts the bag by its handle before resetting the narrow shoulder strap.',
      'Chosen detour is continuous supported stone stairs. No power shortcut, no missed deadline yet. Letters and folder stay in same bag; no extra load magically added.',
      'medium turn and determined face, long stair beyond',
      ('Aren', 'Then we take the long stair.'))
panel('Halfway up the broad stair, Aren braces the gray bag on a waist-high stone rest and eases the strap off his sore left shoulder. Sera waits beside him; nobody is falling and the entrusted mail stays dry.',
      'Bag fully supported by stone before strap removed. Aren hands ordinary, sword sheathed, no line. Existing rescue soreness, not a new injury or skill debt. Same letters still inside bag.',
      'side medium, support surface and tired acting clear',
      ('Sera', 'Set it down. We have time for one breath.'))
panel('Pell reaches the stair rest from the repaired entrance below, carrying only his small tool roll. He studies the narrow bag strap pressed into Aren\u2019s jacket and shifts the bag to the center of the stone rest without taking its custody.',
      'Pell entrance repair complete and wicket stays open. Bag remains on stone, no permanent transfer. Sera holds ledger. No new harness yet, no magic.',
      'intimate practical inspection of strap and shoulder',
      ('Pell', 'One strap doing two shoulders\u2019 work.'))
panel('Aren lifts the bag with both hands by its handle for the final level approach while Pell walks alongside and Sera leads toward the office. He carries it upright with visible effort and accepts the steadier method.',
      'Same manageable bag and same contents; all its weight borne by ordinary arms/body. Narrow strap hangs loose against bag. Sword sheathed; no line. Both garment tears persist.',
      'long level approach, workers returning together; no heroic silhouette')
panel('At the office counter, Sera places the three witnessed-door entries and her route sketch in the yellow folder. She marks the long intact stair as the manual route and crosses out the broken shortcut with one firm stroke.',
      'Yellow folder removed from bag onto counter. Petition plus actual witnessed sheets now folder. Bag remains on floor at Aren\u2019s feet holding outgoing ordinary mail. Route witness is Sera; no inference disguised as observation.',
      'close hands and Sera\u2019s face, two routes distinguished visually',
      ('Sera', 'Inspected entrance. Occupied doors. The broken span is excluded.'))
panel('Maret compares the newly witnessed entries against her address register. She finds the same names under an older landing designation and follows the page with her pencil; Aren leans forward, waiting for the conclusion.',
      'Maret owns register, yellow petition folder open on counter. Sera signed report attached. Gray bag remains with Aren and has not been emptied. No final decision issued yet.',
      'over-shoulder discovery, eyes and matching document shapes',
      ('Maret', 'They are still in the old book. The route was closed; the names were never removed.'))
panel('Maret turns the current register toward the signed inspection and writes a manual return-route entry. Sera watches her finish. Aren releases a breath he has held too long.',
      'Manual return route being registered for inspected stair and witnessed doors; upper-route qualification remains separate. No automated circuit restored yet, no petition answer promised.',
      'medium counter acting with actual writing',
      ('Maret', 'I can receive the petition now. Replies can travel by the inspected stair.'))
panel('The clerk presses her receipt stamp onto a plain case acknowledgment while her other hand keeps the petition inside the office\u2019s incoming tray. Aren watches the paper impression settle; Sera gives a small satisfied nod.',
      'Petition and its yellow folder formally transfer to Maret/Office and stay there. Acknowledgment is a new separate document, not the petition. Bag ordinary outgoing letters remains Aren\u2019s custody.',
      'tactile close stamp with human faces at frame edges',
      ('Maret', 'Received. Manual return route registered.'))
panel('Maret gives Aren the dated acknowledgment and an authorized sorting-carriage docket. He folds them carefully into his cream dispatch wallet, then rests his hand on the still-full gray bag rather than abandoning the rest of the round.',
      'New acknowledgment and carriage docket now Aren wallet. Office keeps yellow petition folder and witness sheets. No reply to petition yet; this is intake proof and authority to carry. No line, weapon sheathed.',
      'close pleased face and careful paper handling',
      ('Aren', 'Something I can bring back.'), ('Maret', 'And somewhere we can send an answer.'))
panel('From a small equipment cupboard behind her counter, Maret places a folded practical load-spreader beside the gray bag. Pell recognizes the two broad padded shoulder straps and the broad hip belt. Aren looks from the issued kit to his compressed shoulder.',
      'New equipment first appears now, after route registration and demonstrated carriage. One dark-brown webbing harness with two shoulder straps and hip belt, no glowing parts. It attaches bag to torso/back; NEVER to sword, pommel or anchor.',
      'medium issued equipment with reactions',
      ('Maret', 'Registered carriage includes a load kit. It belongs to your route.'))
panel('In the office\u2019s adjacent fitting alcove, Pell finishes fastening the same gray bag securely to the new harness on Aren\u2019s back. The bag\u2019s former loose shoulder strap is rolled and tied to its side. Sera steadies the empty harness buckle guide, not the bag\u2019s weight.',
      'Harness now worn over ivory jacket: two broad shoulders plus closed hip belt, same loaded gray bag against back. No new or extra mail, no bag duplication. Right-hip sword sheathed and accessible. Torn left elbow and hem remain exposed.',
      'rear three-quarter medium, complete shoulder-to-hip construction')
panel('Aren stands upright on the fitting floor with the bag\u2019s unchanged load shared across his shoulders and hips. Pell presses two fingers against the hip belt to show where it bears weight; Aren rolls one shoulder cautiously and realizes it no longer twists him sideways.',
      'Same bag and same letters as before fitting. Harness spreads force, adds no strength, lift or magic. Sword remains sheathed; no line. Ordinary planted feet bear full body/load.',
      'medium side with weight-bearing posture and face',
      ('Pell', 'Shoulders and hips share the bag. Your line still pulls only you.'))
panel('A sorting porter offers an additional small bundle beside the alcove. Aren tests the space with a glance, then leaves the extra bundle on the porter\u2019s counter and fastens only his existing bag. He makes the limit his own choice.',
      'Extra bundle never enters Aren inventory. Same load retained, no capacity increase. Porter keeps offered bundle. Harness worn; sword sheathed; no power.',
      'close choice, offered bundle and closed bag distinct',
      ('Aren', 'Next trip. I want this one delivered whole.'))
panel('At the adjacent sorting hall, Aren shows his authorized carriage docket to a receiving attendant who opens the courier access gate. Beyond it, a designated short transfer lane crosses a narrow sorting shaft to a slightly lower receiving platform with a stout fixed metal post. Sera observes from the supported departure deck.',
      'This is an authorized staff courier lane inside sorting hall, NOT the excluded broken public bridge. Aren recovers docket into wallet after inspection. Same bag secured to harness. No line yet, right sword sheathed; Pell remains fitting alcove.',
      'wide clear destination setup; departure, narrow gap, fixed anchor and receiving deck all visible',
      ('Attendant', 'Receiving deck. Use the fixed post.'))
panel('Aren makes the short controlled transfer toward the receiving platform. His anatomical RIGHT hand holds the crescent with its blade pointing clear of his path. One cyan line connects the pommel ring behind his right fist to the fixed post on the destination deck. The secured gray bag stays centered on his back, without swinging away.',
      'Same unchanged mail load, now distributed by harness. One right-pommel-to-visible-post line; no connection to harness, bag, belt or blade. LEFT arm empty for balance. No attack. Both endpoints visible; destination slightly lower, movement brief and local.',
      'wide side with whole body, small gap and both force endpoints unobscured')
panel('With the receiving deck just beneath his boots, Aren uses Hold to finish the transfer before its rail. His attention stays on the stop, jaw quiet and shoulders level. The bag remains snug against the harness; no parcel flies free.',
      'Hold brakes the moving holder and his carried load by sustained concentration; no added force or range. One taut pommel-to-post line during final braking instant, then supported feet. No strike or speech while concentrating. No new tear/injury.',
      'medium full stance and bag contact, rail safely ahead; complete relevant line ends')
panel('Fully supported at the receiving table, Aren has shut off the line and sheathed his sword. He places the gray bag on the table and opens it, allowing the attendant to lift the ordinary outgoing letters into separate sorting trays. The folded old single strap remains tied to the bag side.',
      'Line OFF; right sword SHEATHED. Harness temporarily unbuckled only enough to set bag down. Entrusted mail now physically transfers to receiving attendant; yellow petition folder is NOT among it because Office retained it. No duplicated bag.',
      'medium practical delivery, letters/trays and relieved shoulders visible',
      ('Attendant', 'All seals dry.'))
panel('The receiving attendant signs the carriage receipt against the empty gray bag. Aren takes the receipt with his left hand, leaving the accepted mail behind in the occupied sorting trays. Sera watches from the accessible staff doorway at the table\u2019s side after taking the ordinary perimeter walkway.',
      'Mail custody is sorting office; Aren retains empty bag, harness, acknowledgment, new carriage receipt and original badge. Sera did not teleport across the courier gap; ordinary longer staff walkway exists. No line.',
      'tactile receipt and Aren\u2019s open smile',
      ('Aren', 'Thank you for writing the return address in full.'))
panel('Later at Lower Post, Ossa lays the dated petition acknowledgment beside the delivered-mail receipt. Aren sets the empty bag on the table and unbuckles the harness, still wearing it loosely. Ossa reads the actual return entry, then looks up at the waiting neighbors.',
      'Aren brings receipts back, not the surrendered petition or delivered letters. Yellow folder remains Office; black offer remains Ossa archive. New harness and badge retained. Existing tears remain. No official petition answer yet.',
      'warm medium with receipts foreground and community beyond',
      ('Ossa', 'They have written us a return address. In their own book.'))
panel('Ossa places the agreed inspection payment in Aren\u2019s hand and pins a plain morning collection schedule beside the open entrance. Aren looks from his assigned round to the quiet chair at the sorting table and finally sits down for a moment.',
      'Second paid job completed; no arbitrary coin total or XP. Inspection wage retained, harness retained, manual return authority retained. Schedule confirms recurring paid work, not ownership of residents. Chair moment is real rest.',
      'medium seated relief with posted schedule as secondary object',
      ('Ossa', 'The morning round is paid work, if you want it.'), ('Aren', 'I want it.'))
panel('From the chair Aren notices a small empty room above the sorting hall through its open stair door: plain walls, one square window, enough space for a bed. Ossa follows his glance and rests a hand on the banister. His face holds anticipation rather than triumph over a new enemy.',
      'Aren has not acquired the room or a key yet; he still owns earned wages and recurring work. This is a concrete future choice, not cancelled reward. No magic, no new gear or costume change.',
      'quiet shared sightline toward modest room, enough of both faces',
      ('Ossa', 'Ask me about the rent after your first week.'), ('Aren', 'I will.'))
panel('Pell lays an old maintenance copy beside Sera\u2019s new signed survey work order on the sorting table. He points through the open stair window to a small cyan route beacon on the nearby lift structure. Its steady light is plainly visible in daylight; no creature is shown beside it.',
      'Sera has authorized a local safety survey after route inspection; this is NOT the Office\u2019s pending petition reply. Pell owns old maintenance copy. Present clue only: local beacon glows although older record marked it dark. No cause, sabotage culprit or later repair revealed.',
      'medium work-order-to-real-beacon sightline',
      ('Pell', 'That beacon was marked dark when they closed the circuit.'), ('Sera', 'Then we start by finding its supply.'))
panel('Outside, the repaired postal entrance stays open below the small steadily lit beacon on its neighboring lift tower. In a warm foreground window, Aren, Ossa, Pell and Sera bend over the real work orders around their table. The city beyond is vast and inhabited; their one registered route is a modest bright part of it.',
      'Local Chapter2 victory intact: petition received, manual return route registered, mail delivered, wages paid, harness retained, entrance open. Beacon discrepancy unresolved; no fauna attack or older second-district closure reveal. Next action is bounded local survey.',
      'tall extreme-wide, warm human table foreground and small cyan beacon middle distance',
      ('Aren', 'After the morning post. They know where to send the answer now.'))

assert len(panels) == 49
data = {
    'schema': 'NightglassLongformScript/1',
    'chapter': 2,
    'title': 'A Return Address',
    'premise': 'Aren and Sera turn delivered promises into a witnessed route the city can register. The carrying work earns Aren practical load equipment, an accepted mail delivery and a paid round; a local beacon contradicts its maintenance record.',
    'status': 'complete-editorial-candidate-awaiting-lead-integration',
    'owner_approval': None,
    'panels': panels,
}
(ROOT / 'chapter-2.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
lines = ['# Chapter 2 — A Return Address', '', 'Complete 49-panel editorial candidate. Provisional edition; not owner acceptance. No art generated by this task.', '']
for p in panels:
    lines += [f"## {p['id']} · {p['camera']}", p['action'], f"State: {p['current_state']}"]
    lines += [f"{c['speaker']}: {c['text']}" for c in p['copy']]
    lines += ['']
(ROOT / 'chapter-2.md').write_text('\n'.join(lines))
