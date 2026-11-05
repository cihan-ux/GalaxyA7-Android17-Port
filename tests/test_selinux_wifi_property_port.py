"""Offline tests for the first Exynos7885 Android 17 SELinux property source delta."""
import unittest

from tools.check_selinux_wifi_property_port import (
    BASELINE, CONTEXTS, TARGET_MACROS, PATCH, LEGACY, PORT, validate,
)


class SELinuxWifiPropertyPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = BASELINE.read_text()
        cls.contexts = CONTEXTS.read_text()
        cls.macros = TARGET_MACROS.read_text()
        cls.patch = PATCH.read_text()

    def test_pinned_vendor_property_port(self):
        self.assertEqual(validate(self.base, self.contexts, self.macros, self.patch), [])

    def test_original_vendor_types_are_unchanged(self):
        for line in ("type vendor_cbd_prop, property_type;",
                     "type vendor_radio_prop, property_type;",
                     "type vendor_fastcharge_prop, property_type;"):
            self.assertIn(line, self.base)
        self.assertNotIn(PORT, self.base)
        self.assertIn(LEGACY, self.base)

    def test_rejects_legacy_context_drift(self):
        wrong = self.contexts.replace(
            "ro.vendor.wifi.                u:object_r:vendor_wifi_prop:s0",
            "ro.vendor.wifi.                u:object_r:other_prop:s0")
        self.assertTrue(validate(self.base, wrong, self.macros, self.patch))

    def test_rejects_missing_old_declaration(self):
        self.assertTrue(validate(self.base.replace(LEGACY, ""), self.contexts,
                                 self.macros, self.patch))

    def test_rejects_property_macro_mismatch(self):
        wrong = self.macros.replace("define_prop($1, vendor, internal)",
                                    "define_prop($1, system, internal)")
        self.assertTrue(validate(self.base, self.contexts, wrong, self.patch))

    def test_rejects_extra_selinux_allow_rule(self):
        wrong_patch = self.patch + """
diff --git a/common/vendor/property.te b/common/vendor/property.te
--- a/common/vendor/property.te
+++ b/common/vendor/property.te
@@ -1,1 +1,2 @@
 # property.te
+allow domain self:capability sys_admin;
"""
        self.assertTrue(validate(self.base, self.contexts, self.macros, wrong_patch))


if __name__ == "__main__":
    unittest.main()
