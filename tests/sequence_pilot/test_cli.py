import json
import copy
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from sequence_pilot.cli import PilotError, Workspace, digest, image_info


def png():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"\0" + b"\xff\0\0" * 2 + b"\0" + b"\0\xff\0" * 2)) + chunk(b"IEND", b"")


class PilotTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.plan = {"schema": "NeutralPilotPlan/2", "title": "Test", "panels": [{"panel": 1, "beat": "Staff contacts foot", "copy": []}, {"panel": 2, "beat": "Aftermath", "copy": []}], "routes": [{"id": "A"}, {"id": "B"}]}
        self.write("plan.json", self.plan)
        (self.root / "prompt.txt").write_text("Original adults, staff visibly contacts forefoot.\n")
        (self.root / "source.png").write_bytes(png())

    def tearDown(self):
        self.temp.cleanup()

    def write(self, path, value):
        (self.root / path).write_text(json.dumps(value))

    def candidate(self):
        ws = Workspace(self.root)
        a = ws.reserve("P01", "A", "prompt.txt")
        return ws, ws.register(a["id"], "source.png")

    def observation(self, ws, c, verdict="pass"):
        return {"candidate_id": c["id"], "image_sha256": c["sha256"], "plan_sha256": ws.plan_sha, "reviewer": "independent test reviewer", "checks": {key: {"verdict": verdict, "observation": "Observed in pixels"} for key in ("actors", "event", "contact", "props", "state")}}

    def test_wrong_event_with_valid_hash_cannot_pass(self):
        ws, c = self.candidate()
        obs = self.observation(ws, c)
        obs["checks"]["event"] = {"verdict": "fail", "observation": "Figures stand apart; no staff contact"}
        self.write("observation.json", obs)
        ws.observe(c["id"], "observation.json")
        ws.select("P01", c["id"])
        result = Workspace(self.root).status()
        self.assertFalse(result["integrity_failures"])
        self.assertTrue(result["semantic_defects"])
        self.assertFalse(result["production_eligible"])

    def test_unknown_semantics_never_pass(self):
        ws, c = self.candidate()
        ws.select("P01", c["id"])
        self.assertIn("P01: no independent observations", ws.status()["not_assessed"])
        self.assertFalse(ws.status()["production_eligible"])

    def test_pass_observations_do_not_manufacture_owner_approval(self):
        ws, c = self.candidate()
        self.write("observation.json", self.observation(ws, c))
        ws.observe(c["id"], "observation.json")
        ws.select("P01", c["id"])
        self.assertFalse(ws.status()["production_eligible"])
        self.assertTrue(ws.status()["pending_human_owner"])

    def test_plan_change_blocks_mutation_and_export(self):
        ws, c = self.candidate()
        self.plan["panels"][0]["beat"] = "Different event"
        self.write("plan.json", self.plan)
        stale = Workspace(self.root)
        self.assertTrue(stale.status()["integrity_failures"])
        with self.assertRaises(PilotError):
            stale.select("P01", c["id"])
        with self.assertRaises(PilotError):
            stale.export("never-export")

    def test_stale_observation_image_and_plan_rejected(self):
        ws, c = self.candidate()
        for key in ("image_sha256", "plan_sha256"):
            obs = self.observation(ws, c)
            obs[key] = "0" * 64
            self.write("observation.json", obs)
            with self.assertRaises(PilotError):
                ws.observe(c["id"], "observation.json")

    def test_failed_primary_preserved_and_retry_exhausts(self):
        ws = Workspace(self.root)
        a = ws.reserve("P01", "A", "prompt.txt")
        with self.assertRaises(PilotError):
            ws.reserve("P01", "A", "prompt.txt", retry_of=a["id"], hard_failure="No output")
        ws.fail(a["id"], "Generation returned no output")
        b = ws.reserve("P01", "A", "prompt.txt", retry_of=a["id"], hard_failure="No output")
        ws.fail(b["id"], "Retry still fails")
        for retry in (None, a["id"], b["id"]):
            with self.assertRaises(PilotError):
                ws.reserve("P01", "A", "prompt.txt", retry_of=retry, hard_failure="No output" if retry else None)
        loaded = Workspace(self.root)
        self.assertEqual(2, len(loaded.records("reserved")))
        self.assertEqual(2, len(loaded.records("failed")))

    def test_registered_primary_can_fail_then_retry_without_overwrite(self):
        ws, c = self.candidate()
        original = (self.root / c["path"]).read_bytes()
        ws.fail(c["attempt_id"], "Wrong event")
        ws.reserve("P01", "A", "prompt.txt", retry_of=c["attempt_id"], hard_failure="Fix staff contact")
        self.assertEqual(original, (self.root / c["path"]).read_bytes())
        with self.assertRaises(PilotError):
            ws.register(c["attempt_id"], "source.png")

    def test_unsafe_paths_and_symlinks_rejected(self):
        ws = Workspace(self.root)
        for path in ("../escape.txt", "/etc/passwd"):
            with self.assertRaises(PilotError):
                ws.reserve("P01", "A", path)
        (self.root / "link.txt").symlink_to(self.root / "prompt.txt")
        with self.assertRaises(PilotError):
            ws.reserve("P01", "A", "link.txt")

    def test_reference_provenance_is_required_and_frozen(self):
        (self.root / "refs").mkdir()
        (self.root / "refs/ref.png").write_bytes(png())
        ref = {"id": "original", "path": "refs/ref.png", "sha256": digest(png()), "original": False, "rights_status": "original-created-for-pilot"}
        self.write("refs/manifest.json", {"references": [ref]})
        ws = Workspace(self.root)
        with self.assertRaises(PilotError):
            ws.reserve("P01", "A", "prompt.txt")
        ref["original"] = True
        self.write("refs/manifest.json", {"references": [ref]})
        ws.reserve("P01", "A", "prompt.txt")
        (self.root / "refs/ref.png").write_bytes(b"changed")
        self.assertTrue(Workspace(self.root).status()["integrity_failures"])

    def test_candidate_image_tamper_detected(self):
        ws, c = self.candidate()
        (self.root / c["path"]).write_bytes(b"changed")
        broken = Workspace(self.root)
        self.assertTrue(broken.status()["integrity_failures"])
        with self.assertRaises(PilotError):
            broken.select("P01", c["id"])

    def test_chain_tamper_and_truncation_detected(self):
        ws, _ = self.candidate()
        path = self.root / "events.jsonl"
        original = path.read_text()
        path.write_text(original.replace("Original adults", "Changed adults"))
        self.assertTrue(Workspace(self.root).status()["integrity_failures"])
        path.write_text(original.rstrip("\n"))
        self.assertTrue(Workspace(self.root).status()["integrity_failures"])

    def test_not_png_and_corrupt_png_rejected(self):
        self.assertEqual(2, image_info(png())["width"])
        for bad in (b"not an image", png()[:32], png()[:-1] + b"x"):
            with self.assertRaises(PilotError):
                image_info(bad)

    def test_cannot_select_other_panels_candidate(self):
        ws, c = self.candidate()
        with self.assertRaises(PilotError):
            ws.select("P02", c["id"])

    def test_frozen_marker_protects_plan_before_first_attempt(self):
        (self.root / "plan.sha256").write_text("0" * 64 + "\n")
        ws = Workspace(self.root)
        self.assertTrue(ws.status()["integrity_failures"])
        with self.assertRaises(PilotError):
            ws.reserve("P01", "A", "prompt.txt")

    def test_existing_object_rechecks_changed_material(self):
        ws, c = self.candidate()
        (self.root / c["path"]).write_bytes(b"changed after loading")
        with self.assertRaises(PilotError):
            ws.select("P01", c["id"])

    def test_export_preserves_copy_hashes_missing_panels_and_no_approval(self):
        self.plan["panels"][0]["copy"] = [{"kind": "dialogue", "text": "Exact <copy> — unchanged."}]
        self.write("plan.json", self.plan)
        ws, c = self.candidate()
        ws.select("P01", c["id"])
        dest = self.root / "export"
        with patch("sequence_pilot.cli.Path.cwd", return_value=self.root):
            ws.export(dest)
            with self.assertRaises(PilotError):
                ws.export(dest)
        data = json.loads((dest / "review-data.json").read_text())
        self.assertEqual(self.plan["panels"][0]["copy"], data["panels"][0]["copy"])
        self.assertEqual(c["sha256"], digest((dest / data["panels"][0]["candidate"]["src"]).read_bytes()))
        self.assertIsNone(data["panels"][1]["candidate"])
        self.assertFalse(data["status"]["production_eligible"])
        self.assertIn("window.SEQUENCE_REVIEW_DATA", (dest / "review-data.js").read_text())
        self.assertNotIn("<copy>", (dest / "review-data.js").read_text())

    def draft(self, ws, c):
        return {"schema": "SequenceReviewDraft/1", "plan_sha256": ws.plan_sha,
                "status": "draft-unaccepted", "reviewer_labels_verified": False, "panels": [
                    {"id": "P01", "candidate_id": c["id"], "candidate_sha256": c["sha256"],
                     "lettering": [{"id": "l1", "text": "Wait.", "kind": "dialogue", "speaker": "NERA", "shape": "rounded",
                                    "x": .1, "y": .1, "w": .4, "h": .2, "font_size": 16, "tail": {"x": .4, "y": .5}}],
                     "protected_regions": [{"id": "r1", "label": "Observed face", "x": .6, "y": .2, "w": .2, "h": .2}],
                     "observations": [{"text": "A browser claim of success", "reviewer": "Self-described reviewer", "reviewer_kind": "human", "flag": "positive_evidence"}]},
                    {"id": "P02", "candidate_id": None, "candidate_sha256": None, "lettering": [], "protected_regions": [], "observations": []}]}

    def test_import_roundtrip_retains_layout_but_never_promotes_notes(self):
        self.plan["panels"][0]["copy"] = ["NERA: Wait."]
        self.write("plan.json", self.plan)
        ws, c = self.candidate()
        ws.select("P01", c["id"])
        draft = self.draft(ws, c)
        self.write("draft.json", draft)
        ws.import_draft("draft.json")
        loaded = Workspace(self.root)
        self.assertEqual(1, len(loaded.records("draft_imported")))
        self.assertEqual([], loaded.records("observed"))
        self.assertEqual([], loaded.status()["copy_drift"])
        self.assertIn("P01: no independent observations", loaded.status()["not_assessed"])
        with patch("sequence_pilot.cli.Path.cwd", return_value=self.root):
            loaded.export(self.root / "roundtrip")
        data = json.loads((self.root / "roundtrip/review-data.json").read_text())
        self.assertEqual(draft["panels"][0]["lettering"], data["panels"][0]["lettering"])
        self.assertEqual(draft["panels"][0]["protected_regions"], data["panels"][0]["protected_regions"])
        self.assertEqual("unspecified", data["panels"][0]["observations"][0]["reviewer_kind"])
        self.assertFalse(data["status"]["production_eligible"])

    def test_import_rejects_stale_candidate_and_drops_layout_after_selection_change(self):
        ws, c = self.candidate()
        ws.select("P01", c["id"])
        self.write("draft.json", self.draft(ws, c))
        ws.import_draft("draft.json")
        a = ws.reserve("P01", "B", "prompt.txt")
        other = ws.register(a["id"], "source.png")  # Same image bytes, distinct candidate ID.
        ws.select("P01", other["id"])
        with self.assertRaises(PilotError):
            ws.import_draft("draft.json")
        self.assertNotIn("P01", ws.layouts()[0])
        self.assertTrue(ws.status()["draft_layout_issues"])

    def test_import_rejects_unsafe_geometry_bad_sets_and_acceptance_claims_atomically(self):
        ws, c = self.candidate()
        ws.select("P01", c["id"])
        original = self.draft(ws, c)
        variants = []
        for bad in (float("nan"), float("inf"), -.1, 2, 10 ** 1000, True, "0.1"):
            d = copy.deepcopy(original); d["panels"][0]["lettering"][0]["x"] = bad; variants.append(d)
        d = copy.deepcopy(original); d["panels"].pop(); variants.append(d)
        d = copy.deepcopy(original); d["panels"][1]["id"] = "P01"; variants.append(d)
        d = copy.deepcopy(original); d["plan_sha256"] = "0" * 64; variants.append(d)
        d = copy.deepcopy(original); d["production_eligible"] = True; variants.append(d)
        d = copy.deepcopy(original); d["reviewer_labels_verified"] = True; variants.append(d)
        d = copy.deepcopy(original); d["panels"][0]["lettering"][0]["text"] = "x" * 4001; variants.append(d)
        for d in variants:
            self.write("draft.json", d)
            with self.assertRaises(PilotError):
                ws.import_draft("draft.json")
        with self.assertRaises(PilotError):
            ws.import_draft("../outside.json")
        self.assertEqual([], ws.records("draft_imported"))

    def test_draft_copy_drift_does_not_rewrite_frozen_script(self):
        ws, c = self.candidate()
        ws.select("P01", c["id"])
        self.write("draft.json", self.draft(ws, c))
        ws.import_draft("draft.json")
        self.assertTrue(ws.status()["copy_drift"])
        self.assertEqual([], Workspace(self.root).panels["P01"]["copy"])

    def test_unbound_lettering_file_is_ignored_with_visible_blocker(self):
        ws, c = self.candidate()
        ws.select("P01", c["id"])
        self.write("lettering.json", {"P01": self.draft(ws, c)["panels"][0]})
        self.assertEqual({}, ws.layouts()[0])
        self.assertTrue(ws.status()["draft_layout_issues"])


if __name__ == "__main__":
    unittest.main()
