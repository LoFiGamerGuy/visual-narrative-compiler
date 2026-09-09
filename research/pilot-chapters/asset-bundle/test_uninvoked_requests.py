"""Focused regression for queue guards; fixtures contain no actual artwork."""
import json
import tempfile
from pathlib import Path
from bundle_assets import transport_ledger, withheld_event

BASE={'id':'FL04','attempt_id':'FL04-P','status':'withheld-before-tool-call','reason':'Frozen input conflicts with editorial state; held before invocation.','tool_invoked':False,'returned_artwork':None}

def run():
    checks=[]
    assert withheld_event(BASE);checks.append('explicit guard recognized')
    assert not withheld_event({'id':'FL04','attempt_id':'FL04-P','status':'reviewable-unaccepted'});checks.append('ordinary call not silently excluded')
    for label,change in [('claimed invocation',{'tool_invoked':True}),('artwork',{'returned_artwork':'image.png'}),('output path',{'output_path':'image.png'}),('missing reason',{'reason':''}),('unknown ID',{'id':'BAD'}),('conflicting status',{'status':'success'})]:
        try:withheld_event(dict(BASE,**change))
        except ValueError:checks.append(label+' rejected')
        else:raise AssertionError(label)
    with tempfile.TemporaryDirectory(prefix='uninvoked-',dir=Path(__file__).parent/'local') as t:
        root=Path(t);calls=root/'production/pilot-chapters/calls';calls.mkdir(parents=True);(calls/'FL04-P.json').write_text(json.dumps(BASE))
        ledger=transport_ledger(root,{},137,True)
        assert ledger['invocation_count']==0 and ledger['native_artwork_count']==0 and len(ledger['administrative_uninvoked_requests'])==1;checks.append('guard contributes zero calls and zero natives')
        try:transport_ledger(root,{'FL04-P':{}},137,True)
        except ValueError:checks.append('guard cannot bind registered artwork')
        else:raise AssertionError('guard/native conflict')
    return {'pass':True,'checks':checks}

if __name__=='__main__':print(json.dumps(run(),indent=2))
