from __future__ import annotations

from typing import Any


VISUAL_TARGET = (
    "Clean premium vertical-webtoon illustration with confident linework, broad controlled color shapes, "
    "smooth cel-shaded surfaces, restrained gradients, crisp focal silhouettes, intentional negative space, "
    "minimal environmental particles, readable material separation, and selective detail only at the narrative focal point."
)

NEGATIVE_DIRECTION = (
    "No film grain, no snow filter, no dust veil, no all-over particles, no stippling, no halftone wash, "
    "no canvas texture, no paper texture, no chromatic noise, no edge chatter, no excessive sparks, no random debris, "
    "no indiscriminate bloom, no oversharpening, no muddy fog, no busy background texture, and no decorative micro-detail across every surface."
)

# A restrained median blend is used only on plates whose measured micro-detail
# and full-resolution visual review both indicate pervasive noise. It preserves
# broad forms, line art, material boundaries, and narratively caused debris.
CLEAN_ART_PANELS: dict[int, tuple[str, float, str]] = {
    14: ("edge_chatter", 0.34, "Calm fine edge chatter around the charge while preserving the claw/plank impact."),
    19: ("excessive_micro_texture", 0.38, "Reduce all-over surface grit; preserve the jaw-to-spear contact and body rotation."),
    22: ("chromatic_speckles", 0.36, "Remove stray chromatic pinpoints outside the one verified stress path."),
    25: ("decorative_debris", 0.36, "Suppress incidental flecks; preserve the warning joint silhouette."),
    34: ("indiscriminate_bloom", 0.32, "Tighten the ember effect to the fist and collarbone circuit."),
    36: ("muddy_atmospheric_veil", 0.34, "Clarify the three-stage breath path without flattening cloth, skin, or ember energy."),
    39: ("excessive_micro_texture", 0.36, "Calm background grain; preserve the closing ankle seam and slipping spear."),
    41: ("over_sharpening", 0.34, "Reduce high-frequency edge halos while keeping Elian's eyeline and the recreated fault crisp."),
    42: ("chromatic_speckles", 0.36, "Keep one grounded acceleration line; remove peripheral orange flecks."),
    44: ("excessive_sparks", 0.38, "Reduce non-causal sparks and grit; preserve the fracture stroke, contact, and large ceramic shards."),
    45: ("decorative_debris", 0.40, "Calm fine debris and surface noise; preserve the fall direction and single Overburn fleck."),
    46: ("dust_veil", 0.34, "Clear the quiet verification beat while retaining material separation and the dark jaw seam."),
}


def _u(kind: str, text: str, box: list[float], speaker: str, order: int, *,
       style: str | None = None, tail: list[float] | None = None,
       font: float | None = None, previous: str | None = None,
       action: str = "relettered", justification: str | None = None) -> dict[str, Any]:
    default_font = 0.040 if kind == "dialogue" else 0.034
    return {
        "kind": kind,
        "style": style or ("speech" if kind == "dialogue" else "ledger" if kind == "ui" else kind),
        "speaker": speaker,
        "text": text,
        "previous_text": previous if previous is not None else text,
        "box": box,
        "tail": tail,
        "font_scale": font or default_font,
        "reading_order": order,
        "editorial_action": action,
        "justification": justification,
    }


def _sfx(text: str, box: list[float], order: int, rotate: float = -8.0) -> dict[str, Any]:
    return {
        "kind": "sfx", "style": "belljaw_sfx", "speaker": "environment",
        "text": text, "previous_text": text, "box": box,
        "at": [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2],
        "rotate": rotate, "font_scale": 0.070, "reading_order": order,
        "editorial_action": "recomposed", "justification": "Open SFX follows the force vector and avoids the contact silhouette.",
    }


