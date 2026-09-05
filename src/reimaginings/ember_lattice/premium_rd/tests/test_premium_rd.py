from __future__ import annotations

import json
import copy
import tempfile
import unittest
from pathlib import Path

from ..audit import audit_bundle, audit_links
from ..author import author_template
from ..core import read_json, sha256_bytes, sha256_file, write_json
from ..model import REQUIRED_CRITERIA, rubric_summary, validate_bundle
from ..render import build_site


HERE = Path(__file__).resolve().parents[1]


class PremiumRDTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        authored = author_template(self.root / "data")
        self.manifest_path = Path(authored["manifest"])
        self.rubric_path = Path(authored["rubric"])
        self.manifest = read_json(self.manifest_path)
        self.rubric = read_json(self.rubric_path)
        copied = self.root / "assets" / "source.svg"
        premium_copied = self.root / "assets" / "premium-source.svg"
        copied.parent.mkdir(parents=True)
        copied.write_bytes((HERE / "fixtures" / "source.svg").read_bytes())
        premium_copied.write_bytes((HERE / "fixtures" / "premium-source.svg").read_bytes())
        digests = {"baseline": sha256_file(copied), "premium": sha256_file(premium_copied)}
        for asset in self.manifest["assets"]:
            asset["path"] = "assets/source.svg" if asset["workflow_id"] == "baseline" else "assets/premium-source.svg"
            asset["sha256"] = digests[asset["workflow_id"]]
        for record in self.manifest["render_records"]:
            record["output_hash"] = digests[record["workflow_id"]]
            record["review_status"] = "REVIEWED_PASS"
        failed_asset = dict(next(asset for asset in self.manifest["assets"] if asset["asset_id"] == "premium-p001"))
        failed_asset["asset_id"] = "premium-p001-failed"
        self.manifest["assets"].append(failed_asset)
        failed_record = dict(next(record for record in self.manifest["render_records"] if record["output_asset_id"] == "premium-p001"))
        failed_record.update({"record_id": "render-premium-p001-failed", "output_asset_id": "premium-p001-failed", "review_status": "HARD_FAIL_PRESERVED_DIAGNOSTIC", "failure_classes": ["HAND_EQUIPMENT_INTERACTION"]})
        self.manifest["render_records"].append(failed_record)
        for panel in self.manifest["panels"]:
            panel["lettering_units"] = [
                {"kind": "dialogue", "text": f"Hold the line, beat {panel['order']}.", "box": [.05, .05, .43, .15], "tail": [.36, .24], "reading_order": 1},
                {"kind": "ui", "text": "EMBER THREAD · 12 / 20", "box": [.55, .8, .95, .92], "reading_order": 2},
            ]
        for evaluation in self.rubric["evaluations"]:
            score = 4.2 if evaluation["workflow_id"] == "premium" else 3.1
            evaluation["scores"] = {criterion: score for criterion in REQUIRED_CRITERIA}
            evaluation["evidence"] = "fixture evidence"
        self.manifest["failures"] = [{
            "failure_id": "repair-001", "panel_id": self.manifest["panels"][0]["panel_id"], "workflow_id": "premium",
            "failed_asset_id": "premium-p001-failed", "failure_class": "HAND_EQUIPMENT_INTERACTION", "frozen_variables": ["beat", "camera", "costume"],
            "changed_instruction": "Clarify the exact right-hand grip only.", "status": "REPAIRED", "repaired_asset_id": "premium-p001",
            "non_target_hashes_before": {"p002": digests["premium"]}, "non_target_hashes_after": {"p002": digests["premium"]},
        }]
        write_json(self.manifest_path, self.manifest)
        write_json(self.rubric_path, self.rubric)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def strict_editorial_manifest(self) -> dict:
        manifest = copy.deepcopy(self.manifest)
        manifest["project"]["editorial_schema"] = "LetteringPlan/2.0"
        for panel in manifest["panels"]:
            panel["source_art_hash"] = sha256_bytes(panel["panel_id"].encode("utf-8"))
            panel["negative_space_declaration"] = "reserved before rendering"
            panel["negative_space_regions"] = [[.04, .04, .96, .22], [.04, .74, .96, .95]]
            panel["protected_zones"] = [{"type":"face_eyes","box":[.30,.30,.70,.60]}]
            panel["lettering_exception"] = None
            for unit in panel["lettering_units"]:
                unit["speaker"] = "Fixture speaker"
                unit["style"] = "ledger" if unit["kind"] == "ui" else "speech"
                unit["font_scale"] = .04
                if unit["kind"] == "ui":
                    unit["box"] = [.55, .76, .94, .90]
                else:
                    unit["box"] = [.05, .05, .43, .15]
        return manifest

    def test_valid_bundle_builds_and_audits(self) -> None:
        report = validate_bundle(self.manifest, self.rubric, self.root)
        self.assertEqual("PASS", report["status"], report)
        output = self.root / "site"
        built = build_site(self.manifest, self.rubric, self.root, output)
        self.assertEqual("PASS", built["status"])
        self.assertTrue((output / "index.html").is_file())
        self.assertTrue((output / "readers" / "phone.html").is_file())
        audit = audit_bundle(self.manifest, self.rubric, self.root, output)
        self.assertEqual("PASS", audit["status"], audit)
        self.assertGreater(audit["link_integrity"]["links_checked"], 100)

    def test_hash_mismatch_fails_closed(self) -> None:
        self.manifest["assets"][0]["sha256"] = "f" * 64
        report = validate_bundle(self.manifest, self.rubric, self.root)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("hash mismatch" in error for error in report["manifest"]["errors"]))

    def test_missing_scenario_fails_closed(self) -> None:
        for panel in self.manifest["panels"]:
            panel["scenarios"] = ["hero_close_up"]
        report = validate_bundle(self.manifest, self.rubric, self.root)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("scenario coverage" in error for error in report["manifest"]["errors"]))

    def test_rubric_uses_median_and_weakest_panel(self) -> None:
        summary = rubric_summary(self.rubric, self.manifest)
        self.assertEqual("premium", summary["winner"]["workflow_id"])
        self.assertEqual(84.0, summary["winner"]["median_score"])
        self.assertEqual(84.0, summary["winner"]["weakest_panel_score"])

    def test_broken_link_is_reported(self) -> None:
        site = self.root / "broken"
        site.mkdir()
        (site / "index.html").write_text('<a href="missing.html">broken</a>', encoding="utf-8")
        result = audit_links(site)
        self.assertEqual("FAIL", result["status"])
        self.assertEqual(1, len(result["errors"]))

    def test_lettering_collision_fails_closed(self) -> None:
        manifest = self.strict_editorial_manifest()
        manifest["panels"][0]["protected_zones"] = [{"type":"face_eyes","box":[.05,.05,.43,.15]}]
        report = validate_bundle(manifest, self.rubric, self.root, verify_assets=False)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("collides with protected face_eyes" in e for e in report["manifest"]["errors"]))

    def test_excessive_balloon_area_fails_closed(self) -> None:
        manifest = self.strict_editorial_manifest()
        manifest["panels"][0]["lettering_units"][0]["box"] = [.04,.04,.60,.40]
        manifest["panels"][0]["negative_space_regions"] = [[.02,.02,.62,.42]]
        report = validate_bundle(manifest, self.rubric, self.root, verify_assets=False)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("balloon area exceeds 15%" in e for e in report["manifest"]["errors"]))

    def test_small_phone_type_fails_closed(self) -> None:
        manifest = self.strict_editorial_manifest()
        manifest["panels"][0]["lettering_units"][0]["font_scale"] = .02
        report = validate_bundle(manifest, self.rubric, self.root, verify_assets=False)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("phone-scale type" in e for e in report["manifest"]["errors"]))

    def test_missing_negative_space_declaration_fails_closed(self) -> None:
        manifest = self.strict_editorial_manifest()
        del manifest["panels"][0]["negative_space_declaration"]
        report = validate_bundle(manifest, self.rubric, self.root, verify_assets=False)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("negative_space_declaration" in e for e in report["manifest"]["errors"]))

    def test_duplicate_selected_art_fails_closed(self) -> None:
        manifest = self.strict_editorial_manifest()
        manifest["panels"][1]["source_art_hash"] = manifest["panels"][0]["source_art_hash"]
        report = validate_bundle(manifest, self.rubric, self.root, verify_assets=False)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("duplicate selected source art hash" in e for e in report["manifest"]["errors"]))

    def test_unresolved_clean_art_failure_fails_closed(self) -> None:
        manifest = self.strict_editorial_manifest()
        manifest["failures"][0]["failure_class"] = "film_grain"
        manifest["failures"][0]["status"] = "OPEN"
        manifest["failures"][0].pop("repaired_asset_id", None)
        report = validate_bundle(manifest, self.rubric, self.root, verify_assets=False)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("unresolved clean-art failures" in e for e in report["manifest"]["errors"]))


if __name__ == "__main__":
    unittest.main()
