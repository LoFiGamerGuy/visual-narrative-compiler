# Lead visual inspection notes

Inspector: lead agent. Access date: 2026-09-06.
Method: full-resolution PNG reads from protected sibling worktrees plus tracked SVG/HTML in the isolated worktree. No rasters copied. No third-party comics embedded.

Classification: observation unless marked inference.

## Ember Lattice 16-panel pilot / volume CH01 sources

Paths: `C:\AgentWorkspaces\anime-pipeline-litrpg-manhwa-20260904-001211\experiments\reimaginings\ember-lattice\pilot\source\`

- **p001** (1024×1536): cinematic establishing shot. Two tiny adults on a chain bridge over an ember shaft. Strong scale. Reads as a key visual, not a comics panel with acting. Silhouettes of the two humans are similar at this distance.
- **p002**: adult three-quarter portrait. Identity is lockable (ash-blond, torn gray-green coat, hookblade). Acting is a stock “cool stand.” Left hand is mannequin-stiff. Large empty teal field reserved for HUD.
- **p003**: stacked two-shot. Faces are generic-handsome with limited mouth/eye acting. They do not clearly look at each other. Tracked lettering overlay (`docs/.../ch01/panels/p003.svg`) places two identical 348.2×391.3 rounded rectangles (opacity 0.84) with 9-line speeches. Observation: lettering is mechanically cloned boxes, not organic balloon craft.
- **p004**: monster reveal. Cylindrical “bell jaw” golem is the most distinctive design in the sample. Scale works. Spear on the ground is a readable prop.
- **p006**: charge still with orange speed streaks. Characters absent. Geography matches p001.
- **p007**: Mira vs cylinder jaw on ivory ground (density-low contract). Spear contact is ambiguous; a kite-shaped ivory plane behind the monster confuses shield vs monster anatomy. Inference: layout is a posed illustration, not a contact-clear comics beat.
- **p008**: better contact — spear shaft through the jaw ring, dirt spray. Expression still relatively calm for a wrench/skid beat.
- **p011**: impact with burst lines. Closest to manhwa action grammar in the pilot. Still illustration-floaty; coat physics decorative.
- **p013**: item close-up. Hands are the weakest anatomy in the sample (palm/coins). Face remains generic-serious.
- **p015**: dual attack still. Explosion at the ankle is visible; Mira’s spear does not clearly complete a pin. Poster composition.

## Volume later chapters

- **CH03 p001**: recycles “two adults on a bridge over a void.” More painterly than Candidate B’s “not painterly fantasy” contract (`src/reimaginings/ember_lattice/author_volume.py` STYLE_BLOCK). Glass bridge is a new motif.
- **CH05 p012**: over-shoulder two-shot. One of the better comics compositions (Mira looking back). Identity holds.
- **CH10 p024**: four-person party lineup, low camera, ember door. Key visual / poster, not a sequential ending beat.

Measured PNG sizes (`evidence/measurements.json`): volume sources are **not** a locked 1024×1536. Dominant sizes include 864×1821 (104 files) and 863×1823 (28). One 1536×1024 landscape (the only HARD_FAIL). Overlay SVGs are authored on a 1024×1536 viewBox. Volume CSS (`.scroll{width:min(100%,430px)}`) sizes the phone column to 430px, not 390px.

Inference: lettering geometry and source-art aspect are not a single camera; stretching via `object-fit:fill` on mismatched aspects is a structural risk.

## Premium unique 52-panel CH01

Paths under editorial-gear `experiments/.../premium-rd/ch01-unique/`

- **p002**: photoreal/3D fracturing chain. Visual language is not Candidate B cel/line.
- **p015**: empty collapsing architecture, no cast.
- **p039**: stone-dome monster (not the cylindrical Belljaw). Tableau staging; spear not clearly contacting.

Editorial-clean **p014**: Elian crouch under stone-dome golem; blade not contacting. Cleaner, still a posed illustration.

Observation: even inside Ember, monster design and medium (cel vs painterly vs 3D-chain) are not locked.

## Borrowed Down

`...\borrowed-down\chapters\ch01\lettered-panels\ch01-s01-p01.png` and `ch05\lettered-panels\ch05-s01-p01.png`

Strong print/etching identity. Lettering is a reserved blank paper rectangle plus a caption band; CH01 has a caption under the art; CH05’s reserved box is empty. Not vertical-scroll manhwa grammar. Distinctive world, weak sequential-comics craft.

809 PNGs, 85 exact duplicate files (measurement).

## The City Keeps Oaths

CH01 s01 p01 and CH05 s01 p01 are **landscape cinematic illustrations**, not 2:3 or 800px vertical cuts. Blue/gold prestige fantasy. Crowd extras in CH05 are generic. Owner-facing ledger in Ember docs records owner rejection of this visual result.

Many rasters ~856×599 (landscape).

## Lettering measurements (deterministic)

At 390px width, SVG user-unit conversion:

- Volume CH01–CH10: 10–16 of 24 panels per chapter have min font < 14px; none < 12px. Word totals 396–559/chapter.
- Premium original lettering: 32/52 panels min font < 12px at 390.
- Premium hybrid: 0/52 < 12px; 12/52 < 14px. Word count 302 vs original 343.

Observation: the editorial lettering pass improved phone type size. It did not change source-art causality.

## Review Goodhart (records, not pixels)

`generation-requests.json`: 225 rows; 224 `REVIEWED_PASS`; 1 landscape `HARD_FAIL_PRESERVED_DIAGNOSTIC`. Single reviewer `primary_agent_local_visual_inspection`. 11 unique notes, of which 10 are chapter-batch strings applied to 8 or 24 panels. `mark_art_review.py` writes the same note onto every pending row in a chapter.

Owner approval (`owner-approval.json`): pilot APPROVED; Candidate B “great selection; art and candidate B are amazing”; Phase B required better wording, less balloon occlusion, translucency, more system UI. Commercial clearance false.

## Answers to prompt visual questions

1. Strongest individual stills (p001, p004, p011, some portraits) can look like competent dark-fantasy illustration. Sequences fail first: attack/counter/reversal/aftermath is incomplete; camera does not hold geography; each frame is a new prompt.
2. Generic prestige-fantasy convergence is real on City and on later Ember painterly plates (teal/orange, fog, ruins, serious faces). Borrowed Down escapes that via print language but misses the manhwa target. Pilot Ember is closer to the target genre than City.
3. Character magnetism is weak relative to identity lock. Mira’s undercut is the most iconic silhouette; Elian is generic handsome salvager.
4. Action is assembled from poses. Contact is occasional, deformation rare, aftermath often a sit/stand tableau.
5. Phone readability: HUD/system type sits at ~13px at 390 (13.0–14.3 at 430). Dialogue balloons on p003 are large cloned boxes. Shipped reader tests 430px column width.

Hypothesis (to be scored independently by visual-a/visual-b): panels themselves are below the named ToG/SL craft bar except a minority of stills; sequence failure is the larger reader gap.
