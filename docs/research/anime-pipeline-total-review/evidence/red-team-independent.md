# Independent red-team review of the draft strategy recommendation

Role: Independent Red-Team Reviewer (did not participate in scoring)  
Access date: 2026-09-06  
Worktree: `C:\AgentWorkspaces\anime-pipeline-total-review-20260906-211925`  
Output constraint: this file only. No strategy of my own is recommended as the winner. The job is to stress-test the draft.

Draft under attack (paraphrased, not endorsed):

- **Primary: Strategy C** — human-directed hybrid rebuild. Keep Ember Lattice premise, adult duo, ledger/state, deterministic SVG lettering, fail-closed records. Replace the production spine that turns written beats into finished generated plates. Require a complete phone storyboard, locked drawable assets, layered production (layout / line / bg / flats / effects / text), and human ownership of acting / action / cleanup / lettering / approval. Next step: a frozen 14-panel neutral-or-Ember-payload benchmark, not another ten-chapter volume.
- **Fallback: Strategy D** — greenfield title on the same production spine, only if the owner still rejects Ember after a competent human-first storyboard.
- **Rejected for now: Strategy A** (polish current hybrid) as insufficient because beat-to-art contradictions and pose-assembly are in the plates. **Strategy B** (modular replacement of one stage) as a possible cheaper first experiment but not the leading architecture.

Classification in this memo: **Observation** = stated in the evidence files cited; **Inference** = argument from those observations; **Unevidenced** = a draft or source-draft claim that is not supported by visible outputs in the listed evidence. Pixel facts are not invented. Where Visual A, Visual B, the lead inspector, and the story auditor disagree about the same plate, the conflict is preserved rather than resolved.

---

## 0. How to read this attack

The draft is a **causal story** pretending to be a ranking. It asserts:

1. The plates themselves are the binding constraint (pose-assembly, beat-to-art contradiction).
2. Therefore polishing the current hybrid cannot work.
3. Therefore one-stage modular replacement is not the leading architecture.
4. Therefore the production spine must be replaced.
5. Ember’s premise/cast/ledger are still the right payload.
6. A human-directed layered rebuild is the feasible way to replace that spine.
7. A 14-panel benchmark is the correct next quantum.
8. Greenfield (D) waits until Ember has been given a competent storyboard.

Each of those steps can fail independently. The strongest objections do not require proving C is “wrong.” They require proving that **the evidence does not uniquely select C**, that **A / B / immediate D remain live**, and that several load-bearing claims are either untested, cherry-picked, Goodharted, or contradicted by a minority reviewer.

Rubric rules that the draft is at risk of violating in spirit (`common-rubric.json`):

- Owner rejection outranks internal rubric scores.
- File integrity / hash / schema PASS do not raise sequential-art scores.
- Disagreement of 2+ points is preserved, not averaged away.
- Weights may support, not replace, diagnosis.
- Copyrighted comparables: panel-forensic dimensions that were not assessed stay `not_assessed`.
- Inference must be labeled.

---

## 1. The load-bearing cherry-pick

**Observation.** Independent visual weighted totals after all categories (`scorecard-reconciliation.json`):

| Pipeline | Visual A | Visual B | Midpoint |
| --- | ---: | ---: | ---: |
| borrowed-down | 2.76 | 2.82 | 2.79 |
| ember-lattice-premium-rd-52-panel | 2.53 | 2.86 | 2.69 |
| ember-lattice-editorial-gear-hybrid | 2.37 | 2.97 | 2.67 |
| ember-lattice-ten-chapter-volume | **2.14** | **3.11** | 2.62 |
| the-city-keeps-oaths | 2.38 | 2.48 | 2.43 |
| north-garden-legacy-local | 1.69 | 1.85 | 1.77 |

**Observation.** Visual A and Visual B do not agree on what won.

- A’s order: Borrowed Down ≫ premium Ember ≫ City ≈ editorial ≫ **volume last among the three original IPs**.
- B’s order: **volume first** (only pipeline B places above 3.0) ≫ editorial ≫ premium ≫ Borrowed Down.

**Observation.** Rubric anchors (`common-rubric.json`): 3 = “Competent and functional. A working serial, but not competitive with the owner’s named reference bar.” 2 = “Below professional serial standard.” A’s volume total is a 2-class object. B’s volume total is a 3-class object.

**Inference.** Strategy C is assembled by taking **A’s causal diagnosis** (“pose-assembly is in the plates, so polish is insufficient”) and **B’s / the story auditor’s IP loyalty** (“keep Ember”). That pairing is not a consensus. It is the intersection that most favors a rebuild of Ember rather than:

- polishing the pipeline both reviewers actually agree on (Borrowed Down, delta 0.06), or
- polishing Ember because B already scored it as a working serial, or
- abandoning Ember because A scored it worse than two other titles.

**Observation.** The reconciliation file lists 25 disagreements of 2+ points and then still publishes midpoints. The rubric says those disagreements are “preserved, not averaged away.” Every midpoint in that table averages them away. Using 2.62 as if it were Ember’s score is a Goodharted summary statistic. Using 2.14 vs 3.11 as if the draft had resolved it is worse.

**Observation.** All 25 `b_justification` fields in `scorecard-reconciliation.json` are empty strings. Visual B’s reasons exist in `visual-b/notes.md` and `visual-b/scorecard.json`; they were not carried into the reconciliation object. A later reader of the machine-readable disagreement list cannot see why B scored CH10 propulsion a 4 or North Garden system UI a 3. “Preserved disagreement” that drops the minority reasons is not preservation.

This cherry-pick is the hinge. The rest of the memo shows what happens if you refuse it.

---

## 2. Strongest case that Strategy A (polish) wins

A is not “keep generating ten-chapter dumps.” A is: keep the current hybrid (per-panel ImageGen or equivalent, SVG overlays, HTML readers, ledgers), and spend the next scarce hours on the surfaces that already moved when touched.

### 2.1 The owner already approved this look, and asked for polish

**Observation** (`archivist-inventory.md` §7; `owner-approval.json` as quoted there):

- Pilot: `APPROVED`.
- Owner assessment: “great selection; art and candidate B are amazing.”
- Required Phase B changes were lettering/system, not a new renderer: improve wording; reduce balloon occlusion; test translucency; smaller containers with more text; more visible system menus / XP / skills.

**Inference.** The only recorded owner art-direction success in the Ember line is Candidate B stills plus a punch-list that is Strategy A. The 2026-09-06 owner sentence (“still not like Tower of God or Solo Leveling… pipeline may need improvement, a substantially different approach, or a complete restart”) lists three live options. It does not select C. Treating “or a complete restart” as permission to skip A is selective quotation. “Improvement” is A.

### 2.2 Polish already produced the largest measured page gains

**Observation** (lettering audit; measurements-summary):

- Premium hybrid vs original-lettering on the **same 52 overlay art**: occupied plan area 367.7% → 221.48%; dialogue SVG px 29.7 → 41.0; estimated CSS px at 390 from 11.31 / 10.13 (failing every phone floor) to 15.62 / 13.25 (clearing ADR 14 / 12). Center-seeking `Q512.0,844.8` tails rewritten to short local tails. P033 open-on-balloon collision removed. P049 decompressed. P048/P051 Ledger coverage cut.
- Editorial-clean is a denoise/sharpen pass. Visual A: it helps `controlled_detail`; it does not create choreography. Visual B: targeted-edit `bm08` vs openai-raw `bm08` “proves a real art-direction lever (remove extra wardens; keep the nave).”
- Premium unique `p026` and editorial `p044` are named by Visual A as stills that “would not embarrass a mid-tier key-art pass.”
- Story audit: Premium CH01’s first human line is four words (“Old breaks round off”) vs volume P003’s two long jokes. “That single change is the largest prose improvement in the whole corpus.” A voice pass is “cheaper than regeneration and would immediately raise desire-to-continue.”

**Inference.** When this programme actually edits a layer (lettering geometry, copy length, targeted-edit, median-filter grit), the page moves. The draft treats those moves as proof that the remaining gap is “the spine.” The opposite reading is available: the spine already emits salvageable stills, and the un-run polish is copy, balloon, identity-lock, and per-panel rejection — the same class of work that produced the only owner “amazing.”

