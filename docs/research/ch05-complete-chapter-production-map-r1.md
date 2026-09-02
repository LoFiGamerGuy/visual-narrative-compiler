# CH05 complete-chapter production map r1

Date: 2026-09-02

State: production map for an unaccepted complete review draft

## Outcome

CH05 is a complete 50-panel suspense chapter on paper. Fourteen ComicPanelPlans already have engineering-selected, owner-pending candidates; 36 plans have no candidate. The fastest evidence-preserving route to a chapter that can be reviewed in one pass is therefore:

1. retain the 14 strongest existing candidates as provisional layout assets;
2. generate the 36 missing plans in 12 contiguous, story-ordered batches of three to five plans;
3. assemble and review the whole 50-panel scroll after every batch, while limiting pixel repair to failures that interrupt story causality, identity, continuity, or lettering clearance;
4. defer style unification polish until a readable first chapter exists.

This changes the optimization target from isolated style probes to chapter completion. It does not accept, commercially clear, or declare any candidate an exact production base.

No engineering-selected candidate currently warrants a targeted pixel repair before the first full draft. P009 and P044 need layout mitigation, not regeneration; every other uncovered plan needs a first candidate rather than a repair. Failed existing alternatives remain diagnostics and must not occupy chapter slots.

## Source and planning boundary

- ComicPanelPlan source: `production/comic/ch05-sc01-panel-plans-v1.json` (`3c81b6b2b934062e2a8b0e440ae00d66654c336d4446c73b35ef2c42a14aaf05`)
- Canon state: `production/canon/story-state/ch05-sc01-r1.json` (`ccd0c34bd23e97ff4f1549c2e28c930c168e754231943cd7e9e719a285463e14`)
- Fictional-adult continuity profile: `production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json` (`4a2bac302ad720e67e281e7b59903b8b2c5a43792056175c6add103b873eb3b2`)
- Existing RenderRecord index: `production/comic/run-manifests/ch05-built-in-renderrecord-index-r1.json` (`546eaca1f47e02aea256192dc24653b29912d607b20cdafbcf9bb8eb4b5bf437`)
- Existing sequence plan: `production/comic/run-manifests/ch05-chapter-sequence-production-batches-r1.json` (`d1c14d09b5afb374260ceabbd4594edcbeecf32925f5a826434f860e99106ea9`)
- Existing 14-panel cadence assembly: `docs/research/evidence/ch05-variable-cadence-assembly-r1.json` (`47e1ab10278f1a8e58ba3d2eefb56185fc6a62e57da74dc51e2c2db78aae930a`)
- Active planning structure: ComicPanelPlan only.
- AnimationShotPlan: absent/null.
- E-Conte: absent/null.

The owner's broad approval authorizes continued production and best engineering judgment. It is not interpreted as per-candidate acceptance, commercial clearance, or an exact-base declaration.

## Chapter-level visual grammar

Use a role-aware hybrid that reads as one world rather than four unrelated treatments:

- **Clear-line watercolor:** primary chapter mechanism for travel, physical causality, environmental transitions, wet surfaces, and object interaction.
- **Clean graphic with restrained painterly color:** wide orientation, warning, reveal, and urgent action anchors where silhouette and target direction must read instantly.
- **Premium cel-painted:** faces, deductions, reactions, and intimate continuity beats.
- **Limited ink/flat:** quiet inserts only; keep backgrounds sparse and preserve the tested palette/line family.

Keep the same cold wet-morning palette, line-weight hierarchy, material vocabulary, and adult facial design across mechanisms. Large reveals and action anchors use 1040–1200 px of a 1200 px chapter canvas; medium character beats use 720–960 px; small inserts use 520–720 px. Alternate alignment and gutter length so object clues create pauses while wide panels reset location and direction.

Three classifier corrections improve chapter rhythm: P017 (first mill reveal), P030 (mill-interior reveal), and P048 (farmhouse-smoke reversal) should be full-width or near-full-width reveals, not small inserts.

## Non-negotiable continuity

- Soren is a clearly adult fictional man: short-to-medium wavy light-brown/dark-blond hair, never black or bright blond; light beard/stubble; pale oatmeal work coat over muted blue-gray layers; dark trousers and practical boots.
- Sigrid is a clearly adult fictional woman: dark-brown/near-black hair in a low bun, knot, or compact braid, never blond; dark brows and gray-blue eyes; dark blue-brown practical plaid wrap over gray-green expedition layers; dark trousers and practical boots.
- Preserve role order and exact visible-adult count from each ComicPanelPlan. Never add bystanders.
- Maintain object state: folded route map -> soot-stained twine -> red cloth -> wet ember/drum -> second twine/brass bell -> dry footprint discontinuity -> sealed tin -> dry matches/creek map/blank card -> cut twine -> creek map inside Sigrid's wrap -> unexpected farmhouse smoke.
- Maintain travel direction: farmhouse downhill to mill, careful movement around bridge and mill, then uphill return; P050 has Sigrid leading the urgent run and Soren following with the map.
- P036 must show one continuous fallen plank physically linking Sigrid's brace, Soren's leverage/control, and the elevated tin. The P036 visual reference is composition-only; its swapped hair colors are forbidden.
- No armor, weapons beyond P044's canon pocket knife, monsters, magic, or LitRPG interface elements belong in CH05 without a later ComicPanelPlan revision. Future concepts remain separate and non-canon.

