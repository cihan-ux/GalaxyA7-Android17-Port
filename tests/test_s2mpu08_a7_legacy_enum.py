"""Pinned historical S2MPU08 sparse enumeration parser regressions."""
import unittest

from tools.check_s2mpu08_a7_legacy_enum import audit, parse_enum, read_define

HEADER = """
#define S2MPU08_PMIC_REG_L2CTRL1 0x2D
#define S2MPU08_PMIC_REG_L35CTRL 0x4F
#define S2MPU08_LDO_MIN3 1800000
#define S2MPU08_LDO_STEP2 25000
#define S2MPU08_LDO_VSEL_MASK 0x3F

enum S2MPU08_regulators {
 S2MPU08_LDO1, S2MPU08_LDO2,
 S2MPU08_LDO3, S2MPU08_LDO4, S2MPU08_LDO5,
 S2MPU08_LDO6, S2MPU08_LDO7, S2MPU08_LDO8,
 S2MPU08_LDO9, S2MPU08_LDO10, S2MPU08_LDO11,
 S2MPU08_LDO12, S2MPU08_LDO13, S2MPU08_LDO14,
 /* S2MPU08_LDO15, S2MPU08_LDO16, S2MPU08_LDO17,
 S2MPU08_LDO18, S2MPU08_LDO19, S2MPU08_LDO20,
 S2MPU08_LDO21, S2MPU08_LDO22, S2MPU08_LDO23,
 S2MPU08_LDO24, S2MPU08_LDO25, S2MPU08_LDO26,
 S2MPU08_LDO27, S2MPU08_LDO28, S2MPU08_LDO29,
 S2MPU08_LDO30, S2MPU08_LDO31, S2MPU08_LDO32, */
 S2MPU08_LDO33, S2MPU08_LDO34, S2MPU08_LDO35,
 S2MPU08_LDO36, S2MPU08_LDO37,
 S2MPU08_BUCK1, S2MPU08_BUCK2, S2MPU08_BUCK3,
 S2MPU08_BUCK4, S2MPU08_BUCK5, S2MPU08_BUCK6,
 S2MPU08_BUCK7, S2MPU08_BUCK8,
 // S2MPU08_BUCK9,
 S2MPU08_REG_MAX,
};
"""
LAB = """
#define S2MPU08_A7_LDO2_LEGACY_ENUM_ID   1U
#define S2MPU08_A7_LDO35_LEGACY_ENUM_ID  16U
#define S2MPU08_A7_LDO2_VSEL_REG       0x2dU
#define S2MPU08_A7_LDO35_VSEL_REG      0x4fU
#define S2MPU08_A7_MIN_UV              1800000U
#define S2MPU08_A7_STEP_UV             25000U
#define S2MPU08_A7_VSEL_MASK           0x3fU
"""


class SamsungSparseEnumTests(unittest.TestCase):
    def test_known_old_enum_and_constants(self):
        enum = parse_enum(HEADER)
        self.assertEqual((enum["LDO2"], enum["LDO35"], enum["LDO36"]), (1, 16, 17))
        self.assertEqual(enum["REG_MAX"], 27)
        self.assertEqual(audit(HEADER, LAB), [])
        self.assertEqual(read_define(HEADER, "S2MPU08_PMIC_REG_L35CTRL"), 0x4f)

    def test_reject_incorrectly_active_comment_only_ldo(self):
        self.assertTrue(audit(HEADER.replace("/* S2MPU08_LDO15,", "S2MPU08_LDO15, /*"),
                              LAB))

    def test_reject_wrong_host_enum_constant(self):
        self.assertTrue(audit(HEADER, LAB.replace("16U", "35U")))

    def test_reject_wrong_register_address(self):
        self.assertTrue(audit(HEADER.replace("0x4F", "0x50"), LAB))

    def test_reject_duplicate_enum(self):
        with self.assertRaises(ValueError):
            parse_enum(HEADER.replace("S2MPU08_LDO2,", "S2MPU08_LDO2, S2MPU08_LDO2,"))


if __name__ == "__main__":
    unittest.main()
