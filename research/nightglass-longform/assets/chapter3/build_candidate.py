from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
panels = []
LETTERING = 'Exact copy remains editable outside the raster. Compose for 390-pixel reading; preserve faces, hands, support, envelope custody and every force endpoint. No generated letters, balloons or interface.'

def p(action, copy, camera, state):
    panels.append(dict(id=f'N3-{len(panels)+1:02}', action=action,
        copy=[dict(speaker=s,text=t) for s,t in copy], camera=camera,
        current_state=state, reuse=None, lettering=LETTERING))

p('The following morning, Aren reaches Hessa’s actual lower door by the registered stair. She has turned the little old directional board toward her current landing. He offers her ordinary post from the gray bag, standing comfortably under its two broad straps.',
 [('Caption','The next morning.'),('Hessa','You found me without the shouting.')],
 'wide vertical doorway geography; corrected direction and real occupied home together',
 'Continues Chapter2: Rank1, Tension Line I and Hold I; brass Lower Post badge on red cord; closed cream wallet; dark-brown two-shoulder load-spreader and hip belt; one gray bag centered on back, old single strap rolled at its side. Sword sheathed anatomical RIGHT hip. Old LEFT-elbow and lower-hem tears persist. No line. Hessa receives one ordinary letter, not the pending official reply.')
p('At Dain’s door, Aren makes the same soft two-knuckle tap. The caretaker opens a narrow gap and accepts his ordinary letter without disturbing the dark room beyond.',
 [('Dain','That is the knock. Thank you.')],
 'close quiet handoff and two restrained smiles',
 'Dain is shaved-headed adult in charcoal house robe. No sleeping child shown. One letter leaves bag into Dain custody. Harness worn, blade sheathed, no power; clothing damage unchanged.')
p('Rusk holds his workshop door with one shoulder while Aren collects a tied outgoing packet from his blue-aproned hands. The letter Rusk received yesterday rests beside an unfinished hinge on the workbench.',
 [('Rusk','Same time tomorrow?'),('Aren','Same time.')],
 'medium workshop exchange, work and kept letter visible',
 'New outgoing packet transfers to Aren bag for the ordinary morning collection. Rusk retains yesterday’s received letter. No implausibly rapid personal answer arrives. No black Chapter1 offer or yellow petition folder reappears.')
p('After finishing the morning collection and returning by the long stair, Aren sets the now-empty bag on Ossa’s sorting table. She pays the agreed round against its signed receipt; he separates a little of the earned money into a plain folded paper packet.',
 [('Caption','After the collection run.'),('Ossa','Morning round complete.'),('Aren','This part is for the room.')],
 'intimate receipt, earned coins and small hopeful face',
 'Morning letters have been delivered to the sorting office during the ordinary completed round; receipt is brought back, not the delivered packet. This is an explicit later-morning transition. Earned previous wages retained; no specified coin total. The folded savings packet belongs to Aren, not a lease or key. Empty gray bag and harness retained.')
p('Sera lays her signed local survey order on the table beside Pell’s older maintenance copy. Aren points to the courier fee line before putting his savings away. Through the stair window, the little beacon still shines on the neighboring lift structure.',
 [('Sera','The survey includes your carrying time.'),('Aren','Then tell me what you need moved.')],
 'medium work table to actual beacon sightline',
 'Survey is paid entrusted carrying work established before execution, not a reward invented afterward. Sera owns survey order and ledger; Pell owns older maintenance copy. Ossa remains at Lower Post. Aren secures savings in closed wallet, wears harness with empty bag; no power or drawn blade.')
p('At the guarded upper service walkway, the three stop behind a sound rail. The small cyan beacon stands on a fixed shelf below them beside a stationary postal goods lift. A loose shade edge shifts in the breeze, moving a narrow reflection of its steady light across the lift’s metal suspension collar; the safe public stair continues along the opposite wall.',
 [],
 'extreme-wide complete geography; fixed shelf, upper walkway, goods lift and independent public stair distinct',
 'Lift stationary at its lower stop. All humans supported behind rail. No fauna in this first geography panel. Same local lift/beacon introduced N2-48, not another damaged public bridge. Manual return route remains open independently. Beacon source stays steadily lit as in Chapter2; loose shade moves the reflected strip. No new motor or interface.')
