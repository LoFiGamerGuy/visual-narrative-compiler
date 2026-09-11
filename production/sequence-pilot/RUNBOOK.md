# Run the sequence pilot

This workspace is an original capability experiment, not Ember canon or a production-approved episode. The canonical plan is plan.json; plan.sha256 and the event ledger detect stale evidence. Generated images stay local and ignored. A fresh Git clone includes the code, plan, boards, prompts, observations and hashes, but requires the local art bundle to reproduce the illustrated reader. Unknown provider snapshot/seed cannot be recovered from prompts.

From the implementation checkout:

```bash
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot status
PYTHONPATH=src python -m unittest discover -s tests/sequence_pilot -v
```

Open docs/research/sequence-pilot/reader/index.html directly. Read the sequence, then switch to review to inspect source versus beat, exact copy, image-observed protected regions and geometry. Edit a draft and download its JSON. Reviewer labels in that file are self-reported; they do not establish independent human approval.

Copy the downloaded draft into this workspace, then import it with its actual filename:

```bash
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot import-draft edited-draft.json
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot export docs/research/sequence-pilot/reader-reviewed
```

Export requires a fresh output directory and preserves previous exports. It includes direct images, separate editable lettering, exact script copy and evidence status. Lettering geometry is normalized to the fixed390-by-panel-height canvas, including any letterboxing. Preserve the full image; cropping must not conceal a failed contact or extra actor.

Generation operations are explicit: reserve before a call, retain exact prompt and original-reference hashes, register the returned image, submit independently observed checks, then select a draft. A retry requires a logged hard failure and has a fixed one-retry ceiling. See ../../src/sequence_pilot/README.md for exact command/schema details. The current in-product tool is invoked by the agent; this package does not invent a paid provider adapter.

Never overwrite a candidate or amend a ledger event. Keep failed art and explanations. If the plan or selected image changes, old review/layout evidence is stale. Browser observations remain unverified notes until deliberately submitted through the separate observation command; imported text does not authenticate a human.

Production eligibility deliberately remains false in this pilot implementation. The frozen specification requires skilled human capacity, two independent human comprehension/rubric reviews, owner appeal, acceptable real correction labor and appropriate source rights. Those outcomes cannot be supplied by a CLI role flag.

Research and the precise implemented/unrun boundary are in ../../research/sequence-pilot/START_HERE.md. No existing branch, cache or earlier output should be cleaned or deleted as part of using this workflow.
