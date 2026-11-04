"""Regression tests using verbatim directive lines from pinned upstream board configs.

Source:
exynos7885-dev/device_samsung_exynos7885-common @ f2ce8d2093711026f021cba7036334d381d455ef
MacBookPro34-comma-7/android_device_samsung_universal7885-common @ 98009b1e310f04ca940bf6c1ef1cc0cc144bdb02
Only relevant lines are reproduced; these are not complete build fixtures.
"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_makefile_dependencies import referenced_paths, declared_slsi_variant, unresolved_paths

LINARO = """TARGET_SLSI_VARIANT := linaro
include hardware/samsung_slsi-linaro/config/BoardConfig7885.mk
include device/lineage/sepolicy/exynos/sepolicy.mk
include device/samsung_slsi/sepolicy/sepolicy.mk
"""
BSP = """TARGET_SLSI_VARIANT := bsp
include device/lineage/sepolicy/exynos/sepolicy.mk
include device/samsung_slsi/sepolicy/sepolicy.mk
"""

class PinnedBoardConfigTests(unittest.TestCase):
    def test_linaro_requires_boardconfig7885(self):
        self.assertIn("hardware/samsung_slsi-linaro/config/BoardConfig7885.mk", referenced_paths(LINARO))

    def test_bsp_does_not_include_linaro_boardconfig(self):
        self.assertNotIn("hardware/samsung_slsi-linaro/config/BoardConfig7885.mk", referenced_paths(BSP))

    def test_both_include_samsung_sepolicy(self):
        p = "device/samsung_slsi/sepolicy/sepolicy.mk"
        self.assertIn(p, referenced_paths(LINARO))
        self.assertIn(p, referenced_paths(BSP))

    def test_variant_is_explicit(self):
        self.assertEqual(declared_slsi_variant(LINARO), "linaro")
        self.assertEqual(declared_slsi_variant(BSP), "bsp")

    def test_linaro_missing_dependencies_reported(self):
        self.assertEqual(len(unresolved_paths(LINARO, set())), 3)

    def test_bsp_missing_dependencies_reported(self):
        self.assertEqual(len(unresolved_paths(BSP, set())), 2)