p('A single modest glass ray glides into the open space outside the rail. Its translucent navy wings span about two adult arm-lengths. As the beacon’s sweep moves across the suspension collar, its head turns with the moving reflection.',
 [],
 'medium-wide profile, one ray and light reflection in the same frame; humans secondary behind guardrail',
 'One glass ray only, visibly smaller than the enormous Chapter1 animal. Broad transparent wing surfaces, one focal cyan eye and compact beak; no hidden brood or later threat. Observation only: its head follows this moving light. No human approach or weapon action.')
p('The ray’s beak gently taps the bright metal collar where the sweep has stopped. Pell flinches at the small ringing contact while Aren watches the reflected line, keeping both hands off his sword.',
 [('Aren','It is waiting for the light to move.')],
 'close beak-to-collar reflection, Pell and Aren readable behind rail',
 'Beak makes one small contact, not a crushing bite. Collar and lift remain intact and stationary. Ray never crosses the guardrail. This is evidence about this animal’s immediate behavior, not proof of what caused the Chapter1 incident. No magic or new injury.')
p('Sera closes the service access gate and places the survey barrier across its doorway. Aren points a passing worker toward the still-open ordinary stair on the other side; the worker takes that clear path.',
 [('Sera','Use the public stair while we check the lamp.')],
 'wide practical separation of work zone and continuing public route',
 'Service bay temporarily restricted; registered public/manual route and Lower Post entrance remain open. Aren blade sheathed. Pell remains inside supported service work area with Sera; no teleporting residents onto repair shelf.')
p('Pell opens the lamp junction cover from the guarded walkway. Inside, an old disconnected feed ends in a closed cap while a separate small conduit enters from below. He holds the cover on its hinge; Sera compares it with the old maintenance copy.',
 [('Pell','The feed in this drawing is disconnected. The lamp has another supply.')],
 'tactile close junction, distinct capped old feed and incoming conduit; no dense schematic',
 'No bare-contact work or cutting. Lamp remains on; observation only. Pell’s ordinary tools on a secure tray, not in Aren hands. Old drawing is documentary reference, not assumed current truth. Do not render text into the junction.')
p('They follow the visible small conduit along the wall to a shared pump cabinet on a broad lower landing, using the intact public stair. Pell touches the outside of its separate lamp branch box; through the cabinet grille a domestic pump indicator remains warmly lit.',
 [('Pell','Here. A separate branch from the pump cabinet.')],
 'long side wall with traceable conduit and supported workers; avoid cutaway maze',
 'All reach cabinet by ordinary stairs. No instantaneous change of location. This identifies the visible supply path only; it does not establish who connected it or when. Public pump and lamp branch visibly separate. Aren still carries empty bag/harness, sword sheathed.')
p('Sera adds the observed branch to her survey sheet and signs a limited lamp isolation instruction. Pell waits with his hands clear of the closed control until she passes him the signed sheet.',
 [('Sera','The lamp branch only. The homes keep their water.')],
 'close signed decision and Pell listening; separate enclosed controls in background',
 'A bounded fictional maintenance authorization, not a diagram of real wiring. Sera’s instruction applies to local lamp isolation only; public pump remains running. No automatic authority over other districts. No new power or equipment granted to Aren.')
p('At the enclosed branch control Pell sets the lamp switch to its isolated position and fits its existing lock. The domestic pump’s warm indicator remains lit beside it.',
 [],
 'close single ordinary control action, lamp branch and unaffected pump indicator distinct',
 'Only lamp branch switched off and secured. Old feed remains capped. No human touches exposed energized conductors. Pell retains control lock key with his tools. No household outage, new damage or spark spectacle.')