### 2.3 If Visual B is even partly right, Ember is already a working serial

**Observation.** Visual B, Ember volume: reader_impact mean 3.75; sequential 3.0; art_direction 3.36; genre 3.0; weighted **3.11**. Notes: “Best manhwa-shaped pipeline”; “CH01 vault and CH08 hanging beat are the closest this review gets to a licensed-floor still”; “ten-chapter contacts that still look like one book.” Desire-to-continue 3.5 with an explicit mixed note (stills pull; six-finger/cutout would stop editorial). Throughput 4. Vertical pacing 4 because portrait plates + phone column exist.

**Inference.** Rubric 3 is “a working serial, but not competitive with the named bar.” That is the textbook target for **polish**, not for spine replacement. C is what you do when the object cannot function (anchor 0–1) or when a dimension “would not survive platform editorial” (anchor 2) *and* the failure is architectural. B’s volume scores say many dimensions already function. Elevating a 3 toward a 4 is A (craft, lettering face, identity lock, quieter plates). Replacing the generator because the named bar is 5 is an infinite regress: industry research says licensed weeklies are 5–7 person studios. That is not a finding that the current hybrid cannot be polished; it is a finding that the owner named a studio bar.

### 2.4 The “in the plates” leap does not kill A

The draft’s rejection of A is: beat-to-art contradictions and pose-assembly are **in the plates**, therefore polish is insufficient.

**Observation.** Those contradictions are catalogued (story audit §6; Visual A CH01 `p006→p010`; premium `p043→p044`; CH07 `p012`/`p014`). That catalog is real as a set of claimed observations. What is not real is the hidden lemma: **a defect in a plate can only be fixed by replacing the machine that made all plates.**

Counter-observations:

- Ember already generates **one panel per ComicPanelPlan** (technical audit §2.1, §5). That is not CH05’s 11-strip architecture. Localized retry already exists (`prepare_panel_repair.py`, premium `failures[]`, CH03 orientation repair).
- Premium unique replaced premature-boss `p007`/`p008` by instruction-following. Visual B: “repairs work as instruction-following, not as anatomy repair.” That is a **scope** of repair, not proof that repair cannot be aimed at anatomy/geography if the prompt/review gate changes — which is still A/B, not C.
- Story audit: CH04 is “the only volume chapter whose pictures almost match.” If some chapters almost match, the plates are not a uniform pose-assembly waste. Selective redraw of CH01 action and CH07 P012–P016 is polish.
- Visual A’s own strongest-stills list is dominated by Ember plates (pit, Belljaw, backhand, ankle split, Sable). A that keeps those stills and restages the failures is not “ignoring the plates.”

**Inference.** “The error is in the pixels” is compatible with A (replace those pixels) and with B (change the stage that produces those pixels) and with C (change every stage). It does not uniquely select C. The draft treats a location-of-error claim as an architecture-of-repair claim. That is the weak inference.

### 2.5 Borrowed Down is the agreed object, and its failure is polish-shaped

**Observation.** Borrowed Down is the only pipeline whose A/B weighted totals agree (2.76 / 2.82). Visual A: “panels themselves are closer to a real comic language”; CH03 contact sheet “best sequential page in the review”; lettering is the serial failure (blank rectangles, captions under art). Visual B: “Highest world and print identity”; “Lettering is a mock.” Lettering specialist: localization of the caption band is the best of the set; empty on-art boxes still fail. Both visual reviewers score Borrowed Down lettering_and_mobile at 1.67.

**Inference.** If the programme’s goal is “raise sequential-art scores with the least new machinery,” the agreed diagnosis is: **keep Borrowed Down drawings, replace the lettering path with Ember’s SVG overlay model.** That is A (or B on a single stage: lettering). It does not require Ember, a studio roster, or a new premise. The draft never considers it, because the draft has already decided the payload is Ember.

### 2.6 A is the only strategy that fits the measured labor constraint

See §6. If owner minutes remain null, C is a studio script without a studio. A can be executed as: timed owner session on existing CH01 (economics estimate 50–200 minutes for a 50-panel first pass; G07 20–60 minutes still unrun), plus a copy pass on overlays (story audit: cheap), plus hybrid lettering ported to volume, plus per-panel FAIL instead of `mark_art_review.py` chapter-batch PASS (technical audit). Those are edits to objects that exist.

### 2.7 Goodhart warning for rejecting A

Rejecting A because the current plates are not ToG/SL is using an **unmeasured comparable bar** (see §8) to discard the only route that has owner praise plus measured lettering gains. That is the same class of error as treating volume-validation `PASS` as reader quality.

---

## 3. Strongest case that Strategy B wins over C

B = replace **one** production stage, keep the rest, measure. C = replace the spine, keep only premise/ledger/SVG/records.

The draft already concedes B is “a possible cheaper first experiment.” It then demotes B without running it. That demotion is the part to attack.

### 3.1 C is unfalsifiable; B is the experiment the draft’s own next step already is

**Observation.** The draft’s next step is “a frozen 14-panel neutral-or-Ember-payload benchmark,” not a staffed weekly. Story audit’s next pilot is 12–16 panels with pre-registered pictorial pass/fail. Technical audit’s next-pilot implication: generate one panel per plan (Ember already does), keep SVG, put human minutes on the critical path, stop batch PASS.

**Inference.** A 14-panel benchmark that changes **every** stage (storyboard + locked assets + layout/line/bg/flats/FX/text + human acting ownership + new generator behavior) cannot attribute a win. If the 14 panels read, C’s advocates will say the spine did it. If they fail, C’s advocates can say the experiment was understaffed. B’s version of the same 14 panels changes one stage:

- human phone storyboard / conte, same ImageGen, same SVG; or
- locked 3D/model-sheet blocking, same generator; or
- per-panel human accept/reject with no batch PASS, same generator; or
- compositing/plates (Garden `panelcomp.py` / stage) under Ember casts; or
- identity encoder / IP-Adapter-class lock, same prompts.

That is how you would learn whether C is necessary. Declaring C the “leading architecture” before that test is putting the conclusion in front of the instrument. The draft’s own next quantum is B-sized. Calling it C is branding.

### 3.2 The technical audit already named stage-level causes, not a single spine

**Observation** (technical audit §3, §12):

- Error **introduced** at: sequence-strip generation (CH05, not Ember), lossy prompt compilers (camera modulo, SFX cycle, 4-ref cap, beat-substring subjects), global LoRAs, three-ref under-conditioning, `seed: null`, heuristic protected zones.
- Error **hidden** at: `mark_art_review.py` chapter-batch `REVIEWED_PASS`, hardcoded agent triage, copied hair/wardrobe dicts, prompt-substring gates, lettering fit after box growth, Phase B markdown PASS from status fields.
- Error **amplified** at: strip crop, style-arm multiplication, median-filter “repair,” system-state overlay independent of art.
- Retain: hash addressing, gitignore of art, fail-closed money, SVG lettering, premium-rd link audit.
- Modify: per-panel review, authored-box lettering tests, missing rasters as errors, null model if unknown.
- Ember per-panel correction cost: **medium**. CH05 strip correction: **high**.

**Inference.** Ember’s live comic route is already “one finished source-art panel per request” (archivist G15). The “spine that turns written beats into finished generated plates” is a prompt compiler + ImageGen + batch review. C wants to replace that with layout/line/bg/flats/FX. The audit says the cheapest high-leverage kills are **batch PASS** and **lossy camera/subject compilation** and **identity under-conditioning**. Those are three different single stages. Replacing all of them at once throws away the ability to learn which one was binding.

**Observation.** Garden compositing (G04) produced the **only internally accepted narrative art** (four kitchen panels). Regional LoRA failed; plates + occluder + contact shadow were the modular fix. That path was not transferred to Ember (archivist: “It did not scale to 50-panel chapters”). **Inference.** B-as-compositor is an unrun successor, not a failed one. C ignores a modular spatial stage that already moved acceptance.

### 3.3 Industry R&D is B, not C