def lettering_units() -> dict[int, list[dict[str, Any]]]:
    """The complete revised CH01 lettering source, including silent panels."""
    return {
        1: [],
        2: [_sfx("GONNNG", [.70, .12, .91, .21], 1, -4)],
        3: [_u("dialogue", "Old breaks round off.", [.04, .06, .34, .18], "Elian", 1, tail=[.39, .31])],
        4: [_u("ui", "ELIAN VOSS · LV 3\nSALVAGER · SEED I\nXP 60/100 · HP 44/52 · QI 31/40", [.59, .05, .95, .27], "Brass Ledger", 1, previous="ELIAN VOSS · LV 3 · XP 60 / 100 · SALVAGER · BREATH SEED I · HP 44 / 52 · QI 31 / 40", action="rewritten")],
        5: [
            _u("dialogue", "Tell me that bright edge is old.", [.04, .04, .37, .17], "Mira", 1, tail=[.39, .29], previous="Tell me the bright edge is old.", action="rewritten"),
            _u("dialogue", "Opened clean.", [.67, .80, .95, .91], "Elian", 2, tail=[.58, .70], previous="It was opened clean.", action="rewritten"),
        ],
        6: [
            _u("dialogue", "Both seals?", [.04, .05, .30, .16], "Mira", 1, tail=[.38, .32]),
            _u("dialogue", "Still mine.", [.69, .80, .94, .91], "Elian", 2, tail=[.59, .69]),
        ],
        7: [_sfx("KRAK", [.70, .05, .92, .15], 1, -11)],
        8: [_u("dialogue", "The lift is across. Move before it sings twice.", [.04, .05, .41, .20], "Mira", 1, tail=[.48, .33], previous="The lift is across. We move before it sings twice.", action="rewritten")],
        9: [],
        10: [_u("ui", "BELLJAW WARDEN · LV 6\nBRIDGE CUSTODIAN\nTRAIT · LOAD RESPONSE", [.04, .05, .40, .22], "Brass Ledger", 1, previous="BELLJAW WARDEN · LV 6 · EMBER VAULT BRIDGE CUSTODIAN · VERIFIED TRAIT: LOAD RESPONSE", action="rewritten")],
        11: [],
        12: [
            _u("dialogue", "If it reaches center, the bridge rolls.", [.04, .04, .39, .18], "Elian", 1, tail=[.45, .31]),
            _u("dialogue", "I turn the head. You read the legs.", [.64, .79, .95, .92], "Mira", 2, tail=[.58, .68], previous="Then I turn the head. You read the legs.", action="rewritten"),
        ],
        13: [_u("dialogue", "Right shoulder. Stay behind it.", [.61, .06, .94, .19], "Mira", 1, tail=[.55, .34], previous="Stay behind my right shoulder.", action="rewritten")],
        14: [], 15: [],
        16: [_u("dialogue", "Come on.", [.70, .05, .94, .15], "Mira", 1, tail=[.60, .29])],
        17: [_sfx("THOOM", [.05, .06, .32, .18], 1, 6)],
        18: [],
        19: [_u("dialogue", "It wants the shaft.", [.04, .05, .36, .18], "Mira", 1, tail=[.44, .31])],
        20: [_u("dialogue", "Hold its jaw there.", [.65, .05, .95, .18], "Elian", 1, tail=[.57, .31], previous="Hold the jaw there.", action="rewritten")],
        21: [_u("ui", "FAULT SIGHT I · ACTIVE\nQI 31→19 · 6s\nONE STRESS LINE · COOLDOWN 20s", [.04, .05, .41, .24], "Brass Ledger", 1, previous="FAULT SIGHT I · ACTIVE · QI 31 → 19 · COST 12 · ONE VERIFIED STRESS LINE · 6s · COOLDOWN 20s", action="rewritten")],
        22: [],
        23: [
            _u("dialogue", "Six seconds.", [.04, .05, .28, .16], "Elian", 1, tail=[.37, .28]),
            _u("dialogue", "I can make four useful.", [.70, .80, .95, .92], "Mira", 2, tail=[.61, .70]),
        ],
        24: [], 25: [],
        26: [_sfx("KRAK", [.05, .06, .29, .17], 1, -14)],
        27: [],
        28: [_u("ui", "HP 44→22\nINJURY · CRACKED RIB\nSOURCE · BELLJAW IMPACT", [.60, .05, .95, .23], "Brass Ledger", 1, previous="HP 44 → 22 · INJURY: CRACKED RIB · SOURCE: BELLJAW FORELIMB IMPACT", action="rewritten")],
        29: [],
        30: [
            _u("dialogue", "Elian. Look at me.", [.04, .05, .33, .16], "Mira", 1, tail=[.43, .30]),
            _u("dialogue", "Don't turn that hit into a plan.", [.05, .17, .41, .25], "Mira", 2, tail=[.44, .35], previous="Do not turn that hit into a plan.", action="rewritten", justification="Linked same-speaker beat uses one visual cluster."),
        ],
        31: [_u("dialogue", "The seed won't carry.", [.67, .78, .95, .90], "Elian", 1, style="whisper", tail=[.57, .69])],
        32: [],
        33: [
            _u("dialogue", "That gets us through Chainworks.", [.04, .04, .39, .13], "Mira", 1, tail=[.68, .34], previous="That gets us back through Chainworks.", action="rewritten"),
            _u("dialogue", "Only if you can let go.", [.05, .14, .39, .24], "Elian", 2, tail=[.33, .38]),
            _u("dialogue", "I didn't tell you to spend it.", [.63, .72, .95, .82], "Mira", 3, tail=[.68, .60]),
            _u("dialogue", "I know.", [.69, .84, .94, .93], "Elian", 4, style="whisper", tail=[.40, .63], justification="Explicit split-distance dialogue panel; four short turns are paired into two separated clusters."),
        ],
        34: [_u("ui", "SPARK TALISMAN · CONSUMED\nQTY 1→0 · QI 19→33\nRESTORE 14 · VOLUNTARY CATALYST", [.04, .04, .36, .19], "Brass Ledger", 1, previous="SPARK TALISMAN · TEMPERED · QUANTITY 1 → 0 · QI 19 → 33 · RESTORE 14 · VOLUNTARY CATALYST", action="rewritten")],
        35: [],
        36: [_u("open", "BREATH PATTERN · −30 QI\nQI 33→3", [.05, .81, .40, .92], "Brass Ledger", 1, style="ledger_delta", previous="BREATH PATTERN · −30 QI · QI 33 → 3", action="rewritten")],
        37: [_u("ui", "BREATH SEED I→II\nQI MAX 40→48 · CURRENT 3→11\nFAULT STEP I · COMPATIBLE", [.59, .05, .95, .27], "Brass Ledger", 1, previous="BREATH SEED I → II · BROKEN BREATH UNDER THREAT · QI MAX 40 → 48 · CURRENT 3 → 11 · FAULT STEP I COMPATIBLE", action="rewritten")],
        38: [
            _u("open", "OVERBURN · 1/2\nHP 22→21", [.04, .79, .36, .91], "Brass Ledger", 1, style="ledger_delta", previous="OVERBURN · TICK 1 / 2 · HP 22 → 21", action="rewritten"),
            _u("dialogue", "Breathe again.", [.66, .04, .94, .11], "Mira (off-panel)", 2, style="off_panel", tail=None),
            _u("dialogue", "Working on it.", [.67, .12, .94, .19], "Elian", 3, style="whisper", tail=[.58, .30]),
        ],
        39: [_u("dialogue", "The fault is closing.", [.04, .05, .35, .17], "Mira", 1, tail=[.43, .30])],
        40: [_u("dialogue", "I can load it once.", [.67, .05, .95, .17], "Mira", 1, tail=[.58, .30])],
        41: [
            _u("dialogue", "Don't hold after the turn.", [.04, .05, .37, .17], "Elian", 1, tail=[.45, .30]),
            _u("dialogue", "Wasn't planning to.", [.68, .80, .95, .91], "Mira", 2, tail=[.59, .70]),
        ],
        42: [_u("ui", "FAULT STEP I · ACTIVE\nQI 11→3 · VERIFIED FAULT\nONE BURST · COOLDOWN 8s", [.59, .05, .95, .24], "Brass Ledger", 1, previous="FAULT STEP I · ACTIVE · QI 11 → 3 · COST 8 · ONE BURST ALONG VERIFIED FAULT · COOLDOWN 8s", action="rewritten")],
        43: [_u("dialogue", "Turn.", [.04, .05, .25, .15], "Mira", 1, tail=[.34, .27])],
        44: [_sfx("KLANG", [.66, .05, .93, .18], 1, -8)],
        45: [_u("open", "OVERBURN · 2/2\nHP 21→20", [.04, .80, .35, .91], "Brass Ledger", 1, style="ledger_delta", previous="OVERBURN · TICK 2 / 2 · HP 21 → 20", action="rewritten")],
        46: [], 47: [],
        48: [
            _u("ui", "BELLJAW · DEFEATED\nANCHOR · 1 INTACT\nQUEST · COMPLETED", [.58, .04, .95, .23], "Brass Ledger", 1, previous="BELLJAW WARDEN DEFEATED · BRIDGE ANCHOR 1 INTACT · QUEST COMPLETED", action="rewritten"),
            _u("ui", "+85 XP · LV 3→4\n45/140 XP · HP MAX 56\nATTRIBUTE POINT +1", [.58, .38, .95, .57], "Brass Ledger", 2, previous="KILL SHARE +85 XP · LV 3 60/100 → LV 4 45/140 · HP MAX 52 → 56 · ATTRIBUTE POINT +1", action="rewritten"),
            _u("ui", "CINDER-KEY · RARE ×1\nPROVENANCE · BELLJAW", [.58, .71, .95, .88], "Brass Ledger", 3, previous="CINDER-KEY · RARE ×1 · PROVENANCE: BELLJAW WARDEN", action="rewritten", justification="Reward reconciliation is the narrative beat; three narrow strips total under 25% area."),
        ],
        49: [
            _u("dialogue", "Both hands?", [.62, .03, .94, .09], "Mira", 1, tail=[.55, .12], previous="Can you feel both hands?", action="rewritten"),
            _u("dialogue", "Yes.", [.64, .11, .88, .16], "Elian (off-panel)", 2, style="off_panel", tail=None),
            _u("dialogue", "Blood when you breathe?", [.61, .18, .95, .255], "Mira", 3, tail=None, previous="Any blood when you breathe?", action="rewritten"),
            _u("dialogue", "No.", [.65, .275, .85, .325], "Elian (off-panel)", 4, style="off_panel", tail=None, previous="No."),
            _u("dialogue", "Good. No third answer.", [.62, .345, .94, .415], "Mira", 5, tail=None, previous="Good. You don't get a third answer.", action="rewritten", justification="Care-panel call and response is separated into unambiguous speakers; the first solid Mira contour anchors later solid responses while Elian's off-panel responses use dashed contours."),
        ],
        50: [
            _u("dialogue", "That sound isn't coming down.", [.04, .06, .39, .18], "Elian", 1, tail=[.44, .30]),
            _u("dialogue", "It's climbing.", [.70, .81, .95, .91], "Mira", 2, tail=[.60, .70]),
        ],
        51: [
            _u("ui", "CHOOSE THE CRACK · OFFERED\nSELECT A CLASS PATH\nREACH THE CROWN · REGENT ASCENT ACTIVE", [.35, .12, .70, .37], "Brass Ledger", 1, previous="CHOOSE THE CRACK · OFFERED · SELECT A CLASS PATH · REACH THE HOLLOW MERIDIAN CROWN · BELL REGENT ASCENT ACTIVE", action="rewritten"),
            _u("dialogue", "Choose when the room stops moving.", [.04, .79, .35, .91], "Mira", 2, tail=[.42, .69], previous="Choose after the room stops moving.", action="rewritten"),
            _u("dialogue", "The room may object.", [.69, .80, .95, .91], "Elian", 3, style="whisper", tail=[.60, .70]),
        ],
        52: [
            _u("dialogue", "My pace.", [.70, .06, .94, .16], "Mira", 1, tail=[.61, .26]),
            _u("dialogue", "This time.", [.70, .80, .94, .90], "Elian", 2, style="whisper", tail=[.38, .60]),
            _sfx("GONNNG", [.68, .91, .94, .95], 3, -3),
        ],
    }