p('Back in the same open service-bay geography, the beacon is dark. With no cyan reflection on the collar, the ray lifts its beak away and pauses, its translucent wings still drifting in the air.',
 [],
 'match the earlier beak/collar sightline with the light absent',
 'One same ray, no replacement animal. Lamp OFF; lift still stationary and undamaged. This visibly changes the cue before the animal changes position. Humans remain at safe supported rail; sword sheathed.')
p('The ray drifts away from the collar toward open air above the canal. Sunlight passes through a broad wing, briefly coloring the wall beside Aren’s face. He smiles at the beauty before looking back to the work.',
 [('Aren','There you are.')],
 'quiet wide wonder with close human face at an edge; ray receding',
 'Animal departs without injury or combat reward. No claim that every glass ray will always behave this way. Lamp remains isolated; no future large creature revealed.')
p('Sera writes the light-on and light-off observations on facing halves of her survey sheet. Pell lays the undated branch record beside it, leaving the missing date visible as an empty field rather than inventing an answer.',
 [('Sera','It followed the reflection. We can keep that off the collar.'),('Pell','This connection has no date.')],
 'intimate evidence table on the broad landing, real faces and two distinct records',
 'Local observation supports changing this beacon’s exposure; undated supply remains an unresolved documentary fact. No sabotage or culprit established. Sera retains current survey, Pell older copy. No hypothesis converted into owner-approved canon.')
p('At the dark beacon, Pell shows the loose old shade: its open side faces the exposed suspension collar instead of the fenced guide pane. Sera can see the straight sightline between the shade opening and collar from the protected walkway.',
 [('Pell','The shade is turned toward the suspension. The guide pane is below it.')],
 'medium alignment view with only shade opening, collar and intended guide pane emphasized',
 'Lamp isolated. Two distinct physical targets: exposed collar outside lift travel lane and fixed guide pane inside fenced postal lane. No moving machinery during inspection. This is the immediate repairable local defect; its installer remains unknown.')
p('Sera signs a bounded repair addition on the survey order while Pell indicates the lamp and the stationary goods lift. Pell beckons Rusk from his visibly open nearby workshop; Rusk approaches carrying his ordinary tool case.',
 [('Sera','Shield the lamp. Inspect the lift. One postal circuit, before we reopen it.')],
 'medium work team and closed service gate; Rusk arrival visible',
 'Repair scope authorized before work: lamp shielding/local switched supply and this goods lift only. Rusk blue apron, regular tools; no magic. Ossa remains Lower Post. Paid Aren carrying task continues within the stated order. Manual stair route unaffected.')
p('On his portable work board, Rusk fits a plain dark metal replacement shade against Pell’s removed old one. The new shade has one narrow downward slot; Pell keeps the old shade on the board for the maintenance record.',
 [('Rusk','The light can reach the guide without washing the whole landing.')],
 'close hands, two clearly distinct metal shades, broad simple forms',
 'Old shade removed only while isolated, retained by Pell. One new light replacement shade, not a new sword or armor reward. Its slot orientation is visible without explanatory raster labels. No lift movement.')
p('Aren lifts only the small new shade and places it inside his empty gray bag. Rusk closes the heavy tool case with the removed old shade secured beside its tools. Aren adjusts the familiar harness hip belt and declines the offered case with a small shake of his head.',
 [('Aren','The shade is enough. Take the tools by the stair.')],
 'medium practical load decision, small bag and heavy case distinct',
 'Gray bag now carries ONE light shade, no mail, yellow folder or old black envelope. Same two-shoulder harness/hip belt, no capacity or force upgrade. Rusk retains tools and removed old shade in the case; Pell retains control key. Aren right sword still sheathed; both old tears remain.')
