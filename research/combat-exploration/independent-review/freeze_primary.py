from pathlib import Path
import json,hashlib
root=Path.cwd();out=root/'research/combat-exploration/independent-review';prod=root/'production/combat-exploration'
reg={x['id']:x for x in json.loads((prod/'candidates.json').read_text())['candidates'] if x['attempt_id'].endswith('-P')}
notes={
'01-C1':[
'Aster has a compelling cool assessing face and a severe long dark silhouette; pale bob and white shoulder make her immediately distinct from the original male courier and broad01-C2. Both views largely agree on identity.',
'Crisp bounded planes, fine face/hair drawing and cyan edges retain01, with somewhat silkier facial modeling. The complete sword and clearly wrapped grip support a combat identity rather than a utility prop.',
'Blade becomes pointed rather than a clearly squared chisel tip, and cyan slot reads as a luminous inset rather than proven open space. Stance is tall instead of low, boots gain heels, and sword tip slightly crosses the portrait divider. These are deviations, not a floating grip.',
'Phone preserves the assessing portrait, dark costume mass and sword line; fingers and blade-slot construction need native inspection.'],
'01-C2':[
'Darrow has a strong broad adult face, copper curls and calm heavy-athlete presence. Square jaw, thick neck and planted silhouette create a real alternative to Aster and the original slim black-haired anchor.',
'Faceted armor and selective cyan light retain01 despite added fine skin/cloth texture. Empty rectangular hammer head and its single continuous shaft are visibly constructed and the hand wraps the shaft.',
'The frame is distinctive but reads more as a light outlined frame than a massive impact head; its power premise supplies much of the unusual combat appeal. No hidden central strut or cropped endpoint.',
'Phone keeps the face, broad body and empty head readable; microscopic hand anatomy does not resolve at this size.'],
'02-C1':[
'Tal is lively and charismatic: wide grin, intent sideways eyes and a winding wide stance give the ring weapon an active role. One hand visibly grips the internal crossbar clear of the cutting rim.',
'Warm dark contours, angular colored planes and light painted texture match actual02. Both figure and portrait share the curls, freckles and green collar.',
'Novelty is less certain in the face: source-like broad brows, freckled cheeks and wide asymmetric grin persist strongly despite changed hair, body, clothing and weapon. This is a visual resemblance concern rather than proof of identical pixels.',
'Phone preserves grin, stance and single ring/crossbar; ring reads as a large hoop, with cutting-edge character subtler than its silhouette. No hard contact/framing failure.'],
'02-C2':[
'Rixa has a forceful angular scowl, scarred cheek and spiky pale head silhouette; her taut low stance and large falchion read as a committed fighter. This is a clearer new facial/personality alternative to Tal and the original braid-haired anchor.',
'Warm outlined paint remains faithful. Entire curved blade, simple guard, wrapped handle, complete free hand and both feet are visible.',
'Added scars and jewelry are deviations; the strong green blade and small pale pressure curl communicate a distinct combat instrument without a cloud of effects.',
'Phone retains scowl, pale hair, braced legs and weapon sweep, while native is needed for individual free-hand fingers. No scarce repair recommended.'],
'05-C1':[
'Brann has rugged adult appeal through heavy brows, long dark waves, beard and a tired half-laugh. Broad arms, rust armor and large vent-backed crescent polearm form a memorable powerhouse silhouette, distinct from the original mechanic.',
'Matte broken paint and tactile worn metal retain05. Two separated hands clearly wrap one continuous shaft, with full blade and both boots framed.',
'Weapon is carried horizontally at the waist rather than diagonally above a shoulder; extra vent slits and much surface wear add detail. Those do not erase the clear mechanical fantasy identity.',
'Phone preserves portrait, weapon head and two-hand pose; dark costume texture compresses into mottling and small grip detail is not independently readable.'],
'05-C2':[
'Eris has an attractive attentive adult face, long bound hair and sharp blue/rust torso-to-hip contrast. Her quiet narrow stance differentiates her from Brann; she is more polished and less overtly kinetic.',
'Worn matte painting remains coherent, with somewhat more realistically modeled facial features. The blue grip is visibly held and harpoon, chain and anchor ring read as one weapon.',
'The harpoon point reaches the top image edge without the required clear margin. The chain passes across/against both boot areas instead of resting clearly outside the legs, weakening safe readable tether routing. Barbs and amber cue remain visible.',
'Phone makes the top-edge problem and chain-to-boot tangencies persist; attractive portrait remains clear but the narrow figure offers little room to resolve tether mechanics.'],
'06-C1':[
'Sevrin has compelling restrained presence: long face, heavy-lidded eyes, full lips and swept-back dark waves contrast with the original older buzz-cut worker. Open stopping palm and complete triangular blade supply a deliberate combat pose.',
'Coarse broken brush masses remain visibly different from13 fine hatching. Black-white diagonal torso and small pink weapon throat keep the drawing organized.',
'Grip stays behind the white guard. Blade is much larger than an ordinary stiletto and held low rather than waist-high; tip slightly enters the portrait side of the divider. One weapon and complete figure remain legible.',
'Phone preserves face, open-palm gesture and sharp black blade; precise grip requires native view. No major anatomy or style-collapse repair.'],
'06-C2':[
'Varda has a stern mature face and imposing shield-first presence; low twist hair, white shoulder cape and heavy stance are recognizably different from the earlier06 characters. Large shield makes defense read as an aggressive combat identity.',
'Rough black-white brush treatment and a single pink stripe retain06. Figure and portrait agree on face, hair and collar; both feet and free fist are visible.',
'Shield hand visibly wraps a handle-like element near its left edge, but exact internal mounting/forearm route is occluded. Strongly cinched armor waist and long panels reduce the requested heavyweight breadth; no confident floating-hand failure.',
'Phone retains the face, shield boundary and pink line very well. Internal grip construction remains uncertain rather than certified from the prompt.'],
'13-C1':[
'Vey has an energetic mischievous grin, defined adult shoulders and a springy low stance. The spiky face remains a familiar manga-protagonist type but differs from the earlier curly-haired youthful route judge in hair mass, jaw emphasis, body and combat posture.',
'Fine directional hatching and black-white-red grouping carry13 clearly. Both hands visibly wrap one gently bent continuous staff, and both white end caps and shoes are framed.',
'Two separate red grip regions replace the stipulated one long center grip; lightning branches off the staff rather than simply following its bend. Overall weapon control and silhouette remain coherent.',
'Phone preserves expression, two-hand pose and bending staff, though right cap has a narrow image margin. No mechanical hard repair recommended.'],
'13-C2':[
'Tessa has a focused attractive adult face and a strong athletic stance; high black tail, white suit and controlled open hand give a clear rival presence. Fine manga drawing and red accents remain cohesive.',
'Actual weapon has a two-strut D-shaped handgrip parallel to the curved blade, held out in front; it is not the stipulated single perpendicular tonfa grip alongside the forearm. Hand contact is visible but the weapon/control mechanism has changed.',
'Weapon is additionally drawn across the portrait, contrary to the weapon-free portrait constraint; portrait hair also lacks the generous top margin. These failures coexist with good facial appeal.',
'Phone keeps the face and large crescent blade clear, but cannot repair the wrong handle geometry or extra portrait weapon.'],
'15-C1':[
'Cassian has a clear regal adult face, swept golden waves, lifted chin and open outward palm; this is a new knightly silhouette rather than the original bald moustached aristocrat or earlier older steward.',
'Dense curved engraving genuinely sculpts skin, hair, cloth and brass; the style is realized in marks, not only sepia color. Complete mace and visible shaft grip remain clear.',
'Faceted mace with resonance bands is identifiable and restrained; armored cape/tabard ensemble gains more plating than the simplest brief. Fine ornament does not overwhelm the major pose.',
'Phone retains appraising portrait and mace silhouette while engraving compresses to tone. No hard repair recommended.'],
'15-C2':[
'Othra has severe mature beauty, strong cheekbones and a shaved-side long wave; her asymmetrical bronze/cloth silhouette distinguishes her from Cassian. Large cutout bow is a memorable weapon, though extra brocade and jewelry make the design busier than requested.',
'Controlled engraving persists. One hand visibly holds the bow grip and three large oval openings appear in each limb.',
'Bowstring mechanism is unresolved: a straight tip-to-tip string remains while another diagonal segment runs from the free hand toward a bright crossing and the grip area. The free hand does not simply touch one continuous string as requested.',
'Phone retains face and bow silhouette, but crossing lines become harder to interpret. Attractive engraving does not establish correct bowstring contact.'],
'17-C1':[
'Rook has roguish adult charisma through a crooked grin, broad jaw, long nose and compact muscular stance; topknot, armor and enormous hooked pick are a substantive departure from the original bespectacled cartographer.',
'Thin clean contour, simple shadow planes and warm/cool shapes retain17. Full pick, counterweight, wrapped shaft hand, free fist and both square boots remain visible.',
'Weapon rests across the shoulder instead of entirely outside it, but beak turns away from the head and reads as formidable combat equipment, not a small mining tool.',
'Phone keeps face, loaded-shoulder gesture and pick silhouette especially clear. No hard retry candidate.'],
'17-C2':[
'Eline has bright amused adult appeal, a clean black bob and long poised figure; simplified face and restrained color retain17. Her sling-bow is visually different from the other weapons and from earlier17 civilian inventory.',
'The Y frame and base-hand grip are clear, with one visible stone in a lower fabric pocket.',
'The drawing hand pulls a band well away from that stone-bearing pocket instead of pinching the loaded pouch. Band paths spread around the forearm/frame, leaving the loading/control relation unclear despite plausible individual fingers.',
'Phone preserves the charming portrait and Y silhouette, but the stone is a small spot near the frame while the pull hand is elsewhere. A focused pouch/contact correction is justified.'],
'18-C1':[
'Bram has exuberant champion appeal: enormous grin, strong brows, massive muscular torso and short heavy legs. This visibly differs from the preceding soft-bellied cook and the original pink-haired woman.',
'Broad cartoon masses and colorful modeled planes retain18, with crisp large shape hierarchy. Huge anchor gives a decisive combat silhouette; hand wraps one shaft and two hooks plus one ring are complete.',
'Hook ends are sharp rather than blunt, hair is swept rather than flat-top and the shaft is long, but the single unified weapon and planted weight remain convincing within fantasy stylization.',
'Phone retains laughter, muscular body and complete anchor very clearly. No scarce repair recommended.'],
'18-C2':[
'Ketz has sharp exuberant appeal, purple sweeping hair, balloon sleeves and a long narrow stance. Facial energy shares the18 expressive family and earlier climber, but new hair mass, silhouette and flail produce a meaningful design alternative.',
'Bold colored planes and lively face retain18. One ball, continuous chain and handle are visibly joined, and the hand wraps the grip; ball rests outside the boot.',
'The chain visibly has more than the specified three links, including several broad face-on links and edge-on connectors. This is a count deviation with otherwise coherent control, lower impact than the bow/sling/tonfa failures.',
'Phone preserves grin, sleeves, ball and chain path. The exact three-link requirement is not met merely because the weapon reads well.'],
'19-C1':[
'Silas has refined alluring facial drawing and a long ivory/dark silhouette, with a huge scythe that clearly supports an elegant supernatural combat role. Thin contour, silky modeling and restrained red retain19 rather than collapsing to the preceding realistic older worker portraits.',
'Novelty is the main concern: long fine nose, heavy-lidded eyes, soft mouth and narrow model build remain strongly source-like. Different dark hair, sleeveless robe and scythe do not independently prove an entirely new facial identity; resemblance is a judgment, not an exact-pixel claim.',
'Hand clearly grips the continuous shaft and full blade/feet are framed. Extra jewelry, patterned robe, root counterhook and butt spike exceed the restrained design; no extra summoned character obscures anatomy.',
'Phone retains delicate face and scythe arc, while pale blade and fine ornament lose definition. This has clear appeal but the strongest originality uncertainty in the set.'],
'19-C2':[
'Vire has mature fashion appeal through controlled eyes, sculpted strawberry hair and severe black/silver masses; she is visibly distinct from Silas and the original male anchor. Refined thin contour and silky modeling retain19.',
'Complete foil, wrapped hand and whole figure remain readable; cup guard is round rather than a clear teardrop. The straight-legged spread reads more as a poised fashion stance than a committed forward fencing guard.',
'Foil tip reaches the portrait divider and fine blade becomes faint on phone. Heeled shoes replace flat shoes, and athletic bulk is reduced to a sleek silhouette.',
'Phone strongly preserves portrait and costume; combat intent is subtler than the weapon label suggests. Record this appeal/acting limit without treating it as an owner rejection.']
}
priorities=[('15-C2','Correct the single bowstring path and free-hand contact; remove the extra crossing/branching segment.'),('17-C2','Bring the stone-bearing pouch into the drawing fingers and connect exactly the intended two band runs to the tips.'),('13-C2','Restore one perpendicular tonfa side grip and beside-forearm relation; keep portrait free of weapon.'),('05-C2','Give the complete harpoon tip clear top margin and route its continuous chain clear of both boots.'),('18-C2','Reduce the chain to exactly three large closed links while retaining a single connected ball and handle; lower-priority count correction.')]
reasons=dict(priorities);entries={};a={'01-C1','01-C2','02-C1','02-C2','05-C1','05-C2','06-C1','06-C2','15-C1','17-C1'}
for k,obs in notes.items():
 r=reg[k];native=root/r['path'];assert hashlib.sha256(native.read_bytes()).hexdigest()==r['sha256']
 folder='a37349676a72-c803782e' if k in a else '780009941b09-c803782e';cap=root/'research/combat-exploration/reader/phone-captures'/folder/f'{k}-390.png';assert cap.exists()
 entries[k]={'attempt_id':r['attempt_id'],'sha256':r['sha256'],'native_path':r['path'],'phone_capture_path':str(cap.relative_to(root)),'phone_capture_sha256':hashlib.sha256(cap.read_bytes()).hexdigest(),'reviewed_native':True,'reviewed_phone':True,'observations':obs,'hard_retry_candidate':k in reasons,'hard_retry_reason':reasons.get(k),'owner_approval':None}