FACTION_FAMILIES = [
    {"id":"free-delvers","name":"Free Delver Fieldwork","silhouette":"asymmetric repair plates, exposed tie points, modular pockets","palette":["soot black","weathered teal","witness brass"],"materials":["salvaged steel","oiled leather","reversible stitch-cloth"],"iconography":"open knot and three tally cuts","upgrade_language":"added braces and visible repairs; never ornamental glow","tradeoff":"easy to service but carries public provenance and favors"},
    {"id":"ash-crown","name":"Ash Crown Contract-Forged","silhouette":"forward wedges, crown-notched spines, debt-cord channels","palette":["charcoal","arterial crimson","polished black brass"],"materials":["pressure steel","lacquered cord","heat glass"],"iconography":"broken crown over a closed loop","upgrade_language":"narrower, more coercive load paths and additional contract sockets","tradeoff":"burst efficiency transfers wear or debt to a named bearer"},
    {"id":"civic-meridian","name":"Civic Meridian Office Issue","silhouette":"rectilinear housings, numbered seals, tamper bars","palette":["ivory enamel","bureau blue","registry brass"],"materials":["enamel plate","certified brass","ledger glass"],"iconography":"vertical lift line inside a square","upgrade_language":"added verification windows and lawful access teeth","tradeoff":"reliable only while credentials and maintenance fees remain valid"},
    {"id":"verdigris","name":"Verdigris Communion Grownwork","silhouette":"ribbed vessels, root hinges, porous fins","palette":["oxidized green","wet umber","pale mineral blue"],"materials":["living copper","mire reed","calcified resin"],"iconography":"three roots sharing one droplet","upgrade_language":"new circulation channels and scar rings","tradeoff":"self-repairs by consuming clean water, salts, or bodily heat"},
    {"id":"bellwright","name":"Bellwright Remnant Resonance","silhouette":"tuned arcs, clapper weights, concentric interruption gaps","palette":["smoked ivory","ember orange","dark iron"],"materials":["bell ceramic","tuning steel","resonance glass"],"iconography":"open bell crossed by a silent line","upgrade_language":"clearer harmonic gaps and fewer, larger tuned parts","tradeoff":"power depends on timing; mistimed resonance injures allies and structures"},
    {"id":"archive-concord","name":"Archive Concord Witnesscraft","silhouette":"folding frames, visible hinges, paired lenses","palette":["ink violet","parchment gray","cold gold"],"materials":["memory glass","blackwood","silvered thread"],"iconography":"two eyes sharing one ledger line","upgrade_language":"additional evidence layers and reversible seals","tradeoff":"records exact use, exposing secrets and limiting deniability"},
]


