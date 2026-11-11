"""Fail-closed modern kernel Android research config checks."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_exynos7885_linux615_android_config import (
    ENABLE_ONLY, REQUIRED_COMPILED, FRAGMENT, parse_fragment, check_features,
    check_version,
)

UTILS = """
const bool isAtLeastU = (api_level_full >= 3400);
const bool isAtLeastV = (api_level_full >= 3500);
const bool isAtLeast25Q2 = (api_level_full >= 3600);
const bool isAtLeast25Q4 = (api_level_full >= 3610);
const bool isAtLeast26Q4 = (api_level_full >= 3710);
"""
LOADER = """
if (!isAtLeastKernelVersion(4, 9)) return 3;
if (isAtLeastU && !isAtLeastKernelVersion(4, 14)) return 4;
if (isAtLeastV && !isAtLeastKernelVersion(4, 19)) return 5;
if (isAtLeast25Q2 && !isAtLeastKernelVersion(5, 4)) return 6;
if (isAtLeast25Q4 && !isAtLeastKernelVersion(5, 10)) return 7;
if (isAtLeast26Q4 && !isAtLeastKernelVersion(5, 15)) return 7;
"""
MAKEFILE = "VERSION = 6\nPATCHLEVEL = 15\nSUBLEVEL = 0\nEXTRAVERSION = -rc1\n"


class Linux615ResearchConfigurationTests(unittest.TestCase):
    def test_reviewed_fragment_is_exact_enable_only(self):
        self.assertEqual(set(parse_fragment(FRAGMENT.read_text())), ENABLE_ONLY)

    def test_reject_unknown_or_disabled_setting(self):
        text = FRAGMENT.read_text()
        with self.assertRaises(ValueError):
            parse_fragment(text + "\nCONFIG_ANDROID_BINDER_IPC=n\n")
        with self.assertRaises(ValueError):
            parse_fragment(text + "\nCONFIG_SECURITY_SELINUX_DEVELOP=n\n")
        with self.assertRaises(ValueError):
            parse_fragment(text + "\nCONFIG_ANDROID_BINDERFS=y\n")

    def test_all_evaluated_flags_must_be_enabled(self):
        positive = "\n".join(f"CONFIG_{x}=y" for x in REQUIRED_COMPILED)
        self.assertEqual(check_features(positive), [])
        for key in ("ANDROID_BINDERFS", "SECURITY_SELINUX", "MMC_DW_EXYNOS", "BPF_SYSCALL"):
            broken = positive.replace(f"CONFIG_{key}=y", f"# CONFIG_{key} is not set")
            self.assertTrue(any(key in x for x in check_features(broken)))

    def test_reject_duplicate_evaluated_settings(self):
        with self.assertRaises(ValueError):
            check_features("CONFIG_BPF=y\nCONFIG_BPF=n\n")

    def test_615_kernel_passes_version_gate_not_runtime_features(self):
        results = check_version(MAKEFILE, LOADER, UTILS)
        self.assertEqual(results[3700], (True, (5, 10)))
        self.assertEqual(results[3710], (True, (5, 15)))

    def test_reject_wrong_kernel_or_missing_release_identifier(self):
        for bad in (MAKEFILE.replace("PATCHLEVEL = 15", "PATCHLEVEL = 4"),
                    MAKEFILE.replace("-rc1", "-rc2")):
            with self.assertRaises(ValueError):
                check_version(bad, LOADER, UTILS)


if __name__ == "__main__":
    unittest.main()
