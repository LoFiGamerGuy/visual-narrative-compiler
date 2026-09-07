"""Confirm portable source coverage before freezing a delivery archive."""
from pathlib import Path
import importlib.util,json,subprocess
R=Path(__file__).resolve().parents[2];H=R/'research/world-components/asset-bundle'
spec=importlib.util.spec_from_file_location('wc_bundle',H/'bundle_assets.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
manifest,sources=m.gather(R,60)
covered={p.resolve() for p in sources.values()}
raw=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z','--',*m.PREFIXES],cwd=R)
files=[R/p.decode() for p in raw.split(b'\0') if p]
missing=[str(p.relative_to(R)) for p in files if p.resolve() not in covered]
assert not missing,missing
assert R/'research/world-components/reader/browser_qa.mjs' in covered
assert R/'research/world-components/reader/capture_repairs.mjs' in covered
assert R/'production/world-components/.gitignore' in covered
assert sources['START_HERE.cmd']==H/'START_HERE.cmd'
report={'schema':'WorldComponentBundleCoverage/1','pass':True,'tracked_and_untracked_source_files':len(files),'archive_files':len(sources),'missing_source_files':missing,'launcher_mapping':'research/world-components/asset-bundle/START_HERE.cmd -> archive root START_HERE.cmd','scope':list(m.PREFIXES),'excluded':'Runtime/scratch/local caches and original tool directories; root ACTIVE_PIPELINE.md is a repository index, not required by the standalone study. Archive receipts are emitted after freeze and accompany the ZIP.','portable_dependencies':'Reader builder resolves its root from parents[3]; archive helper from HERE.parents[2]. Relative source bindings are included. Preservation checker is original-workspace audit tooling, not required for portable viewing or rebuild.'}
(H/'coverage-preflight.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
