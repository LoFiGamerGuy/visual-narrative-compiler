"""Check Chapter9 capture source/copy bindings; never claims visual inspection."""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image

BASE = Path(__file__).resolve().parent
CHECKS = BASE.parent
ROOT = CHECKS.parents[2]

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture_folder')
    parser.add_argument('--prior')
    args = parser.parse_args()
    folder = CHECKS / args.capture_folder
    output = folder / 'source-copy-check.json'
    assert not output.exists(), 'Preserve the earlier proof; use a new capture folder'
    baseline = read(BASE / 'baseline-hashes.json')
    for name, record in baseline['files'].items():
        assert sha(BASE / name) == record['sha256'], name
    before = read(BASE / 'reading-snapshot.json')
    current = read(folder / 'reading-snapshot.json')
    assert current['chapters'][:8] == before['chapters']
    assert current['comparisons'] == before['comparisons']
    assert not current['source_issues']
    old_overrides = read(BASE / 'lettering-overrides.json')['panels']
    overrides = read(ROOT / 'production/nightglass-longform/reader/lettering-overrides.json')['panels']
    assert all(overrides[k] == v for k, v in old_overrides.items())
    old_selected = read(BASE / 'selected.json')['selected']
    selected = read(ROOT / 'production/nightglass-longform/selected.json')['selected']
    assert all(selected[k] == v for k, v in old_selected.items())
    chapter = next(c for c in current['chapters'] if c['number'] == 9)
    assert chapter['total'] == 42
    authority = ROOT / chapter['script_path']
    assert sha(authority) == chapter['script_sha256']
    script = {p['id']: p for p in read(authority)['panels']}
    records = []
    for panel in chapter['panels']:
        if not panel['available']:
            continue
        assert panel['copy'] == script[panel['id']]['copy']
        assert [{k: line[k] for k in ('speaker', 'text')} for line in panel['lettering']] == panel['copy']
        assert sha(ROOT / panel['source']) == panel['sha256']
        crop = panel.get('crop')
        if crop:
            native = ROOT / crop['source_path']
            assert sha(native) == crop['source_sha256']
            with Image.open(native) as source, Image.open(ROOT / panel['source']) as derivative:
                assert list(source.size) == crop['source_dimensions']
                assert source.crop(crop['box_xyxy']).convert('RGB').tobytes() == derivative.convert('RGB').tobytes()
        records.append({'id': panel['id'], 'sha256': panel['sha256'], 'copy': panel['copy']})
    assert len(records) == chapter['available']
    prior_count = None
    if args.prior:
        prior = read(CHECKS / args.prior / 'reading-snapshot.json')
        prior_chapter = next(c for c in prior['chapters'] if c['number'] == 9)
        now = {p['id']: p for p in chapter['panels']}
        old = [p for p in prior_chapter['panels'] if p['available']]
        assert all(now[p['id']] == p for p in old)
        prior_count = len(old)
    output.write_text(json.dumps({
        'snapshot_sha256': sha(folder / 'reading-snapshot.json'),
        'script_sha256': sha(authority), 'available': len(records), 'total': 42,
        'previous351_and_comparisons_exact': True,
        'all_old_overrides_and_selected_records_exact': True,
        'prior_chapter9_records_exact_count': prior_count,
        'source_copy_records': records,
        'capture_hashes': {str(p.relative_to(folder)): sha(p) for p in sorted(folder.rglob('*')) if p.suffix in ('.png', '.jpg')},
        'visual_verdict': 'Not made by this source/copy checker; actual inspection must be recorded separately.'
    }, ensure_ascii=False, indent=2) + '\n')
    print('Source/copy preservation PASS:', len(records), '/ 42; no visual verdict')

if __name__ == '__main__':
    main()
