"""Unbound, opt-in A7 mailbox driver Kconfig/Makefile integration regression."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from stage_exynos7885_mailbox_kernel_integration import (
    stage_kbuild_text, KCONFIG_STANZA, MAKEFILE_LINE, SOURCE, OPTION,
)

BASE_KCONFIG = 'menuconfig MAILBOX\n bool "Mailbox"\n\nif MAILBOX\nconfig EXYNOS_MBOX\n bool "Exynos"\n\nendif\n'
BASE_MAKEFILE = 'obj-$(CONFIG_MAILBOX) += mailbox.o\nobj-$(CONFIG_EXYNOS_MBOX) += exynos-mailbox.o\n'


class MailboxKbuildStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = SOURCE.read_text(encoding="utf-8")

    def test_opt_in_and_existing_upstream_driver_preserved(self):
        kc, mk = stage_kbuild_text(BASE_KCONFIG, BASE_MAKEFILE, self.code)
        self.assertEqual(kc.count("config EXYNOS_MBOX"), 1)
        self.assertEqual(kc.count("config " + OPTION), 1)
        self.assertIn("default n", KCONFIG_STANZA)
        self.assertTrue(kc.rstrip().endswith("endif"))
        self.assertEqual(mk.count(MAKEFILE_LINE), 1)
        self.assertIn("CONFIG_EXYNOS_MBOX", mk)

    def test_duplicate_or_unpinned_config_fails(self):
        kc, mk = stage_kbuild_text(BASE_KCONFIG, BASE_MAKEFILE, self.code)
        with self.assertRaises(ValueError):
            stage_kbuild_text(kc, mk, self.code)
        with self.assertRaises(ValueError):
            stage_kbuild_text("config MY_CONFIG\n", BASE_MAKEFILE, self.code)

    def test_dangerous_compatibility_swap_fails(self):
        with self.assertRaises(ValueError):
            stage_kbuild_text(
                BASE_KCONFIG, BASE_MAKEFILE,
                self.code.replace("samsung,exynos7885-acpm-mbox-prototype",
                                  "samsung,exynos-acpm-ipc"))

    def test_unexpected_mmio_write_fails(self):
        with self.assertRaises(ValueError):
            stage_kbuild_text(BASE_KCONFIG, BASE_MAKEFILE,
                              self.code + "\nwritel(0xffff, regs);")

    def test_kernel_option_is_not_default_enabled(self):
        self.assertNotIn("default y", KCONFIG_STANZA)
        self.assertNotIn("select EXYNOS7885_ACPM_MBOX_LAB", KCONFIG_STANZA)


if __name__ == "__main__":
    unittest.main()
