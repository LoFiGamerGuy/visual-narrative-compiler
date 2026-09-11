# Frozen reader QA expectations before generated outputs

Scope: browser functionality and actual layout; no automatic artwork acceptance or owner votes.

- Actual offline Chromium at 390×844, 1024×768 and 1440×1000. No external assets or horizontal page overflow. Full native image aspect ratios, no cropping. Phone captures bind displayed source, call, dataset, reader code and screenshot hashes.
- Twenty-four final selected artworks must decode. Pending states explicitly show unavailable art and disable responses. Image load failure also disables new responses.
- Browse exact category, scale, subject and story-path values. Shared-subject comparison uses full images and makes no recognition claim. Compare two or three scenes; stack on phone. Native zoom and keyboard Escape work.
- All retained attempts remain accessible with attempt IDs, native sources and call provenance. Texture and structural edits remain distinguishable through their exact attempt and correction reason.
- All new ratings, comfort and notes begin blank; shortlist starts false. Nine dimensions remain independent, including recognition and texture. N/A differs from null. Earlier preferences remain separately read-only, with an exact-byte download.
- Export/import roundtrip preserves choices. Stale dataset, plan, experiment, source attempt/hash/order, invalid ratings, extra assertions and incomplete choices reject atomically. A changed dataset must not silently inherit prior votes.
- AI observations are source-bound, collapsed and separate from owner responses. Report links and local native/reference links resolve. No generated semantic acceptance is inferred from geometry checks.
- Final selected phone captures cover all24 artworks. Earlier captures remain tied to their original dataset and are not relabeled after a source change.
