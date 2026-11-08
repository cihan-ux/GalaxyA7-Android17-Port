"""Negative- and positive-case tests for the A7 modern DTS research scaffold."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_exynos7885_a7_dts_scaffold import DTS_PATH, verify_dts


class A7DtsScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = DTS_PATH.read_text(encoding="utf-8")

    def test_scaffold_is_identity_correct_and_deliberately_non_bootable(self):
        self.assertEqual(verify_dts(self.good), [])

    def test_reject_a8_identity(self):
        bad = self.good.replace('"samsung,a7y18lte"', '"samsung,jackpotlte"')
        self.assertTrue(verify_dts(bad))

    def test_reject_guessing_a8_memory_map(self):
        bad = self.good + '\n/ { memory@80000000 { device_type = "memory"; reg = <0 0x80000000 0x40000000>; }; };\n'
        self.assertTrue(verify_dts(bad))

    def test_reject_enabling_unverified_peripherals(self):
        self.assertTrue(verify_dts(self.good + '\n&mmc_0 { status = "okay"; };\n'))

    def test_reject_selinux_downgrade(self):
        self.assertTrue(verify_dts(self.good + '\n/ { chosen { bootargs = "androidboot.selinux=permissive"; }; };\n'))

    def test_comments_dont_trigger_restrictions(self):
        self.assertEqual(verify_dts(self.good + '\n/* &mmc_0 { status = "okay"; }; */\n'), [])

    def test_reject_includes_other_than_soc(self):
        self.assertTrue(verify_dts(self.good.replace('#include "exynos7885.dtsi"', '#include "exynos7885-jackpotlte.dts"')))


if __name__ == "__main__":
    unittest.main()
