"""Offline regression tests for A7 ACPM ↔ GS101 compatibility blocker."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_a7_acpm_bridge_gate import audit


def fixture():
    return {
        "old_soc": '''compatible = "samsung,exynos-acpm-ipc";
            reg = <0x0 0x11C40000 0x1000>, <0x0 0x02052000 0x1B000>;
            initdata-base = <0x4B80>;''',
        "old_board": '''compatible = "samsung,s2mpu08mfd";
            acpm-ipc-channel = <2>;''',
        "old_mfd_h": "#define SHIFT_TYPE 8\n#define SHIFT_REG 0\n",
        "old_acpm_mfd": '''FUNC_READ
            set_protocol(type, TYPE) | set_protocol(reg, REG)
            read_protocol(config.cmd[1], DEST)''',
        "modern_acpm": '''#define ACPM_GS101_INITDATA_BASE 0xa000
            .compatible = "google,gs101-acpm-ipc";''',
        "modern_pmic": """#define ACPM_PMIC_TYPE GENMASK(11, 8)
            #define ACPM_PMIC_REG GENMASK(7, 0)
            #define ACPM_PMIC_CHANNEL GENMASK(15, 12)
            ACPM_PMIC_READ""",
        "modern_soc": "compatible = \"samsung,exynos7885\";",
        "lab_c": "int s2mpu08_a7_acpm_pack_read(void) { return 0; }",
        "lab_h": "#define A7_ACPM_TRANSPORT_CHANNEL      2U\n#define A7_ACPM_PMIC_WIRE_CHANNEL      0U",
    }


class AcpmCompatibilityGateTests(unittest.TestCase):
    def test_pin_compatible_set_and_distinct_sram_map(self):
        self.assertEqual(audit(fixture()), [])

    def test_reject_fake_exynos7885_compatibility(self):
        src = fixture()
        src["modern_acpm"] += '\n.compatible = "samsung,exynos7885-acpm-ipc";'
        self.assertTrue(audit(src))

    def test_reject_changed_acpm_sram_offset(self):
        src = fixture()
        src["modern_acpm"] = src["modern_acpm"].replace("0xa000", "0x4B80")
        self.assertTrue(audit(src))

    def test_reject_modern_new_acpm_node(self):
        src = fixture()
        src["modern_soc"] += '\nacpm { compatible = "google,gs101-acpm-ipc"; };'
        self.assertTrue(audit(src))

    def test_reject_wrong_old_transport_channel(self):
        src = fixture()
        src["old_board"] = src["old_board"].replace("<2>", "<0>")
        self.assertTrue(audit(src))

    def test_reject_real_io_in_lab(self):
        src = fixture()
        src["lab_c"] += "\nacpm_do_xfer(handle, xfer);"
        self.assertTrue(audit(src))


if __name__ == "__main__":
    unittest.main()
