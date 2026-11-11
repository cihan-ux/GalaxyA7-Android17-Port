"""Unit tests for pinned SLSI system_ext SELinux makefile conversion."""
import unittest

from tools.check_slsi_sepolicy_layout_port import (
    LEGACY, TARGET, PATCH, OLD_PUBLIC, OLD_PRIVATE, NEW_PUBLIC, NEW_PRIVATE, verify,
)


class SlsiSePolicyLayoutPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = LEGACY.read_text()
        cls.new = TARGET.read_text()
        cls.patch = PATCH.read_text()

    def test_exact_upstream_policy_layout(self):
        self.assertEqual(verify(self.old, self.new, self.patch), [])

    def test_three_expected_edits_only(self):
        self.assertEqual(self.old.count(OLD_PUBLIC), 2)
        self.assertEqual(self.old.count(OLD_PRIVATE), 1)
        self.assertEqual(
            self.old.replace(OLD_PUBLIC, NEW_PUBLIC).replace(OLD_PRIVATE, NEW_PRIVATE),
            self.new,
        )

    def test_refuse_wider_layout_modification(self):
        changed = self.new.replace("BOARD_VENDOR_SEPOLICY_DIRS",
                                   "SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS")
        self.assertTrue(verify(self.old, changed, self.patch))

    def test_refuse_legacy_drift(self):
        self.assertTrue(verify(self.old + "BOARD_PLAT_PUBLIC_SEPOLICY_DIR += foo\n",
                               self.new, self.patch))

    def test_refuse_extra_policy_bypass(self):
        extra = self.patch + (
            "\ndiff --git a/sepolicy.mk b/sepolicy.mk\n"
            "--- a/sepolicy.mk\n+++ b/sepolicy.mk\n"
            "@@ -1,1 +1,2 @@\n #\n+BOARD_SEPOLICY_BYPASS := true\n"
        )
        self.assertTrue(verify(self.old, self.new, extra))


if __name__ == "__main__":
    unittest.main()
