"""Build an isolated editable Chapter 1 review edition from frozen evidence."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'research/aws-editorial-20260910'

def main():
    packet = json.loads((AREA / 'packet.json').read_text())
    baseline = json.loads((AREA / 'reader/baseline.json').read_text())
    edits = json.loads((AREA / 'revision.json').read_text())
    revised = copy.deepcopy(baseline)
    revised_packet = copy.deepcopy(packet)
    for change in edits['changes']:
        panel = next(p for p in revised['panels'] if p['id'] == change['panel'])
        evidence = next(p for p in revised_packet['panels'] if p['id'] == change['panel'])
        if change['kind'] == 'replace_copy':
            for rows in (panel['copy'], panel['lettering'], evidence['reading_copy'], evidence['lettering']):
                found = [r for r in rows if r['text'] == change['before']]
                assert len(found) == 1, change['panel']
                found[0]['text'] = change['after']
        elif change['kind'] == 'add_caption':
            copy_row = {'speaker': 'Caption', 'text': change['after']}
            letter = dict(position='above', x=.05, y=0, w=.9, target=[.5,.5],
                          caption=True, card=False, no_tail=True, **copy_row)
            panel['copy'].insert(0, copy_row); panel['lettering'].insert(0, letter)
            evidence['reading_copy'].insert(0, copy_row); evidence['lettering'].insert(0, letter)
        elif change['kind'] == 'intent_only':
            assert evidence['action_intent'] == change['before']
            evidence['action_intent'] = change['after']; panel['alt'] = change['after']
        else:
            raise ValueError('Unknown edit')
        panel['lettering_reviewed'] = False
    for p in packet['panels']:
        assert hashlib.sha256((ROOT / p['image_path']).read_bytes()).hexdigest() == p['image_sha256']
    revised_packet['owner_acceptance'] = None
    revised_packet['revision_source'] = 'research/aws-editorial-20260910/revision.json'
    (AREA / 'revised-packet.json').write_text(json.dumps(revised_packet, indent=2)+'\n')
    (AREA / 'reader/revised.json').write_text(json.dumps(revised, indent=2)+'\n')
    (AREA / 'reader/data.js').write_text('window.REVIEW_EDITIONS='+json.dumps(dict(baseline=baseline,revised=revised),ensure_ascii=True)+';\n')
    print('Built 48-panel review edition; all original image hashes verified.')

if __name__ == '__main__': main()
