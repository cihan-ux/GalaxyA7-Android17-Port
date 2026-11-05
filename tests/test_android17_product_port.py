"""Offline tests for the staged LineageOS 24.0 a7y18lte product makefiles."""
from pathlib import Path
import unittest

from tools.check_android17_product_port import (
    PORT, ROOT, check_product, observed_blockers,
)

TARGET_API = ROOT / "tests/fixtures/lineage24/product_launched_with_o.mk"


class Android17ProductPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.products = (ROOT / PORT / "AndroidProducts.mk").read_text()
        cls.product = (ROOT / PORT / "lineage_a7y18lte.mk").read_text()
        cls.target_api = TARGET_API.read_text()

    def test_staged_product_invariants(self):
        self.assertEqual(check_product(self.products, self.product, self.target_api), [])

    def test_android11_lunch_style_is_rejected(self):
        old = self.products.replace(
            "lineage_a7y18lte-trunk_staging-userdebug", "lineage_a7y18lte-userdebug"
        )
        self.assertTrue(any("three-component" in s or "Legacy" in s
                            for s in check_product(old, self.product, self.target_api)))

    def test_shipping_api_spoofing_is_rejected(self):
        changed = self.product + "\nPRODUCT_SHIPPING_API_LEVEL := 37\n"
        self.assertTrue(check_product(self.products, changed, self.target_api))

    def test_losing_device_inheritance_is_rejected(self):
        changed = self.product.replace(
            "$(call inherit-product, device/samsung/a7y18lte/device.mk)", ""
        )
        self.assertTrue(any("inheritance" in s
                            for s in check_product(self.products, changed, self.target_api)))

    def test_historical_kernel_vintf_vendor_selinux_are_not_claimed_compatible(self):
        facts = observed_blockers(ROOT)
        self.assertTrue(any("target-level=3" in fact for fact in facts))
        self.assertTrue(any("version=4.4.302" in fact for fact in facts))
        self.assertTrue(any("SELinux dirs declared=True" in fact for fact in facts))
        self.assertTrue(any("vendor product inherited=True" in fact for fact in facts))
        self.assertTrue(any("pinned legacy product shipping API=28" in fact for fact in facts))
        self.assertTrue(any("historical Android Binder IPC enabled=True" in fact for fact in facts))
        self.assertTrue(any("historical BPF syscall enabled=False" in fact for fact in facts))


if __name__ == "__main__":
    unittest.main()
