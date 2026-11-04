import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_dependency_provenance import CANDIDATES, eligible_for_manifest

class DependencyProvenanceTests(unittest.TestCase):
    def test_all_discovered_candidates_remain_blocked(self):
        self.assertTrue(all(not eligible_for_manifest(c) for c in CANDIDATES))

    def test_proprietary_blobs_never_eligible(self):
        for c in CANDIDATES:
            if c.contains_proprietary_blobs:
                self.assertFalse(eligible_for_manifest(replace(c, license_verified=True, firmware_match_verified=True, pinned_commit="a"*40)))

    def test_license_required(self):
        c = CANDIDATES[0]
        self.assertFalse(eligible_for_manifest(replace(c, firmware_match_verified=True, pinned_commit="a"*40)))

    def test_firmware_compatibility_required(self):
        c = CANDIDATES[0]
        self.assertFalse(eligible_for_manifest(replace(c, license_verified=True, pinned_commit="a"*40)))

    def test_exact_revision_required(self):
        c = CANDIDATES[0]
        self.assertFalse(eligible_for_manifest(replace(c, license_verified=True, firmware_match_verified=True)))

    def test_validated_source_candidate_can_pass(self):
        c = CANDIDATES[0]
        self.assertTrue(eligible_for_manifest(replace(c, license_verified=True, firmware_match_verified=True, pinned_commit="a"*40)))

    def test_non_hex_pin_rejected(self):
        c = CANDIDATES[0]
        self.assertFalse(eligible_for_manifest(replace(c, license_verified=True, firmware_match_verified=True, pinned_commit="z"*40)))
