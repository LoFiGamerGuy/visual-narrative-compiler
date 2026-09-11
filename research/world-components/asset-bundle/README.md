# Portable world component study

Extract the ZIP and open START_HERE.cmd on Windows, or docs/world-components/index.html in a browser. Native PNGs, nine original anchors, exact prompts, call receipts, independent review and reader source are included. The archive does not carry browser-saved owner choices; export those from the reader separately.

The builder can rebuild all source bindings with `python3 research/world-components/reader/build_reader.py --require-complete`. Generation uses the built-in image tool and is not automatically replayed by this script. Metadata fields not returned by the tool remain unknown.

The Python archive helper verifies source hashes and restores only missing or byte-identical files, refusing differing existing content. Use its --help for commands. Local archives, scratch/browser profiles, previous experiment namespaces and original tool-return directories are excluded; all new native copies and supplied references are included.

The local delivery ZIP is `local/final-v1/world-components-portable.zip`, with SHA256 and byte count in `archive-receipt.json` alongside it. The extracted archive deliberately does not contain another copy of itself or its post-freeze receipts. Share the ZIP as a file; local Windows paths are not public web links.
