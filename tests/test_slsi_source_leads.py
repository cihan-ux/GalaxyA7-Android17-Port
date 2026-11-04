import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_slsi_source_leads import LEADS, SourceLead, ready

class SlsiSourceLeadTests(unittest.TestCase):
    def test_interfaces_repository_discovered(self):
        self.assertTrue(any(x.repository.endswith("_interfaces") for x in LEADS))

    def test_six_candidate_entries(self):
        self.assertEqual(len(LEADS), 6)

    def test_all_candidates_blocked(self):
        self.assertTrue(all(not ready(x) for x in LEADS))

    def test_default_branch_is_not_compatibility(self):
        self.assertFalse(ready(replace(LEADS[0], observed_default_branch="lineage-18.1")))

    def test_license_alone_is_insufficient(self):
        self.assertFalse(ready(replace(LEADS[0], license_review_complete=True)))

    def test_all_three_evidence_flags_required(self):
        self.assertTrue(ready(replace(LEADS[0], exact_baseline_commit_verified=True, license_review_complete=True, integration_verified=True)))

    def test_integration_missing_blocks(self):
        self.assertFalse(ready(replace(LEADS[0], exact_baseline_commit_verified=True, license_review_complete=True)))