**Observation** (industry-research-draft §5, §15): WEBTOON S-1 names Shaper (2D sketch → 3D character for pose/clothes reuse) and Constella (3D pose → 2D in the creator’s style) as answers to **repetitive pose/clothing resketch**, plus AI Painter for color assist. Platforms are not documented as replacing storyboard→line→flat→shade with a full-scene generator, nor as replacing the generator with a full human factory in one step. CLIP/SORAJIMA 3D backgrounds are asset libraries, i.e. one stage.

**Inference.** The professionally attested AI-adjacent move is **modular pose/identity/color assistance on a locked board**. That is B. C’s layered roster (layout/line/bg/flats/effects/text) is the **pre-AI weekly factory**. Importing the factory as the “leading architecture” for a programme whose live renderer is built-in ImageGen is a category jump: either the humans draw the layers (then the generator is gone, and you have staffed D-level labor on Ember), or the generator still paints finished plates from a storyboard (then you have B: add conte, keep the spine). The draft writes the first sentence and will operationally get the second unless the owner hires. B names that honestly.

### 3.4 Ember already is the “one panel per plan” spine C claims to install

**Observation.** Technical audit next-pilot: “if the owner wants a serial rather than a wrapper, generate one panel per ComicPanelPlan, keep SVG lettering, keep fail-closed money/identity policy.” Ember volume already does that (G15: “one finished source-art panel per request”). CH05 strips and Borrowed Down 3×2 sheets are the multi-beat error. City used 3-panel strips. Ember rejected multi-moment sheets for individual critical panels (archivist inheritance table).

**Inference.** For Ember, C’s “replace the production spine” overstates the discontinuity. The discontinuity C actually wants is **human layered finish**, not per-panel generation. Per-panel generation is already there. The missing piece is either review/identity/storyboard (B) or a drawing workforce (C/D). Calling the missing piece “the spine” smuggles in a studio.

### 3.5 Lettering already was a successful modular replacement

**Observation.** Premium hybrid vs original is a replaced lettering stage on frozen art. Visual A scores premium lettering_and_mobile 2.89 vs volume 2.00. Lettering specialist: hybrid phone_readability 3 vs original 1. Volume and premium are different objects (24× deep wording vs 52× short fight), so “v2 improved the page” across them is a category error — which the lettering audit already flags.

**Inference.** B has a completed existence proof inside this corpus: swap lettering, keep rasters, scores move. The draft keeps SVG lettering (the successful B) and then says B is not leading. Inconsistent.

### 3.6 Cost and option value

**Observation.** Economics: measured paid spend $1.057377; built-in ImageGen monetary cost **null**; human minutes **null**; accepted panels post-CH01 = 0. Kill criterion: further chapter-scale generation before a timed owner session leaves accepted-panel rate at 0.

**Inference.** C front-loads storyboard, model sheets, and a layered roster before any new evidence that those layers bind. B spends the next owner hour on one gate (review) or one lock (sheets/3D) and reuses 240+52 existing plates as the control. If B fails (human storyboard in, ImageGen out, same pose-assembly), **then** C is supported. The draft wants C to skip the falsification step because it is already sure. Certainty is not in the scorecards.

---

## 4. Strongest case for immediate Strategy D (new story now)

The draft sequences D as a fallback after a competent Ember storyboard. Immediate D is: do not spend the next scarce cycle proving Ember can be boarded.

### 4.1 Owner rejection already exists, and it outranks Ember loyalty

**Observation.** Rubric: “Owner rejection outranks internal rubric scores.” Owner 2026-09-06: still not like ToG/SL; improvement **or** different approach **or** complete restart. Owner 2026-09-04 LitRPG prompt (archivist §7) is a binding diagnosis of earlier attempts: too busy; generic painterly fantasy; did not evoke ToG/SL/TBATE readable cinematic action; unattractive lettering; weak spectacle; complexion homogenization; missing LitRPG machinery.

**Observation.** Ember was the attempt to fix that diagnosis (numeric Ledger, Candidate B, individual panels). There is **no post-volume owner-approval JSON** (archivist G15, G18). Phase B was authorized from the **pilot**. Commercial clearance remains false. The 2026-09-06 sentence post-dates the editorial pass and still states the gap.

**Inference.** Waiting for “a competent human-first storyboard” before allowing D treats Ember as entitled to another cycle after the owner has already said restart is on the table. That is the programme’s established pattern: one more bible, one more PASS, one more slice. Immediate D is what you do if you believe owner speech over internal IP attachment.

### 4.2 Ember’s page-level premise scores do not justify a keep-first rule

**Observation** (story audit §1 table, finished pages):

| Dimension | Volume pages | Premium pages | Bible/ledger |
| --- | --- | --- | --- |
| Premise | 3 | 3.5 | 4.5 |
| Adult cast appeal | 3.5 | 3 (identity drift) | 4 |
| Progression engine | 4 arithmetic / 2 theatrical | 3 | 5 |
| Visual identity | 3 establishing / 2 combat | 3 atmosphere / 2 same orange-fault | 4 |
| Emotional hook | 2 | 2.5 | 4 |

Desire-to-continue 2.5 (medium confidence). Emotional engagement 2. Opening hook 2.5 volume. CH10 ending is a poster plus “next volume.” CH07 thematic centerpiece is “narrated over the wrong picture.”

**Observation.** Internal `premise-evaluation.json` scored Ember **99/100 before pages existed** (story audit §0). Style-candidate B 96/100 is a pre-volume number (archivist G14).

**Inference.** Immediate D’s case is that “keep the premise” is a bible score, not a page score. A 99-point paragraph is Goodhart. If the next 14 panels must anyway be newly staged to a causality contract (story audit §11), the IP is optional **by the story auditor’s own rule**. Immediate D just refuses to spend the optional Ember tax.

### 4.3 Visual A: Ember is the generic-prestige failure class

**Observation.** Visual A Q2: generic prestige-fantasy convergence is **yes** for Ember (volume, premium unique, editorial-clean) **and** City; **no** for Borrowed Down and North Garden kitchen. Elian = fair sharp-jawed blonde in tattered coat; Mira = redhead-undercut-shield stamp; environments = cracked ashlar, chains, orange lava-cracks, teal glass at different zooms; faces share one rendering. “Ember optimized for ‘same character every time’ and got a mannequin.” Magnetism would be a face a reader could pick out of a lineup of LitRPG protagonists; “He does not have it.”

**Observation.** Visual A weighted volume **2.14**, below City (2.38) and far below Borrowed Down (2.76). If A is the reviewer you trust on “what a stranger sees,” Ember is the wrong keep.

**Inference.** Immediate D (or D using Borrowed Down’s print language, which is a cousin) is the move that escapes the failure class the owner named (“converged on the same generic painterly fantasy look”). C-with-Ember-payload keeps the mannequin and the teal-orange dungeon and hopes storyboard will give them souls. A’s evidence is that the identity is the generator’s prior. New names on the same prior is still Ember. Immediate D at least allows a new visual contract (Borrowed Down already demonstrated one).

### 4.4 Three IPs already proved that “new story” is not the scarce object — unless the new story is designed after the sequential diagnosis

The story auditor’s objection to D: Borrowed Down, City, and Ember each began with originality ADRs, style probes, and ten-chapter outlines; each failed in-between panels, silent cost, item continuity, fight grammar. “A fourth premise would be scored in a JSON (Ember’s was 99) and would not fix pose-assembly.”

That objection is strong **against a fourth ten-chapter bible**. It is weak against immediate D defined as: **one 12–16 panel visual contract, new names, no 99-point premise file, no Movement II.** That is identical to the draft’s next step except it does not drag Elian/Mira identity drift (volume coat vs premium open shirt; ceramic Belljaw vs beetle-Belljaw; Mira orange vs burgundy — story audit; Visual B Mira hair flips inside premium CH01).

**Inference.** Immediate D is the draft’s 14-panel benchmark with the identity-lock problem **removed**. The draft’s “Ember-optional payload” already admits this. Sequencing it after a failed Ember board adds a cycle whose only purpose is sentimental.

### 4.5 Ledger and SVG are portable; they are not a reason to keep the plot

