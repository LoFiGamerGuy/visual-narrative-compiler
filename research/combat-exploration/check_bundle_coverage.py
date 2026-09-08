"""Check tracked/untracked source coverage before freezing the portable package."""
from pathlib import Path
import importlib.util,json,subprocess
R=Path(__file__).resolve().parents[2]
H=R/'research/combat-exploration/asset-bundle'
spec=importlib.util.spec_from_file_location('bundle',H/'bundle_assets.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
report=H/'coverage-preflight.json'
if not report.exists():report.write_text('{}\n')
rows=json.loads((R/'production/combat-exploration/candidates.json').read_text())['candidates']
manifest,sources=b.gather(R,len(rows))
raw=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard','--',*b.PREFIXES],cwd=R)
paths=sorted(set(p for p in raw.decode().split('\0') if p))
mapping={'research/combat-exploration/asset-bundle/START_HERE.cmd':'START_HERE.cmd'}
missing=[p for p in paths if mapping.get(p,p) not in sources]
out={'schema':'CombatExplorationBundleCoverage/1','pass':not missing,
     'source_files_checked':len(paths),'archive_files':len(sources),
     'missing':missing,'path_mapping':mapping,
     'scope':'All Git tracked and nonignored source files in the three new namespaces; all registered ignored native images and references separately verified by gather. ACTIVE_PIPELINE.md is a repository pointer outside package scope.',
     'source_paths':paths,'archive_paths':sorted(sources)}
report.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['source_paths','archive_paths']}))
raise SystemExit(0 if out['pass'] else 1)
