"""Offline regression tests for A7 pinned HAL declaration and override audit."""

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_lineage18_hal_declarations import audit, main


def by_name(report, name):
    return next(entry for entry in report["declarations"] if entry["name"] == name)


class A7Lineage18HALAuditTests(unittest.TestCase):
    def test_existing_pinned_sources_are_a7_target_level_three(self):
        report = audit()
        self.assertEqual(report["target_level"], "3")
        self.assertEqual(report["common_hal_entries"], 49)
        self.assertEqual(report["device_hal_entries"], 4)
        self.assertTrue(report["research_only"])

    def test_device_empty_override_marks_nfc_without_runtime_claim(self):
        report = audit()
        nfc = by_name(report, "android.hardware.nfc")
        self.assertEqual(nfc["source_effect"], "device_empty_override")
        self.assertEqual(nfc["common"][0]["versions"], ["1.2"])
        self.assertTrue(nfc["device"][0]["override"])
        self.assertFalse(nfc["device"][0]["has_service_declaration"])
        self.assertEqual(by_name(report, "vendor.nxp.nxpnfc")["source_effect"], "common_only")
        self.assertTrue(any("not proof" in line for line in report["caveats"]))

    def test_a7_touch_override_adds_stylus_declaration(self):
        report = audit()
        touch = by_name(report, "vendor.lineage.touch")
        self.assertEqual(touch["source_effect"], "device_declares_override")
        self.assertEqual(touch["common"][0]["interfaces"], ["IGloveMode/default"])
        self.assertEqual(touch["device"][0]["interfaces"],
                         ["IGloveMode/default", "IStylusMode/default"])

    def test_radio_fqnames_remain_visible(self):
        report = audit()
        radio = by_name(report, "android.hardware.radio")
        self.assertEqual(radio["source_effect"], "common_only")
        self.assertEqual(len(radio["common"]), 2)
        self.assertIn("@1.4::IRadio/slot1", radio["common"][1]["fqnames"])
        self.assertIn("@1.2::ISap/slot2", radio["common"][1]["fqnames"])

    def test_device_fingerprint_keymaster_are_not_assumed_common(self):
        report = audit()
        for name in ["android.hardware.biometrics.fingerprint", "android.hardware.keymaster"]:
            entry = by_name(report, name)
            self.assertEqual(entry["source_effect"], "device_only")
            self.assertTrue(entry["critical_for_port"])

    def test_mismatched_target_levels_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.xml"
            b = Path(tmp) / "b.xml"
            a.write_text('<manifest type="device" target-level="3"><hal><name>a</name></hal></manifest>')
            b.write_text('<manifest type="device" target-level="4"><hal><name>b</name></hal></manifest>')
            with self.assertRaisesRegex(ValueError, "different target-level"):
                audit(a, b)

    def test_unsupported_format_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.xml"
            b = Path(tmp) / "b.xml"
            a.write_text('<manifest type="device" target-level="3"><hal format="secret"><name>a</name></hal></manifest>')
            b.write_text('<manifest type="device" target-level="3"><hal><name>b</name></hal></manifest>')
            with self.assertRaisesRegex(ValueError, "unexpected HAL format"):
                audit(a, b)

    def test_missing_manifest_rejected_without_success_output(self):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["--common", "/not/a/real/path.xml"])
        self.assertEqual(code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("cannot parse", stderr.getvalue())

    def test_cli_emits_structured_research_json(self):
        with redirect_stdout(StringIO()) as output:
            self.assertEqual(main([]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["schema_version"], 1)
        self.assertTrue(report["research_only"])
        self.assertEqual(by_name(report, "android.hardware.nfc")["source_effect"],
                         "device_empty_override")


if __name__ == "__main__":
    unittest.main()