CHAIN_DEFS = [
    ("hookline", "Elian leverage blade", "main_hand", "free-delvers", ["Bent-Tooth Hook", "Witness-Hook Shortblade", "Regentbreaker Hook"], ["short inward hook", "split-backed hook with tally spine", "long counterweighted crescent with one silent notch"], ["redirects one light object or limb", "stores one verified load angle for a repeat pull", "shares a timed pull across consenting allies"], ["poor reach; jars injured ribs", "stored angle expires when geometry changes", "each linked ally accepts visible strain"], ["scrap tooth + grip cord", "Belljaw ivory + witness brass", "Regent plate + four-party timing seal"], ["CH01–02", "CH05–07", "CH09–10"]),
    ("coat", "Elian survival coat", "body", "free-delvers", ["Frayed Salvager Coat", "Cross-Stitched Loadcoat", "Shared-Seam Mantle"], ["long torn hem", "diagonal rib braces", "four detachable load tabs"], ["conceals and secures salvage", "redistributes one blunt impact away from a marked injury", "lets allies brace a declared seam"], ["snags on tight machinery", "braces restrict breath until loosened", "fails if risk was not declared aloud"], ["coat lining + waxed thread", "mire reed + ivory splints", "archive thread + consent clasp"], ["CH01", "CH05–08", "CH18–24"]),
    ("seals", "portable seal kit", "utility", "civic-meridian", ["Iron Seal Capsule", "Forked Writ Seal", "Consent-Notary Seal"], ["thumb brass capsule", "Y-shaped stamp jaw", "paired open rings"], ["stabilizes one damaged mechanism", "chooses repair access or route access", "records who accepted a transferred load"], ["consumed on use", "choice permanently closes the other writ channel", "cannot certify coerced or hidden terms"], ["iron dust + registry wax", "sponsor writ fragment + split key", "archive foil + two witness signatures"], ["CH01–03", "CH09–12", "CH19–27"]),
    ("spear", "Mira formation spear", "main_hand", "free-delvers", ["Dark-Teal Spear", "Socketline Partisan", "Crosslock Standard"], ["clean leaf point", "forked butt and sliding grip", "offset bannerless crossbar"], ["anchors precise thrust lines", "loads floor sockets without surrendering point control", "defines a shared formation axis"], ["long shaft suffers in cramped routes", "socket use fixes Mira's pivot", "formation breaks if one member exceeds declared reach"], ["teal ashwood + steel leaf", "Chainworks socket + grip leather", "Regent tuning bar + four repair marks"], ["CH01", "CH05–07", "CH09–10"]),
    ("shield", "Mira load shield", "off_hand", "free-delvers", ["Ivory Split Shield", "Counterweight Splitshield", "Open-Center Bastion"], ["tall ivory slab with split", "split slab with low pendulum", "two crescent plates around an open handspan"], ["wedges and redirects frontal load", "converts one rotation into planted force", "protects allies without hiding their sightlines"], ["weak to rear torque", "pendulum punishes sudden direction changes", "center gap exposes Mira if formation spacing fails"], ["bell ceramic + arm straps", "counterweight chain + Mire resin", "Bailiff yoke + transparent archive brace"], ["CH01", "CH06–08", "CH10–16"]),
    ("satchel", "Orin medical workshop", "back", "free-delvers", ["Nine-Stitch Satchel", "Triage Frame", "Witness Surgeon Rig"], ["boxy nine-pocket bag", "folding rib frame", "open circular brace with three tool arms"], ["carries finite treatment modules", "stabilizes one moving patient", "records which injury costs were deferred"], ["only nine sealed uses", "healer loses mobility while deployed", "reveals prognosis to patient and party"], ["treated canvas + brass needles", "Mire bone + folding hinges", "memory glass + consent ribbon"], ["CH03–04", "CH06–09", "CH14–22"]),
    ("lanes", "Sable debt mobility", "legs", "ash-crown", ["First-Lane Greaves", "Crownfork Runners", "Unbound Forkstep"], ["single red shin channel", "two crown-notched heel forks", "open heels with severed cord loops"], ["borrows one burst of speed", "chooses two narrow pre-paid routes", "converts witnessed debt refusal into lateral escape"], ["adds one debt stack", "cannot stop inside a chosen lane", "works only after refusing a genuine advantage"], ["pressure steel + debt cord", "Bailiff tooth + contract lacquer", "cut debt cord + witness silver"], ["CH04", "CH08–10", "CH17–25"]),
    ("lens", "fault-reading optics", "head", "archive-concord", ["Cracked Survey Lens", "Paired Quoin Lens", "Consent Prism"], ["single chipped monocle", "hinged unequal lenses", "clear triangular brow frame"], ["reveals static stress", "compares present load with one prior state", "separates accepted load from transferred load"], ["blind spot at moving joints", "memory overlay can lag in combat", "cannot read intent, only recorded agreement"], ["survey glass + copper clip", "memory glass + quoin hinge", "archive foil + civic consent field"], ["CH02–03", "CH11–15", "CH24–30"]),
    ("breath", "cultivation regulator", "core", "bellwright", ["Ember Reed", "Three-Note Sternum Cage", "Quiet Meridian Diaphragm"], ["one curved reed", "three open chest arcs", "low floating half-ring"], ["steadies one broken inhale", "paces three safe breath phases", "lets the bearer abort a realm attempt without collapse"], ["dries and cracks after use", "audible cadence reveals timing", "aborting sacrifices stored Qi and a crafted reed"], ["mire reed + ember salt", "Belljaw clapper + rib-safe straps", "Regent membrane + three spent reeds"], ["CH03–05", "CH09–14", "CH22–30"]),
    ("anchor", "portable formation anchor", "utility", "civic-meridian", ["Bridge-Tooth Clamp", "Chainworks Traveling Anchor", "Public-Line Brace"], ["one biting C-clamp", "paired roller jaws", "wide folding tripod"], ["claims one structural foothold", "moves a safe point along a chain", "stabilizes public infrastructure while a party fights"], ["damages soft material", "requires continuous crank attention", "users become liable for visible civic damage"], ["bridge tooth + iron seal", "counterchain + ratchet", "lift rail + public repair bond"], ["CH02", "CH05–07", "CH20–26"]),
    ("key", "Cinder-Key path relic", "relic", "bellwright", ["Cinder-Key", "Forked Cinder-Key", "Fourth-Door Tuning Key"], ["thumb-length split key", "two unequal prongs", "long hollow key with four missing teeth"], ["offers compatible paths", "opens one class branch while sealing another", "unseals an archive cadence"], ["unbound and tactically inert", "choice creates faction obligations", "requires all four missing tooth-provenances"], ["Belljaw ankle ember", "class oath + preserved anchor", "Regent note + three archive witnesses"], ["CH01", "CH02–07", "CH10–20"]),
    ("cord", "risk-sharing cord", "party", "archive-concord", ["Witness Cord", "Declared-Load Braid", "Four-Hand Covenant"], ["thin paired thread", "flat braid with open knots", "four radial loops around empty center"], ["marks who saw a decision", "distributes one declared strain", "enables party-scale authority without a crown"], ["records secrets in its fibers", "hidden injury breaks distribution", "any member can veto and end the technique"], ["silver thread + wax", "four repair scraps + spoken terms", "consent foil + unclaimed crown socket"], ["CH11–13", "CH18–22", "CH28–30"]),
]


