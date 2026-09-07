# Final reader QA

The final reader displays 20 comparison boards and 18 sequence panels. All 10 retained-primary / selected-retry pairs remain reviewable with exact attempt IDs, PNG hashes and hashed call records. Earlier primaries remain intact. Sequence selection is six R plus twelve P. No owner ratings or approval were entered.

The complete art/UI run passed at 390×844, 1024×768 and 1440×1000: full natural image aspect ratios, no horizontal overflow, desktop comparison rows and phone stacks, native image views, keyboard controls, exact frozen dialogue order, source hashes, and explicit missing-file handling. Both comparison and sequence exports passed actual file download/import/reload; ten malformed/stale cases were rejected atomically for each. Temporary test choices were restored. Read story hides repeated panel tools; Review panels reveals them without changing choices. Fresh pages default to reading.

Actual final captures inspected include every sequence repair pair across the phone/tablet/desktop set. The long P04 phone image remains complete and its source links can be reached by scrolling. Wrapped hashes stay within the dialog; the close button remains accessible. Continuous reading preserves complete images and the exact below-art lettering. Any cropping or continuity defect inside a generated PNG remains a source-art issue, not a reader crop. Independent scene/art reviews establish the limits of the images; this UI pass does not establish mechanical continuity or owner comfort.

After final source-bound observations arrived, the focused notes check passed all three sizes: three route disclosures start collapsed, route text and all eighteen panel observations exactly match source data, panel notes appear only in Review panels, choices remain unchanged, and both footer report links resolve on both pages. Actual expanded-note captures were inspected: text is readable and wraps naturally. The disclosures identify AI observations separately from owner responses. No score, owner winner or production acceptance is inferred.

Evidence:
- `browser-qa.json`: complete 20+18 art/UI and repair-pair receipt.
- `notes-browser-qa.json`: final note-only integration and current code/data hashes.
- `primary-browser-qa.json`: preserved complete primary baseline.
- `repair-browser-qa.json`: preserved comparison repair integration.
- `reading-toggle-qa.json`: focused real-choice toggle/reload/restoration check.
- `test_builder.py`: 20 passing integrity tests, including stale notes, incomplete route bindings, separate sequence repair provenance, and unchanged owner dataset identity after adding observations.

Final dataset SHA-256:
- Comparison: `b49eb70d68d7790aae6b3c0412df1df8359c45d665390f4663eb6b47b294783f`
- Sequence: `a5c96d8028d0b92d7f87682965f5533d0ed468ee7e197de60bfdc7d85ea6650e`
- Comparison review notes: `923cd5076b91a796d4b499aae2ffda265a697d96ad5e295c9553902c250b0bcf`
- Sequence review notes: `6856a42e1d6d73313c1b895b13406ef3ee1199cb6f1cf8a52f476ca8ed0525c7`

Reader code and generated UI are frozen for packaging. The task-owned browser remains available for a restored portable-reader spot check. No old namespace was changed by this reader task.
