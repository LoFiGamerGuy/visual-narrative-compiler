# Visual-direction selection gallery

Open `docs/research/visual-directions/index.html` locally. It loads local scripts and source rasters; no server, external font or network script is required. The twenty options stay in numerical order and have no author ranking.

- Tap a board to see the complete image; choose **Native pixels** to inspect the original resolution or open the PNG separately. Escape returns from the image to comparison before closing the comparison.
- Star directions for a shortlist. Character, Drawing style, World and Monster likes are separate, so the owner can combine preferences across options.
- Check **Compare** on two to four cards. The floating comparison tray stays accessible while scrolling. At narrow sizes, swipe the comparison horizontally; full boards are retained without cropping.
- **Notes & concept** keeps editable owner notes separate from the original concept brief and image provenance. Notes are limited to 4,000 characters per image.
- **Save / load → Export selections** downloads a portable JSON file. Import replaces the current browser selection only after validating all twenty exact source IDs/hashes, experiment, frozen brief hashes and dataset. Stale or tampered files are rejected without changing preferences. Preferences carry no production-approval field or action.

Browser storage is scoped to the experiment and exact dataset SHA. Rebuilding with changed selected pixels creates a separate storage scope; it never silently transfers preferences to different art. If browser storage is unavailable, the gallery says so and export still works. Keep an exported JSON for handoff or long-term retention; browser storage alone is not a durable archive.

The comparison lineup is temporary viewing state. Favorites, component likes and notes are the saved and exported preferences. The footer's **Study details** link opens the technical handoff; implementation details do not appear in the save/export success flow.

## Build and checks

From the new worktree root:

```sh
python research/visual-directions/build_gallery.py
python research/visual-directions/build_gallery.py --require-complete
node research/visual-directions/gallery_qa.mjs --require-complete
```

The builder only writes `docs/research/visual-directions/gallery-data.{js,json}`. It reads the frozen concepts/experiment and lead-owned candidate/selection manifests, validates PNG identity/dimensions/SHA and never modifies raster files. An unselected direction is visibly pending. The final-build flag fails unless all twenty have actual selected images.

The QA helper uses a fresh page on CDP9361 with a task-owned profile in `research/visual-directions/.scratch/gallery-browser/profile`. It does not run an older namespace's helper or write its scratch directory. Start the installed local Chromium binary with `--headless --no-sandbox --disable-dev-shm-usage --remote-debugging-port=9361 --allow-file-access-from-files --user-data-dir=<new-worktree>/research/visual-directions/.scratch/gallery-browser/profile`; supply the existing browser library directory through `LD_LIBRARY_PATH` if required by this environment. Override the port using `GALLERY_QA_PORT`.

QA covers actual rendered art at 390×844, 1024×768 and 1440×1000, fit/native zoom, nested Escape, two-to-four comparison, independent preferences, shortlist/family filters, actual browser JSON download and file-input import, reload persistence, source hashes, and atomic rejection of stale/tampered/acceptance-bearing payloads. It restores the original preference state at the end. Screenshots and example exports stay under the new scratch directory; the source-bound receipt is `gallery-browser-qa.json`.

## Realized display labels

The frozen prompt describes intended rendering. The card's brief remains available as such; a narrow builder overlay labels the observed result more accurately without rewriting those source documents. These descriptions follow lead and independent native-image observations; they are not owner preferences or acceptance decisions.

| Direction | Displayed style | Intended style preserved in brief |
| --- | --- | --- |
| 02 | Color adventure comic | Kinetic color manga |
| 05 | Painted industrial adventure | Retro cel animation |
| 07 | Geometric graphic illustration | Minimal flat graphic |
| 11 | Monochrome brush ink | Monochrome dry-brush manga |
| 12 | Stop-motion look | Handcrafted stop-motion |
| 20 | Pixel / voxel-inspired fantasy | Hand-pixel fantasy |

Direction 05 appears under Paint & wash. The visible 07 label makes no claim of strict flatness or absent gradients.

`overview.html` provides all twenty uncropped boards in two numbered, printable sheets. It links each board back to the interactive gallery. The optional `overview-01-10.png` and `overview-11-20.png` are browser screenshots of these actual boards, not newly generated images.
