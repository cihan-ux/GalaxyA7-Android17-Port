import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_makefile_dependencies import dynamic_dependency_lines

class DynamicDependencyTests(unittest.TestCase):
    def test_dynamic_include(self):
        self.assertEqual(dynamic_dependency_lines("include $(DEVICE_PATH)/BoardConfig.mk"), [1])

    def test_static_include(self):
        self.assertEqual(dynamic_dependency_lines("include hardware/samsung/mkbootimg.mk"), [])

    def test_dynamic_configured_file(self):
        self.assertEqual(dynamic_dependency_lines("BOARD_CUSTOM_BOOTIMG_MK := $(HARDWARE_PATH)/mkbootimg.mk"), [1])

    def test_static_configured_file(self):
        self.assertEqual(dynamic_dependency_lines("BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk"), [])

    def test_dynamic_inherit_product(self):
        self.assertEqual(dynamic_dependency_lines("$(call inherit-product, $(DEVICE_PATH)/device.mk)"), [1])

    def test_static_inherit_product(self):
        self.assertEqual(dynamic_dependency_lines("$(call inherit-product, vendor/samsung/a7y18lte/a7y18lte-vendor.mk)"), [])

    def test_comments_ignored(self):
        self.assertEqual(dynamic_dependency_lines("# include $(DEVICE_PATH)/BoardConfig.mk"), [])

    def test_unrelated_variable_assignment_ignored(self):
        self.assertEqual(dynamic_dependency_lines("OTHER := $(DEVICE_PATH)/device.mk"), [])
