import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_device_report import parse_report, evaluate

class DeviceReportTests(unittest.TestCase):
    def test_expected_model(self):
        data = parse_report("ro.product.model=SM-A750F\nro.product.device=a7y18lte\nro.build.version.sdk=29")
        self.assertFalse(any(x.startswith("STOP") for x in evaluate(data)))

    def test_reject_wrong_model(self):
        data = parse_report("ro.product.model=SM-A750FN")
        self.assertTrue(any(x.startswith("STOP") for x in evaluate(data)))

    def test_reject_unexpected_key(self):
        with self.assertRaises(ValueError):
            parse_report("ro.serialno=SECRET")

    def test_reject_duplicate_key(self):
        with self.assertRaises(ValueError):
            parse_report("ro.product.model=SM-A750F\nro.product.model=SM-A750F")

    def test_reject_shell_injection_like_text(self):
        with self.assertRaises(ValueError):
            parse_report("ro.product.model=$(echo secret)")
