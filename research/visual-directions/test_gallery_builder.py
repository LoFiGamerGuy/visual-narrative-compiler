"""Source-bound gallery failure checks in temporary new-namespace fixtures."""
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
spec = importlib.util.spec_from_file_location('gallery_builder', HERE / 'build_gallery.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class GallerySourceChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / 'production/visual-directions'
        self.source.mkdir(parents=True)
        self.out = self.root / 'docs/research/visual-directions'
        real = builder.SOURCE
        for name in ['concepts.json', 'experiment.json']:
            (self.source / name).write_bytes((real / name).read_bytes())
        self.candidate = copy.deepcopy(json.loads((real / 'candidates.json').read_text())['candidates'][0])
        png = builder.ROOT / self.candidate['path']
        self.candidate['path'] = 'production/visual-directions/test-source.png'
        (self.source / 'test-source.png').write_bytes(png.read_bytes())
        self.selected = {self.candidate['id']: self.candidate['attempt_id']}
        self.write_manifests()
        self.patches = [patch.object(builder, 'ROOT', self.root), patch.object(builder, 'SOURCE', self.source), patch.object(builder, 'OUT', self.out)]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in self.patches: p.stop()
        self.tmp.cleanup()

    def write_manifests(self):
        (self.source / 'candidates.json').write_text(json.dumps({'candidates': [self.candidate]}))
        (self.source / 'selected.json').write_text(json.dumps({'selected': self.selected}))

    def build(self, complete=False):
        with contextlib.redirect_stdout(io.StringIO()):
            return builder.build(complete)

    def test_pending_slots_have_no_fake_candidate(self):
        result = self.build()
        self.assertEqual(result['available_count'], 1)
        self.assertEqual(sum(c['candidate'] is None for c in result['cards']), 19)
        self.assertFalse(result['production_accepted'])

    def test_final_rejects_incomplete_without_publishing(self):
        with self.assertRaises(ValueError): self.build(True)
        self.assertFalse((self.out / 'gallery-data.js').exists())

    def test_wrong_hash_rejected(self):
        self.candidate['sha256'] = '0' * 64
        self.write_manifests()
        with self.assertRaises(ValueError): self.build()

    def test_wrong_dimensions_rejected(self):
        self.candidate['width'] += 1
        self.write_manifests()
        with self.assertRaises(ValueError): self.build()

    def test_selected_attempt_must_match_direction(self):
        self.selected = {'20': self.candidate['attempt_id']}
        self.write_manifests()
        with self.assertRaises(ValueError): self.build()

    def test_path_cannot_escape_new_production_namespace(self):
        self.candidate['path'] = '/tmp/old-source.png'
        self.write_manifests()
        with self.assertRaises(ValueError): self.build()

    def test_unknown_selected_attempt_rejected(self):
        self.selected = {'01': 'nonexistent'}
        self.write_manifests()
        with self.assertRaises(ValueError): self.build()

    def test_nonreviewable_status_rejected(self):
        self.candidate['status'] = 'accepted'
        self.write_manifests()
        with self.assertRaises(ValueError): self.build()


if __name__ == '__main__':
    unittest.main()
