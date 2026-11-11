"""Tests for the pinned LineageOS 24.0 Android 17 kernel loader-version gate."""
import unittest

from tools.check_android17_netbpf_gate import (
    GATE_NAMES, PINNED_CONNECTIVITY_COMMIT,
    evaluate, kernel_version, minimum_loader_kernel, parse_loader_gates,
)

UTILS = """
const bool isAtLeastU = (api_level_full >= 3400);  // 34
const bool isAtLeastV = (api_level_full >= 3500);  // 35
const bool isAtLeast25Q2 = (api_level_full >= 3600);  // 36.0
const bool isAtLeast25Q4 = (api_level_full >= 3610);  // 36.1
const bool isAtLeast26Q4 = (api_level_full >= 3710);  // 37.1
"""
LOADER = """
if (!isAtLeastKernelVersion(4, 9)) return 3;
if (isAtLeastU && !isAtLeastKernelVersion(4, 14)) return 4;
if (isAtLeastV && !isAtLeastKernelVersion(4, 19)) return 5;
if (isAtLeast25Q2 && !isAtLeastKernelVersion(5, 4)) return 6;
if (isAtLeast25Q4 && !isAtLeastKernelVersion(5, 10)) return 7;
if (isAtLeast26Q4 && !isAtLeastKernelVersion(5, 15)) return 7;
"""


class Android17NetBpfGateTests(unittest.TestCase):
    def setUp(self):
        self.gates = parse_loader_gates(LOADER, UTILS)

    def test_expected_release_gates(self):
        self.assertEqual(minimum_loader_kernel(3700, self.gates), (5, 10))
        self.assertEqual(minimum_loader_kernel(3710, self.gates), (5, 15))
        self.assertEqual(minimum_loader_kernel(3600, self.gates), (5, 4))
        self.assertEqual(minimum_loader_kernel(3500, self.gates), (4, 19))

    def test_pinned_4_4_kernel_fails_android17_loader_version_gate(self):
        self.assertEqual(evaluate(3700, (4, 4, 302), self.gates),
                         (False, (5, 10)))
        self.assertEqual(evaluate(3710, (4, 4, 302), self.gates),
                         (False, (5, 15)))

    def test_version_gate_pass_alone_does_not_test_features(self):
        self.assertEqual(evaluate(3700, (5, 10, 0), self.gates),
                         (True, (5, 10)))
        self.assertEqual(evaluate(3710, (5, 10, 0), self.gates),
                         (False, (5, 15)))

    def test_reject_missing_upstream_gate(self):
        with self.assertRaises(ValueError):
            parse_loader_gates(LOADER.replace("isAtLeast26Q4 && ", ""), UTILS)
        with self.assertRaises(ValueError):
            parse_loader_gates(LOADER, UTILS.replace("isAtLeast25Q4", "renamed"))

    def test_reject_kernel_less_than_4_9_missing(self):
        with self.assertRaises(ValueError):
            parse_loader_gates(LOADER.replace("!isAtLeastKernelVersion(4, 9)",
                                             "!isAtLeastKernelVersion(4, 8)"), UTILS)

    def test_parse_kernel_version_exactly(self):
        self.assertEqual(kernel_version("VERSION = 4\nPATCHLEVEL = 4\nSUBLEVEL = 302\n"),
                         (4, 4, 302))
        with self.assertRaises(ValueError):
            kernel_version("VERSION = 4\nPATCHLEVEL = 4\n")

    def test_pinned_source_revision_documented(self):
        self.assertEqual(len(PINNED_CONNECTIVITY_COMMIT), 40)
        self.assertIn("isAtLeast26Q4", GATE_NAMES)


if __name__ == "__main__":
    unittest.main()
