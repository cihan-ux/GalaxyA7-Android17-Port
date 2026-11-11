"""Compiler-backed, isolated Galaxy A7 SELinux Wi-Fi regression tests."""
import unittest

from tools.check_slsi_wifi_cil import (
    CIL_SMOKE, FORBIDDEN_ACCESS, GUARD, MACROS, POLICY,
    SOURCE_CALL, TYPE_LINE, UPSTREAM, UPSTREAM_HAL,
    compile_smoke, source_gate,
)


class SlsiWifiCilTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.macros = MACROS.read_text()
        cls.patch = POLICY.read_text()
        cls.upstream = UPSTREAM.read_text()
        cls.hal = UPSTREAM_HAL.read_text()

    def test_pinned_source_and_target_expansion(self):
        self.assertEqual(source_gate(self.macros, self.patch, self.upstream, self.hal), [])
        self.assertIn(SOURCE_CALL, self.upstream)
        self.assertIn("vendor_internal_property_type", TYPE_LINE)
        self.assertIn("neverallow", GUARD)

    def test_reject_broad_public_wifi_type(self):
        widened = self.patch.replace("+" + SOURCE_CALL,
                                     "+vendor_public_prop(vendor_wifi_prop)")
        self.assertTrue(source_gate(self.macros, widened, self.upstream, self.hal))

    def test_reject_missing_macro_neverallow(self):
        weak = self.macros.replace(
            "neverallow { coredomain -init -dumpstate }",
            "allow { coredomain -init -dumpstate }")
        self.assertTrue(source_gate(weak, self.patch, self.upstream, self.hal))

    def test_standalone_cil_compiles_with_neverallow(self):
        rc, log = compile_smoke(CIL_SMOKE)
        self.assertEqual(rc, 0, log)

    def test_compiler_rejects_forbidden_core_access(self):
        rc, log = compile_smoke(CIL_SMOKE + FORBIDDEN_ACCESS)
        self.assertNotEqual(rc, 0, "forbidden CIL access must fail compilation")
        self.assertIn("neverallow", log.lower())


if __name__ == "__main__":
    unittest.main()