**Observation.** Technical/archivist: ComicPanelPlan, RenderRecord, SVG lettering, system-state validation, fail-closed money are North Garden inheritances, not Ember-the-novel. Story audit: “Do not throw away the ledger design, the adult pair, Belljaw-as-instrument, or the CH04 loss.” That list mixes portable infrastructure (ledger, SVG) with IP (adult pair, Belljaw, CH04).

**Inference.** Immediate D can keep the ledger code and SVG compositor and drop Elian. The draft’s “keep Ember premise” treats a validator and a dungeon-instrument metaphor as if they were one object. They are not. D now is the clean split: keep machinery, drop a premise that scores 2 on hook/emotion on the page.

### 4.6 Minority: if any IP is kept, the agreed scores do not pick Ember

Borrowed Down midpoint 2.79, both reviewers. City 2.43, both reviewers. Ember volume 2.62 only after illegal averaging of a 0.97 gap. Immediate D can be “abandon Ember, do not automatically start IP #4, put the next 14 panels on the print-language that actually differentiated.” That is still D relative to the draft (the draft’s D is greenfield on C’s spine). It is the strongest anti-Ember ranking available from the scorecards.

---

## 5. Challenge: is the Ember premise actually worth keeping?

The draft’s keep-list: Ember Lattice premise, adult duo, ledger/state infrastructure, deterministic SVG lettering, fail-closed records. The last three are not the premise. Challenge the first two.

### 5.1 What “the premise” is, on paper vs on the page

**Observation.** Written promise (story audit §3): failed adult salvager who sees structural faults; dungeon as colossal instrument; Ledger records contribution not consent; party refuses expendable-parts logic; transferred-risk / shared timing rather than invulnerability. Story auditor: “a better LitRPG argument than ‘numbers go up.’”

**Observation.** On finished volume pages the same auditor says that promise is **mostly spoken**. Sabotage clue (straight shear vs rounded wear) is not in volume P001–P003 art. Premium unique P003 still shows a generic glowing orange crack, blade already drawn, Belljaw already on the far platform (script reveal P009), Mira absent. CH07 protection gate — “the volume’s thematic centerpiece” — is “a kneeling man touching a glowing floor crack while Mira stands unthreatened by a pump.” Unlettered art has three visual verbs for almost all system events: orange hairline, orange chest/hand fire, orange floor circle/pentacle. Class = pentacle. Cultivation = power-up stills, not the bible’s ugly breath.

**Inference.** A premise that cannot be recovered from pictures without the overlay is not a visual serial premise. It is a prose engine with key art. Keeping “the premise” while replacing the picture machine assumes the prose engine is the scarce good. The page scores say the scarce good is pictorial grammar. Grammar is not Ember-specific (story audit’s eight-beat causality list is IP-neutral).

### 5.2 Adult duo: consistency without magnetism, and not actually locked

**Observation.** Visual A: Elian recognizable across 240 frames (blonde undercut, green eyes, grey-green coat, brass belt) and not magnetic. Expression range: profile stoic, three-quarter smirk, combat grimace, injured stoic. Mira more magnetic because of undercut-plus-shield, not acting; face is the same determined frown. Visual B: “Mira’s hair is not a character; it is a sample” (premium undercut in `p008`/`p044` vs longer hair in `p019`/`p046`). Story: identity drifts volume vs premium (tattered gray-green coat vs darker open shirt; beetle-Belljaw). Future-cast of twelve additional adults is “a reservoir, not a cast the reader has met.”

**Inference.** “Keep the adult duo” keeps a recognizable mannequin and a shield silhouette. It does not keep a locked model sheet, because none held across two Ember generations one day apart (volume morning 2026-09-04; unique 52 that evening). C’s “locked drawable assets” are a hoped-for object, not an Ember asset on disk. Gear/future-cast SVGs are “circle-head / triangle-arm diagrams” and “geometric SVG family icons,” not character drawings (Visual A). They do not raise silhouette scores for pages a reader would scroll.

### 5.3 The ledger is the real keep; it is also the metronome that killed propulsion

**Observation.** Story audit: architecture is the strongest part (reconciled SystemState, no item respawn, injury IDs, quest `FAIL` / `COMPLETED_WITH_LOSS`, CH04 loss). Density almost identical CH01–CH06 (`16/6/2`, four system moments, ~24 dialogue units) because `system-bible.md` locks “exactly four meaningful Ledger moments” per chapter. Chapter ends explain the next objective, then park a status card. Meta lines: “Then our volume problem is no longer getting out.” / “Then the next volume begins with evidence.” Technical audit: system-state arithmetic is independent of whether the SVG Ledger is attached to the correct beat; “a PASS ledger with wrong art **looks** like a working LitRPG.”

**Inference.** Keeping “ledger/state infrastructure” without killing the four-moment / 24-panel template keeps the thing that made Ember a “ledger with illustrations.” The story auditor already said: keep the ledger, kill the template. The draft’s keep-list does not mention killing the template. That omission lets C rebuild the picture machine and then author another 24-panel four-moment Ember, which is how the last volume happened.

### 5.4 Pre-page scores and Phase B PASS are not evidence of premise quality

**Observation.** Premise 99/100 pre-pages. Phase B audits `01`–`04` report PASS on fight causality and “causally shown” class evolution; story auditor: those documents score completeness against plans and ledgers; they are “false as a description of CH07 P012–P016 rasters.” `write_phase_b_audits.py` emits PASS after checking `review_status` (technical audit). `mark_art_review.py` writes one notes string onto 8 or 24 panels (lead visual; 224 `REVIEWED_PASS` / 1 diagnostic; 11 unique notes).

**Inference.** The institutional evidence that Ember is “the strongest argument for a serial in this repository” (story takeaway) is partly the same Goodhart stack the technical audit dismantled. Discount it. What remains is: an adult two-hander, a distinctive monster family (Belljaw/Glassback — both visual reviewers), a CH04 loss that almost reads, and a numeric inventory a validator can check. That is not nothing. It is also not unique enough to sequence all other IPs behind a storyboard that does not exist.

### 5.5 Opening craft vs named-bar transferable craft (without stealing ToG/SL panels)

Even using only **publisher copy** from the comparables draft (not panel forensics): ToG’s official hook is a desire inventory; SL’s is humiliation + family bills + a System that changes a decision. Ember volume P001 is an establishing pit plus a caption about a six-year-early wake (story; Visual A: 7-line block on the establishing shot). The picture does not show a schedule, a wake, or wrong wear.

**Inference.** The Ember *premise as currently told* does not implement the transferable opening the comparables draft itself extracted from official copy. Keeping the premise means rewriting the open (premium script already does: silent P001, four-word shear). A rewritten open on new names is D. A rewritten open on Elian is A/C. The premise is not doing independent work in that choice.

**Preserve minority.** Story auditor still judges Ember the strongest **argument** in-repo for the owner’s stated LitRPG/manhwa goal, vs Borrowed Down’s civic gravity and City’s oath-roads. Visual B judges volume the best manhwa-shaped book. Those are live. They do not survive contact with A’s ranking or with page-level hook/emotion scores without a further argument the draft does not make.

---

## 6. Challenge: is a human-directed rebuild feasible given owner time?

This is the sharpest attack on C as an **operational** recommendation. C can be correct as craft theory and still be infeasible.

### 6.1 The denominator is empty

**Observation** (economics §6; technical §5; archivist §11):

- `human_review_minutes`: **null** on every live ledger checked.
- G07 blinded packet: 20 required timed decisions, **0 taken**, minutes null.
- CH05 live review-time contract: 39 subjects, 0 events, minutes null.
- CH01 kitchen: `human_review_status` not yet performed; reviewer on the accepted record is “Codex visual review,” not the owner; `commercial_release_allowed: false`.
- CH03–CH13: 0 owner accepted.
- Ember volume / premium / editorial: no post-pilot owner-approval JSON; owner_approval on generation requests `PENDING`.
- CH06–CH13: no recorded owner-approval JSON at all (archivist unknown: whether those rasters were ever seen by the owner).

GOAL.md success measures include accepted-panel rate and human minutes. Both empty after four internal-research kitchen panels.

**Inference.** C requires “human ownership of acting/action/cleanup/lettering/approval.” The programme has not collected a single timed owner minute on a blinded 16-candidate packet. Designing a layered studio workflow whose critical path is that person is a plan that assumes a resource the ledgers say has not been switched on.