## Lettering-safe rule

Every rendered panel remains text-free. Protect the exact canonical normalized safe zone as a quiet field: top-left `[0.04, 0.04, 0.30, 0.18]`, top-right `[0.66, 0.04, 0.30, 0.18]`, or centered top `[0.25, 0.04, 0.50, 0.16]`. No face, person, important hand, causal object, or essential silhouette may enter it. Transparent overlap is reviewable only when phone-size expression and silhouette remain clear. Use an outside-art band before regenerating otherwise good art.

## Every ComicPanelPlan in reading order

Legend: **reuse** means engineering-selected but still owner-pending; **new** means no current candidate; **reuse + layout** means keep pixels and solve safe-field contrast in layout before considering regeneration.

| # | Story beat / composition | Coverage and next action | Mechanism / cadence | Safe zone |
|---:|---|---|---|---|
| 01 | Leave farmhouse before grass dries; downhill departure wide | reuse `c019`; keep `c001` only as wrong-direction diagnostic | clear-line watercolor, full-width orientation | top-left |
| 02 | Sigrid checks smoke against folded map; over-shoulder | reuse `c002` | cel-painted, medium character clue | top-right |
| 03 | Soren sees prints overlap rather than lead trail; boot/track clue | reuse `h002`; keep `c003` as geometry/occlusion diagnostic | clear-line watercolor, small clue insert | top-left |
| 04 | Silent exchanged look, then continue; opposite thirds | **new**; establish paired facial continuity before trail sequence | cel-painted, medium two-shot | top-right |
| 05 | Rainwater runnel crosses path; no people | **new**; calm moving-water bridge between reaction and action | clear-line watercolor, wide environmental pause | centered top |
| 06 | Sigrid steps first and points to old marker; Soren waits | **new**; enforce Sigrid-leading weight shift and readable pointing hand | clear-line watercolor, full-width directional action | top-right |
| 07 | Mill-wheel sketch on marker; stone close-up | **new**; keep the carved circle unmistakable and text-free | limited ink/flat, small insert | centered top |
| 08 | Soren folds map to hide farmhouse/expose creek | **new**; readable hands and before/after fold geometry | cel-painted with simplified surround, medium clue | top-right |
| 09 | Wet branches narrow trail; Sigrid leads | reuse + layout `c005`; `c004` is lower-motion backup | clear-line watercolor, tall transition | top-left; outside-art band preferred |
| 10 | Sigrid hears water before seeing it; listening profile | **new**; expression and open dark woods establish sensory turn | cel-painted, medium close | top-right |
| 11 | Soren finds soot-stained twine on thorn; hand insert | **new**; legible twine/thorn contact and soot contrast | clear-line watercolor, medium-small causal clue | top-left |
| 12 | Twine points downhill as if pulled taut/released | **new**; one diagonal force vector, no characters | limited ink/flat, small pause | centered top |
| 13 | Pair follow creek instead of tracks; descending rear wide | **new**; make route change and role silhouettes unmistakable | clear-line watercolor, full-width transition | top-left |
| 14 | Smoke disappears behind ridge shoulder; no people | **new**; restrained smoke endpoint and negative space | limited ink/flat watercolor, small sensory insert | centered top |
| 15 | Sigrid marks sight-loss on map with wet thumb | **new**; thumb obscures route line without illegible hand anatomy | cel-painted, medium clue | top-left |
| 16 | Soren says smoke is closer; adults walk without facing | **new**; dialogue-capable two-shot with clear profiles | cel-painted, medium two-shot | top-right |
| 17 | Abandoned mill first appears below, broken roofline | **new**; chapter's first major reveal, no people | clean graphic restrained paint, large full-width reveal | centered top |
| 18 | Smoke rises behind mill, not chimney | **new**; telephoto spatial contradiction must read instantly | clear-line watercolor, small-medium sensory insert | centered top |
| 19 | Sigrid stops Soren from open bridge | reuse `c006`; `h003` is flatter backup, `c007` occlusion diagnostic | clean graphic, full-width warning action | top-left |
| 20 | Cross creek on stones below bridge | **new**; separated stepping rhythm, water/weight causality | clear-line watercolor, full-width action | top-right |
| 21 | Fresh red cloth moves from lower branch | **new**; isolate cloth and wind vector, unreadable background | limited ink/flat, small insert | centered top |
| 22 | Soren stops Sigrid touching cloth | **new**; hands nearly meet but do not touch marker | cel-painted, medium two-shot | top-right |
| 23 | Circle toward collapsed loading door | **new**; side travel through grass, preserve mill geography | clear-line watercolor, wide transition | top-left |
| 24 | Thin smoke thread rises from drum hidden behind stone | **new**; reveal drum location, no people | limited ink/flat watercolor, small sensory insert | centered top |
| 25 | Drum holds wet pine needles and damp ember | **new**; overhead evidence arrangement | limited ink/flat, small object insert | centered top |
| 26 | Sigrid tests heat without disturbing ember | reuse `c008` | cel-painted, medium single-person causal beat | top-right |
| 27 | Soren sees second twine entering mill wall | **new**; line must visibly continue from hand/eyeline into darkness | cel-painted/clear-line hybrid, medium clue | top-left |
| 28 | Line tied to small brass bell inside doorway | **new**; exact line-to-bell connection, bell still | limited ink/flat, small object insert | centered top |
| 29 | Sigrid chooses wall opening; Soren watches exterior | reuse `h004`; keep `c009` as safe-zone diagnostic | clean graphic, wide dual-target threshold | top-left |
| 30 | Daylight bars stripe standing water and broken gears | **new**; second major location reveal, no people | clean graphic restrained paint, large full-width interior reveal | centered top |
| 31 | Sigrid finds dry prints ending at water | **new**; crouched silhouette and dry/wet boundary | cel-painted, medium clue | top-left |
| 32 | Soren sees prints restart far side facing back | **new**; deep perspective and reversed toe direction | clear-line watercolor, medium-deep clue | top-right |
| 33 | Quiet drip rings outside bell once; both freeze | **new**; different depths, single sensory event, no decorative motion | cel-painted, medium reaction | top-left |
| 34 | Neither moves toward bell; empty doorway dominates | **new**; held negative-space suspense | cel-painted with restrained detail, medium-wide two-shot | top-right |
| 35 | Sealed tin isolated on upper beam | reuse `c010` | clear-line watercolor, small reveal | centered top |
| 36 | Soren reaches tin with one plank; Sigrid braces | reuse `h006`; `c012` is valid cel backup; `c011`/`h005` diagnostics | clear-line watercolor, tall causal anchor | top-right |
| 37 | Tin contents: matches, creek map, blank card | **new**; three objects readable, no accidental writing | limited ink/flat, small object spread | centered top |
| 38 | Map marks farmhouse square and mill circle | **new**; exactly two deliberate symbols and route geography | clear-line watercolor, small-medium map insert | centered top |
| 39 | Third upstream mark extends beyond torn map edge | **new**; Soren finger stops at edge, third mark distinct | cel-painted/clear-line hybrid, medium clue | top-left |
| 40 | Sigrid concludes smoke was a signal | reuse `c013`; `c020` lower-density backup | clear-line watercolor, medium deduction close | top-right |
| 41 | Hidden drum goes out in rain | **new**; thinning smoke and wet metal, no people | limited ink/flat watercolor, small sensory pause | centered top |
| 42 | Bell rings again from creek side | **new**; empty doorway plus one taut line establishes changed source | clear-line watercolor, small-medium sensory clue | centered top |
| 43 | Leave tin open and retreat together | **new**; cautious backward weight shift, tin remains on stone | clear-line watercolor, full-width retreat | top-left |
| 44 | Soren cuts taut twine with pocket knife | reuse + layout `c014` | limited ink/flat, small causal insert | top-right; outside-art band preferred |
| 45 | Bell stays silent after cut; creek and mill exterior | **new**; hold stillness long enough to register consequence | limited ink/flat, small quiet pause | centered top |
| 46 | Sigrid stores creek map inside wrap, not notebook | reuse `c015` | cel-painted, medium continuity close | top-right |
| 47 | Pair climb uphill under cleared sky | **new**; reverse the earlier travel vector, no smoke visible | clear-line watercolor, full-width return transition | top-left |
| 48 | Farmhouse visible from ridge; its chimney now smokes | **new**; chapter reversal needs house/smoke legible at phone size | clean graphic restrained paint, large full-width reveal | centered top |
| 49 | Soren realizes stove was never lit | reuse `c016` | clean graphic, medium target-change reaction | top-left |
| 50 | Sigrid runs for house; Soren follows with map | reuse `h001`; `c017` action backup, `c018` flatter backup | cel-painted, full-width urgent hero | top-right |

