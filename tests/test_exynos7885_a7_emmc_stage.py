"""Regression tests for the A7 source-derived eMMC lab overlay."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_exynos7885_a7_emmc_stage import PATH, check_source


class A7EmmcTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = PATH.read_text(encoding="utf-8")

    def test_only_expected_a7_emmc_overrides(self):
        self.assertEqual(check_source(self.good), [])

    def test_reject_a8_include(self):
        self.assertTrue(check_source(self.good.replace("exynos7885-a7y18lte.dts", "exynos7885-jackpotlte.dts")))

    def test_reject_unverified_regulator(self):
        self.assertTrue(check_source(self.good.replace("non-removable;", "vmmc-supply = <&wrong_rail>;\n non-removable;")))

    def test_reject_wrong_clock(self):
        self.assertTrue(check_source(self.good.replace("<26000000>", "<24000000>")))

    def test_reject_missing_pins(self):
        self.assertTrue(check_source(self.good.replace("&sd0_bus8", "&sd0_bus4")))

    def test_reject_additional_peripheral(self):
        self.assertTrue(check_source(self.good + '\n&serial_2 { status = "okay"; };\n'))


if __name__ == "__main__":
    unittest.main()
