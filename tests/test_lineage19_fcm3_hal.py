"""Source-only FCM3 declaration coverage; never equate XML coverage with ROM boot."""
import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_lineage19_fcm3_hal import audit, parse_version, instance_declared

MATRIX = """<compatibility-matrix version="1.0" type="framework" level="3">""" + "".join(
    f'<hal format="hidl" optional="false"><name>{n}</name><version>{v}</version>'
    f'<interface><name>{iface}</name><instance>default</instance></interface></hal>'
    for n, v, iface in (
        ("android.hardware.audio", "4.0", "IDevicesFactory"),
        ("android.hardware.audio.effect", "4.0", "IEffectsFactory"),
        ("android.hardware.drm", "1.1", "IDrmFactory"),
        ("android.hardware.gatekeeper", "1.0", "IGatekeeper"),
        ("android.hardware.graphics.allocator", "2.0", "IAllocator"),
        ("android.hardware.graphics.composer", "2.1-2", "IComposer"),
        ("android.hardware.graphics.mapper", "2.0-1", "IMapper"),
        ("android.hardware.health", "2.0", "IHealth"),
        ("android.hardware.media.omx", "1.0", "IOmx"))
) + "</compatibility-matrix>"
COMMON = """<manifest type="device" target-level="3">
<hal format="hidl"><name>android.hardware.audio</name><version>4.0</version>
<interface><name>IDevicesFactory</name><instance>default</instance></interface></hal>
<hal format="hidl"><name>android.hardware.graphics.composer</name><version>2.4</version>
<interface><name>IComposer</name><instance>default</instance></interface></hal>
<hal format="hidl"><name>android.hardware.drm</name><version>1.0</version>
<interface><name>IDrmFactory</name><instance>default</instance></interface></hal>
</manifest>"""
DEVICE = """<manifest type="device" target-level="3"></manifest>"""


class ManifestCoverageTests(unittest.TestCase):
    def test_reports_incomplete_declarations_without_claiming_runtime(self):
        report = audit(DEVICE, COMMON, MATRIX)
        statuses = {r["hal"]: r["status"] for r in report["hal_groups"]}
        self.assertEqual(statuses["android.hardware.audio"], "plausible_declaration")
        self.assertEqual(statuses["android.hardware.graphics.composer"], "plausible_declaration")
        self.assertEqual(statuses["android.hardware.drm"], "version_not_observed")
        self.assertIn("android.hardware.gatekeeper", report["needs_further_evidence"])
        self.assertIsNone(report["runtime_compatible"])

    def test_requires_matching_interface_and_instance(self):
        edited = COMMON.replace("<instance>default</instance>", "<instance>other</instance>")
        report = audit(DEVICE, edited, MATRIX)
        self.assertEqual(report["hal_groups"][0]["status"], "interface_not_observed")

    def test_ignores_empty_override_marker(self):
        original = COMMON.replace(
            "<version>1.0</version><interface><name>IDrmFactory</name><instance>default</instance></interface>",
            "")
        xml = original.replace("<name>android.hardware.drm</name>",
                               '<name>android.hardware.drm</name>')
        result = audit(DEVICE, xml, MATRIX)
        self.assertEqual(result["hal_groups"][2]["status"], "not_declared_in_two_sources")

    def test_version_range_and_regex_instance(self):
        self.assertEqual(parse_version("2.1-2"), (2, 1))
        self.assertTrue(instance_declared("legacy/0", {"regex:[^/]+/[0-9]+"}))
        self.assertFalse(instance_declared("notmatching", {"regex:[^/]+/[0-9]+"}))

    def test_refuses_wrong_fcm_or_target_level(self):
        with self.assertRaises(ValueError):
            audit(DEVICE, COMMON, MATRIX.replace('level="3"', 'level="4"'))
        with self.assertRaises(ValueError):
            audit(DEVICE.replace('target-level="3"', 'target-level="5"'), COMMON, MATRIX)


if __name__ == "__main__":
    unittest.main()