STANDALONE_ITEMS = [
    ("Roundoff Chalk","tool","utility","free-delvers","flat triangular chalk cage","bone chalk / soot brass","marks old fatigue separately from fresh shear","washes away in wet zones","turns Elian's private read into shared evidence","ground bone + lamp soot","choose visibility or stealth","CH02","broken-circle icon; chipped edge persists"),
    ("Chain-Kiss Gloves","armor","hands","free-delvers","open knuckles, hooked palms","oiled leather / link steel","grips moving chain without locking the wrist","reduces fine tool control","protects the hand that caught Mira's spear","chain scales + tendon thread","grip safety versus precision","CH03","three palm hooks, never claws"),
    ("Borrowed Breath Ampoule","consumable","belt","ash-crown","red glass lung vial","heat glass / debt lacquer","restores 10 Qi immediately","transfers 6 HP loss to a named later hour","embodies delayed institutional cost","ember salt + signed debt cord","drink now or keep future health","CH04","one visible red hour band"),
    ("Mire-Salt Poultice","consumable","belt","verdigris","folded green rib pad","mire reed / mineral salt","reduces movement penalty from one blunt injury","consumes body heat and slows cultivation","care competes with progression","clean water + mire salts","mobility versus realm practice","CH03","darkens as heat is taken"),
    ("Clapper-Wedge","tool","utility","bellwright","small asymmetric tuning wedge","bell ceramic / tuning steel","silences one resonant mechanism for eight beats","stores the interrupted note and releases it on removal","creates timed quiet, not free safety","Belljaw chip + steel leaf","safe removal or weaponized release","CH05","single orange notch"),
    ("Ash Crown Winner's Token","seal","relic","ash-crown","black coin cut like a crown tooth","black brass / contract glass","grants the holder sole claim to one reward","voids allied contribution credit","makes betrayal mechanically legible","Bailiff seal + debt signature","claim power or preserve party credit","CH04","one side mirror-black, one side blank"),
    ("Verdigris Pump Heart","component","pack","verdigris","ribbed copper seed","living copper / pale resin","repairs fluid machinery and grows one temporary conduit","dies if removed from clean flow twice","stores the cost of saving the pump","pump core + mineral water","keep alive or salvage rare copper","CH06","scar rings record removals"),
    ("Glassback Echo Scale","component","pack","bellwright","clear plate with moving hairline","resonance glass / silver dust","records one three-note pattern","shatters if used to brute-force a fourth note","rewards patient pattern learning","Glassback scale + quiet wax","memory tool or single-use lure","CH03","hairline moves, no glitter"),
    ("Counterseal Rivet","component","small","civic-meridian","square rivet with open center","registry brass / enamel","repairs certified gear without voiding its record","requires a lawful serial and fee","ties maintenance to bureaucracy","brass mark ×4 + office stamp","legal repair or illicit freedom","CH11","blue enamel corner only"),
    ("Rib-Cage Lacing","armor","body","free-delvers","diagonal external laces","waxed cord / ivory splint","lets an injured bearer declare a safe twist limit","enemy can read the limit too","injury becomes visible coordination data","coat lining + splint","conceal weakness or coordinate honestly","CH03","left/right placement never swaps"),
    ("Cold Ledger Shard","relic","utility","archive-concord","thin violet rectangle with broken corner","memory glass / cold gold","replays one verified transaction at full provenance","also reveals the bearer's adjacent transaction","evidence costs privacy","archive glass + bloodless witness seal","public proof or private leverage","CH12","always one missing corner"),
    ("Liftkeeper's Thumb","tool","utility","civic-meridian","stubby ivory key with roller","enamel / brass","manually advances a stalled public lift one level","locks the user out of the next lift cycle","civic access becomes personal delay","lift tooth + maintenance bond","save this car or preserve future access","CH16","grease-black roller"),
    ("Mourning Rivet","seal","body","free-delvers","black rivet tied with pale thread","iron / witness thread","prevents one repaired item from being silently replaced","blocks further enhancement until its loss is named","keeps sacrifice visible","broken gear fragment + name","memory versus optimization","CH09","never polished"),
    ("Mire Choir Stopper","tool","utility","verdigris","three-prong porous plug","living copper / reed","diverts one flow channel without killing it","must be watered every hour","nonlethal control creates upkeep","mire copper + clean cloth","carry water or accept collapse","CH06","three wet pores"),
    ("Crownspike Bailiff Tooth","component","heavy","ash-crown","long black wedge","pressure steel / red enamel","pierces certified barriers and contract seals","brands the carrier as a claimant","power creates legal pursuit","Bailiff tooth + claim wax","weaponize or present as evidence","CH04","one crown notch"),
    ("Belljaw Ankle Plate","component","heavy","bellwright","curved ivory load plate","bell ceramic / soot iron","makes armor exceptionally stable under one known vector","brittle under redirected load","victory's lesson becomes gear grammar","Belljaw plate + resin","armor plate or forge substrate","CH02","fracture line must remain visible"),
    ("Public Heat Chit","currency","seal","civic-meridian","perforated brass strip","brass / blue wax","pays one household heat cycle or one civic forge hour","cannot do both","grounds crafting in household stakes","earned contract credit","warm a home or forge gear","CH18","serial perforations"),
    ("Sumpglass Needle","weapon","off_hand","verdigris","transparent hooked needle","sump glass / living copper","threads cultivation energy through liquid","breaks in dry air after three exchanges","environment defines tactical value","sump glass + wet sheath","heal flow or cut flow","CH06","always visibly wet"),
    ("Quoin-Maker's Square","tool","utility","archive-concord","folding unequal square","blackwood / cold gold","tests whether a structure's stated load matches its actual load","cannot identify the liar","turns suspicion into admissible discrepancy","blackwood + memory hinge","record evidence or preserve access","CH13","one arm shorter"),
    ("Hush Bell","relic","neck","bellwright","small open bell with no clapper","smoked ivory / black cord","cancels the wearer's footfall on a chosen rhythm","also cancels their spoken warning","stealth competes with consent","bell ceramic + severed clapper","silence or coordination","CH15","empty center, no glow"),
    ("Debt-Cord Shears","tool","utility","ash-crown","short opposing crescent blades","pressure steel / witness silver","cuts one active debt cord","converts the remaining obligation into public evidence","escape creates testimony","Bailiff tooth + silver hinge","private freedom or public accusation","CH08","red cord residue remains"),
    ("Anchor-Breath Tea","consumable","belt","verdigris","flat two-chamber flask","mire leaf / brass","steadies breath during stationary guarding","halves burst movement while active","supports Mira's stillness and exposes its limit","mire leaf + hot clean water","hold ground or keep mobility","CH05","two chambers, green steam"),
    ("Regent Membrane","component","relic","bellwright","translucent concentric skin","resonance membrane / cold gold","stores one cadence without amplifying it","replays pain from the original strike","boss reward carries bodily memory","Regent membrane + quiet frame","training archive or dangerous weapon","CH10","four concentric tears"),
    ("Unclaimed Crown Socket","relic","party","archive-concord","empty crown-shaped housing","black brass / memory glass","accepts distributed authority instead of a sole bearer","remains inert unless every linked member can withdraw","makes accountable leadership mechanical","sponsor crown + four witness cords","centralize or distribute command","CH27","empty center is invariant"),
]