## Story-ordered generation batches

Each batch is a contiguous review unit. Existing candidates remain visible as anchors, but only missing plans consume new generations. Generate the missing panels first; create alternates only after the batch has a complete causal read.

| Batch | Plans | New / reuse | Narrative job | Continuity and review gate |
|---|---|---:|---|---|
| B01 | P001–P004 | 1 new / 3 reuse | Establish departure, map, anomalous prints, silent agreement | Lock adult faces/hair/wardrobe and downhill direction; P004 must match P002/P003 identities |
| B02 | P005–P009 | 4 new / 1 reuse | Runnel -> marker -> map refold -> narrowing trail | Sigrid leads P006/P009; Soren handles map P008; wetness and direction persist |
| B03 | P010–P013 | 4 new / 0 reuse | Hear water -> find twine -> infer force -> choose creek | Twine is soot-stained and points downhill; P013 visibly changes route |
| B04 | P014–P018 | 5 new / 0 reuse | Lose smoke -> discuss distance -> reveal mill -> locate false smoke source | Preserve ridge/mill/smoke geography; P017 and P018 form a reveal/contradiction pair |
| B05 | P019–P023 | 4 new / 1 reuse | Avoid bridge -> cross below -> notice marker -> stop contact -> approach mill | Use P019 as dual-character anchor; bridge remains above as they cross stones below |
| B06 | P024–P027 | 3 new / 1 reuse | Reveal drum -> inspect ember -> test heat -> discover second line | Same drum/ember state across cuts; Sigrid's hand never touches ember |
| B07 | P028–P031 | 3 new / 1 reuse | Show bell trap -> choose wall opening -> reveal interior -> find false tracks | Maintain line-to-bell connection and consistent doorway/wall-opening geography |
| B08 | P032–P036 | 3 new / 2 reuse | Reverse prints -> bell reaction -> deliberate pause -> spot tin -> retrieve it | P033/P034 freeze-and-hold rhythm; P035 position must support P036's one-plank geometry |
| B09 | P037–P040 | 3 new / 1 reuse | Inventory evidence -> read symbols -> find third mark -> infer signal | Exact contents and square/circle/third-mark logic must survive phone-size reduction |
| B10 | P041–P044 | 3 new / 1 reuse | Drum extinguishes -> bell source shifts -> retreat -> cut line | Source change is causal; open tin remains behind; P044 cut point is explicit |
| B11 | P045–P047 | 2 new / 1 reuse | Confirm silence -> protect map -> begin uphill return | Map transfers into plaid wrap; sky clears; no mill smoke or bell motion after cut |
| B12 | P048–P050 | 1 new / 2 reuse | Reveal farmhouse smoke -> recognition -> urgent run | House position consistent across all three; smoke is new; Sigrid leads and Soren carries map |