### 6.2 Industry labor shape is a small firm, not a side project

**Observation** (industry draft; economics §6.3):

- KOCCA 2024: 5.9 creative days/week, 10.1 hours/creative day, 6.3 days/episode.
- Seoul / DCS / SORAJIMA: 7–9 stages; weekly color typically ≥3 specialists; one Japanese webtoon studio example 6–7 artists on one series.
- Kakao/Manta/WEBTOON contest: ~50-cut professional episode quantum.
- KBS anecdote (economics): 65–70 panels ≈ 32–36 hours of storyboard labor **alone**.
- Kim / factory split: writing, adaptation, storyboard, character, line, background, colour, post; typically five to six people including producers.
- Internal 2026-08-31 registry estimate 12–25 hours/chapter once LoRAs/templates exist: **explicitly unmeasured** for this programme; economics warns that treating it as a forecast “would launder an unmeasured guess into a plan.”

**Observation.** C’s roster (phone storyboard, locked drawable assets, layout/line/bg/flats/effects/text, human acting/cleanup/lettering/approval) **is** that firm.

**Unevidenced.** Any claim that the owner will staff it, hire it, or personally absorb 32–36 storyboard hours plus finish. No hiring plan, no production cap (`NORTH_GARDEN_APPROVED_PRODUCTION_CAP_USD` blank; CH05 budget domain `DISABLED_NO_PRODUCTION_SPEND_OR_UPLOAD_AUTHORITY`), no timed owner session.

**Inference.** Economics implication 8 (“Human-directed hybrid is the only class of strategy whose labor shape resembles the 32–36 h / 5–6 person industry ranges”) is true as a **description of C’s cost** and is not evidence of **feasibility**. It is the opposite: it is the reason C may be dead on arrival if the owner remains a single un-clocked reviewer.

### 6.3 C increases human minutes; this programme’s failure mode is that those minutes never start

**Observation.** Industry inference (industry §16): generative pipelines that dump unique rasters move almost all of conte/acting/hands/identity/balloon/color/phone QC **after** generation. Unless correction is layer-local, review time exceeds generation time.

C tries to move QC **before** generation (storyboard, sheets) **and** keep it after (cleanup, approval). That is more human minutes, not fewer. Generation-only Ember/CH06 groups are ~7–8 minutes of caller-visible ImageGen per 40-panel chapter if parallel (economics §5.4) — a number the economics draft forbids comparing to professional labor hours. C would replace an 8-minute generate with days of specialist labor. That is correct professionalization. It is also the thing this owner has not done for a 20-item packet.

**Inference.** If the binding constraint is “owner does not sit,” C is the strategy most sensitive to that constraint. A and B can degrade to “one timed hour on existing plates.” C cannot. A C executed by agents writing storyboards and then batch-PASSING them is Phase B all over again (`write_phase_b_audits.py`). The draft has no mechanism that forces owner minutes > 0. `comic_input_gate.py` already requires timed human minutes > 0 for production repair — and therefore never fires on real CH05 art (technical audit §2.6). C will hit the same gate or will bypass it with a new synonym for “agent review.”

### 6.4 The renderer behind C is unspecified, and every specified renderer is blocked or uncleared

**Observation.**

- Live path: built-in Codex ImageGen; model/endpoint/seed/cost null; commercial uncleared; training-on-inputs unverified vs API default (economics §2).
- Selected-but-unused: OpenAI GPT Image 2 API (G07); not the chapter executor.
- Local Comfy + Anima + NoobAI-named files + adult LoRAs: commercial block or unrecorded license (NoobAI card commercial prohibition; Anima INTERNAL_BASELINE_ONLY; LoRA consent packet not found).
- FLUX.2-dev VAE: non-commercial dependency.
- BFL: training-use on inputs/outputs; ineligible for adult refs.
- Tapas: “AI generated content is not allowed” (official, accessed 2026-09-06).
- WEBTOON 2025 contest: any generative AI disqualifies.
- Canvas: no official AI clause found; silence is not permission (economics; industry).
- Originals contracts: unread.

**Inference.** C “replaces the production spine” but must still emit plates. Options:

1. Humans draw layers → needs the studio that is not evidenced (§6.2).
2. ImageGen still paints from a storyboard → that is B, and rights remain uncleared.
3. Local Comfy with cleared weights that do not exist yet → a research programme, not a 14-panel next step.

The draft does not choose. Without a renderer decision, C is a staffing wish plus the current uncleared generator. Feasibility is then identical to A plus unpaid storyboard labor the owner may not perform.

### 6.5 “Locked drawable assets” are not in the tree in a form C can consume

**Observation.** Visual A on gear/future-cast: six geometric family icons; twelve circle-head / triangle-arm diagrams; “not sequential art and not character drawings.” Premium 52-panel reader interleaves unique plates with benchmark stills; geography cannot be one place (Visual B). Volume sources are not a locked 1024×1536 (measurements: 864×1821 ×104, 863×1823 ×28, many others; overlay viewBox 1024×1536; CSS phone column 430px not 390). Identity refs for Ember are a handful of generated sheets, not a front/side/back model pack (industry: Manta requires sheets; CLIP: front/side/back/full body).

**Inference.** C’s first month is asset creation, not comics. That is correct studio practice. It is also how this programme already burns cycles (future-cast bible, gear HTML, style candidates) without locking the pages. Feasibility depends on stopping at 2–3 locked bodies and one room. The draft does not impose that stop. Future-cast of twelve adults is the known failure mode (story audit: do not put twelve more designs through the generator before CH01 causality works).

---

## 7. Visual A vs Visual B: the 25-cell split and Ember 2.14 vs 3.11

### 7.1 The 25 cells are not 25 aesthetic disagreements

**Observation.** `disagreement_count`: 25. Sixteen of the 25 are `north-garden-legacy-local`. Five are Ember volume. One is premium. Three are editorial-gear-hybrid. Zero are Borrowed Down. Zero are City.

**Observation.** Visual A’s North Garden sample: `pagecomp3/page03_p06–p10.png`, `pagecomp/page01_p06/p08`, actstage JPGs. Painted kitchen two-shots. No lettering. Visual A notes: “Visible sample is a kitchen two-shot plus style-probe stills.”

**Observation.** Visual B’s North Garden sample: `garden-work/northgarden/out` previz strips (`ch01_strip.jpg`, `ch01_sheet.jpg`, faceless geometry), style boards (`sigrid_r3.jpg` vs `r5.jpg`). Explicit note: “No sequential painted chapter exists in `production/accepted` (JSON only).” Evidence paths for B’s emotional_engagement 1 cite the strips, not `pagecomp3`. B: “Acting cannot function without faces.” A’s emotional_engagement 3 cites `pagecomp3/p08` blocking.

**Inference.** Most of the 25-cell headline is **incommensurable sampling**, not a reliability crisis about Ember. A scored the only internally accepted painted sequence. B scored the previz comic and concluded there was no painted serial. Both can be internally consistent. Averaging A’s kitchen 3s with B’s faceless-disc 1s is meaningless. The draft should not use “25 cells differ by 2+” as a generic uncertainty fog that makes C look like the cautious choice. The fog is concentrated on a pipeline that is not Ember.

North Garden 2+ list includes A=0 vs B=2/3 on balloons, tails, type, system UI, localization, vertical pacing. A’s 0s: no balloons on accepted rasters. B’s 2–3s: previz lettering **is** the comic (Visual B: “Lettering *is* the comic. Faceless geometry means there is almost no drawing for balloons to hide.”). Those deltas are corpus definitions. They should have been split into two pipeline IDs. They were not.

### 7.2 Ember volume 2.14 vs 3.11 is a real, systematic split — and it is not “the 25 cells”

Only **five** Ember-volume dimensions hit the 2+ rule:

| Dimension | A | B | What each scored |
| --- | ---: | ---: | --- |
| curiosity_and_chapter_end_propulsion | 2 | 4 | A: CH10 p024 group poster; curiosity is CH04 p018. B: cites ch01/ch08 p024 + chapter HTML |
| vertical_pacing | 2 | 4 | A: equal full-bleed, 12px gutters, sticky nav. B: “Portrait plates and 430px phone reader are the right machine.” |
| visual_economy | 1 | 3 | A: every panel a complete painting; no rest. B: cites p002 + HUD overlay (reserved teal field) |
| value_hierarchy | 2 | 4 | A: ember pops; mid-gray stone swallows figures; cream p007 clearer. B: cites p001 and CH08 p013 (peak stills) |
| environment_integration | 2 | 4 | A: p001 integrates; p007 cutouts and p010 sky do not. B: cites p001 and CH08 p013 |

**Observation.** Category means still differ everywhere: reader 2.5 vs 3.75; sequential 1.78 vs 3.0; art 2.27 vs 3.36; genre 2.17 vs 3.0; lettering 2.0 vs 2.44; production 2.1 vs 2.7. The 0.97 weighted gap is mostly **one-point optimism**, not the five 2+ cells. Lettering is the closest category. Production is closer than art. The fight is reader-impact, sequential, and art-direction — exactly the dimensions C wants to spend a studio on.

**Inference.** Two incompatible Ember objects are being scored:

- **A’s Ember:** illustration posters stacked; cream cyclorama / outdoor-in-pit as serial-stopping; mannequin faces; caption-causal fights. Sample weighted to CH01 action chain, p013 hands, empty p019 / ch05 p022 overlays, CH03/CH05/CH10 contacts.
- **B’s Ember:** manhwa-shaped book; reserved UI corners; Fault Sight → ankle as an intended combat sentence; CH08 hanging; six-finger and cutout as below-platform but not category-killing. Sample weighted to CH01/CH04/CH08, diagnostics of repaired fails, Elian reference sheet.

They did not look at the same chapters at full resolution. Story audit flags the same issue for itself (CH02/03/05/06/08/09 from contacts; medium confidence). **Unevidenced:** that either sample is the volume. **Inference:** C depends on A’s Ember being the true object. A (the strategy) depends on B’s Ember being close enough to salvage. The draft cannot use both.

### 7.3 B’s vertical_pacing 4 looks Goodharted

**Observation.** Rubric dimension is `vertical_pacing` under sequential_storytelling, not “phone column exists.” Visual A: no short/tall beats; 12px gutters; sticky nav. Industry: gutter height is a directing tool; WEBTOON-adjacent CLIP guidance ≥200px between panels on 800px canvas; vary panel height. Volume CSS: `border-bottom:12px`. Premium phone: `clamp(26px,6vw,84px)` plus six `deep-gutter` panels — i.e. the 52-panel reader is the one that actually attempted pacing.

**Inference.** Scoring 4 because “the right machine” exists confuses **format** with **pacing**. That single Goodharted 4 (weight 0.22 category, one of nine sequential dimensions) does not by itself create the 3.11 total, but it shows B’s scoring rule is more generous to Ember’s architecture than to Ember’s scroll. C-advocates should not treat B’s 3.11 as a second visual critic confirming licensed-floor craft. B says explicitly: “None of these pipelines would survive platform editorial as a weekly title.” The 3.11 is “best in this set / competent machine,” not “bar met.”

### 7.4 Peak-still vs sequence sampling

**Observation.** B’s environment_integration 4 and value_hierarchy 4 cite `p001` and `ch08/p013` — plates both reviewers would likely agree are strong stills (A’s strongest-stills list includes p001; B lists p001, p015, ch08 p013). A’s 2s cite the failure plates in the same fight (`p007`, `p010`).

**Inference.** This is classic cherry-picking inside a dimension. A scores the sequence’s worst spatial breaks. B scores the book’s best integration. Rubric 3 is “competent serial,” 4 is “would not embarrass a mid-tier licensed platform title **on this dimension**.” A 4 that ignores cream-cutout combat in CH01 is a stills score. The draft’s rejection of strategy A uses sequence failure. You cannot simultaneously (a) credit B’s 4s that were stills-based and (b) reject polish because sequences fail. Pick one scoring rule.

### 7.5 Editorial 2-vs-4 cells are definition fights

**Observation.** Editorial-gear-hybrid: opening_hook 2 vs 4; memorability 2 vs 4; quiet_spectacle 2 vs 4. A: editorial pages sampled are mid-fight denoise; hook/memorability inherited from unique 52; quiet not in the sampled clean frames. B: scores the method plus the 52-panel sequence those plates sit in.

**Inference.** If editorial is a **filter**, A is right (do not give it a new hook score). If editorial is **the published 52-panel hybrid chapter**, B is right (the reader sees a chapter, not a denoise paper). The pipeline ID bundles unique + clean-art + gear HTML. That bundle is confused. C’s “layered production” would be equally confused if gear icons and future-cast diagrams keep getting scored as if they were pages.

### 7.6 What the split does to the draft

- If you **preserve** the 2+ rule and refuse averaging, Ember volume is not one number. It is “A: below professional serial / B: working serial.” C is mandatory only on A’s object. A (strategy) is mandatory only on B’s object. The draft picks C anyway.
- If you **trust agreed pipelines**, Borrowed Down is the center, and Ember-first C is not supported.
- If you **trust B’s notes** (“best manhwa-shaped,” hybrid lettering is the only deterministic localizable object), the leading move is polish/modular lettering+review on Ember, i.e. A/B.
- If you **trust A’s notes** (illustration stacked, mannequin, cream cyclorama), keeping Ember’s premise is the wrong payload, i.e. D or polish-Borrowed-Down.

**None of those four consistent readings is C-keep-Ember-replace-spine.** C is the inconsistent reading.

---

## 8. Challenge: comparable-works analysis overclaims ToG / SL craft

The comparables draft is more careful than the strategy draft that will want to lean on it. It marks panel-forensic dimensions `not_assessed`. The overclaim is in the **synthesis that is then used as a bar**.

### 8.1 What was actually assessed

**Observation.** Method: licensed public pages, publisher copy, interviews; no third-party panels downloaded. Grid (§4): ToG shot-size, depth/value, line, anatomy/acting/hands, costume, color-script, effects, attack/counter, balloon/SFX/UI, quiet-panel ratio, exact hook seconds = **N**. SL: most of the same N; attack/counter “A” only as anime adaptation intent (Cartoon Brew), with manhwa beats N; color “A” only as “full-color marketed.”

**Observation.** Sources used as if they were panel craft: SIU interviews (world-first construction, football-like positions, “not boring the readers”), Yen Press look-inside **contents** (Prologue → Double Dungeon → Commandments), Tappytoon logline, Le Monde on Disciples succession, Sleepy-C **ORV** studio process (sister-studio, not SL), CLIP STUDIO generic webtoon tips, VFX Voice / Cartoon Brew **anime** staff.

### 8.2 Where the draft (and the strategy that cites this bar) overclaims

**Unevidenced as panel-level facts about ToG/SL:**

- That ToG Ep. 0 actually pictures a personal want in one beat (official **copy** does; pictures `not_assessed`).
- That SL’s manhwa has readable attack/counter/reversal grammar (anime action director studied live-action; “not the webtoon’s panel geometry”).
- Quiet-to-spectacle ratios.
- Line confidence, hands, balloon geometry, System-window originality as drawn.
- That REDICE lighting/pose direction on ORV is true of Solo Leveling plates.
- Early-vs-late ToG line density (explicitly “not independently measured here”).

**Observation.** Comparables §6 then states “the primaries’ transferable bar” as six bullets (first-screen want; spatial/rule machine; role-legible bodies; variable rhythm; lettering as directing; storyboard/QC) and concludes our rasters fail it because they are “prompted illustration sheets.”

**Inference.** Those six bullets are a reasonable **practitioner synthesis**. They are not a scored comparable. Using them as if Visual A/B had held Ember against ToG panels violates the rubric rule that copyrighted comparables stay `not_assessed` where panels were not sampled. The strategy draft’s “not like ToG/SL” is **owner speech** (valid, and it outranks scores). It is not a completed craft assessment of ToG/SL. Collapsing those two is how “we failed a bar we did not measure” becomes “therefore stand up a Korean weekly factory.”

### 8.3 Sister-studio and anime leakage

