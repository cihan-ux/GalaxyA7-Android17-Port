import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_slsi_historical_branches import COMPONENTS, EVIDENCE, historical_coverage, valid_sha, verified

class SlsiHistoricalBranchTests(unittest.TestCase):
    def test_twelve_unverified_entries(self):
        self.assertEqual(len(EVIDENCE), 12)

    def test_all_components_unverified_by_default(self):
        self.assertFalse(any(historical_coverage().values()))

    def test_valid_sha(self):
        self.assertTrue(valid_sha("a"*40))

    def test_invalid_sha_rejected(self):
        self.assertFalse(valid_sha("not-a-commit"))

    def test_one_verified_component_does_not_complete_set(self):
        e = replace(EVIDENCE[0], verified_sha="a"*40)
        coverage = historical_coverage((e,))
        self.assertTrue(coverage[e.component])
        self.assertEqual(sum(coverage.values()), 1)

    def test_wrong_branch_cannot_pass(self):
        e = replace(EVIDENCE[0], branch="lineage-24.0", verified_sha="a"*40)
        self.assertFalse(verified(e))

    def test_wrong_component_cannot_pass(self):
        e = replace(EVIDENCE[0], component="other", verified_sha="a"*40)
        self.assertFalse(verified(e))
