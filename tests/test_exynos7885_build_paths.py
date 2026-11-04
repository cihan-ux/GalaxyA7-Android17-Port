import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_exynos7885_build_paths import assignment_dependencies, direct_dependency_report

class Exynos7885BuildPathTests(unittest.TestCase):
    def test_bootimg_assignment(self):
        self.assertEqual(assignment_dependencies("BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk")["BOARD_CUSTOM_BOOTIMG_MK"], "hardware/samsung/mkbootimg.mk")

    def test_kernel_source_assignment(self):
        self.assertEqual(assignment_dependencies("TARGET_KERNEL_SOURCE := kernel/samsung/exynos7885")["TARGET_KERNEL_SOURCE"], "kernel/samsung/exynos7885")

    def test_ignores_comment(self):
        self.assertEqual(assignment_dependencies("# BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk"), {})

    def test_ignores_make_variable(self):
        self.assertEqual(assignment_dependencies("TARGET_KERNEL_SOURCE := $(OTHER_PATH)"), {})

    def test_unrelated_assignment_not_included(self):
        self.assertEqual(assignment_dependencies("FOO := hardware/samsung/mkbootimg.mk"), {})

    def test_missing_bootimg_path_reported(self):
        r = direct_dependency_report("BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk")
        self.assertIn("hardware/samsung/mkbootimg.mk", r["unresolved_assigned_paths"])

    def test_known_bootimg_path_resolved(self):
        r = direct_dependency_report("BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk", {"hardware/samsung/mkbootimg.mk"})
        self.assertEqual(r["unresolved_assigned_paths"], [])

    def test_include_and_assignment_separated(self):
        r = direct_dependency_report("include hardware/samsung_slsi-linaro/config/BoardConfig7885.mk\nBOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk")
        self.assertEqual(len(r["includes"]), 1)
        self.assertEqual(len(r["assigned_paths"]), 1)
