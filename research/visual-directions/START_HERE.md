# Twenty visual directions

**Latest owner feedback:** [Nine starred directions, explicit rejections and retained component exceptions](owner-shortlist.md) are recorded from the owner's subsequent chat messages. Starforge Nomad is separated as a possible future game-art direction. The generation-time reviews below remain historical evidence; the new preference record supplies the current shortlist and aesthetic constraints.

Open the [selection gallery](../../docs/research/visual-directions/index.html) or [all twenty at a glance](../../docs/research/visual-directions/overview.html). Each numbered board gives you a large portrait plus the same character in a world with a creature. These are independent original concepts made in response to your rejection of the previous art and characters.

You can choose a whole direction or mix elements. Use the star to shortlist a board; use **Character**, **Drawing style**, **World** and **Monster** independently; select two to four boards for comparison. Open an image to inspect native detail. Notes and choices save in that browser; **Save / load → Export selections** makes a file you can keep or share. You can also simply tell me the option numbers and what you like about each.

There is no author-selected winner. Some options deliberately sit in related medium families; the difference can lie in face/build, costume, acting, setting or creature as well as rendering. The gallery's style descriptions reflect actual outputs where they differ from their frozen briefs. These boards explore taste; they do not prove a consistent cast across a sequence.

## Native art and exact briefs

All original returned PNGs are preserved under `production/visual-directions/candidates/`, with separate close portrait and full-body/world areas inside each board. The [candidate manifest](../../production/visual-directions/candidates.json) lists every native file, dimensions and SHA-256. The [twenty concept briefs](../../production/visual-directions/concepts.json) and [experiment contract](../../production/visual-directions/experiment.json) remain frozen. Each exact tool prompt is in `production/visual-directions/prompts/NN-primary.txt`; each actual call receipt is under `calls/` in the same namespace.

Only the existing built-in image-generation tool was used for the new artwork. No previous cast image or third-party artwork was supplied as a reference. Direct paid spend is $0; underlying raster model/snapshot, seed, usage and billing allocation remain null. The study does not claim human-drawn production assets, commercial clearance or owner approval.

The [independent actual-art review](independent-review.md) records shared style families, visible ambiguities and differences between the intended and realized look. It does not rank your taste. [Measured results](results.json) record the finished counts, attempts and hashes.

## Open or rebuild locally

From this isolated checkout:

```bash
python research/visual-directions/build_gallery.py --require-complete
python -m http.server 9364 --bind 127.0.0.1
```

Then open `http://127.0.0.1:9364/docs/research/visual-directions/index.html`. The gallery also works directly from its local HTML file and has no external font, script or image dependency. It needs JavaScript for filtering, comparison and saving choices.

The native art remains local and ignored; Git contains prompts, code and evidence. A fresh clone needs the [separate asset bundle](asset-bundle/README.md). Its restoration verifies all file hashes and refuses to replace any differing existing file. The final bundle also includes the two overview image sheets.

## Delivery and preservation

The isolated branch is `autonomous/visual-directions-20260907-1230`, based on structural delivery `8212771a53447152ea457b9e67b6aa0fc9141ffb`. Prior work remains on its existing branches and worktrees; the owner's rejection changes the active direction, not the preservation policy. Previous art budgets remain closed.

The preservation scope is explicit in [the initial baseline](protected-initial.json): all twelve prior worktree HEADs and Git statuses, pre-existing refs, and byte hashes/file metadata for 1,105 files in the previous structural experiment, excluding scratch/runtime/bytecode and duplicate local archive copies. This is not a claim of hashing every machine or model-cache file. [The final comparison](protected-final.json) and [verification summary](verification.md) give the actual results.

After you choose a shortlist, the useful next step is to combine those preferences into a coherent design sheet and a small sequential test. No character, style or world is being forced into canon by this gallery.