p('From the upper service gate, Sera points out a fixed guarded maintenance shelf one short step down across a narrow opening. Its black metal anchor post is bolted into the masonry, separate from the stationary lift car. The longer intact service stair reaches the same shelf from the opposite end.',
 [('Sera','Fixed post. Clear shelf. I will watch the landing.')],
 'wide transparent geometry with upper departure, small gap, lower fixed shelf and ordinary stair',
 'This is a supported fixed work platform, never the lift roof or moving car. No sharp obstruction on landing. Rusk takes longer stair with tools; Pell accompanies him. Aren bag with shade secure on back. No active line yet; no airborne helpers.')
p('Aren makes the short transfer toward the fixed shelf. His RIGHT hand holds the crescent clear of his path; one thin cyan line runs from its rear pommel ring to the shelf’s bolted black post. The small gray bag stays centered on the harness.',
 [],
 'wide side, full body small gap and complete unobscured line endpoints',
 'One line only, RIGHT pommel to fixed masonry-supported post; never blade, harness, bag or lift car. LEFT hand empty for balance. Boots briefly above the small gap, destination directly beneath. One shade in bag; no added load. Intact supports and existing garment tears remain.')
p('Aren concentrates on Hold as both boots meet the clear shelf before its railing. His jaw is quiet, knees settling, and the centered bag does not swing into the post. The cyan connection remains taut during this last stopping instant.',
 [],
 'medium full support and both relevant endpoints, no simultaneous tool work',
 'Previously learned Hold brakes Aren and carried load; no new range/force. No speech or attack during concentration. Right sword remains clear of rail; no new snag, tear or wound. Helpers approach by stair outside current frame.')
p('Fully supported beside the isolated beacon, Aren has released the line and sheathed his sword. He hands Pell the single shade from the bag now resting open on the ledge. Rusk arrives through the ordinary stair gate with the tool case, its removed old shade secure beside the tools.',
 [],
 'close uncomplicated transfer with faces; fixed floor beneath all adults',
 'New shade transfers Aren to Pell. Aren bag now empty and open on ledge; right sword sheathed and line OFF before handoff. Rusk reaches the shelf by the previously shown ordinary stair, not by magic. Old shade remains in Rusk’s case after its visible packing at the work board, not installed again. All supported, lamp isolated.')
p('Pell seats the new shade around the dark lamp while Rusk supports its lower edge from the same stable shelf. The narrow slot points down toward the fenced guide pane, away from the exposed collar; Aren watches with empty hands clear of the mechanism.',
 [],
 'medium installation, slot direction and protected feet visible',
 'Pell and Rusk perform ordinary mechanical fitting, not Aren during Hold. No active line. Lamp still isolated. New shade installed once; old shade and tools on fixed ledge. No moving lift.')
p('From behind the guardrail Sera checks the new shade’s sightline against the guide pane, then closes its inspection hatch. The exposed suspension collar is plainly outside the shade’s narrow opening.',
 [('Sera','The collar is outside the light path.')],
 'close physical sightline and human verification, no schematic substitute',
 'Alignment verified while dark by actual geometry; performance still untested. Service gate closed behind workers before power test. No claims that the entire city is safe or all fauna controlled. Same local equipment only.')
p('At the enclosed control cabinet Pell closes the new guarded local lamp switch assembly after documenting its separate branch. The old abandoned feed remains capped; the domestic pump indicator remains on beside the secured lamp control.',
 [('Pell','Now the lamp has its own recorded stop.')],
 'medium closed controls and paper record, ordinary working hands',
 'Qualified fictional maintenance completes an authorized enclosed local cutoff; no detailed real wiring recipe. Supply route recorded, lamp still OFF until test. Pump service uninterrupted. No unexplained restoration of old feed or new power source.')
p('Pell examines the lift’s intact suspension collar and the restrained cable with the car held on its mechanical stop. Rusk steadies the inspection cover; Sera records the local check from the supported walkway.',
 [],
 'close load-bearing collar, restrained cable and open inspection cover; workers safely supported',
 'Stationary goods lift; no person stands on unverified car or uses magic to support it. Collar/cable must appear intact, with no severed/frayed cable later called sound. Any actual generated structural damage would require a storyboard correction, not a caption certifying it.')
