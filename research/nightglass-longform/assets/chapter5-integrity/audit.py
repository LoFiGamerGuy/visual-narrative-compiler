"""Read-only cross-worker Chapter5 preserved provenance and resource audit."""
import base64, collections, datetime, hashlib, json, re
from pathlib import Path
from PIL import Image

out = Path(__file__).resolve().parent
root = out.parents[3]
chapter = root/'production/nightglass-longform/chapter5'
def path(value):
    p = Path(value)
    return p if p.is_absolute() else root/p
def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
def read(p):
    return json.loads(p.read_text())
def relation(source, target, box):
    source_image = Image.open(source)
    expected = source_image.crop(box).convert('RGBA')
    actual = Image.open(target).convert('RGBA')
    assert expected.size == actual.size and expected.tobytes() == actual.tobytes(), str(target)

selected_path = root/'production/nightglass-longform/selected.json'
selection = read(selected_path)
selected = {k:v for k,v in selection['selected'].items() if k.startswith('N5-')}
assert set(selected) == {f'N5-{i:02d}' for i in range(1,43)}
selection_digest = hashlib.sha256(json.dumps(selected,sort_keys=True).encode()).hexdigest()
calls, native_paths, native_hashes, units = [], set(), {}, collections.defaultdict(list)
group_counts = collections.Counter()
canonical = sorted(p for p in chapter.glob('*/calls/*.json')
                   if not any(x in p.name for x in ('tool-return','return-metadata')))
ids = set()
for record_path in canonical:
    d = read(record_path)
    aid = d.get('id',d.get('attempt_id'))
    assert aid and aid not in ids and aid == record_path.stem
    ids.add(aid)
    assert d['status']=='returned' and d['tool']=='image_gen.imagegen'
    match = re.fullmatch(r'(N5-\d+(?:-\d+)?)-(P|R1)',aid)
    assert match, aid
    unit, phase = match.groups()
    units[unit].append(phase)
    group_counts[record_path.parents[1].name] += 1
    args_path = path(d['arguments_path']) if d.get('arguments_path') else record_path.parents[1]/'requests'/record_path.name
    args = read(args_path)
    if 'args' in d:
        assert args==d['args'], aid
    prompt_digest = hashlib.sha256(args['prompt'].encode()).hexdigest()
    if 'prompt_sha256' in d:
        assert d['prompt_sha256']==prompt_digest, aid
    prompt_file = args_path.with_suffix('.txt')
    prompt_text_note = 'no separate TXT; exact request JSON is canonical'
    if prompt_file.exists():
        text = prompt_file.read_text()
        if text == args['prompt']:
            prompt_text_note = 'TXT equals submitted prompt'
        else:
            assert text == args['prompt']+'\n', aid
            prompt_text_note = 'auxiliary TXT has one extra trailing LF; exact request JSON/embedded args/prompt SHA agree'
    assert set(args).issubset({'prompt','referenced_image_paths'})
    actual_refs = args.get('referenced_image_paths',[])
    assert len(actual_refs)==len(d['references']), aid
    references = []
    for supplied, ref in zip(actual_refs,d['references']):
        actual = path(supplied)
        assert actual==path(ref['path']) and actual.is_file()
        assert sha(actual)==ref['sha256'], (aid,ref['path'])
        references.append({'path':str(actual.relative_to(root)),'sha256':ref['sha256']})
    original = path(d.get('source_path',d.get('native_source')))
    native = path(d.get('path',d.get('native_copy')))
    expected_sha = d.get('sha256',d.get('native_sha256'))
    assert native.is_relative_to(chapter) and not native.is_symlink()
    assert sha(original)==sha(native)==expected_sha, aid
    native_paths.add(native)
    native_hashes[expected_sha]=aid
    raw_path = path(d['raw_return_path']) if d.get('raw_return_path') else record_path.with_name(aid+'-tool-return.json')
    raw = read(raw_path)
    assert base64.b64decode(raw['image_url'].split(',',1)[1])==native.read_bytes(), aid
    assert str(original) in raw['output_hint'], aid
    metadata = record_path.with_name(aid+'-return-metadata.json')
    if metadata.exists():
        m=read(metadata)
        assert raw['output_hint']==m['output_hint'] and len(raw['image_url'])==m['image_url_length'], aid
    for field in ('model_snapshot','seed','billing'):
        assert field in d and d[field] is None, (aid,field)
    assert d.get('owner_approval') is None, aid
    submitted = d.get('submitted_utc',d.get('submitted_at'))
    assert submitted, aid
    timing = 'recorded submitted timestamp; return timestamp, where present, is local preservation time'
    if aid=='N5-31-32-P':
        assert d['actual_invocation_start_utc'] is None and 'unknown' in d['submission_timing_note']
        timing = d['submission_timing_note']
    calls.append({'id':aid,'group':record_path.parents[1].name,'phase':phase,'status':'PASS',
                  'record':str(record_path.relative_to(root)),'record_sha256':sha(record_path),
                  'args_path':str(args_path.relative_to(root)),'args_sha256':sha(args_path),
                  'prompt_sha256':prompt_digest,'auxiliary_prompt_text':prompt_text_note,'references':references,
                  'native':str(native.relative_to(root)),'original':str(original),
                  'native_sha256':expected_sha,'raw_return_sha256':sha(raw_path),
                  'raw_auxiliary_metadata_checked':metadata.exists(),
                  'submitted_timestamp_field':submitted,'timing_qualification':timing,
                  'unknown_model_seed_billing_preserved':True})

