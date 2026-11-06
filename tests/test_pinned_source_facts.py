"""Regressions sourced from full upstream files, not hand-copied excerpts."""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

FIXTURES = Path(__file__).parent / "fixtures/upstream"


def source(path):
    return (FIXTURES / path).read_text(encoding="utf-8")


def literal_assignment(text, key):
    return re.search(r"^" + re.escape(key) + r"\s*(?::=|=)\s*([^#\n]+)", text, re.M).group(1).strip()


class PinnedSourceFactTests(unittest.TestCase):
    def test_requested_kernel_defconfig_exists(self):
        config = literal_assignment(source("device/BoardConfig.mk"), "TARGET_KERNEL_CONFIG")
        self.assertTrue((FIXTURES / "kernel/arch/arm64/configs" / config).is_file())

    def test_current_common_source_selects_clang(self):
        self.assertEqual(literal_assignment(source("common/BoardConfigCommon.mk"),
                                            "TARGET_KERNEL_CLANG_COMPILE"), "true")

    def test_kernel_version_from_makefile(self):
        text = source("kernel/Makefile")
        version = ".".join(literal_assignment(text, k) for k in ("VERSION", "PATCHLEVEL", "SUBLEVEL"))
        self.assertEqual(version, "4.4.302")

    def test_product_shipping_api_from_current_pin(self):
        self.assertEqual(literal_assignment(source("device/lineage_a7y18lte.mk"),
                                            "PRODUCT_SHIPPING_API_LEVEL"), "28")

    def test_retrofit_super_size_matches_backing_devices(self):
        text = source("device/BoardConfig.mk")
        devices = literal_assignment(text, "BOARD_SUPER_PARTITION_BLOCK_DEVICES").split()
        total = sum(int(literal_assignment(text, f"BOARD_SUPER_PARTITION_{d}_DEVICE_SIZE"))
                    for d in devices)
        self.assertEqual(int(literal_assignment(text, "BOARD_SUPER_PARTITION_SIZE")), total)
        self.assertLess(int(literal_assignment(text, "BOARD_SAMSUNG_DYNAMIC_PARTITIONS_SIZE")), total)
        self.assertEqual(literal_assignment(text, "BOARD_SUPER_PARTITION_METADATA_DEVICE"), "SYSTEM")

    def test_kernel_cmdline_uses_same_super_metadata_device(self):
        metadata = literal_assignment(source("device/BoardConfig.mk"), "BOARD_SUPER_PARTITION_METADATA_DEVICE")
        self.assertIn(f"androidboot.super_partition={metadata}",
                      source("kernel/arch/arm64/configs/lineage_a7y18lte_defconfig"))

    def test_common_vintf_target_level_is_legacy(self):
        manifest = ET.fromstring(source("common/manifest.xml"))
        self.assertEqual(manifest.get("target-level"), "3")

    def test_slsi_candidate_declares_exynos7885_but_is_a_separate_source(self):
        text = source("slsi-config/BoardConfig7885.mk")
        self.assertEqual(literal_assignment(text, "TARGET_SOC_BASE"), "exynos7885")
        self.assertEqual(literal_assignment(text, "TARGET_LINUX_KERNEL_VERSION"), "4.4")
        self.assertIn("soong_config_set", source("slsi-config/BoardConfigCommon.mk"))


if __name__ == "__main__":
    unittest.main()
