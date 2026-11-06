import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_source_evidence import DEFAULT_ROOT, DEFAULT_RESEARCH_MANIFEST, main, verify_evidence


class SourceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "fixtures"
        shutil.copytree(DEFAULT_ROOT, self.root)
        self.inventory = self.root / "manifest.json"

    def update_inventory(self, change):
        data = json.loads(self.inventory.read_text())
        change(data)
        self.inventory.write_text(json.dumps(data))

    def errors(self):
        return "\n".join(verify_evidence(self.root))

    def test_recorded_upstream_bytes_match_pins(self):
        self.assertEqual(verify_evidence(), [])

    def test_modified_fixture_is_rejected(self):
        fixture = self.root / "common/BoardConfigCommon.mk"
        fixture.write_text(fixture.read_text().replace("TARGET_KERNEL_CLANG_COMPILE := true",
                                                     "TARGET_KERNEL_CLANG_COMPILE := false"))
        self.assertIn("SHA-256 mismatch", self.errors())
        self.assertIn("Git blob SHA mismatch", self.errors())

    def test_missing_fixture_is_rejected(self):
        (self.root / "device/device.mk").unlink()
        self.assertIn("cannot read UTF-8 source", self.errors())

    def test_floating_revision_is_rejected(self):
        self.update_inventory(lambda d: d["files"][0].update(revision="lineage-18.1"))
        self.assertIn("immutable lowercase Git SHA", self.errors())

    def test_wrong_research_pin_is_rejected(self):
        manifest = Path(self.temp.name) / "research.xml"
        original = DEFAULT_RESEARCH_MANIFEST.read_text()
        manifest.write_text(original.replace("f17643ba01010c45b628d5acb8f48350ded61606", "0" * 40))
        self.assertTrue(any("does not match research manifest" in e
                            for e in verify_evidence(self.root, manifest)))

    def test_url_must_bind_same_revision(self):
        self.update_inventory(lambda d: d["files"][0].update(raw_url="https://example.invalid/file"))
        self.assertIn("raw_url must identify", self.errors())

    def test_duplicate_inventory_entry_is_rejected(self):
        self.update_inventory(lambda d: d["files"].append(d["files"][0].copy()))
        self.assertIn("duplicate fixture entry", self.errors())

    def test_duplicate_json_key_is_rejected(self):
        self.inventory.write_text('{"schema_version": 1, "schema_version": 2}')
        self.assertIn("Duplicate JSON key", self.errors())

    def test_traversal_is_rejected(self):
        self.update_inventory(lambda d: d["files"][0].update(fixture="../outside.mk"))
        self.assertIn("without traversal", self.errors())

    def test_symlink_outside_inventory_is_rejected(self):
        path = self.root / "device/BoardConfig.mk"
        path.unlink()
        path.symlink_to(DEFAULT_ROOT / "device/BoardConfig.mk")
        self.assertIn("escapes evidence directory", self.errors())

    def test_unrecorded_source_is_rejected(self):
        (self.root / "unrecorded.mk").write_text("include hardware/example/config.mk\n")
        self.assertIn("Unrecorded fixture files: unrecorded.mk", self.errors())

    def test_proprietary_vendor_repository_is_excluded(self):
        self.update_inventory(lambda d: d["files"][0].update(repository="owner/proprietary_vendor"))
        self.assertIn("proprietary vendor artifacts are excluded", self.errors())

    def test_invalid_field_types_report_errors(self):
        for key, value in (("repository", []), ("license", {}), ("manifest_project", [])):
            with self.subTest(key=key):
                original = self.inventory.read_text()
                self.update_inventory(lambda d: d["files"][0].update({key: value}))
                self.assertTrue(verify_evidence(self.root))
                self.inventory.write_text(original)

    def test_cli_returns_failure_for_missing_inventory(self):
        self.inventory.unlink()
        with redirect_stdout(StringIO()):
            self.assertEqual(main(["--root", str(self.root)]), 1)


if __name__ == "__main__":
    unittest.main()
