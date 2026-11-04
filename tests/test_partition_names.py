import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_partition_names import parse_names, assess

class PartitionNamesTests(unittest.TestCase):
    def test_basic_names(self):
        self.assertEqual(parse_names("boot\nsystem\nvendor\n"), {"boot", "system", "vendor"})

    def test_duplicate_names(self):
        self.assertEqual(parse_names("boot\nboot\n"), {"boot"})

    def test_reject_device_path(self):
        with self.assertRaises(ValueError):
            parse_names("/dev/block/by-name/boot")

    def test_reject_raw_ls_output(self):
        with self.assertRaises(ValueError):
            parse_names("lrwxrwxrwx 1 root root 12 boot -> /dev/block/sda")

    def test_super_is_hint_only(self):
        report = "\n".join(assess({"boot", "super"}))
        self.assertIn("Dynamic-layout hints: super", report)
        self.assertIn("NOT VERIFIED", report)
