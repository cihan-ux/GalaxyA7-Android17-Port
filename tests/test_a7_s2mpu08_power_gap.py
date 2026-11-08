"""Regression tests for A7 hardware PMIC and voltage-regulator source gap."""
import unittest

from tools.check_a7_s2mpu08_power_gap import (
    audit_sources, config_declares, makefile_references, pmic_node_and_rails,
)


def evidence():
    return {
        "legacy_dts": """
            s2mpu08mfd@00 {
                compatible = "samsung,s2mpu08mfd";
                acpm-ipc-channel = <2>;
                regulators {
                    l2_reg: LDO2 {
                        regulator-name = "vqmmc";
                    };
                    l35_reg: LDO35 {
                        regulator-name = "vmmc";
                    };
                };
            };
        """,
        "legacy_mfd_kconfig": "config MFD_S2MPU08\n  bool \"S2MPU08\"\n",
        "legacy_mfd_makefile": "obj-$(CONFIG_MFD_S2MPU08) += s2mpu08_core.o\n",
        "legacy_reg_kconfig": "config REGULATOR_S2MPU08\n  tristate \"S2MPU08\"\n",
        "legacy_reg_makefile": "obj-$(CONFIG_REGULATOR_S2MPU08) += s2mpu08.o\n",
        "legacy_mfd_core": "int s2mpu08_read_reg(void) { exynos_acpm_read_reg(); }",
        "legacy_regulator": "S2MPU08_LDO35\nS2MPU08_LDO36\n",
        "modern_mfd_kconfig": "config MFD_SEC_CORE\n",
        "modern_mfd_makefile": "obj-$(CONFIG_MFD_SEC_CORE) += sec-core.o\n",
        "modern_reg_kconfig": "config REGULATOR_S2MPS11\n",
        "modern_reg_makefile": "obj-$(CONFIG_REGULATOR_S2MPS11) += s2mps11.o\n",
        "modern_sec_core": "s2mpu02 \n",
    }


class S2MPU08PowerAuditTests(unittest.TestCase):
    def test_pinned_source_fixture_reports_actual_missing_driver(self):
        status, problems = audit_sources(evidence())
        self.assertEqual((status, problems), ("blocked", []))

    def test_reject_old_board_rail_mismatch(self):
        data = evidence()
        data["legacy_dts"] = data["legacy_dts"].replace('"vmmc"', '"vdd_ldo35"')
        self.assertTrue(audit_sources(data)[1])

    def test_reject_missing_acpm_transport(self):
        data = evidence()
        data["legacy_mfd_core"] = data["legacy_mfd_core"].replace("exynos_acpm", "nonexistent")
        self.assertTrue(audit_sources(data)[1])

    def test_modern_driver_is_not_silently_classified_as_blocked(self):
        data = evidence()
        data["modern_mfd_kconfig"] += "config MFD_S2MPU08\n"
        self.assertEqual(audit_sources(data)[0], "source-evidence-changed")

    def test_reject_modern_compatible_as_old_gap(self):
        data = evidence()
        data["modern_sec_core"] += '\n"samsung,s2mpu08mfd";'
        self.assertTrue(audit_sources(data)[1])

    def test_real_kconfig_and_makefile_parsing(self):
        self.assertTrue(config_declares("config REGULATOR_S2MPU08\n", "REGULATOR_S2MPU08"))
        self.assertFalse(config_declares("# config REGULATOR_S2MPU08\n", "REGULATOR_S2MPU08"))
        self.assertTrue(makefile_references("obj-$(CONFIG_REGULATOR_S2MPU08) += s2mpu08.o\n", "REGULATOR_S2MPU08"))
        self.assertFalse(makefile_references("# obj-$(CONFIG_REGULATOR_S2MPU08) += s2mpu08.o\n", "REGULATOR_S2MPU08"))

    def test_pmic_node_and_rails_exact(self):
        self.assertEqual(pmic_node_and_rails(evidence()["legacy_dts"]), [])
        self.assertTrue(pmic_node_and_rails("compatible = \"samsung,s2mpu02-pmic\";"))


if __name__ == "__main__":
    unittest.main()