BUILD_ARCHETYPES = [
    {"name":"Declared Fault Runner","core":"Fault Sight + physical acceleration + witness tools","tactics":"reads one line, declares it, then commits only after a partner loads it","cost":"low tolerance for changing geometry","relationship_pressure":"must disclose incomplete reads"},
    {"name":"Shared-Load Bastion","core":"split shield + socket spear + load braid","tactics":"redirects force into prepared allies and architecture","cost":"formation spacing and consent are mandatory","relationship_pressure":"cannot privately absorb every hit"},
    {"name":"Field Triage Mechanist","core":"finite treatment satchel + repair clamps","tactics":"stabilizes bodies and gear during movement","cost":"every saved resource closes another treatment option","relationship_pressure":"must name triage preferences"},
    {"name":"Unbound Lane Duelist","core":"route greaves + debt-cutting tools","tactics":"creates and abandons narrow movement lanes","cost":"best burst requires refusing an offered advantage","relationship_pressure":"trust depends on visible debt choices"},
    {"name":"Resonance Patient","core":"echo scale + breath regulator","tactics":"waits for complete cadence before countering","cost":"poor against irregular swarms","relationship_pressure":"asks allies to hold while evidence matures"},
    {"name":"Verdigris Flowkeeper","core":"living copper + water economy","tactics":"reroutes hazards and grows temporary cover","cost":"clean water and heat upkeep","relationship_pressure":"party comfort becomes crafting fuel"},
    {"name":"Civic Breach Auditor","core":"lawful seals + load evidence","tactics":"turns infrastructure permissions into battlefield constraints","cost":"credential revocation and public liability","relationship_pressure":"truth may close routes people need"},
    {"name":"Consent Lattice Conductor","core":"witness cords + distributed authority socket","tactics":"shares timing and strain without a singular commander","cost":"one veto ends the technique","relationship_pressure":"leadership depends on reversible agreement"},
]


