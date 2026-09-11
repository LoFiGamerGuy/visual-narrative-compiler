"""Read-only alias contract tests; never invokes the managed builder."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
modules=[]
for name,path in [('reader',ROOT/'research/encounter-lab/reader/build_reader.py'),('bundle',ROOT/'research/encounter-lab/asset-bundle/bundle_assets.py')]:
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);modules.append(module)
count=0
for module in modules:
    f=module.edit_provenance
    for record in [{'retry_of':'NG01-P','retry_reason':'observed defect'},{'source_attempt_id':'NG01-P','reason':'observed defect'},{'retry_of':'NG01-P','source_attempt_id':'NG01-P','retry_reason':'observed defect','reason':'observed defect'}]:
        assert f(record)==('NG01-P','observed defect');count+=1
    for records in [({'retry_of':'NG01-P','source_attempt_id':'BP01-P'},),({'retry_reason':'a','reason':'b'},),({'source_attempt_id':'NG01-P'},{'retry_of':'BP01-P'}),({'reason':'a'},{'retry_reason':'b'}),({'reason':''},)]:
        try:f(*records)
        except ValueError:count+=1
        else:raise AssertionError('Conflicting alias accepted')
    assert f({}, {})==(None,None);count+=1
rows=[]
for path in sorted((ROOT/'production/encounter-lab/calls').glob('*.json')):
    raw=path.read_bytes();call=json.loads(raw)
    if call.get('source_attempt_id'):
        normalized=modules[0].edit_provenance(call)
        assert normalized==modules[1].edit_provenance(call)
        assert path.read_bytes()==raw
        rows.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'normalized_source':normalized[0],'evidence_hash_recorded':bool(call.get('evidence_sha256'))})
print(json.dumps({'pass':True,'alias_checks':count,'actual_legacy_calls':rows,'original_call_bytes_unchanged':True},indent=2))
