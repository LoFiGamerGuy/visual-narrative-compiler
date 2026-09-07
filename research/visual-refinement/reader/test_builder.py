"""Integrity boundaries in disposable fixtures under this reader's scratch folder."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('refinement_builder', HERE / 'build_reader.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuilderGuards(unittest.TestCase):
    def setUp(self):
        scratch = HERE / '.scratch/tests'
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.root = Path(self.temp.name)
        self.source = self.root / 'production/visual-refinement'
        self.source.mkdir(parents=True)
        self.out = self.root / 'docs/research/visual-refinement'
        source = builder.SOURCE
        self.plan = json.loads((source / 'comparison-plan.json').read_text())
        self.seq = json.loads((source / 'sequence-design/panel-plan.json').read_text())
        self.candidate = copy.deepcopy(json.loads((source / 'candidates.json').read_text())['candidates'][0])
        raw = (builder.ROOT / self.candidate['path']).read_bytes()
        (self.source / 'fixture.png').write_bytes(raw)
        self.candidate['path'] = 'production/visual-refinement/fixture.png'
        for style in self.plan['styles']:
            style['reference'] = {'path': self.candidate['path'], 'sha256': self.candidate['sha256']}
        self.selected = {self.candidate['id']: self.candidate['attempt_id']}
        self.write()
        self.patches = [patch.object(builder, 'ROOT', self.root), patch.object(builder, 'SOURCE', self.source), patch.object(builder, 'OUT', self.out)]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in self.patches: p.stop()
        self.temp.cleanup()

    def write(self):
        for name, value in [('comparison-plan.json', self.plan), ('sequence-plan.json', self.seq),
                            ('candidates.json', {'candidates': [self.candidate]}), ('selected.json', {'selected': self.selected})]:
            (self.source / name).write_text(json.dumps(value))

    def test_twenty_slots_but_only_actual_selected_pixels(self):
        data = builder.build_comparison()
        self.assertEqual(data['available_count'], 1)
        self.assertEqual(len(data['entries']), 20)
        self.assertEqual(sum(e['candidate'] is None for e in data['entries']), 19)
        self.assertIsNone(data['owner_approval'])

    def test_incomplete_final_does_not_publish(self):
        with self.assertRaises(ValueError): builder.build_comparison(True)
        self.assertFalse((self.out / 'comparison-data.js').exists())

    def test_bad_hash_preserves_previous_output(self):
        builder.build_comparison()
        before = (self.out / 'comparison-data.js').read_bytes()
        self.candidate['sha256'] = '0' * 64
        self.write()
        with self.assertRaises(ValueError): builder.build_comparison()
        self.assertEqual(before, (self.out / 'comparison-data.js').read_bytes())

    def test_bad_dimensions_rejected(self):
        self.candidate['width'] += 1
        self.write()
        with self.assertRaises(ValueError): builder.build_comparison()

    def test_namespace_escape_rejected(self):
        self.candidate['path'] = '/tmp/not-the-new-study.png'
        self.write()
        with self.assertRaises(ValueError): builder.build_comparison()

    def test_selected_identity_mismatch_rejected(self):
        self.selected = {'19-B': self.candidate['attempt_id']}
        self.write()
        with self.assertRaises(ValueError): builder.build_comparison()

    def test_excluded_style_cannot_enter_controlled_set(self):
        self.plan['styles'][0]['id'] = '20'
        self.write()
        with self.assertRaises(ValueError): builder.build_comparison()

    def test_source_reference_hash_is_checked(self):
        self.plan['styles'][0]['reference']['sha256'] = '0' * 64
        self.write()
        with self.assertRaises(ValueError): builder.build_comparison()

    def test_stale_ai_notes_rejected(self):
        (self.source / 'review-notes.json').write_text(json.dumps({'schema': 'RefinementReviewNotes/1', 'experiment_id': self.plan['experiment_id'],
            'entries': {self.candidate['id']: {'attempt_id': 'stale', 'sha256': self.candidate['sha256'], 'observations': ['An observation.']}}}))
        with self.assertRaises(ValueError): builder.build_comparison()

    def test_notes_do_not_reset_owner_dataset(self):
        before = builder.build_comparison()
        (self.source / 'review-notes.json').write_text(json.dumps({'schema': 'RefinementReviewNotes/1', 'experiment_id': self.plan['experiment_id'],
            'entries': {self.candidate['id']: {'attempt_id': self.candidate['attempt_id'], 'sha256': self.candidate['sha256'], 'observations': ['Source-bound observation.']}}}))
        after = builder.build_comparison()
        self.assertEqual(before['dataset_sha256'], after['dataset_sha256'])
        self.assertEqual(after['entries'][0]['ai_observations'], ['Source-bound observation.'])

    def test_no_invented_provisional_styles(self):
        data = builder.build_sequence()
        self.assertEqual(data['styles'], [])
        self.assertEqual(data['available_count'], 0)
        self.assertEqual(data['total_count'], 18)
        self.assertEqual(len(data['panels']), 6)
        with self.assertRaises(ValueError): builder.build_sequence(True)

    def test_exact_panel_order_required(self):
        self.seq['panels'].reverse()
        self.write()
        with self.assertRaises(ValueError): builder.build_sequence()

    def test_provisional_styles_must_be_from_shortlist(self):
        self.seq['provisional_styles'] = [{'id': i, 'title': i} for i in ['01', '03', '20']]
        self.write()
        with self.assertRaises(ValueError): builder.build_sequence()

    def repair_fixture(self, reason=True):
        retry = copy.deepcopy(self.candidate)
        retry['attempt_id'] = self.candidate['id'] + '-R'
        retry['retry_of'] = self.candidate['attempt_id']
        if reason: retry['retry_reason'] = 'Required interaction is missing.'
        (self.source / 'candidates.json').write_text(json.dumps({'candidates': [self.candidate, retry]}))
        (self.source / 'selected.json').write_text(json.dumps({'selected': {retry['id']: retry['attempt_id']}}))
        return retry

    def test_repair_retains_both_source_bindings(self):
        retry = self.repair_fixture()
        data = builder.build_comparison()
        repair = data['entries'][0]['repair']
        self.assertEqual(repair['before']['attempt_id'], self.candidate['attempt_id'])
        self.assertEqual(repair['after']['attempt_id'], retry['attempt_id'])
        self.assertEqual(repair['reason'], retry['retry_reason'])
        self.assertEqual(repair['record_sha256'], builder.sha(self.source / 'candidates.json'))

    def test_sequence_repair_uses_own_manifest_and_retains_primary(self):
        self.seq['provisional_styles'] = [{'id': i, 'title': i} for i in ['13', '18', '19']]
        self.write()
        primary = copy.deepcopy(self.candidate)
        primary.update(id='13-P01', attempt_id='13-P01-P')
        retry = {**primary, 'attempt_id': '13-P01-R', 'retry_of': '13-P01-P', 'retry_reason': 'Gate state is wrong.'}
        (self.source / 'sequence-candidates.json').write_text(json.dumps({'candidates': [primary, retry]}))
        (self.source / 'sequence-selected.json').write_text(json.dumps({'selected': {'13-P01': '13-P01-R'}}))
        data = builder.build_sequence()
        repair = data['entries'][0]['repair']
        self.assertEqual(repair['before']['attempt_id'], '13-P01-P')
        self.assertEqual(repair['after']['attempt_id'], '13-P01-R')
        self.assertEqual(repair['record_path'], 'production/visual-refinement/sequence-candidates.json')
        self.assertEqual(builder.build_comparison()['entries'][0]['candidate']['attempt_id'], self.candidate['attempt_id'])

    def sequence_notes_fixture(self):
        self.seq['provisional_styles'] = [{'id': i, 'title': i} for i in ['13', '18', '19']]
        self.write()
        rows = [{**self.candidate, 'id': f'{style}-P{panel:02}', 'attempt_id': f'{style}-P{panel:02}-P'} for style in ['13', '18', '19'] for panel in range(1, 7)]
        (self.source / 'sequence-candidates.json').write_text(json.dumps({'candidates': rows}))
        (self.source / 'sequence-selected.json').write_text(json.dumps({'selected': {c['id']: c['attempt_id'] for c in rows}}))
        notes = {'schema': 'RefinementReviewNotes/1', 'experiment_id': self.seq['experiment_id'], 'entries': {'13-P01': {'attempt_id': rows[0]['attempt_id'], 'sha256': rows[0]['sha256'], 'observations': ['Panel observation.']}}, 'routes': [{'style_id': '13', 'observations': ['Route observation.'], 'source_bindings': {c['id']: {'attempt_id': c['attempt_id'], 'sha256': c['sha256']} for c in rows[:6]}}]}
        return notes

    def test_sequence_notes_do_not_reset_owner_dataset(self):
        notes = self.sequence_notes_fixture()
        before = builder.build_sequence()['dataset_sha256']
        (self.source / 'sequence-review-notes.json').write_text(json.dumps(notes))
        after = builder.build_sequence()
        self.assertEqual(before, after['dataset_sha256'])
        self.assertEqual(after['route_observations'][0]['observations'], ['Route observation.'])
        self.assertEqual(after['entries'][0]['ai_observations'], ['Panel observation.'])

    def test_sequence_route_notes_require_all_six_exact_sources(self):
        notes = self.sequence_notes_fixture()
        notes['routes'][0]['source_bindings'].pop('13-P06')
        (self.source / 'sequence-review-notes.json').write_text(json.dumps(notes))
        with self.assertRaises(ValueError): builder.build_sequence()

    def test_sequence_panel_notes_reject_stale_retry(self):
        notes = self.sequence_notes_fixture()
        notes['entries']['13-P01']['attempt_id'] = '13-P01-old'
        (self.source / 'sequence-review-notes.json').write_text(json.dumps(notes))
        with self.assertRaises(ValueError): builder.build_sequence()

    def test_repair_requires_declared_reason(self):
        self.repair_fixture(False)
        with self.assertRaises(ValueError): builder.build_comparison()

    def test_repair_record_conflict_rejected(self):
        retry = self.repair_fixture()
        calls = self.source / 'calls'
        calls.mkdir()
        (calls / (retry['attempt_id'] + '.json')).write_text(json.dumps({'retry_of': self.candidate['attempt_id'], 'retry_reason': 'A conflicting reason.'}))
        with self.assertRaises(ValueError): builder.build_comparison()


if __name__ == '__main__':
    unittest.main()