p('All four return behind the upper guardrail, with Aren wearing the refastened harness and empty bag. Pell closes the service gate; the fixed shelf is empty, the lift car is empty, and Rusk’s tools and old parts are secured on the work board.',
 [],
 'wide clean test setup, every person outside moving lane',
 'Aren crossed back by the ordinary service stair; no implied second magic flight. Sword sheathed and line OFF. Service gate closed; only empty goods car will move. Public/manual stair remains separately open.')
p('Pell activates the local test control. A narrow cyan strip now falls onto the fixed guide pane inside the fenced postal lane; the exposed collar stays dark. Far beyond the rail, the same ray glides over the canal without turning toward the collar.',
 [],
 'wide light path and quiet fauna behavior in one readable scene',
 'One controlled local lamp test; pump remains running. Ray’s visible non-approach during this trial is evidence, not a universal guarantee. No radiant spell, monster defeat, combat XP or new skill. Empty car not moving yet.')
p('The empty goods car finishes its short climb at the upper loading stop, level with the fixed shelf and clear of the dark exposed collar. Pell watches the stopped runner while Sera watches the matched platform edges.',
 [],
 'side view of supported mechanism and empty moving car; no human passengers',
 'Only this local goods circuit under test. The empty ascent is complete; car now at UPPER loading stop before the next test load. Lamp narrow and shielded. Human feet behind rail; no sword or line assists machinery. Show intact cable and car supported at its stop.')
p('On the stationary upper loading shelf, Aren places one modest test bundle in his otherwise empty gray bag. Sera checks it against the existing permitted mail-load mark while Pell holds the stopped car door open.',
 [('Aren','A mail load. Nothing extra.')],
 'close bounded load and bag, known harness beside it',
 'Temporary test bundle is plain wrapped workshop ballast, not entrusted post, petition or reply. Within existing goods-car rating; no new capacity number invented. Bag unfastened from harness and supported on shelf. Sword sheathed. All hands clear until car stopped.')
p('Behind the closed service gate, the team watches the same gray bag ride down inside the goods car. Its one small test bundle stays enclosed; the car moves steadily while no person rides with it.',
 [],
 'wide proof of useful mechanical carriage; humans and mail car distinct',
 'Bag carried by ordinary tested lift, not Aren’s magic. Harness remains worn empty on Aren. One bag only, no extra mail. Lamp narrow, collar dark; ray absent from current frame. Manual stair available alongside.')
p('At the lower receiving shelf, Aren takes the stopped car’s gray bag and opens it on the fixed counter. Rusk lifts the single test bundle back out into his own tool case while Sera signs the completed local inspection.',
 [('Sera','This circuit. These two stops. Mail only.')],
 'medium stopped-car unloading and signed scope, no simultaneous unsupported load',
 'Aren and team reached lower stop by public stair. Test ballast removed into Rusk custody before any real mail enters bag. Empty gray bag returns Aren; no duplicate ballast later. Inspection approves only this goods circuit, no passenger lift or broken public bridge.')
p('Ossa opens the lower receiving hatch from inside the post hall. Hessa and Dain look through at the now-level stopped car; Hessa sets a modest outgoing packet on the counter, and Dain gestures toward the hall’s sleeping-room corridor.',
 [('Hessa','We can hand it over here?'),('Dain','Without that bell?'),('Ossa','Here. Quietly.')],
 'warm interior reveal of usable receiving hatch and distinct neighbors',
 'Receiving hatch reopened after signed tests, not before. Hessa packet remains on Ossa counter for next collection, not in Aren’s empty bag. Dain’s household not shown. Manual stair and prior wages/authority remain valid.')
