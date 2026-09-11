# Story, progression, and action audit

Role: Story, Progression, and Action Editor  
Worktree: `C:\AgentWorkspaces\anime-pipeline-total-review-20260906-211925`  
Date: 2026-09-06  
Authority rule: **scripts and finished pages are the proof corpus**. Bibles, ledgers, Phase B `PASS` notes, and the existing `volume-story-audit.md` are treated as claims, not as evidence that those claims reached the reader.

Every finding is tagged **Observation**, **Inference**, or **Recommendation**. Rubric scale matches `docs/research/anime-pipeline-total-review/common-rubric.json` (0–5). Schema integrity, hash continuity, and SystemState `PASS` do not raise story scores.

---

## 0. Method and corpus

### Pages actually inspected (not sampled from audits)

**Ember Lattice ten-chapter volume (lettered HTML + source rasters)**

- Volume readers: `docs/reimaginings/ember-lattice/volume/chapters/ch01`–`ch10` (`full.html`, SVG overlays).
- Source rasters: `C:\AgentWorkspaces\anime-pipeline-litrpg-manhwa-20260904-001211\experiments\reimaginings\ember-lattice\` (pilot `source/p001–p016.png`; volume `ch01`–`ch10/source`; QA contact sheets).
- Scripts/plans/copy: `production/reimaginings/ember-lattice/volume/chapters/ch0N/{comic-panel-plans,lettering-copy,system-state}.json`; `volume/progression.html`; `volume/dialogue-and-density-metrics.json`; `volume/action-choreography.json`.

**Ember Lattice premium CH01 (52-panel)**

- Script: `production/reimaginings/ember-lattice/premium-rd/ch01-premium-script.md`.
- Unique rasters: `C:\AgentWorkspaces\anime-pipeline-ember-lattice-premium-rd-20260904-150943\experiments\reimaginings\ember-lattice\premium-rd\ch01-unique\` (28 PNGs + contact).
- Hybrid lettering: `docs/reimaginings/ember-lattice/premium-rd/panels/hybrid\`; `production/reimaginings/ember-lattice/premium-rd/assets/ch01-hybrid\`.
- Lettering report: `reimaginings/ember-lattice/premium-rd/lettering-editorial-report.md`.

**Sibling stories (scripts + finished pages)**

- Borrowed Down: bibles/outline/audits in `C:\AgentWorkspaces\anime-pipeline-reimagining-20260903`; rasters in that worktree's `experiments/reimaginings/borrowed-down\` (CH01 reading draft, lettered `ch01-s01-p01`, `ch01-s06-p05`).
- The City Keeps Oaths: bibles/outline/audits in `C:\AgentWorkspaces\anime-pipeline-reimagining-clean-webtoon-20260903-213010`; rasters in that worktree's `experiments/reimaginings/the-city-keeps-oaths\` (CH01 reading draft + `ch01-s01-p01`; CH10 phone preview).
- North Garden: `production/canon/story-state`, `production/scene-beats`, `production/comic` in this worktree (plans/state only; no competing ten-chapter raster corpus here).

**Bibles read as intention, not as success**

- `reimaginings/ember-lattice/*.md` plus `premium-rd/story-package.md`, `volume-story-audit.md`, `future-cast-bible.md`.

### What this audit will not treat as proof

- Phase B audits `01`–`04` all report `PASS` on fight causality, genre promise, and “causally shown” class evolution. Those documents score completeness against plans and ledgers. They do not score whether a stranger can read the beat from the picture.
- Internal premise evaluation scored Ember Lattice **99/100 before pages existed** (`production/reimaginings/ember-lattice/premise-evaluation.json`).
- `volume-story-audit.md` already names compression, converged voice, and late antagonists. That diagnosis is confirmed here **only where pages and copy still show it**. The premium CH01 script addresses several of those faults on paper; unique rasters cover 28 of 52 panels, so the 52-panel “premium rewrite” is not a fully new visual chapter.

---

## 1. Answers to the five required questions

### 1. Does Ember Lattice have a sufficiently strong premise, cast, progression engine, visual identity, and emotional hook to justify further investment?

**Recommendation: invest in the premise and the CH01–CH04 dramatic spine as a short causality pilot payload. Do not invest in further ten-chapter Ember Lattice production, future-cast expansion, or more bible layers until a stranger can read one fight, one cost, and one class change from pictures plus short speech.**

| Dimension | Volume pages (CH01–CH10) | Premium CH01 pages | Bible / ledger |
|---|---|---|---|
| Premise | 3 — dungeon-as-instrument + transferred-risk is legible in captions more than in objects | 3.5 — shear-clue is attempted; still a generic orange crack | 4.5 — strongest original LitRPG argument in the corpus |
| Adult cast appeal | 3.5 — Elian/Mira/Orin/Sable silhouettes work; faces often poster-handsome | 3 — identity drift (open shirt, darker hair, beetle-Belljaw) | 4 — engines are written |
| Progression engine | 4 arithmetic / 2 theatrical | 3 — more silent panels in lettering, still glow-as-level-up | 5 — provenance, gates, irreversible spend |
| Visual identity | 3 establishing / 2 combat language | 3 cinematic atmosphere / 2 same orange-fault vocabulary | 4 on paper |
| Emotional hook | 2 | 2.5 | 4 |

**Observation.** The series promise in `story-package.md` is specific and adult: a failed salvager who can see breaks, a dungeon that is a colossal instrument, a Ledger that records contribution but not consent, and a party that refuses to treat people as expendable parts. That is a better LitRPG argument than “numbers go up.”

**Observation.** On finished volume pages, that promise is mostly spoken. CH01 opens with a strong abyss-and-bridge picture, then a caption that explains the six-year-early wake. The sabotage clue (straight shear vs rounded wear) is not in volume P001–P003 art. The Spark Talisman choice is staged as a two-object menu in the hands. The CH07 protection gate — the volume’s thematic centerpiece — is a kneeling man touching a glowing floor crack while Mira stands unthreatened by a pump.

**Inference.** The property is worth keeping as a *payload*, not as a production schedule. Further volume chapters would multiply the same 24-panel template: caption, status plate, posed two-shot, orange-fault combat, loot glow, reconciliation. That is not a serialization engine. It is a ledger with illustrations.

### 2. Story architecture vs reader propulsion: coherent ledgers vs addictive urgency

**Observation.** Architecture is the strongest part of Ember Lattice. Every chapter closes a reconciled SystemState. Items do not respawn. Injuries have IDs. Quests can `FAIL` or `COMPLETED_WITH_LOSS`. CH04’s `claim-verdigris-seal` stays failed. Density metrics are almost identical across CH01–CH06 (`16/6/2` low/moderate/high; four system moments each; ~24 dialogue units). `system-bible.md` locks that cadence: “exactly four meaningful Ledger moments” per chapter.

**Observation.** Volume chapter endings routinely explain the next objective in polished speech, then park a status card. CH01 Mira/Elian: “Then our volume problem is no longer getting out.” CH10 Mira: “Then the next volume begins with evidence. This one ends with everyone still here to read it.” Those lines break serial immersion and replace a hook image with a production memo.

**Inference.** A reader who likes spreadsheets will trust this book. A reader who likes *what happens next* is given summaries of what already happened. Urgency is asserted (Bell Regent climbing, public lift, debt default) and then spent on UI. The architecture would support addictive serialization if panel budgets followed event load and if the last image of each chapter changed the direction of travel without naming “volume.”

**Recommendation.** Keep the ledger. Kill the four-moment chapter template and the 24-panel uniform length. End on an object, a body, or a door — never on a recap.

### 3. Action causality completeness vs pose assembly

**Observation.** `action-choreography.json` requires `geography → intention → initiation → contact/interruption → consequence → response → adaptation → payoff/state` and lists action panel orders. Volume CH01 marks P005–P011, P014–P015 as action. The pictures are mostly single-figure or two-figure stances with an orange accent.

Causal chain that *almost* exists in CH01 (pilot/volume):

1. P001 bridge over abyss — geography (good).
2. P005 side-on map — geography (readable on contact sheet).
3. P006 charge — initiation (Belljaw on boards).
4. P007–P008 Mira plant / clamp — contact, but P007–P008 jump to a cream/white field unlike the vault.
5. P011 impact — contact exists; Elian is punched; he still holds the blade; the chain is nearby rather than the destination of a backhand.
6. P015 combo finish — spectacle pose, jaw not clamped, shield geometry changed, ankle is an explosion not a hairline seam.

**Observation.** The impact panel is overwritten by lecture. Volume SVG `docs/reimaginings/ember-lattice/volume/chapters/ch01/panels/p011.svg` places a cream balloon over the punch:

> Contact never happened. Forelimb changed angle after the jaw clamp—remember that when it comes again.

That is the definition of pose-plus-caption replacing aftermath. Premium script P025–P029 specify silent warning, silent impact, silent collision, then a long gutter. Premium unique `ch01-unique/p026.png` is a better hit (limb, body, debris, Mira in depth). It is still a freeze-frame, not a three-panel consequence (hit / rib / hang).

**Inference.** The pipeline can generate *a* dramatic still for a named beat. It does not yet generate the *in-between* panels that make a still into comics: weight shift, missed distance, object that falls, partner’s face registering cost. ComicPanelPlan `camera` fields cycle a closed vocabulary (`expressive mature close-up`, `controlled object insert`, `calm negative-space wide`, …) even when they contradict the beat. CH01 P001 beat is an establishing abyss; its plan camera is `expressive mature close-up`. That is assembly language, not staging.

### 4. What improved across successive stories vs what only improved in documentation

Improved **on pages** (real, bounded):

- Adult human design: from North Garden kitchen pair → Borrowed Down laboring adults → City Keeps Oaths civic adults → Ember Lattice combat adults. Faces and bodies read as adults in all three reimaginings.
- Distinct world thumbnails: vertical sea + crane (Borrowed Down CH01 P01); luminous road over cloud (City CH01 P01); chain bridge over furnace shaft (Ember CH01 P001).
- Diegetic craft instead of floating generic RPG chrome: burdencraft knots, oathlight roads, Brass Ledger plates (the last only in lettering overlays).
- Ember volume has the only explicit numeric LitRPG the owner asked for, and the only irreversible inventory that a validator can check.
- Premium CH01 lettering is actually shorter. P003 is four words: “Old breaks round off.” Volume P003 is two long jokes about singing anchors and professional opinions.
- Ember CH08 P002 visualizes Sable’s debt as glowing arm-links — one of the few pages where a mechanic is a body, not a paragraph.

Improved **only in documentation**:

- Ember `story-package.md` mystery table, reversal map, movement II–III, future-cast of twelve adults. None of that is on a finished page except Orin (CH03) and Sable (CH04).
- `volume-story-audit.md` already lists the exact prose failures that remain in the lettered volume.
- Phase B fight-causality and continuity audits `PASS` while CH07 P012/P014 do not show the protection choice they claim.
- Premise evaluation 99/100, style-candidate scores, density PASS, phone overflow PASS.
- Future-cast bible (Ilyra, Tovan, Nemea, Cassian, …) is a reservoir, not a cast the reader has met.
- Premium 52-panel *script* is a real craft upgrade; 28 unique rasters plus reused baselines mean the upgrade is incomplete as a delivered chapter.

### 5. Should the next pilot use Ember Lattice, a new story, or a neutral benchmark sequence?

**Recommendation: a neutral sequential-art benchmark, with Ember Lattice CH01 (premium script beats, not volume 24-panel art) as the optional story payload. Do not start a fourth original IP. Do not extend Ember to CH11–CH30.**

Rationale is in §12. Short version: a new story would reproduce the documented pattern (bible → 99-point premise score → 24-panel template → Phase B PASS). Ember’s existing ten chapters already prove the ledger. They do not prove comics. The missing proof is eight to sixteen pages in which a stranger can recover initiation, miss, cost, and shared finish without reading a plan file.

---

## 2. Story-owned rubric scores

Scored from **finished lettered volume pages** unless noted. Premium CH01 called out in comments.

| Dimension | Score | Confidence | Evidence |
|---|---:|---|---|
| immediate_genre_legibility | 3 | high | Dungeon, boss, HP/Qi plates, loot exist in overlays. Unlettered rasters read as dark-fantasy stills; class/XP are not in the paint. |
| opening_hook | 2.5 vol / 3.5 prem script | high | Vol P001 image is strong; copy dumps schedule lore. Premium P001 silent + P003 four-word clue is the right hook; unique P003 still shows Belljaw too early and a generic glowing crack. |
| emotional_engagement | 2 | high | Injuries are blood spots and guarded ribs; partners lecture. CH07 protection and CH04 defeat are explained, not felt. |
| curiosity_and_chapter_end_propulsion | 2.5 | high | Class offer and climbing pulse are real hooks. Meta “volume” lines and reconciliation cards spend them. |
| memorability | 3 | high | Belljaw, split-shield Mira, Sable debt-arm, hanging bell-Regent. Combat language (orange crack, ceramic quadruped, leaping man) repeats until it is wallpaper. |
| desire_to_continue_reading | 2.5 | medium | Adult pair and dungeon instrument could pull a genre reader. After two chapters of identical density and voice, the pull is the ledger, not the people. |
| panel_to_panel_causality | 2 | high | See §7 catalog. Geography panels work; contact/aftermath often skip. |
| acting_and_reaction_clarity | 2 | high | Default faces: grim handsome, grim determined, grim injured. Mira’s anger is a frown. Elian smirks in vol P003 while the bridge fails. |
| action_choreography | 2 | high | Vectors are claimed in copy (“right-to-left,” “bottom-to-top”). Pictures are posed impacts. |
| impact_and_aftermath | 2 | high | Vol P011 impact talks. Vol P016 aftermath is the best quiet page in CH01 — then P017–P024 explain the theme. |
| system_clarity | 4 overlay / 2 paint | high | Ledger arithmetic is excellent. On art, skills = orange line, cultivation = chest fire or floor pentacle, class = glowing circle. |
| progression_satisfaction | 2.5 | high | Gains are earned in the validator. On page they cluster (CH03, CH07, CH10) and look like the same glow. |
| combat_application_of_progression | 2.5 | high | Fault Sight/Step are sometimes a hairline, more often a smash. Rift Mark is a magic circle (CH07 P016). |
| items_gear_skills_with_meaningful_choices | 3 ledger / 2 page | high | Talisman vs seals is a real choice. Vol P013 shows both in the hands as a shop UI. Bent spear (CH04 P015) is not bent. |
| understandable_stakes_and_constraints | 3 | high | Lift, pump, debt, one-winner seal are named. Public city is almost never seen; “city” is a caption. |
| balance_between_system_information_and_drama | 2 | high | Four system moments per chapter by policy. Drama shares balloons with tactics and theme. |

Owner-named comparable bar (Tower of God, Solo Leveling) is **not** reached on any story dimension scored from these pages. Competent serial would be a 3. This volume is a 2–3 with a 4 in off-page accounting.

---

## 3. Premise, opening hook, adult cast, emotional engine

### Premise

**Observation.** Ember Lattice’s locked promise: failed adult salvager Elian Voss sees structural faults; Hollow Meridian wakes six years early; Brass Ledger offers a brutal path through a dungeon-instrument; Ash Crown externalizes risk; the fantasy is shared timing, not invulnerability.

That is stronger than Borrowed Down’s gravity-debt city and City Keeps Oaths’ oath-roads **for the owner’s stated LitRPG/manhwa goal**, because it makes XP, class, cultivation, inventory, and boss grammar one vocabulary (fault, load, cadence, provenance). City and Borrowed Down are original civic fantasies; they are not the requested genre machine.

**Observation.** Internal selection (`premise-evaluation.json`) picked Ember over Skygrave Cartographer and Red Current Forge on a rubric written before candidates, total 99 vs 90 vs 88. Those scores include `immediate_litrpg_legibility: 12/12` and `action_spectacle: 12/12` for a concept paragraph. **Inference.** That file measures appetite, not delivery.

### Opening hook

**Observation — Ember volume CH01.**

- P001 raster (`…/pilot/source/p001.png`): two readable adults on a chain bridge over a furnace shaft. Good. They are not “tiny silhouettes”; the beat overclaims scale.
- Overlay caption: “The Hollow Meridian was not scheduled to wake for another six years. The chains disagree with the schedule.” The picture does not show a schedule, a wake, or wrong wear. The hook is a prose dump on a good establishing shot.
- P003 (`…/pilot/source/p003.png`): poster two-shot. Beat: “failing bridge anchor remains visible between their adult faces.” No anchor is visible. Elian’s mouth is nearly a smirk. Mira’s split shield and copper bob *are* distinctive.
- Dialogue: “That anchor is singing… professional opinion…” / “Professional opinion revised. The bridge has a landlord…” First human speech is interchangeable wit.

**Observation — Ember premium CH01.**

- Script P001 is silent. Hybrid SVG for P001 has no balloons. That is the correct open.
- Script P003: fingertips on a shear face; “Old breaks round off.” Hybrid overlay is those four words. Craft upgrade.
- Unique raster `ch01-unique/p003.png`: Elian crouches at a **glowing orange stone crack**, hooked blade already drawn, Belljaw already on the far platform (script reveal is P009), Mira absent, hanging bell in background. The specific clue (bright straight metal tooth vs rounded old break) is not pictured. The monster is present too early.

**Observation — Borrowed Down CH01 P01** (`…/borrowed-down/chapters/ch01/lettered-panels/ch01-s01-p01.png`): crane, tram, workers, vertical water, caption “In Veyr, down arrives by schedule.” World-hook is immediate. A blank beige rectangle eats part of the art (lettering-band leftover). The hook is better than Ember’s caption; the page craft is wounded.

**Observation — City Keeps Oaths CH01 P01** (`…/the-city-keeps-oaths/chapters/ch01/panels/ch01-s01-p01.png`): adult pathwright on a pearl road over clouds. Reading draft lettering: “Every road in Caelune remembers.” Civic-fantasy hook, illustration-first. Not LitRPG. Stronger “I want to be in this place” than Ember, weaker “I want to see the next number/fight.”

**Observation — North Garden CH01.** Scene beat: “A quiet practical argument under emergency conditions; spatial separation carries tension.” No dungeon, no progression, no serial hook. It is a pipeline ancestor, not a competitor for this product question.

### Adult cast appeal

**Observation.** Elian (27, ash-blond, hooked blade, frayed coat) and Mira (32, copper bob, split shield, spear) are designed as working adults. Orin (forge-medic, satchel, silver temple) and Sable (asymmetric black hair, debt glow, saber) separate cleanly on contact sheets. This is a real gain over generic teen-Isekai defaults.

**Observation.** Appeal on page is often fashion-plate: open coats, beauty lighting, hip-cocked stances. Working-partner fluency is claimed (vol P007 “practiced and wordless” in premium script; volume P003 is a magazine cover). Premium unique P006 on the contact sheet looks like a tabletop glowing cube, not belt seals. Identity drifts between volume (tattered gray-green coat, split shield) and premium (darker open shirt, beetle-Belljaw, Mira hair toward burgundy).

**Observation.** Future-cast bible specifies twelve additional adults with engines, secrets, and “avoid” lists. **Inference.** That document improves *planning* for adult serial range. It does not exist in the reader’s experience. Putting twelve more designs through the same generator before CH01 causality works would multiply identity drift.

### Emotional engine

Written engine (bible): Elian believes usefulness means spending himself; Mira refuses to treat sacrifice as strategy; Sable’s debt is coerced consent; Orin will not cosmetically erase irresponsibility.

**Observation from copy.** Characters announce the engine:

- CH05: “Do not hide a sacrifice inside the word 'efficient' and expect us to thank the arithmetic.”
- CH07: “Choose the person first and let the class catch up.” / “Your class changed after your choice did.”
- CH10: “Nobody carries this alone.” / “For once, the difference is voluntary.”

**Observation from pictures.** CH01 P016 (`…/pilot/source/p016.png`) is the emotional page that works: Elian sits, blood on the shirt, Cinder-Key on the boards, Mira standing watch, Belljaw down. No one needs to say “cost matters.” Volume then spends eight more panels explaining class, medic, and “volume problem.”

**Inference.** The emotional engine is real in the authors’ heads and fake-felt on the scroll because aftermath is not given silent time, and because every speaker can deliver the theme.

---

## 4. LitRPG / cultivation clarity

### What the ledger does well (off-page, but real)

**Observation.** XP thresholds, carry, provenance, HP/Qi costs, skill ranks/cooldowns/conditions, item quantities, rarity, crafting consumption, quest FAIL, faction and trust, cultivation gates that require a *kind of act* (broken breath under threat; three-note hold with injured hand; protection over damage; accept hostile cadence) are specified and validated. This is rarer and more honest than most AI LitRPG attempts. CH04 defeat grants discovery XP, not a pity boss-kill. CH08 rescue is accepted with no XP promise. CH07 pump is `COMPLETED_WITH_LOSS`.

### What the reader gets

**Observation.** Unlettered art has three visual verbs for almost all system events: (1) orange hairline or crack, (2) orange chest/hand fire, (3) orange floor circle or pentacle.

Examples:

- Class selection CH01 P019 / CH02 P004 / CH07 P016: floor sigil. CH07 P016 (`…/volume/ch07/source/p016.png`) is a crouch over a pentagram — generic occult UI, not Brass Ledger plates, not “Rift Temperer.”
- Cultivation CH01 P014: ember ring around a kneeling man. Premium unique P034–P038: chest glow, sitting meditation, vertical light column. Cultivation bible demands ugly physical breath (receive / buckle / force through diaphragm). The pictures are power-up stills.
- Fault Sight: sometimes a line (CH01 P009), often a glowing smash target.
- Rift Mark’s “nonliving fault after survived pattern, 4s, 22 Qi” is not picturable from CH07 P016–P017 without the overlay.

**Observation.** Lettering *does* carry the numbers. Volume CH01 P002 status plate; skill/cost plates; end-state cards. Premium CH01 splits reconciliation into three strips (script P048) and keeps 15 silent panels. That is the right UI philosophy. It is still overlay-dependent. If the overlay is stripped, the genre collapses to “people hit a ceramic monster until orange happens.”

**Inference.** LitRPG clarity is currently a lettering feature, not a pictorial one. Cultivation is specified as posture and breath; it is drawn as fire. A reader cannot distinguish Seed II from Channel I from Rift Draw III without reading the plate.

**Recommendation.** One pictorial grammar, enforced in art direction: Fault = hairline on material, never a decal; cultivation = collarbone fissure + ugly inhale, never aura; class = terminal with two unread paths, never a pentacle; item spend = object crushed while the spared object stays on the belt, never both in the palms.

---

## 5. Encounter escalation, reversals, spectacle, rewards, chapter-end propulsion

### Escalation (architecture vs pages)

Written zone grammar (`story-package.md`): one new physical rule per floor — line/load (Belljaw), moving supports (Chainworks), three-note weak point (Glassback), migrating sigil (Bailiff), scarcity (Kiln), fluid lanes (Sump), room-as-weapon (Hound), debt timing (Maw), vertical Crosslock (Crownshaft), dungeon-as-instrument (Regent).

**Observation from contact sheets.** Zones *do* change color and architecture: ember shaft; chain cages (CH02); glass rails (CH03); teal industrial wet (CH04–CH08); hanging bell machine (CH10). That is a real production success.

**Observation.** Enemy bodies rhyme too hard: Belljaw, Glassback, Collapse Hound, Brass Maw, Bell Regent are all pale ceramic/stone machines with orange seams. Distinctive as a *family*, muddy as an escalation. CH03 Glassback reads as a white spider on glass (good). CH07 Hound is another pale quadruped on a beam. CH10 Regent is the one true spectacle design (hanging bell on legs).

**Observation.** Human antagonist pressure is late, as `volume-story-audit.md` said. CH01 has no Ash Crown on page (correct, if the shear clue existed). CH02 rescued delver is a cage + end-caption. Sable arrives CH04 already explaining the one-winner contract. Masked agents are CH08 machinery. Sponsor writ is CH10 loot.

### Reversals

Written reversals that are **structurally** present: early wake is sabotage; weak class reads lines; Bailiff migrates the “correct” weak point; CH04 is a loss; CH07 kill is the wrong gate; Sable debt is a countdown; Regent core is not the sponsor’s real object.

**Observation.** CH04 is the best reversal *on paper* and the only volume chapter whose pictures almost match: Sable exists as a rival silhouette; Bailiff is a white spiked giant with a chest glow; Elian is pinned to a teal wall (P016); Sable takes something from water (P018); party limps out. Failures: Mira’s spear in P015 is straight; Elian’s weapon in that frame looks like a straight sword; “migrating sigil” is a static orange dot; Elian’s post-impact talk continues in copy.

**Observation.** CH07 reversal is **narrated over the wrong picture**. Beat P012: “Elian abandons the killing angle and Fault Steps to the seam that can divert the plate from Mira.” Raster `…/volume/ch07/source/p012.png`: Elian kneeling, back to camera, hand on a glowing floor crack; Mira standing unharmed by the pump; no Hound, no ceiling plate, no open kill. Dialogue: “Killing angle is open… I cannot choose both.” / “Choose the person first and let the class catch up.” P014 raster: two figures standing in water looking at a pump spraying orange — beat claims Breath Channel I routing a falling plate. The reversal happens in balloons.

### Spectacle

**Observation.** Best spectacle stills: CH01 P001 abyss; CH01 P015 ankle smash; CH02 cages and falling body; CH10 hanging Regent; premium P026 hit; premium P044 two-vector finish. These are illustration peaks, not fight peaks. Quiet/spectacle contrast is templated (2 high-density panels per early chapter), not earned.

### Rewards

**Observation.** Loot is provenance-tagged in the ledger and often a brass object on the ground (CH01 P016 key-like tool; CH07 P022 cache). Crafting CH05/CH09 is forge stills plus characters explaining that “if nothing is lost, it was only decoration.” Rewards do not change stance or route *in the next panel*; they change the JSON.

### Chapter-end propulsion

| Chapter | Written end beat | What the last pictures/copy actually do |
|---|---|---|
| CH01 | class offer + pulse climbing | P023–P024 lift + overlay; spoken “volume problem”; Cinder-Key class as floor glow |
| CH02 | Ash Crown named | delver + carapaces + Orin-looking close-up P024; clue is copy |
| CH04 | Sable has the seal | extraction and bloodied shoulder — closest to a true sting |
| CH07 | class + lost sluice | standing reconciliation, satchel grief in two lines |
| CH10 | writ + fourth door | heroic four-person lineup in front of a glowing crack (`…/ch10/source/p024.png`); party looks uninjured; writ not visible; Mira’s arm injury not visible; Elian at 8 HP stands like a poster; copy says “next volume” |

**Observation — siblings.** Borrowed Down CH01 last lettered panel: crowd, Mae and Dax facing a vertical sea, Dax pointing a red line at the wall. The hook is an image (gravity is wrong *that way*). City CH10 phone preview: civic ensemble, “Every witness may withdraw” / “Accepted” / “Witness… beyond.” Shorter speech, still pose-conversation, but the last turn is a world answering, not a meta-volume line.

**Recommendation.** Ban the words `volume`, `Ledger agrees`, `professional`, `arithmetic`, and `inventory` from spoken dialogue except the Ledger itself. End CH01 on the pulse in the chain. End CH04 on Sable walking away with the seal and Mira’s bent spear in the gutter. End CH07 on Orin looking at acid where the satchel was, class plate *after*. End CH10 on the city seal on a document, party too hurt to pose.

---

## 6. Beat-to-art contradiction catalog

Paths are absolute. These are **Observations**.

### Ember volume CH01

| ID | Script/plan beat | Finished page | Contradiction |
|---|---|---|---|
| P001 | Tiny silhouettes; sealed bell lift | `…\ember-lattice\pilot\source\p001.png` | Figures large and readable; lift not a distinct sealed machine |
| P001 plan camera | `expressive mature close-up` in `volume/chapters/ch01/comic-panel-plans.json` | Establishing wide | Plan camera is template residue |
| P003 | Failing anchor between faces | `…\pilot\source\p003.png` | No anchor; poster posing; smirk |
| P007–P008 | Vault combat | contact `…\volume\qa\ch01-source-contact.jpg` | Cream/white field vs charcoal vault |
| P011 | Backhand into chain before hook lands; silent lesson | `…\pilot\source\p011.png` + `docs\…\ch01\panels\p011.svg` | Punch to torso; blade in hand; balloon lectures the miss |
| P013 | Crush Spark Talisman; Iron Seals stay on belt | `…\pilot\source\p013.png` | Right fist crushes a star-medal; left palm **presents two coin-seals**; extra digit risk; choice staged as a shop |
| P015 | Mira pins jaw; Fault Step along hairline; split shield | `…\pilot\source\p015.png` | Open bell-jaw; oval shield; exploding orange joint; Mira thrusting not pinning |
| P016 | Cinder-Key thumb-length brass-and-ember | `…\pilot\source\p016.png` | Brass pliers/tool; otherwise the best aftermath still |
| P019–P020 | Two unread class paths | contact + HTML beat “studies Kiln Appraiser” | Floor rune, not a two-path terminal |
| P024 | Lift closes on class offer | contact P024 | Belljaw-like body still in frame; heroic standing |

### Ember volume CH04

| ID | Beat | Page | Contradiction |
|---|---|---|---|
| P015 | Bailiff crown spike **bends** Mira’s spear | `…\volume\ch04\source\p015.png` | Spear is straight; clash is sparks on a spiked cylinder; Elian’s weapon reads as a straight sword |
| P016 | Shoulder impact, fractured scapula, cracked lens | `…\volume\ch04\source\p016.png` | Pin to a door; grimace; no lens; not a scapula event |

### Ember volume CH07 (thematic centerpiece)

| ID | Beat | Page | Contradiction |
|---|---|---|---|
| P012 | Abandon open kill; Fault Step to divert ceiling plate from Mira | `…\volume\ch07\source\p012.png` | Kneeling crack-touch; Mira idle at pump; no plate, no Hound, no kill angle |
| P014 | Channel I, two pulses, route fault off pump | `…\volume\ch07\source\p014.png` | Two backs, pump spraying orange; no falling ceiling |
| P016 | Accept Rift Temperer; Rift Mark conditions | `…\volume\ch07\source\p016.png` | Pentacle on the floor |

Copy at P012/P015/P023 tells the reader what the pictures omitted.

### Ember volume CH10

| ID | Beat | Page | Contradiction |
|---|---|---|---|
| P001 caption | “a city beneath it” | contact P001 | Dungeon chamber, no city |
| P018 | Channel II = accept hostile cadence | contact P018 | Standing man with orange rings |
| P024 | Fourth door, Sponsor Writ, injured close | `…\volume\ch10\source\p024.png` | Four-person poster; glowing slot; no writ; bodies look fresh |

### Ember premium CH01 unique rasters

| ID | Script | Page | Contradiction |
|---|---|---|---|
| P003 | Shear tooth vs rounded wear; blade sheathed; Mira later | `…\premium-rd\ch01-unique\p003.png` | Orange stone crack; blade out; Belljaw already present |
| P006 (contact) | Hands/eyes; Iron Seals on belt | `ch01-unique-contact.png` cell | Tabletop glowing cube |
| P026 | Interrupted strike, no dialogue | `…\ch01-unique\p026.png` | Better hit; Mira spectates; Belljaw identity ≠ volume ceramic bell-jaw |
| P034–P038 | Ugly breath phases | contact | Chest fire / seated miracle |
| P044 | Hook bites hairline as Mira redirects jaw | `…\ch01-unique\p044.png` | Two-vector spectacle; Mira airborne on the body; crack is a glowing split |

**Observation.** Unique PNG folder contains 28 files for a 52-panel script. Manifest reuses baseline `bm001.png` across early panels. **Inference.** Premium CH01 is a lettering-and-partial-reshoot of the 16/24-panel core, not a fully staged 52-panel chapter.

### Phase B audits vs pages

`docs/reimaginings/ember-lattice/phase-b-audits/02-ch03-ch04-fight-causality-and-arithmetic.md` and `04-ch07-ch10-final-and-repair-wave.md` claim sequences “visibly establish geography, intention, initiation, contact/interruption, consequence…” and that Channel I / Rift Temperer are “causally shown.” **Observation.** Those PASS results track plan language and ledger rows. They are false as a description of CH07 P012–P016 rasters.

---

## 7. Dialogue and voice (scripts vs lettered pages)

**Observation.** Volume spoken/internal words: 3,821 across 240 panels (`dialogue-and-density-metrics.json`). That is not too many words. It is too many *ideas per balloon*, and too many speakers sharing one rhetoric.

Repeated engines in lettering-copy:

- Accounting: professional, arithmetic, inventory, contract, efficient, Ledger agrees.
- Aphorism: “X is not Y; it is Z.”
- Theme diagnosis of another character.
- Meta: “volume problem,” “next volume,” “belonged to this story” (CH09).

CH01 volume first three human lines are jokes. Premium CH01 first human line is four words about wear. That single change is the largest prose improvement in the whole corpus — and it is only fully specified for CH01.

**Observation.** Combat balloons caption visible geometry (“One intact anchor behind us. One boss ahead. If it reaches the center…”). Premium script rule — tactical speech only for timing, invisible cost, or changed plan — is not applied to the ten-chapter overlays.

**Recommendation.** A voice pass is cheaper than regeneration and would immediately raise desire-to-continue. It cannot fix CH07 P012, because the missing beat is pictorial.

---

## 8. Cross-story comparison (pages, not bibles)

| | North Garden | Borrowed Down | City Keeps Oaths | Ember volume | Ember premium CH01 |
|---|---|---|---|---|---|
| Premise on page 1 | Kitchen argument (plan only here) | Gravity-as-schedule, vertical sea | Roads remember promises | Abyss + lore caption | Silent abyss (script); unique P003 clue attempt |
| Genre machine | None | Burdencraft, not LitRPG | Covenant chords, not LitRPG | Numeric LitRPG in overlays | Same, fewer words |
| Adult appeal | Practical pair | Laboring adults, print-epic | Civic adults, clean cel | Combat adults, handsome | Same, identity drift |
| Fight causality | n/a in this corpus | Still-heavy; 2 creature repairs | Conversation > combat | Pose assembly | Better hits, still poses |
| Chapter-end hook | n/a | Image of sea-as-wrong-down | World answers / “beyond” | Recap + “volume” | Script: lift + GONNNG |
| What the pages prove | Pipeline ancestor | Distinct world thumbnail; lettering-band damage | Webtoon-shaped lettering; civic tone; weak LitRPG | Ledger + adult dungeon stills | Shorter copy can exist; art did not fully follow |

**Inference.** Each reimagining improved *packaging* (viewer, phone preview, overlays, audits). Story propulsion did not monotonically improve. Ember added the genre machine the owner wanted and then used it as a metronome. City has the most “licensed webtoon-shaped” lettered scroll. Borrowed Down has the most memorable opening object (down for sale). Ember has the only honest numeric progression. None of the three, on pages, has addictive fight causality.

**Observation.** Borrowed Down CH08 and CH10 required targeted repairs for spent-knot reuse and wrong creature anatomy (`FINAL_AUDIT.md`). Those are story-continuity failures caught after generation — the same class of problem as Ember’s unbent spear and menu-seals.

---

## 9. What a serial reader actually receives, chapter by chapter (volume)

Compressed. Full lettering is in the JSON; this is the **page** experience.

- **CH01.** Strong place. Weak first talk. Fight is a handful of stills. Cost is a punch and a sitting man. Then eight panels of class TED talk. Hook exists (pulse, key) and is spent.
- **CH02.** Class choice is a glow. Rescue-in-a-cage is the most causal action set in the early volume (chain, falling person, mites). Ash Crown is a closing caption. Delver is a clue-delivery device.
- **CH03.** Orin arrives (good face). Rib treatment is a shirtless insert. Glassback on glass is a new toy. Then Seed III + Rift Draw + loot in a burst. Three-note pattern is not audible/visible as three beats; it is more orange.
- **CH04.** Best human conflict. Sable design works. Loss is real in the ledger and *almost* real in the limp-out. Spear does not stay bent. Rival ideology is a speech at the door.
- **CH05.** Necessary scarcity chapter. Looks like forge stills and ampoules. Failed Channel is a man clutching a glowing chest. Theme is spoken in chorus.
- **CH06.** Teal water and pump: new geography. Mire Choir menace is low. Three-person combo is claimed; pictures are people standing in lanes with orange.
- **CH07.** The book’s argument. Pictures do not stage the choice. Class is a pentacle. Satchel death is two lines.
- **CH08.** Sable debt-arm (P002) is the mechanic-as-body win. Brass Maw is a giant gear-mouth. Agents steal a token offstage. Rescue is virtuous in JSON.
- **CH09.** Forge menu. Crosslock is four people and a cable. Mira’s arm cut is copy. Regent underside is a good last-page monster.
- **CH10.** Too many completions for 24 panels. Cadence, level-up, heal, platform death, Channel II, Rift Draw III, three quests, writ, door. Poster ending.

Premium CH01 *script* redistributes CH01 correctly (wrong wake → grammar → miss → talisman → ugly breath → shared line → pulse). Unique art only partially follows. Until the other nine chapters receive that treatment **and new pictures**, the volume remains a proof of accounting.

---

## 10. Investment judgment

**Observation.** Money-and-time already bought: ten lettered Ember chapters, a 52-panel CH01 script, 28 unique premium rasters, a future-cast bible, and three prior original volumes.

**Inference.** Additional Ember *chapters* have a low expected story return because the binding constraint is not “need more plot.” The constraint is “generator and plans produce beat-labeled stills; lettering explains the stills.” Plot inventory is already larger than pictorial inventory.

**Recommendation.** Further investment is justified only as:

1. A short, scored, story-bearing **causality pilot** (below), using Ember names if that reduces world-invention cost.
2. A dialogue pass on existing CH01–CH10 overlays if the owner wants a readable review copy of the current art (cheap, incomplete).
3. Not: Movement II bibles, more future-cast sheets, another ten-chapter template, or a fourth IP.

Do not throw away the ledger design, the adult pair, Belljaw-as-instrument, or the CH04 loss. Throw away the belief that those things have already been *told in comics*.

---

## 11. Next-pilot recommendation

### Decision

**Neutral benchmark sequence, Ember-optional payload. Not a new story. Not Ember CH11.**

### Why not a new story

**Observation.** Borrowed Down, City Keeps Oaths, and Ember Lattice each began with originality ADRs, style probes, and ten-chapter outlines. Each produced adult stills and a viewer. Each failed the same sequential-art tests: in-between panels, silent cost, item continuity, fight grammar that can be restated from pictures. A fourth premise would be scored in a JSON (Ember’s was 99) and would not fix pose assembly.

### Why not more Ember Lattice volume

**Observation.** CH02–CH10 already exist as 216 additional panels of the same density machine. Extending to the fourth meridian / sponsor face (Cassian Vey in the future-cast) would add names to a pipeline that cannot yet show “Elian chooses Mira over a kill.”

### Why a neutral benchmark, and how Ember may sit inside it

**Recommendation.** Commission **one** 12–16 panel vertical sequence with pre-registered pictorial pass/fail, independent of IP loyalty:

1. Two adult coworkers enter a dangerous structure (no caption explaining the world).
2. One object clue of sabotage the reader can notice before anyone speaks.
3. Enemy grammar shown in three beats (wind-up, contact, changed angle) before the counter.
4. Failed strike: warning insert, hit, silent injury, partner sees it.
5. Irreversible item spend: consumed object destroyed, spared object **never leaves the belt**.
6. Shared finish: two readable vectors, one material break, stillness before loot.
7. System confirmation only after the body result; no spoken theme.
8. End image changes direction of travel (pulse, door, stolen token) with ≤8 spoken words.

Scoring: a blinded reader restates the fight without the plan file. If they cannot, the page failed regardless of SystemState.

**Ember Lattice CH01 premium script already lists those beats** (P001–P052 contains them). It may be the payload **if and only if every panel is newly staged to the script**, including the currently missing unique rasters, and if Belljaw/Elian/Mira identity is locked to one model sheet. Success is the 12–16 page subset, not “finish the 52” as a vanity length.

If the owner wants the benchmark to be IP-neutral to avoid identity drift across Ember’s two art generations, write original one-off names and a one-room dungeon-instrument. Do not write a new ten-chapter bible.

### What not to carry into the pilot

- 24-panel uniform length.
- Exactly four Ledger cards.
- Camera-field templates that contradict beats.
- Spoken “volume,” theme diagnosis, and geometry captioning.
- Floor pentacles as class.
- Future-cast extras.
- Phase B-style PASS that treats plan alt-text as visibility.

---

## 12. Confidence and gaps

- **High:** Ember volume CH01, CH04, CH07, CH10 rasters and all ten chapters’ lettering-copy; premium script vs 28 unique rasters; sibling CH01 opens and CH10/CH01 ends; density template; meta-volume lines.
- **Medium:** Ember CH02, CH03, CH05, CH06, CH08, CH09 judged from QA contact sheets plus copy, not every full-resolution panel. Contact sheets are sufficient to see pose-sameness and zone color; they can hide a single causal gem.
- **Low / not scored:** North Garden finished kitchen rasters (plans only in this worktree). Licensed comparable *pages* (out of scope for this role; no copyrighted imitation).
- **Not verified:** whether premium hybrid SVGs composite unique rasters or baseline/volume art for the 24 non-unique indices. Manifest shows baseline reuse; a panel-by-panel hash join was not completed here.

---

## 13. One-page owner takeaway

Ember Lattice is the strongest **argument** for a serial in this repository: adult partners, honest scarcity, a dungeon that teaches grammar, a Ledger that is evidence rather than a god. It is not yet a strong **comic**. The ten-chapter volume proves that a validator can love a story the eye cannot parse. Premium CH01 proves the authors know the fix (silence, shear clue, ugly breath, shared vectors) and that generation still draws orange cracks, pentacles, and posters. Borrowed Down and City Keeps Oaths prove that new worlds and prettier thumbnails do not automatically create propulsion.

**Do not fund another book. Fund one fight that a stranger can retell.** If that fight is Elian, Mira, and the bridge, use the premium script as the score and demand the pictures play the notes. If that fight cannot be delivered, the constraint is the picture machine, not the premise — and no new story will save it.
