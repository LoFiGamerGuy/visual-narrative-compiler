# Repair-view integration inspection

2026-09-07. Dataset `b49eb70d68d7790aae6b3c0412df1df8359c45d665390f4663eb6b47b294783f`; selected comparison boards 20/20, sequence art 0/18. This is progressive UI evidence, not final sequence QA or owner approval.

The actual retained-primary and selected-retry PNGs for 18-A, 18-B, 19-A and 19-B loaded at 390×844, 1024×768 and 1440×1000. Phone pairs stack with full image width; tablet and desktop pairs share a row. Inspection of actual captures confirms readable titles, attempt IDs, wrapped image hashes and native links. The close button remains available while scrolling. The targeted failure and changed reference conditioning appear above the pair, explicitly identifying that the inputs differ. No owner response controls appear in this evidence view.

The images are displayed at their complete natural aspect ratio; the reader does not add cropping. Any cropping inside a generated source board remains part of that source. No artwork was edited for this integration.

The updated sequence page displays the three provisional style tabs and six ordered missing-art cards per style. Frozen dialogue appears below each placeholder; no image is substituted and response controls remain disabled for missing candidates.

`repair-browser-qa.json` retains the exact automated receipt, including source/record hashes, all four pairs at all three sizes, source-bound preference behavior, keyboard controls, atomic invalid-import rejection, real export/import/reload, and explicit file-failure behavior. Actual captures are under `.scratch/browser/repair-*.png` and `sequence-13-390.png`. The final receipt will be rerun once sequence art is complete.