p('At midday, Sera lays the signed local repair report and its simple retained-part sketches beside Maret’s current register at the public counter. Aren stands alongside with the empty gray bag on his new harness; Pell and Rusk remain at the lower works.',
 [('Caption','At midday.'),('Sera','Observed supply. Corrected light path. One tested postal circuit.')],
 'medium familiar office counter with tangible report and tired satisfied faces',
 'Explicit transition by intact public stair, no teleportation. Sera retains ledger but submits one report copy; original local inspection remains Lower Post. Retained parts stay physically at works, not secretly destroyed. Maret has the original yellow petition folder from Chapter2.')
p('Maret places the substantive reply to the petition beside the restored current-door entries. She reads its decision to Aren and Sera before folding it, allowing Aren to hear that the neighbors’ evidence actually changed the working record.',
 [('Maret','The witnessed addresses are back in the current register. Regular collection is approved.')],
 'close official decision with Maret’s human concentration and Aren’s dawning smile',
 'First substantive petition reply, distinct from Chapter2 intake acknowledgment and Sera safety order. Applies to actually witnessed addresses and this service, not every absent resident or upper-route licensing. Reply is new plain office paper; original petition remains archived in yellow folder.')
p('Maret places a certified copy of the old closure instruction behind the reply and encloses both in one plain cream envelope with a blue office seal. Aren waits with empty hands on the counter until the seal is finished.',
 [('Maret','The old instruction is enclosed. Your correction has to travel with its history.')],
 'tactile single envelope preparation, enclosed pages and seal clearly separate',
 'One new envelope contains reply plus closure-copy enclosure. No black silver-circle offer, no yellow folder transfer. Old instruction’s second district is not exposed in art or dialogue yet; page faces turned away or blank for later editable copy. Maret retains original archive.')
p('Aren accepts the sealed cream-and-blue office envelope in his LEFT hand and places it into the empty gray bag resting on the counter. Sera signs the dispatch line as witness, then closes her ledger.',
 [('Aren','Lower Post. I know the door.')],
 'medium careful entrusted handoff, warm competence over triumphant UI',
 'Official reply now in Aren custody, single envelope inside bag. Test ballast already removed; no ordinary outgoing packet silently added. Right sword sheathed; line OFF. Harness unchanged and no rank increase. Every prior wage and badge retained.')
p('At the upper end of the newly inspected local circuit, Aren sets the closed gray bag inside the stopped goods car and steps behind the latched gate. The ordinary descending stair is visible beside him; he will meet the bag below.',
 [],
 'wide real dispatch through repaired infrastructure, supported courier and separate mail car',
 'Bag contains the single sealed official reply. Lift carries mail only, never Aren or Sera. Harness worn empty, no pommel line. Upper loading point reached from office by existing route; no previously barred upper license gate crossed.')
p('The goods car arrives level with Lower Post’s receiving shelf. Aren reaches it from the adjoining ordinary stair as Ossa opens the inside hatch. He places the stopped bag on the fixed counter and opens it toward her.',
 [],
 'medium meeting of mail circuit, walking courier and recipient; all supports clear',
 'No human rode the car. One bag physically arrived by local lift; Aren descended by visible public stair. Car stopped before hatch access. Official sealed envelope remains bag until next panel. Sera follows stairs off frame, no teleporting.')
p('Aren hands the one still-sealed cream envelope to Ossa across her own sorting counter. She supports it with both hands and studies the written destination before opening it; neighbors wait in the warm hall behind her.',
 [('Ossa','They have sent us an answer.')],
 'intimate receiving hands and Ossa’s genuine emotion',
 'Formal first reply physically delivered to Lower Post; custody transfers Aren to Ossa now. Bag empty. Original yellow petition stays Office, black Chapter1 offer stays Ossa archive, older closure copy still enclosed with reply. No instant document duplication.')
p('Ossa opens the envelope and lays its official reply on the sorting table. Rusk, Hessa and Dain lean close as she reads their entries aloud. The still-folded closure-copy enclosure rests beneath the opened envelope, unread.',
 [('Ossa','Rusk. Hessa. Dain. In the current register.'),('Rusk','Then she can write back.')],
 'close shared paper and four distinct faces, sincere relief without cheering crowd',
 'Reply and enclosure now Ossa table. This confirms current visited doors and recurring collection; no population census or entire-city victory. Rusk means his daughter can use the recognized return address, not that her next letter has already arrived. No reveal from enclosure yet.')
