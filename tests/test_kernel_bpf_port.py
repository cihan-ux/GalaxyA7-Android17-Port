"""Regression tests for the a7y18lte Android 17 kernel BPF source patch."""
import unittest

from tools.check_kernel_bpf_port import (
    BASELINE, DISABLED, ENABLED, KERNEL, PATCH, read_version, verify_patch,
)


class KernelBpfPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = BASELINE.read_text()
        cls.makefile = (KERNEL / "Makefile").read_text()
        cls.patch = PATCH.read_text()

    def test_kernel_is_the_pinned_4_4_302_baseline(self):
        self.assertEqual(read_version(self.makefile), "4.4.302")
        self.assertIn(DISABLED, self.config)
        self.assertNotIn(ENABLED, self.config)

    def test_patch_applies_and_only_enables_bpf_syscall(self):
        self.assertEqual(verify_patch(self.config, self.makefile, self.patch), [])

    def test_refuse_other_kernel_version(self):
        older = self.makefile.replace("SUBLEVEL = 302", "SUBLEVEL = 177")
        self.assertTrue(verify_patch(self.config, older, self.patch))

    def test_refuse_changed_kernel_context(self):
        changed = self.config.replace("CONFIG_EVENTFD=y", "CONFIG_EVENTFD=n")
        self.assertTrue(verify_patch(changed, self.makefile, self.patch))

    def test_refuse_additional_kernel_changes(self):
        extra = self.patch + """
diff --git a/arch/arm64/configs/lineage_a7y18lte_defconfig b/arch/arm64/configs/lineage_a7y18lte_defconfig
--- a/arch/arm64/configs/lineage_a7y18lte_defconfig
+++ b/arch/arm64/configs/lineage_a7y18lte_defconfig
@@ -5060,1 +5060,1 @@
-CONFIG_SECURITY_SELINUX_BOOTPARAM=y
+# CONFIG_SECURITY_SELINUX_BOOTPARAM is not set
"""
        self.assertTrue(verify_patch(self.config, self.makefile, extra))

    def test_refuse_patch_if_bpf_already_enabled(self):
        changed = self.config.replace(DISABLED, ENABLED)
        self.assertTrue(verify_patch(changed, self.makefile, self.patch))


if __name__ == "__main__":
    unittest.main()
