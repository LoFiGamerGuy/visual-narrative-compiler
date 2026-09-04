from __future__ import annotations

import copy
import json
import unittest

from . import pipeline


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pipeline.compile_all()

    def test_complete_volume_contract(self) -> None:
        result = pipeline.validate_all(write=False)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["counts"], {"panels": 240, "prompts": 80, "letters": 240, "chapters": 10})

    def test_ids_are_unique_and_chronological(self) -> None:
        ids = []
        for cid in pipeline.CHAPTERS:
            doc = pipeline.load(pipeline.PROD / "chapters" / cid.lower() / "comic-panel-plans.json")
            self.assertEqual([p["display_order"] for p in doc["panels"]], list(range(1, 25)))
            ids.extend(p["panel_id"] for p in doc["panels"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_safe_zone_is_ltrb(self) -> None:
        doc = pipeline.load(pipeline.PROD / "chapters" / "ch01" / "comic-panel-plans.json")
        broken = copy.deepcopy(doc["panels"][0])
        broken["safe_zones"] = [[0.8, 0.2, 0.4, 0.5]]
        l, t, r, b = broken["safe_zones"][0]
        self.assertFalse(0 <= l < r <= 1 and 0 <= t < b <= 1)

    def test_prompts_are_text_free_and_hash_bound(self) -> None:
        doc = pipeline.load(pipeline.PROD / "chapters" / "ch10" / "prompt-manifest.json")
        for row in doc["prompts"]:
            self.assertEqual(pipeline.sha_text(row["prompt"]), row["prompt_sha256"])
            self.assertIn("no text", row["prompt"].lower())
            self.assertIn("empty caption rectangles", row["prompt"].lower())

    def test_irreversible_edges_chain(self) -> None:
        graph = pipeline.load(pipeline.PROD / "continuity-graph.json")["nodes"]
        carried = []
        for node in graph:
            self.assertEqual(node["requires"], carried)
            carried += [x for x in node["adds"] if x not in carried]
            self.assertEqual(node["state_after"], carried)

    def test_cross_medium_structures_absent(self) -> None:
        for cid in pipeline.CHAPTERS:
            doc = pipeline.load(pipeline.PROD / "chapters" / cid.lower() / "comic-panel-plans.json")
            self.assertIsNone(doc["animation_shot_plan"])
            self.assertIsNone(doc["e_conte"])
            self.assertTrue(all(p["animation_shot_plan"] is None and p["e_conte"] is None for p in doc["panels"]))


if __name__ == "__main__":
    unittest.main()
