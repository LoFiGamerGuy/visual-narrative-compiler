#!/usr/bin/env python3
"""Final NR package coverage preflight; does not create an archive."""
from pathlib import Path
import argparse,importlib.util,json,subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('nightglass_bundle',HERE/'bundle_assets.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-art',type=int,required=True)
    args=parser.parse_args()
    report=HERE/'coverage-preflight.json'
    if not report.exists():report.write_text('{}\n')
    manifest,sources=b.gather(ROOT,args.expected_art)
    raw=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard','--',*b.PREFIXES,'ACTIVE_PIPELINE.md'],cwd=ROOT)
    paths=sorted(set(p for p in raw.decode().split('\0') if p))
    base='research/nightglass-refinement/asset-bundle/'
    mapping={base+'START_HERE.cmd':'START_HERE.cmd'}
    external={base+n for n in b.EXTERNAL_RECEIPTS}
    missing=[p for p in paths if p not in external and mapping.get(p,p) not in sources]
    out={'schema':'NightglassBundleCoverage/1','pass':not missing,'source_files_checked':len(paths),'archive_files':len(sources),
         'missing':missing,'path_mapping':mapping,'external_receipt_exceptions':sorted(external),
         'scope':'All tracked/nonignored files in the three NR namespaces plus ACTIVE_PIPELINE.md. Registered ignored new attempts, nine anchors, eighteen CE sources and twenty-four previous WC sources verified separately by gather. Runtime/local content excluded intentionally.',
         'expected_native_count':args.expected_art,'source_paths':paths,'archive_paths':sorted(sources)}
    report.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('source_paths','archive_paths')},indent=2))
    raise SystemExit(0 if out['pass'] else 1)
if __name__=='__main__':main()