BOSS_REWARD_FAMILIES = [
    {"boss":"Belljaw Warden","grammar":"load response and redirected fracture","rewards":["Cinder-Key","Belljaw Ankle Plate","Clapper-Wedge"],"choice":"path access versus durable load armor"},
    {"boss":"Glassback Choir","grammar":"three-note memory and moving weak points","rewards":["Glassback Echo Scale","Paired Quoin Lens","Hush Bell"],"choice":"record the pattern or weaponize its silence"},
    {"boss":"Crownspike Bailiff","grammar":"single-winner adjudication","rewards":["Bailiff Tooth","Crownfork Runners","Debt-Cord Shears"],"choice":"claim coercive mobility or build an exit from debt"},
    {"boss":"Mire Choir","grammar":"flow division without killing the system","rewards":["Pump Heart","Sumpglass Needle","Mire Choir Stopper"],"choice":"save infrastructure or harvest combat material"},
    {"boss":"Collapse Hound","grammar":"removing weak structures","rewards":["Traveling Anchor","Loadcoat Braces","Mourning Rivet"],"choice":"portable safety or visible memorial lock"},
    {"boss":"Brass Maw","grammar":"tuning civic machinery","rewards":["Three-Note Sternum Cage","Liftkeeper's Thumb","Public Heat Chit"],"choice":"personal cultivation or public access"},
    {"boss":"Bell Regent","grammar":"shared cadence under ascent pressure","rewards":["Regentbreaker Hook","Crosslock Standard","Regent Membrane"],"choice":"finish a weapon, a formation, or an archive"},
    {"boss":"Fourth-Door Notary","grammar":"consent fields and reversible authority","rewards":["Consent Prism","Four-Hand Covenant","Unclaimed Crown Socket"],"choice":"read consent, share load, or restructure command"},
]


FUTURE_CAST_ROWS = [
    ("Orin Pell","ally, medic, and exacting craft mentor","Free Delvers","late 30s; compact, deliberate, always balanced over both feet","square satchel frame and rolled sleeves","long tired eyes, cropped black curls, one silver temple patch","nine-pocket canvas, bone splints, brass closures","Nine-Stitch Satchel","three-step triage: stop, name, spend","keep people alive long enough to learn","having to rank lives","clinically distant yet keeps every broken tool","he falsified one Ash Crown death time to protect a survivor","Elian must accept treatment; Mira must stop hiding pain","CH03","satchel loss forces a smaller, more honest practice","silver temple patch; nine pocket tabs; no flowing coat","miracle healer, carefree comic medic, resemblance to Elian"),
    ("Sable Renn","rival, antagonist, eventual provisional ally","Ash Crown","mid 20s; lean forward pitch, weight always on toes","twin red heel forks and one shoulder higher","black asymmetrical bob, amber eyes, debt scar behind left ear","pressure-steel shin channels, cropped contract jacket","First-Lane Greaves","committed linear bursts, no safe stop","become impossible to revoke","worth ending when debt ends","hates rigged contracts but wins them","her first debt signature was forged by a guardian","forces Elian to distinguish reading from ownership; tests Mira's mercy","CH04","from debt-fueled speed to witnessed refusal","left-ear scar; twin heel forks; no cape","secretly harmless rival, cat burglar silhouette, easy redemption"),
    ("Ilyra Quoin","mentor and discredited bellwright","Bellwright Remnant","early 60s; tall, narrow, hearing posture turned sideways","three tuning arcs carried like ribs","shaved head, heavy white brows, burn notch in upper lip","layered soot apron over ivory resonance braces","Three-Note Sternum Cage","counters only after hearing a complete cycle","prove the instrument was built to record consent","another student becoming a weapon","merciless about timing, tender with damaged bells","she helped suppress the Ledger consent field under civic order","offers Elian truth at the cost of Mira's trust","CH09–11","mentor becomes witness, then defendant","lip notch; three arcs; never carries a sword","mystic crone, omniscient mentor, vague prophecy"),
    ("Tovan Rusk","lift captain and public-duty ally","Free Delvers","40s; broad torso, shortened right leg, rolling gait","wide key ring balanced against one braced boot","round shaved face, moss beard, brass tooth","maintenance coat with blue civic patches turned inside out","Liftkeeper's Thumb","terrain control through lifts, gates, counterweights","keep shift workers moving","becoming a symbol instead of a mechanic","defies orders but craves official certification","he once closed a lift on an unregistered crew","makes Elian answer to civilians, challenges Mira's formation priorities","CH12","field captain to public infrastructure organizer","short right-leg brace; brass tooth; key ring","jolly innkeeper, bumbling bureaucrat, giant hammer user"),
    ("Nemea Silt","morally ambiguous cultivator and flowkeeper","Verdigris Communion","early 30s; fluid shoulders, bare feet, unsettling stillness","ribbed copper water frame around the spine","deep-brown skin, pale blue irises, rope twists tied low","porous reed layers, living copper channels, no leather","Mire Choir Stopper","redirects liquid, heat, and Qi rather than striking","keep the Sump alive as a person-like ecology","dry civic extraction","saves systems before individuals","she planted a pump failure to force public negotiation","tempts Elian with nonviolent control; refuses Mira's person-first triage","CH06","from ecosystem absolutist to negotiated steward","spinal water frame; blue irises; always wet hem","nature saint, poison witch, barefoot waif"),
    ("Cassian Vey","strategic antagonist and civic sponsor official","Civic Meridian Office","50s; immaculate average build, occupies space through attendants","perfect square ivory collar and one vertical blue seal","soft gray hair, unremarkable face, unblinking hazel eyes","certified enamel coat with concealed pressure weave","Sponsor Writ Seal","turns permissions, liabilities, and schedules into weapons","prevent civic collapse under any administration","uncontrolled public panic","genuinely protects continuity by sacrificing the unregistered","his office did not start the scheme; he inherited and optimized it","offers Elian lawful authority; treats Mira as an expensive stabilizer","CH10 shadow, CH17 face","public steward to exposed optimizer who must choose continuity or consent","no crown; one blue vertical seal; spotless cuffs","cackling noble, military tyrant, physically imposing villain"),
    ("Bryn Corda","chainwright craftswoman and reluctant ally","Free Delvers","late 20s; powerful forearms, compact center, grease-grounded stance","double coil harness framing both shoulders","freckled face, blunt blond braid, missing right eyebrow tip","short leather apron, reversible sleeves, exposed tool loops","Chainworks Traveling Anchor","builds moving safe points while others fight","make repairs people can understand and own","beautiful relics nobody can service","abrasive about craft, sentimental about public hardware","she sells one design to Ash Crown to fund lift repairs","makes Elian choose repairability; clashes with Mira over prototype risk","CH05","scavenger smith to cooperative workshop founder","double coils; eyebrow gap; no oversized forge gloves","cheerful blacksmith, dwarf coding, magical instant forging"),
    ("Varo Quell","Ash Crown retrieval chief","Ash Crown","late 30s; long-limbed, relaxed until contracts activate","black triangular cloak opening around a rigid spine rail","close-shaved dark hair, pale left eye, narrow nose break","pressure-weave suit with detachable claimant plates","Winner's Token","removes options before drawing a narrow blade","retire with every subordinate's debt canceled","being recorded as the one who chose","protective commander who enforces abusive contracts","he is personally liable for Sable's forged debt","turns Elian's evidence into hostage leverage; respects Mira's explicit terms","CH08","field hunter to compromised whistleblower or final enforcer","pale left eye; spine rail; no mask","smirking assassin, sadistic torturer, generic raven motif"),
    ("Hana Mire","archive investigator and conditional ally","Archive Concord","mid 40s; upright, narrow hands always visible","two unequal lens frames and a folding square","straight black chin-length hair, gold-flecked brown eyes","violet witness coat with reversible parchment lining","Cold Ledger Shard","reconstructs transactions while allies hold the scene unchanged","make proof survive power","evidence becoming spectacle","demands consent but withholds her own motives","she is Cassian Vey's estranged older sister","presses Elian toward publicity and Mira toward procedural patience","CH11","investigator to custodian of public testimony","unequal lenses; visible hands; violet/parchment reversal","detective trenchcoat cliché, infallible lie detector, secret assassin"),
    ("Rell Thorne","debt broker, fixer, and morally ambiguous operator","Independent / Ash Crown","30s; soft-bodied, quick hands, seated authority","many narrow cords radiating from one low belt","warm brown face, shaved crown with side curls, split lower lip","layered clerk vest, no armor, contract cords sleeved in silk","Debt-Cord Shears","negotiates and cuts obligations mid-conflict","own one obligation no patron can call","being needed only as a parasite","kind in person, predatory in aggregate","keeps a private ledger of debts he secretly paid","offers Sable exits that implicate others; sells Elian truthful partial maps","CH14","broker to witness or architect of a new coercion","split lip; radial belt cords; never carries coins visibly","greedy merchant caricature, cowardly informant, comic relief"),
    ("Ysabet Glass","resonance rival and uneasy ally","Bellwright Remnant","early 20s adult; long reach, dancer's recovery, chin lifted to listen","one translucent scale fan along left forearm","dark copper curls cropped on right, gray eyes, glass scar on jaw","smoked-ivory plates over flexible black knit","Glassback Echo Scale","stores and returns the third note of any exchange","out-hear the mentor who abandoned her","silence and irrelevance","vain performer who practices anonymous rescue work","her hearing is failing from stored resonance","forces Elian to finish patterns; challenges Mira's quiet leadership","CH13","rival virtuoso to adaptive tactician without perfect hearing","jaw scar; left scale fan; no instrument weapon","singing bard, elegant ice mage, cruel prodigy"),
    ("Dagan Holt","retired delver, official inspector, obstructive mentor","Civic Meridian / Free Delvers","late 60s; heavy seated posture, one arm ending below elbow","broad empty right sleeve pinned across a ledger board","dark weathered face, clouded right eye, iron-gray beard fork","old delver coat under current enamel sash","Quoin-Maker's Square","halts fights by declaring unsafe structures and forcing reroutes","make the city remember why codes exist","another preventable collapse","rigid rule-follower who forged the first Free Delver waiver","his lost arm was the original consent-field test","blocks reckless progress, then teaches Mira how to relinquish center","CH16","inspector to public witness against his own office","empty sleeve; clouded eye; forked beard; no prosthetic weapon","wise old warrior, gruff dad substitute, surprise powerhouse"),
]


