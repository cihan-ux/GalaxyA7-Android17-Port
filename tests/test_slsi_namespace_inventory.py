import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_slsi_namespaces import namespaces, inventory, DEFAULT_CONFIG

class SlsiNamespaceTests(unittest.TestCase):
    def test_pinned_complete_config_has_five_namespaces(self):
        result = namespaces(DEFAULT_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(result, sorted([
            "hardware/samsung_slsi-linaro/exynos",
            "hardware/samsung_slsi-linaro/exynos5",
            "hardware/samsung_slsi-linaro/graphics",
            "hardware/samsung_slsi-linaro/interfaces",
            "hardware/samsung_slsi-linaro/openmax",
        ]))

    def test_missing_interfaces_is_reported(self):
        paths = namespaces(DEFAULT_CONFIG.read_text(encoding="utf-8"))
        result = inventory(DEFAULT_CONFIG.read_text(encoding="utf-8"), paths[:])
        self.assertEqual(result["unresolved"], [])
        result = inventory(DEFAULT_CONFIG.read_text(encoding="utf-8"),
                           [p for p in paths if not p.endswith("/interfaces")])
        self.assertEqual(result["unresolved"], ["hardware/samsung_slsi-linaro/interfaces"])

    def test_empty_inventory_reports_all_five(self):
        result = inventory(DEFAULT_CONFIG.read_text(encoding="utf-8"), [])
        self.assertEqual(len(result["unresolved"]), 5)

    def test_unrelated_namespace_is_ignored(self):
        self.assertEqual(namespaces("OTHER += hardware/samsung_slsi-linaro/graphics"), [])

    def test_dynamic_namespace_is_rejected(self):
        with self.assertRaises(ValueError):
            namespaces("PRODUCT_SOONG_NAMESPACES += $(SLSI_PATH)/graphics")

    def test_continuation_and_comment(self):
        source = "PRODUCT_SOONG_NAMESPACES += \\ \n"  # trailing space terminates assignment
        self.assertEqual(namespaces(source), [])
        self.assertEqual(namespaces("PRODUCT_SOONG_NAMESPACES += \\\n hardware/samsung_slsi-linaro/graphics # comment"),
                         ["hardware/samsung_slsi-linaro/graphics"])
