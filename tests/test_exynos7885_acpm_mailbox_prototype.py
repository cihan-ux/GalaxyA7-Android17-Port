"""Mailbox register and accidental binding safety checks."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_exynos7885_acpm_mailbox_prototype import audit, SOURCE

OLD = "#define INTGR1 0x001C\n#define INTMR0 0x0010\n#define INTMR1 0x0024\n"
NEW = "#define EXYNOS_MBOX_INTGR1 0x40\n#define EXYNOS_MBOX_INTMR0 0x28\n"


class MailboxPrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = SOURCE.read_text()

    def test_legacy_vs_modern_registers(self):
        self.assertEqual(audit(self.c, OLD, NEW, "", ""), [])

    def test_accept_pinned_style_inline_register_comments(self):
        modern = (
            "#define EXYNOS_MBOX_INTGR1 0x40 /* Generation register */\n"
            "#define EXYNOS_MBOX_INTMR0 0x28 /* Mask register */\n"
        )
        self.assertEqual(audit(self.c, OLD, modern, "", ""), [])

    def test_reject_wrong_old_offset(self):
        self.assertTrue(audit(self.c, OLD.replace("0x001C", "0x0040"), NEW, "", ""))

    def test_reject_guess_new_hardware_offset(self):
        self.assertTrue(audit(self.c.replace("0x001c", "0x0040"), OLD, NEW, "", ""))

    def test_reject_binding_original_monolithic_compatible(self):
        self.assertTrue(audit(
            self.c.replace("samsung,exynos7885-acpm-mbox-prototype",
                           "samsung,exynos-acpm-ipc"), OLD, NEW, "", ""))

    def test_reject_automatic_integration(self):
        self.assertTrue(audit(self.c, OLD, NEW, "",
                              "obj-$(CONFIG_EXYNOS_MBOX) += exynos7885-acpm-mbox-prototype.o"))

    def test_reject_unsafe_interrupt_mask_write(self):
        extra = "\nwritel(0xffff, mb->regs + EXYNOS7885_ACPM_INTMR0);"
        self.assertTrue(audit(self.c + extra, OLD, NEW, "", ""))

    def test_reject_missing_range_check(self):
        self.assertTrue(audit(
            self.c.replace("msg->chan_id >= EXYNOS7885_ACPM_MAX_CHANNELS",
                           "msg->chan_id >= 1024U"), OLD, NEW, "", ""))


if __name__ == "__main__":
    unittest.main()