p('Ossa signs Aren’s receipt for the reply and passes the signed copy back to him. The original delivered reply stays under her palm; beyond her shoulder the newly usable receiving hatch remains open.',
 [('Aren','Please keep that one.'),('Ossa','I intend to.')],
 'tactile receipt and affectionate exchange, actual kept reply visible',
 'Reply belongs to Lower Post, not carried away by Aren. One delivery receipt copy returns Aren’s LEFT hand then cream wallet. Service restored, names recorded, first answer delivered: local arc complete. No reward cancelled by subsequent hook.')
p('Sera pays the previously agreed survey carrying fee against the completed order. Aren sets the earned coins beside his morning savings packet, then removes his gloves and sits at the sorting table as Ossa serves a simple late meal.',
 [('Sera','Carrying work complete.'),('Aren','Then I can sit for this one.')],
 'warm medium earned rest, gloves laid down and untouched meal awaiting him',
 'Two distinct Chapter3 paid jobs: recurring morning round and agreed survey carrying task. No arbitrary sum or XP. Money stays Aren, part saved toward room. Harness unbuckled and hung on chair with empty bag; sword sheathed at right hip, no active power. Room/key not yet acquired; no week-long time jump.')
p('While Aren eats, Sera unfolds the certified old closure copy from the delivered envelope. Its second entry names Bell Basin. Rusk places a recent ordinary workshop invoice beside it, pointing to the same place in its return line.',
 [('Sera','This instruction closes Bell Basin too.'),('Rusk','I bought hinges there last month.')],
 'close two independent documents and serious listening faces; meal remains in scene',
 'Older closure instruction is the same enclosure introduced at office, not a newly conjured clue. Rusk invoice is his own workshop record brought from blue apron pocket. It supports recent activity in another district, not present population or culprit. No villain face, hidden monster or future damage revealed.')
p('Final tall frame: the local goods car waits level at the open postal hatch, its shielded beacon throwing only a narrow cyan guide. Above, Aren sits among the neighbors in warm light with his saved wages beside the meal. Beyond their window the vast city has many other occupied lights; the closed instruction lies open on their table.',
 [('Aren','Then we take them a copy. After the morning post.')],
 'tall extreme-wide with intimate table foreground and repaired local circuit below; larger city beyond',
 'Victories intact: paid recurring round, retained harness/Hold/badge/manual route, inspected local mail circuit, actual official reply/current-door correction, earned rest and room savings. Next bounded investigation is a delivery to Bell Basin, not a villain hunt or simultaneous new universe. No claim of human acceptance or permanent owner canon.')

assert len(panels)==47, len(panels)
data=dict(schema='NightglassLongformScript/1',chapter=3,title='The Light Between Addresses',
 premise='Aren’s paid route leads a small team to a misdirected, undocumented beacon supply. They spare the glass ray, repair one local postal circuit and deliver the district’s first official answer, with another living address left inside the old closure order.',
 status='complete-editorial-candidate-awaiting-lead-integration',owner_approval=None,panels=panels)
(ROOT/'chapter-3.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
lines=['# Chapter 3 — The Light Between Addresses','',data['premise'],'','47 real story panels. Complete editorial candidate; no artwork generated.','']
for panel in panels:
    lines += [f"## {panel['id']}",'',panel['action'],'',f"Camera: {panel['camera']}",'',f"State: {panel['current_state']}",'']
    lines += [f"- **{c['speaker']}:** {c['text']}" for c in panel['copy']]
    lines += ['']
(ROOT/'chapter-3.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'panels':len(panels),'copy_items':sum(len(p['copy']) for p in panels),'max_words_per_panel':max(sum(len(c['text'].split()) for c in p['copy']) for p in panels)},indent=2))
