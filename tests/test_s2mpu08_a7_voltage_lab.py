"""Source guard regressions for S2MPU08 no-I/O first ARM64 C port."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_s2mpu08_a7_voltage_lab import check_source, SOURCE, HEADER


class S2MPU08VoltageLabGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = SOURCE.read_text()
        cls.h = HEADER.read_text()

    def test_bounded_source_passes(self):
        self.assertEqual(check_source(self.c, self.h), [])

    def test_reject_driver_registration(self):
        self.assertTrue(check_source(self.c + "\nmodule_platform_driver(my_driver);", self.h))

    def test_reject_voltage_writes(self):
        self.assertTrue(check_source(self.c + "\nregmap_update_bits(foo, 0, 0, 0);", self.h))
        self.assertTrue(check_source(self.c + "\n.enable = regulator_enable_regmap,", self.h))

    def test_reject_wrong_voltage_range(self):
        self.assertTrue(check_source(self.c, self.h.replace(
            "S2MPU08_A7_LDO35_BOARD_MAX_UV  3000000U",
            "S2MPU08_A7_LDO35_BOARD_MAX_UV  3375000U")))

    def test_reject_wrong_regulator_selectors(self):
        self.assertTrue(check_source(self.c, self.h.replace("0x4fU", "0x50U")))

    def test_reject_legacy_revision_workaround_silently_dropped(self):
        self.assertTrue(check_source(self.c, self.h.replace(
            "s2mpu08_a7_needs_rev0_ldo_guard", "removed_rev0_guard")))


if __name__ == "__main__":
    unittest.main()
