import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_slsi_candidate import SlsiEvidence, assess

class SlsiCandidateTests(unittest.TestCase):
    def test_platform_constants_match(self):
        self.assertTrue(assess()["platform_constants_match"])

    def test_candidate_branch_differs(self):
        self.assertFalse(assess()["branch_matches"])

    def test_candidate_is_not_approved(self):
        self.assertFalse(assess()["eligible"])

    def test_chipset_mismatch_blocks(self):
        e = replace(SlsiEvidence(), chipset="exynos2100")
        self.assertFalse(assess(e)["eligible"])

    def test_matching_branch_alone_does_not_approve(self):
        e = replace(SlsiEvidence(), candidate_branch="lineage-18.1")
        self.assertFalse(assess(e)["eligible"])

    def test_missing_license_blocks(self):
        e = replace(SlsiEvidence(), file_headers_apache_2=False)
        self.assertFalse(assess(e)["eligible"])

    def test_full_evidence_can_pass(self):
        e = replace(SlsiEvidence(), candidate_branch="lineage-18.1",
                    exact_revision_pinned=True, bsp_dependencies_resolved=True,
                    build_compatibility_verified=True)
        self.assertTrue(assess(e)["eligible"])