assert len(entries)==18
j={'schema':'CombatExplorationIndependentPrimaryReview/1','experiment_id':'CE-20260908-01','status':'frozen_all18_primary_native_and_phone','owner_approval':None,'exposure':'Read original9 native anchors, frozen plan and exact prompts. No lead output verdict supplied before assessment. Independent review is informed by prior rejected studies, not blinded to history.','rubric_sha256':hashlib.sha256((out/'frozen-rubric.md').read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256((prod/'combat-plan.json').read_bytes()).hexdigest(),'phone_scope':'Every actual1536x1024 source inspected native and as a complete360x240 board in390x844 reader capture. First ten and last eight batches are bound to unchanged sources; no choices entered or acceptance inferred.','entries':entries,'retry_priorities':[{'priority':i+1,'id':k,'attempt_id':reg[k]['attempt_id'],'sha256':reg[k]['sha256'],'reason':v}for i,(k,v)in enumerate(priorities)],'allocation_advice':'Four main mechanism/framing repairs plus one lower-priority link-count repair. Reserve sixth slot rather than seek a prettier variant.19-C1 novelty remains a substantive creative concern, not certified originality or a simple mechanical repair.'}
(out/'primary-findings.json').write_text(json.dumps(j,indent=2)+'\n')
md='''Independent primary combat review — CE-20260908-01

All18 actual primary boards inspected at native size and in source-bound390×844 reader captures, with complete art rendered360×240. Frozen rubric and plan preceded outputs. No lead output verdict was supplied before assessment. This review knows the original anchors and preceding rejected studies; it is independent, not blinded to that history. Owner preferences beyond stated steering, individual choices and approval remain unknown.

The set substantially improves combat identity over the civilian component cast: clear signature weapon families, confident facial close-ups and purposeful body poses.01-C1's cool assessment,02-C2's sharp scowl,05-C1's rugged half-laugh,17-C1's roguish grin and18-C1's exuberant champion show different kinds of appeal. This is an AI visual judgment, not evidence that the owner will like them. Broad champions, slender rivals and controlled veteran types coexist, although many women still share a long-legged narrowed-waist ideal.

Drawing systems are broadly realized:02 warm outlined paint,05 matte tactile painting,06 coarse brush,13 fine action hatching,15 genuine curved engraving,17 economical clear contours,18 broad expressive cartoon volume and19 silky fashion drawing.01 gains somewhat more modeled texture than its original, and warm-colored treatments overlap at the family level. There is no clear whole-route collapse into one generic renderer. Novelty is uneven:19-C1 retains the strongest source-like facial/model construction;02-C1's freckles/brows/grin also echo its source.17-C1 and18-C1 are strong counterexamples to calling every board a reskin.

Portraits generally retain appeal and identity at phone scale. Full-body hands, strings and chain joints are often too small to verify there and require native inspection. Left portrait areas frequently exceed the approximately30% target, reducing full-figure space; generous margins are inconsistent. This is a common presentation deviation, not a reason to redraw every appealing board. Some sword tips enter the portrait side without obscuring a face.13-C2 explicitly adds the weapon into its portrait, a clearer layout failure.

Weapon silhouettes are varied and recognizably combat-oriented. The most significant failures are15-C2 string geometry,17-C2 loaded-pouch contact and13-C2 tonfa construction.05-C2 also lacks top margin and clean chain routing.18-C2's link count is a lower-priority exact-spec failure with an otherwise coherent flail. A striking face or weapon outline does not resolve these mechanisms.

Recommended bounded order:

'''
for i,(k,v)in enumerate(priorities):md+=f'{i+1}. {k}-P — {v}\n'
md+='''
Reserve the sixth slot. A creative redesign for19-C1 originality would need a deliberate decision about facial identity rather than an unspecified beauty retry. Preserve that concern even if no retry is allocated. Written progression concepts often use stored/delayed/returned force, but their limitations and instruments differ; the small power cues on these boards cannot prove staged growth, actual fighting choreography or reader comprehension.

Per-attempt observations follow; exact source and screenshot hashes are in primary-findings.json.

'''
for k,obs in notes.items():md+=k+'-P\n\n'+'\n\n'.join(obs)+'\n\n'
md+='''Strongest positive counterexample:18-C1 combines a new muscular adult, instantly readable joyful face and massive complete anchor in an unmistakable18 drawing system, without relying on extra effects. Strongest failure counterexample:15-C2 remains appealing and faithfully engraved while its drawn string geometry does not explain the promised one-string control. This is a reviewable unaccepted combat-character exploration, not a finished continuity-tested cast or owner-selected winner.
'''
(out/'primary-findings.md').write_text(md)
print('Frozen18 entries;5 candidates. JSON SHA256',hashlib.sha256((out/'primary-findings.json').read_bytes()).hexdigest())
