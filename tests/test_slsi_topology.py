import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_slsi_topology import REQUIRED, DISCOVERED, missing_paths, complete

class SlsiTopologyTests(unittest.TestCase):
    def test_six_distinct_slsi_paths(self):
        self.assertEqual(len(REQUIRED), 6)

    def test_current_inventory_is_incomplete(self):
        self.assertFalse(complete())

    def test_five_missing_paths(self):
        self.assertEqual(len(missing_paths()), 5)

    def test_full_inventory_is_structurally_complete(self):
        self.assertTrue(complete(REQUIRED))

    def test_missing_config_is_detected(self):
        self.assertIn("hardware/samsung_slsi-linaro/config", missing_paths(REQUIRED - {"hardware/samsung_slsi-linaro/config"}))
