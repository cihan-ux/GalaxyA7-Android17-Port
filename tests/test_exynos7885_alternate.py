import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from check_exynos7885_alternate import differences, compatible_without_device_evidence, PINNED_SLSI_VARIANT, ALTERNATE_SLSI_VARIANT

class Exynos7885AlternateTests(unittest.TestCase):
    def test_cache_conflict(self):
        self.assertEqual(differences()["cache"],(262144000,209715200))
    def test_system_conflict(self):
        self.assertEqual(differences()["system"],(4093640704,3833593856))
    def test_boot_agrees(self):
        self.assertNotIn("boot",differences())
    def test_recovery_agrees(self):
        self.assertNotIn("recovery",differences())
    def test_slsi_variant_conflicts(self):
        self.assertNotEqual(PINNED_SLSI_VARIANT,ALTERNATE_SLSI_VARIANT)
    def test_device_compatibility_unverified(self):
        self.assertFalse(compatible_without_device_evidence())
