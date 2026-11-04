import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_makefile_dependencies import (
    configured_file_paths, all_file_dependencies, unresolved_file_dependencies
)

# Verbatim relevant lines from exynos7885-dev pinned source commits.
BOARD = """include hardware/samsung_slsi-linaro/config/BoardConfig7885.mk
BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk
include device/samsung_slsi/sepolicy/sepolicy.mk
"""
PRODUCT = """$(call inherit-product, vendor/samsung/exynos7885-common/exynos7885-common-vendor.mk)
$(call inherit-product, hardware/samsung_slsi-linaro/config/config.mk)
PRODUCT_CFI_INCLUDE_PATHS += hardware/samsung_slsi/scsc_wifibt/wpa_supplicant_lib
"""

class MakefileConfiguredDependencyTests(unittest.TestCase):
    def test_custom_boot_image_makefile_is_found(self):
        self.assertEqual(configured_file_paths(BOARD), {"hardware/samsung/mkbootimg.mk"})

    def test_three_direct_and_configured_board_dependencies(self):
        self.assertEqual(len(all_file_dependencies(BOARD)), 3)

    def test_all_board_dependencies_unresolved_without_inventory(self):
        self.assertEqual(len(unresolved_file_dependencies(BOARD, set())), 3)

    def test_available_paths_reduce_missing_set(self):
        available = {"hardware/samsung/mkbootimg.mk"}
        self.assertNotIn("hardware/samsung/mkbootimg.mk", unresolved_file_dependencies(BOARD, available))

    def test_product_inherit_references_are_found(self):
        self.assertIn("vendor/samsung/exynos7885-common/exynos7885-common-vendor.mk", all_file_dependencies(PRODUCT))
        self.assertIn("hardware/samsung_slsi-linaro/config/config.mk", all_file_dependencies(PRODUCT))

    def test_product_namespace_is_not_a_file_include(self):
        self.assertNotIn("hardware/samsung_slsi/scsc_wifibt/wpa_supplicant_lib", all_file_dependencies(PRODUCT))

    def test_unrelated_assignment_is_not_dependency(self):
        self.assertEqual(configured_file_paths("FOO := hardware/samsung/other.mk"), set())

    def test_comment_does_not_create_dependency(self):
        self.assertEqual(configured_file_paths("# BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk"), set())
