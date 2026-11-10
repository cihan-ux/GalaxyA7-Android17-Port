"""Mutation checks for ACPM read-only descriptor snapshot source."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_a7_acpm_descriptor_snapshot import SRC, HDR, audit


class DescriptorSnapshotSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SRC.read_text()
        cls.header = HDR.read_text()

    def test_source_keeps_inert_guards(self):
        self.assertEqual(audit(self.source, self.header), [])

    def test_reject_accidental_io(self):
        self.assertTrue(audit(self.source + "\nwritel(1, regs);", self.header))
        self.assertTrue(audit(self.source + "\nvolatile unsigned int *p;", self.header))

    def test_reject_missing_double_view_check(self):
        self.assertTrue(audit(self.source.replace("first == second", "first != second"), self.header))

    def test_reject_unsafe_descriptor_length(self):
        self.assertTrue(audit(self.source.replace("result.layout.mlen != 16U", "result.layout.mlen != 1024U"), self.header))

    def test_reject_unchecked_queue_index(self):
        self.assertTrue(audit(self.source.replace("first != second || first >= qlen", "first > qlen"), self.header))

    def test_reject_bypassing_prefix_bounds(self):
        self.assertTrue(audit(self.source.replace("a7_acpm_validate_fw_prefix(", "unsafe_prefix("), self.header))


if __name__ == "__main__":
    unittest.main()