## Existing candidate disposition

The provisional chapter should use these exact candidates now:

- P001 `c019`: correct downhill departure; phone-scale identity relies mainly on wardrobe, acceptable for a distant establishing wide.
- P002 `c002`: strong quiet orientation and clean top-right field.
- P003 `h002`: corrected crossing-track geometry and clean safe zone.
- P009 `c005`: best grounded trail motion; requires outside-art or carefully translucent lettering treatment.
- P019 `c006`: strongest warning gesture and role order.
- P026 `c008`: strongest heat/hand/smoke causal read.
- P029 `h004`: corrected safe zone and dual target staging.
- P035 `c010`: effective quiet object reveal.
- P036 `h006`: strongest single-plank causal geometry; `c012` is the valid cel-painted alternate.
- P040 `c013`: strongest stable deduction beat; `c020` is the lower-density alternate.
- P044 `c014`: readable cut causality; requires outside-art or carefully translucent lettering treatment because of safe-field contrast.
- P046 `c015`: strong evidence-protection continuity beat.
- P049 `c016`: readable target-change realization.
- P050 `h001`: strongest polished urgent-return hero; `c017` is the stronger grounded-motion alternate if the cel finish breaks sequence continuity.

Do not place `c001`, `c003`, `c007`, `c009`, `c011`, or `h005` in the chapter draft; retain them as failure diagnostics.

## Completion and iteration policy

After each batch, rebuild the complete 50-slot scroll with explicit placeholders for still-missing panels, then inspect: story order, role binding, hair/wardrobe drift, exact cast count, object-state continuity, target direction, safe-zone occupancy, and 390 px phone readability. A batch is complete when every plan has one reviewable candidate and the sequence reads causally; polish alternates are secondary.

The first 50-panel review draft may mix mechanisms and remain unaccepted. Once it exists, use the full scroll—not isolated beauty—to rank the smallest refinements. Regenerate only panels that fail identity, causality, continuity, target direction, or phone readability. Resolve safe-field contrast in lettering/layout before spending a new image call. That keeps engineering improvement parallel to story production without allowing instrumentation to consume the production milestone.