**Observation.** Sleepy-C/ORV (Comics Beat 2023) is used to fill SL’s production process. Cartoon Brew / VFX Voice are anime. unOrdinary / Weak Hero are “gap-fill” without panel assessment either, then used as a warning that simpler art can serialize.

**Inference.** Transferable production craft (storyboard is the directing record; episode ends are budgeted; specialized color/QC/letters credits on TBATE Tapas page) is on firmer ground because it is **credited process**, not pictures. That supports B/C as **process hypotheses**. It does not support claims that Ember’s line quality is X points below SIU’s, or that Candidate B charcoal-cel “is/isn’t” DUBU. Visual A already labeled the only honest version: if the bar is ToG/SL **staging/acting/causality/phone rhythm**, no pipeline’s strongest still is that craft (**inference**); if the bar is “would this pass as a fantasy illustration,” some premium Ember and City stills would. Comparables §5’s “soft painterly / 3D-cinematic plates” vs Visual A’s “charcoal contour is a real choice and holds” is an unresolved visual disagreement inside our own corpus, let alone against un-downloaded licensed pages.

### 8.4 Popularity theater

**Observation.** Comparables correctly says 1.3B views is not craft proof, then still leads with it. Strategy thinking that “the named bar” is ToG/SL **as market objects** will import that theater.

**Inference.** Owner-named titles are a taste instruction, not a measured rubric row. A 14-panel benchmark scored against SIU interview maxims will Goodhart into “opens with a want” captions. That is Ember CH01 already (caption dumps the want). The comparable that would matter is a blinded stranger retelling a fight (story audit). That test does not require ToG panels. The comparables draft’s useful remainder is process (conte before line, sheets, 3D bg, lettering in thumbnails). Its dangerous remainder is a fake panel bar.

---

## 9. Unevidenced, weakly evidenced, and internally contradicted claims

Claims below are flagged in the **source drafts** and in the **strategy draft’s leaps**. Not every sentence in a draft is a sin; these are the ones that cannot carry C.

### 9.1 Strategy-draft leaps (not evidenced by outputs)

| Claim | Problem |
| --- | --- |
| Polish is insufficient **because** contradictions are in the plates | Location of error ≠ unique repair architecture (§2.4). |
| B is not the leading architecture | Conceded as cheaper first experiment; not run; demoted anyway. |
| Replace the spine that turns beats into plates | Ember already does one panel per plan; the unreplaced stages are review/compiler/identity. |
| Keep Ember premise as payload | Page scores 2–3; 99/100 is pre-page; identity not locked; owner post-volume approval absent. |
| Human-directed layered rebuild | Human minutes null; no staff; renderer unspecified; assets not drawable sheets. |
| Next step = frozen **14**-panel | Story audit said 12–16; industry professional quantum ~50; 14 cannot demonstrate weekly fitness. Number is arbitrary. |
| D only after Ember storyboard fails | Owner already listed complete restart; Ember-optional is already in the story auditor’s pilot. |
| Neutral-or-Ember 14-panel will inform spine replacement | If all stages change, attribution is impossible. |

### 9.2 Pixel-observation conflicts (do not resolve; do not invent)

**Observation conflict.** Lead inspector: p001 “two tiny adults”; silhouettes similar at distance. Visual A: “tiny figures… two unreadable silhouettes.” Story auditor: “They are not ‘tiny silhouettes’; the beat overclaims scale.” Same path `pilot/source/p001.png`. **This memo does not pick a pixel fact.** Any strategy that depends on “p001 is a strong comic open” or “p001 fails as panel one because figures are unreadable” is standing on a disputed observation.

**Observation conflict.** Story: volume P001 figures “large and readable.” Visual A/lead: opposite. Story’s opening_hook 2.5 vs Visual A 3 vs Visual B 4 — three numbers, one plate.

**Observation (process).** Visual B did not walk `ComfyUI/` and treated accepted kitchen as JSON-only. Visual A scored `pagecomp3` rasters. North Garden scores are not a disagreement about the same pixels.

### 9.3 Story audit — inference that reads as fact

- “The property is worth keeping as a *payload*, not as a production schedule.” **Recommendation/inference.** Page table does not show a 4 on premise.
- “A reader who likes spreadsheets will trust this book.” **Inference.**
- “Further volume chapters would multiply the same 24-panel template.” **Inference** about unbuilt chapters; density template on CH01–CH06 is observation.
- CH07 P012/P014 “false as a description of rasters” vs Phase B PASS: **observation** if those rasters were opened; this reviewer did not re-open them. Treat as story-auditor observation, not independently verified here.
- “Premium CH01 is a lettering-and-partial-reshoot… not a fully staged 52-panel chapter.” Supported by 28 unique files / 28 unique generation calls (archivist; story). Hash-join of which 24 indices are baseline reuse: story says **not verified**.
- North Garden “plans only in this worktree” — true of the story auditor’s method; false as a statement that kitchen rasters do not exist (they do; A scored them).

### 9.4 Lettering audit — estimates labeled, still easy to launder

Phone px are **estimates** (`font-size × display_width / viewBox_width`). Compact grids ~6 CSS px are estimates. Balloon area is bbox, not filled path; plan 221.48% is the locked number. UI-density HTML is **stale** (original type on hybrid plates). Volume “phone” is 430px while ADR/bible say 390. **Unevidenced:** that hybrid “satisfied the owner” — owner has no recorded editorial-pass approval; hybrid failed smaller-type, deeper-wording, 84% opacity (0.94 actual).

Silent overlay counts: lettering audit 15/52 empty hybrid SVGs; measurements-summary `silent_or_no_tspan` 20 for premium-hybrid. **Do not flatten.** Different parsers (plan units vs tspan presence).

### 9.5 Technical / Goodhart list (evidenced as gaming, not as art)

These **are** evidenced, and the strategy draft should not forget them when it keeps “fail-closed records”:

- `mark_art_review.py` one notes string → N `REVIEWED_PASS` (lead: 225 rows, 224 PASS, 11 unique notes, 10 chapter-batch strings).
- `compile_ch05_complete_chapter_agent_triage.py` `fail: 0` by construction.
- `validate_ch05_cross_panel_semantic_gates.py` passes on prompt **text**.
- Continuity hair/wardrobe: dict equality, not pixels.
- `audit_volume.py` expands lettering boxes then tests fit.
- Density 159/60/21 assigned by order sets, then counted.
- `write_phase_b_audits.py` hardcoded PASS from status.
- Clean-art `_clean_plate()` 3×3 median can lower noise metrics by blurring.
- Protected zones: heuristic rectangles, `protected_overlap_types: []` on all 59 premium units.
- Phone type: authored scale, not OCR.
- Tracked `volume-validation.json` PASS while this checkout has no `experiments/` rasters.
- Ember `model: "imagegen-default"` vs CH05 honest null.
- System-state expected finals authored by the same script that validates them.
- Generation-request count: 224 in `volume-master.json` vs 225 `new_generated_sources` in `volume-validation.json` — not averaged (economics correctly refuses).
- Premium-rd unit tests use uniform rubric 4.2 vs 3.1 — machinery, not art.
- `generation-requests.json`: single reviewer `primary_agent_local_visual_inspection`.

**Inference.** Keeping “fail-closed records” without changing **what they measure** keeps the Goodhart engine. C that retains those gates will again ship PASS volumes. A/B that only add storyboard will too, unless the gate becomes “blinded stranger retells the fight” (story) or timed owner minutes > 0 (economics).

### 9.6 Economics / industry inferences that nudge C

- “Human-directed hybrid is the only class whose labor shape resembles industry” — true of labor **shape**, not of available labor.
- 12–25 h/chapter — unmeasured guess.
- Canvas AI-tag blogs — contradicted by official policy fetch; correctly rejected in economics; do not reimport.
- WEBTOON Originals AI clauses — **null**.
- Built-in ImageGen cost $0 in ledgers — **convention**, not invoice; monetary cost null.
- Electricity $0.25/70-panel chapter — not a measured North Garden figure.

### 9.7 Archivist hypotheses that can be laundered into “inheritance improved”

