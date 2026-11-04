import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_makefile_dependencies import referenced_paths, unresolved_paths, source_gate, REQUIRED_LINARO, REQUIRED_BSP, declared_slsi_variant

class MakefileDependencyTests(unittest.TestCase):
    def test_linaro_board_include(self):
        self.assertIn("hardware/samsung_slsi-linaro/config/BoardConfig7885.mk", referenced_paths("include hardware/samsung_slsi-linaro/config/BoardConfig7885.mk"))

    def test_bsp_sepolicy_include(self):
        self.assertIn("device/samsung_slsi/sepolicy/sepolicy.mk", referenced_paths("include device/samsung_slsi/sepolicy/sepolicy.mk"))

    def test_inherit_product(self):
        self.assertIn("vendor/samsung/a7y18lte/a7y18lte-vendor.mk", referenced_paths("$(call inherit-product, vendor/samsung/a7y18lte/a7y18lte-vendor.mk)"))

    def test_comment_is_ignored(self):
        self.assertEqual(referenced_paths("# include vendor/samsung/foo.mk"), set())

    def test_assignment_does_not_imply_dependency(self):
        self.assertEqual(referenced_paths("FOO := hardware/samsung_slsi-linaro/config/BoardConfig7885.mk"), set())

    def test_unresolved_path(self):
        source = "include hardware/samsung/mkbootimg.mk"
        self.assertEqual(unresolved_paths(source, set()), {"hardware/samsung/mkbootimg.mk"})

    def test_linaro_gate_requires_both_paths(self):
        source = "\n".join("include " + p for p in REQUIRED_LINARO)
        self.assertFalse(source_gate(source, set(), REQUIRED_LINARO))
        self.assertTrue(source_gate(source, REQUIRED_LINARO, REQUIRED_LINARO))

    def test_bsp_gate_rejects_linaro_only_source(self):
        source = "\n".join("include " + p for p in REQUIRED_LINARO)
        self.assertFalse(source_gate(source, REQUIRED_LINARO, REQUIRED_BSP))