assert len(calls)==37 and len(ids)==37
assert set(chapter.glob('*/candidates/*.png'))==native_paths
for unit, phases in units.items():
    assert phases.count('P')==1 and phases.count('R1')<=1, (unit,phases)
    if 'R1' in phases:
        primary=next(c for c in calls if c['id']==unit+'-P')
        repair=next(c for c in calls if c['id']==unit+'-R1')
        assert primary['native_sha256'] in {r['sha256'] for r in repair['references']}, unit

selected_checks=[]
for panel, d in sorted(selected.items()):
    target=path(d['path'])
    assert sha(target)==d['sha256'] and not target.is_symlink(), panel
    if d.get('crop'):
        c=d['crop'];source=path(c['source_path'])
        assert sha(source)==c['source_sha256'], panel
        if c.get('source_dimensions'):
            assert list(Image.open(source).size)==c['source_dimensions'], panel
        relation(source,target,c['box_xyxy'])
        operation='lossless crop'
    else:
        source=target
        operation='whole native/identical full frame'
    if panel=='N5-01':
        assert target==path(selection['selected']['N3-04']['path'])
        assert d['sha256']==selection['selected']['N3-04']['sha256']
        source_call='historical N3-04-05-P reuse; no Chapter5 call'
    else:
        assert sha(source) in native_hashes, panel
        source_call=native_hashes[sha(source)]
    if panel=='N5-09':
        assert source_call=='N5-08-P'
        operation='planned actual08 detail crop; no separate09 call'
    selected_checks.append({'panel':panel,'status':'PASS','path':str(target.relative_to(root)),
                            'sha256':d['sha256'],'source_call':source_call,'operation':operation})

references=[]
for records_path in sorted(chapter.glob('*/references/records.json')):
    for ref in read(records_path):
        target, source=path(ref['path']),path(ref['source_path'])
        assert sha(target)==ref['sha256'] and sha(source)==ref['source_sha256']
        if ref.get('source_dimensions'):
            assert list(Image.open(source).size)==ref['source_dimensions']
        relation(source,target,ref['box_xyxy'])
        references.append({'path':str(target.relative_to(root)),'sha256':ref['sha256'],'status':'PASS'})

# Original unaffected companion tiers remain selected from their primaries.
for panel, aid in {'N5-22':'N5-21-22-P','N5-24':'N5-23-24-P','N5-26':'N5-25-26-P','N5-35':'N5-35-36-P'}.items():
    assert next(x['source_call'] for x in selected_checks if x['panel']==panel)==aid
after={k:v for k,v in read(selected_path)['selected'].items() if k.startswith('N5-')}
assert selected==after, 'Chapter5 selected art records changed during audit'
primaries=sum(c['phase']=='P' for c in calls)
repairs=sum(c['phase']=='R1' for c in calls)
report={'status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'read-only canonical Chapter5 provenance/resource audit; no new visual or full-reading claim',
        'chapter5_calls_returned':len(calls),'primaries':primaries,'structural_repairs':repairs,
        'pending':0,'recorded_tool_failures':0,'finishes':0,'prior_lifetime_calls':179,
        'reconciled_lifetime_calls':179+len(calls),'remaining_initial320':320-179-len(calls),
        'remaining_chapter5_ceiling65':65-len(calls),'calls_by_group':dict(group_counts),
        'lead_helper_scope_calls':group_counts['lead'],'one_primary_max_one_R1_each_unit':True,
        'generation_units':dict(units),'canonical_candidates_no_orphans':True,
        'selected_chapter5_records_sha256':selection_digest,'selected_panel_count':len(selected),
        'selected_art_records_unchanged_during_audit':True,
        'reviewed_complete_at_audit_start':selection.get('reviewed_complete'),
        'selected_checks':selected_checks,'calls':calls,'reference_derivatives':references,
        'timing_exception':'N5-31-32-P preparation timestamp predates usage pause; actual invocation start unknown, explicit null retained; one real return counted.',
        'visual_reviews':'Separate actual native/phone/full-reader reviews; this audit does not replace them.',
        'writes':'Only this audit directory; no canonical call record, selection, reader, ZIP or extraction edited.'}
(out/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('status','chapter5_calls_returned','primaries','structural_repairs','reconciled_lifetime_calls','remaining_initial320','remaining_chapter5_ceiling65','selected_panel_count','calls_by_group')},indent=2))
print(f'Reference derivatives verified: {len(references)}')