LOADOUTS = [
    {"character":row[0],"signature":row[7],"secondary":item,"silhouette_rule":row[4],"tactical_grammar":row[8]}
    for row,item in zip(FUTURE_CAST_ROWS,["Rib-Cage Lacing","Debt-Cord Shears","Hush Bell","Public-Line Brace","Sumpglass Needle","Forked Writ Seal","Traveling Anchor","Winner's Token","Consent Prism","Cold Ledger Shard","Echo Scale","Declared-Load Braid"])
]


ACQUISITION_SCHEDULE = [
    {"window":"CH01–03","purpose":"survival and provenance","acquisitions":["Cinder-Key","Roundoff Chalk","Belljaw Ankle Plate","Mire-Salt Poultice"],"constraint":"one Spark Talisman is permanently gone; two Iron Seals remain finite"},
    {"window":"CH04–06","purpose":"defeat, repair, and environmental choice","acquisitions":["First-Lane Greaves","Triage Frame","Socketline Partisan","Verdigris Pump Heart"],"constraint":"rebuilds compete with treatment and civic repair"},
    {"window":"CH07–10","purpose":"party recombination and Regent clear","acquisitions":["Regentbreaker Hook","Crosslock Standard","Counterweight Splitshield","Regent Membrane"],"constraint":"Relic maintenance exceeds normal party income"},
    {"window":"CH11–15","purpose":"evidence and liability","acquisitions":["Cold Ledger Shard","Paired Quoin Lens","Forked Writ Seal","Hush Bell"],"constraint":"using evidence exposes adjacent private records"},
    {"window":"CH16–20","purpose":"public routes and coercion exits","acquisitions":["Public-Line Brace","Debt-Cord Shears","Declared-Load Braid","Consent-Notary Seal"],"constraint":"lawful access can be revoked; public choices create obligations"},
    {"window":"CH21–25","purpose":"distributed cultivation and leadership","acquisitions":["Quiet Meridian Diaphragm","Unbound Forkstep","Shared-Seam Mantle","Consent Prism"],"constraint":"best upgrades require refusing singular advantage"},
    {"window":"CH26–30","purpose":"city-scale shared load","acquisitions":["Four-Hand Covenant","Unclaimed Crown Socket","Fourth-Door Tuning Key"],"constraint":"any linked member retains a real veto"},
]
