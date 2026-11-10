"""Mutation checks for the staged 19.1 product and Android 11 source provenance."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_lineage19_port import validate  # noqa: E402

class Lineage19PortTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xml = (ROOT / "manifests/lineage-19.1-a7y18lte-local.xml").read_text()
        d = ROOT / "port/lineage-19.1/device/samsung/a7y18lte"
        cls.reg = (d / "AndroidProducts.mk").read_text()
        cls.product = (d / "lineage_a7y18lte.mk").read_text()

    def test_reviewed_baseline_passes(self):
        self.assertEqual(validate(self.xml, self.reg, self.product), [])

    def test_rejects_unpinned_kernel(self):
        self.assertTrue(validate(self.xml.replace("6020dfa8315134187f07ca903c9d2ed7ee0256f5", "lineage-18.1"),
                                 self.reg, self.product))

    def test_rejects_android17_lunch_tuple(self):
        self.assertTrue(validate(self.xml, self.reg.replace(
            "lineage_a7y18lte-userdebug",
            "lineage_a7y18lte-trunk_staging-userdebug"), self.product))

    def test_rejects_undocumented_shipping_api_override(self):
        self.assertTrue(validate(self.xml, self.reg,
                                 self.product + "\nPRODUCT_SHIPPING_API_LEVEL := 28\n"))

    def test_rejects_missing_device_inheritance(self):
        self.assertTrue(validate(self.xml, self.reg,
                                 self.product.replace(
                                     "$(call inherit-product, device/samsung/a7y18lte/device.mk)", "")))

    def test_rejects_unvetted_selinux_bypass(self):
        self.assertTrue(validate(self.xml, self.reg,
                                 self.product + "\nSELINUX_IGNORE_NEVERALLOWS := true\n"))

    def test_rejects_duplicate_manifest_path(self):
        xml = self.xml.replace("</manifest>", '  <project path="device/samsung/a7y18lte" />\n</manifest>')
        self.assertTrue(validate(xml, self.reg, self.product))

if __name__ == "__main__":
    unittest.main()