Inheritance table is mostly **hypothesis**. “Ember adds numeric Ledger + Candidate B; owner approved pilot style, then 2026-09-06 still below ToG/SL” is the honest row. “Whether inheritance improved the page” is repeatedly unlabeled in casual summary and labeled in the table. Strategy C’s “keep Ember because each step added tools” is the archivist’s **tools** column, not the **page** column. Editorial “page pixels change only on 12 cleaned panels plus lettering SVG.”

### 9.8 Comparables §5 visual claims

“Inspected volume rasters remain soft painterly / 3D-cinematic plates” vs Visual A line_and_shape 3 “charcoal contour is a real choice.” Premium p002 “photoreal/3D fracturing chain” (lead) is a **medium** break, not the whole volume. Candidate B was selected against painterly C (`style-candidate-review.md` as cited). Production “still converges to illustration” is **inference**. Do not treat comparables §5 as a third visual reviewer equivalent to A/B.

### 9.9 Throughput and “we already have a book”

240 lettered Ember panels, 300 Borrowed Down, 240 City, 52 premium, 50×6 CH05 arms: **observation** of files. Unaccepted, uncleared, non-reproducible: **observation**. Using corpus size as production fitness is Goodhart (technical: validator volume is overhead). C’s “not another ten-chapter volume” is right about **not multiplying the template**. It is not evidence the next object must be a new spine.

### 9.10 Rights claims that cannot support a publishable C

No generated candidate commercially cleared. Codex vs API training-on-inputs **unverified**. Adult LoRA consent packet **not found**. NoobAI commercial prohibition is a primary-source **sourced fact**. Immediate publication of current rasters is a rights decision, not an engineering merge (economics). C that still uses ImageGen plates inherits the block. C that redraws everything by hand is a studio. Neither is evidenced as ready.

---

## 10. Minority conclusions to preserve

Do not let the strategy draft flatten these.

1. **Visual B:** Ember volume is the best manhwa-shaped object in the set; weighted 3.11; CH01 vault / CH08 hanging nearest to a licensed-floor still; LitRPG machinery understandable when overlays are on; editorial/hybrid is the best **method** even if sequential quality remains the premium rasters; strongest stills can be competitive as single images.
2. **Visual A:** Borrowed Down drawings are the closest to comics language; North Garden kitchen is the most comic-like ink; Ember stills are competent **illustration** not comic panels; generic prestige-fantasy is the Ember/City failure class; strongest stills list still includes Ember p001/p004/p026/p044 and Sable p018.
3. **Visual A+B agreement:** Borrowed Down ~2.8; City ~2.4; North Garden <2; lettering is a failure on Borrowed Down; none survive platform editorial as a weekly; action is pose-assembled almost everywhere; phone 390 vs volume 430 split is real.
4. **Story auditor:** Keep ledger, kill 24-panel / four-moment template; do not start a fourth ten-chapter IP; do not extend Ember to CH11–CH30; voice pass is cheap; CH04 is the best reversal; CH07 is the argument and the pictures miss it; premium **script** already lists the causality beats; blinded-reader retell is the test; Phase B PASS is not visibility.
5. **Lettering specialist:** Hybrid improved obstruction/phone/tails, not depth/smaller type/84% opacity; volume implemented deeper wording and 84% at the cost of giant cards and a 430px column; comparing volume v2 to premium hybrid without the 24-vs-52 denominator is a category error; localization is weak on every Ember surface; SFX are competent stickers.
6. **Technical:** One panel per plan + SVG + fail-closed money should be retained; strip generation and batch PASS are the highest-leverage amplifiers; records reproduce, pictures do not; clean checkout cannot show the comic.
7. **Economics:** Do not protect sunk $1.06 or unmetered ImageGen; protect owner hours; kill criterion is more generation before a timed owner session; Tapas closed to AI; Canvas silence ≠ permission; built-in cost is null not zero.
8. **Industry:** Conte is gateable before line; lettering belongs in thumbnails; 3D/asset identity is the professional floor; platform AI is pose/color/recs, not full-scene finals; contest gen-AI ban; no measured QC-minutes study for AI vs hand.
9. **Comparables (the careful part):** Process credits (TBATE stack; ORV storyboard-first; Disciples succession on staging) are usable. Panel craft of ToG/SL is `not_assessed`. unOrdinary/Weak Hero as “acting + weekly question without key-visual finish” is a live alternative bar the owner did not name but the draft should not erase.
10. **Lead inspector:** Sequences fail first; stills can look like competent dark-fantasy illustration; Goodhart of `REVIEWED_PASS` is a records fact; overlay vs source aspect mismatch is a structural risk (`object-fit:fill`).
11. **Owner speech:** Candidate B “amazing”; lettering punch-list; later “still not like ToG/SL”; three options including restart. Pilot approval ≠ volume acceptance ≠ commercial clearance.

---

## 11. What would actually falsify the draft (without picking a winner)

The draft should not be allowed to win by eloquence. Minimum tests, all cheaper than a studio:

1. **Timed owner session** with minutes ≠ null on a frozen packet (G07 still qualifies). If the owner will not sit, C is infeasible and A/B/D must be re-ranked under that constraint. If the owner sits and rejects Ember stills that B scored 4, D moves up. If the owner still loves Candidate B and asks for balloons/system, A moves up.
2. **A one-stage 12–16 panel run (B)** with pre-registered pictorial pass/fail (story audit §11) and **only one** stage changed vs a control generated the old way. If pose-assembly survives a human storyboard, C gains. If it dies when batch PASS dies, C is unnecessary.
3. **Blinded stranger retell** of one existing fight (CH01 action or CH04 loss) from pictures plus short speech, no plan file. If they can retell CH04, A-on-CH04-class chapters is live. If they cannot retell anything, A’s “polish the current hybrid as shipped” is weaker — but B (add in-betweens, same generator) is still not eliminated.
4. **Stop averaging 2+ disagreements.** Report Ember as A:2.14 / B:3.11, not 2.62. If the lead cannot act without a single number, they are violating the rubric they froze.
5. **Do not cite ToG/SL panel craft.** Cite owner taste, process interviews, and our pages. Mark the rest `not_assessed`.
6. **Name the renderer and the human roster** with a budget line. If both are “owner, evenings, ImageGen,” the strategy is A or B regardless of the letter C.

Until those are done, the strongest honest statement is:

**The evidence does not uniquely support Strategy C as primary.** It supports a **disjunction**: A if B’s Ember and the owner’s Candidate B praise are controlling; B if the technical audit’s stage-level causes are controlling; immediate D if A’s ranking, generic-prestige diagnosis, empty owner-minutes, and owner “complete restart” are controlling. C is the combination that takes A’s pessimism about plates, B’s optimism about Ember-the-IP, industry’s studio org chart, and the story auditor’s payload loyalty — the one combination that has not been shown to be feasible and has not been shown to be necessary.

---

## 12. Sources used (this memo)

Read in this worktree only, except where those files themselves cite sibling raster paths (not re-opened here, no pixel adjudication):

- `docs/research/anime-pipeline-total-review/common-rubric.json`
- `docs/research/anime-pipeline-total-review/evidence/lead-visual-inspection.md`
- `docs/research/anime-pipeline-total-review/evidence/visual-a/notes.md`
- `docs/research/anime-pipeline-total-review/evidence/visual-a/scorecard.json` (Ember volume block + summaries)
- `docs/research/anime-pipeline-total-review/evidence/visual-b/notes.md`
- `docs/research/anime-pipeline-total-review/evidence/visual-b/scorecard.json` (North Garden sample + Ember volume block)
- `docs/research/anime-pipeline-total-review/evidence/scorecard-reconciliation.json`
- `docs/research/anime-pipeline-total-review/evidence/story-audit-draft.md`
- `docs/research/anime-pipeline-total-review/evidence/technical-audit-draft.md`
- `docs/research/anime-pipeline-total-review/evidence/lettering-audit-draft.md`
- `docs/research/anime-pipeline-total-review/evidence/economics-draft.md`
- `docs/research/anime-pipeline-total-review/evidence/industry-research-draft.md`
- `docs/research/anime-pipeline-total-review/evidence/comparables-draft.md`
- `docs/research/anime-pipeline-total-review/evidence/archivist-inventory.md`
- `docs/research/anime-pipeline-total-review/evidence/measurements-summary.json`

No git commit. No other files modified. No strategy declared as the winner.
