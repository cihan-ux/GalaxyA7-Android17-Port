import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_partition_arithmetic import PartitionPlan, audit

class PartitionArithmeticTests(unittest.TestCase):
    def test_pinned_sum_matches(self):
        self.assertEqual(audit()["physical_total"], 4882169856)

    def test_metadata_reserve(self):
        self.assertEqual(audit()["metadata_reserve"], 4000000)

    def test_original_constants_have_no_arithmetic_errors(self):
        self.assertEqual(audit()["issues"], [])

    def test_incorrect_super_size_is_blocked(self):
        p = replace(PartitionPlan(), super=4882169855)
        self.assertTrue(any("differs" in x for x in audit(p)["issues"]))

    def test_oversized_dynamic_group_is_blocked(self):
        p = replace(PartitionPlan(), dynamic_group=5000000000)
        self.assertTrue(any("exceeds" in x for x in audit(p)["issues"]))

    def test_zero_partition_size_is_blocked(self):
        p = replace(PartitionPlan(), boot=0)
        self.assertTrue(any("non-positive" in x for x in audit(p)["issues"]))

    def test_no_device_verification_claim(self):
        self.assertFalse(audit()["device_verified"])
