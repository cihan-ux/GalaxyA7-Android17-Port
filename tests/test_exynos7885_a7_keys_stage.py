"""Safety and regression checks for A7 experimental GPIO key mapping."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_exynos7885_a7_keys_stage import PATH, check_source


class A7KeysLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = PATH.read_text(encoding="utf-8")

    def test_good_source_mapping(self):
        self.assertEqual(check_source(self.good), [])

    def test_swapped_volume_pins_rejected(self):
        self.assertTrue(check_source(self.good.replace("gpios = <&gpa1 5 GPIO_ACTIVE_LOW>;",
            "gpios = <&gpa1 6 GPIO_ACTIVE_LOW>;")))

    def test_missing_power_wakeup_rejected(self):
        self.assertTrue(check_source(self.good.replace("\n\t\t\twakeup-source;", "")))

    def test_wrong_power_keycode_rejected(self):
        self.assertTrue(check_source(self.good.replace("linux,code = <KEY_POWER>;",
            "linux,code = <KEY_VOLUMEUP>;")))

    def test_reject_foreign_a8_include(self):
        self.assertTrue(check_source(self.good.replace("exynos7885-a7y18lte-emmc-lab.dts",
            "exynos7885-jackpotlte.dts")))

    def test_reject_permissive_bootargs(self):
        self.assertTrue(check_source(self.good + '\n/ { chosen { bootargs = "androidboot.selinux=permissive"; }; };\n'))

    def test_reject_unverified_memory(self):
        self.assertTrue(check_source(self.good + '\n/ { memory@80000000 { reg = <0 0x80000000 0x40000000>; }; };\n'))


if __name__ == "__main__":
    unittest.main()
