import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_slsi_8890q_pins import SHAS, REQUIRED, HistoricalCandidate, eligible, valid_sha

class Slsi8890qPinsTests(unittest.TestCase):
    def test_five_verified_branch_head_pins(self):
        self.assertEqual(len(SHAS), 5)
        self.assertTrue(all(valid_sha(s) for s in SHAS.values()))

    def test_interfaces_not_pinned(self):
        self.assertEqual(REQUIRED - SHAS.keys(), {"interfaces"})

    def test_candidate_blocked(self):
        self.assertFalse(eligible())

    def test_all_compatibility_flags_still_block_missing_interface(self):
        c = HistoricalCandidate(True, True, True)
        self.assertFalse(eligible(c))

    def test_invalid_sha_rejected(self):
        self.assertFalse(valid_sha("x"*40))

    def test_older_branch_does_not_imply_7885_compatibility(self):
        self.assertFalse(HistoricalCandidate().chipset_7885_config_verified)
