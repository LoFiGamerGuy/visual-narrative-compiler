import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from . import pipeline


class PipelineTests(unittest.TestCase):
    def test_sha_is_stable(self):
        self.assertEqual(pipeline.sha_text("down"), pipeline.sha_text("down"))

    def test_safe_zone_semantics(self):
        z = [0.05, 0.06, 0.4, 0.2]
        self.assertLess(z[0], z[2])
        self.assertLess(z[1], z[3])

    def test_contact_dimensions(self):
        images = [Image.new("RGB", (64, 32), "teal") for _ in range(6)]
        sheet = pipeline.make_contact(images, 3, 2, 40, "TEST")
        self.assertEqual(sheet.width, 3 * 40 + 4 * 12)

    def test_volume_source_is_exact(self):
        chapters = pipeline.source_chapters()
        self.assertEqual([c["id"] for c in chapters], pipeline.CHAPTERS)
        self.assertTrue(all(len(c["sequences"]) == 6 for c in chapters))


if __name__ == "__main__":
    unittest.main()
