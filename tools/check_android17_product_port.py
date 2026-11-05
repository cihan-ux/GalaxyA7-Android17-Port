#!/usr/bin/env python3
"""Offline guard for the experimental Android 17 Galaxy A7 product delta.

This is a source-level check, not Soong, VINTF, kernel, or device validation.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
PORT = Path("port/lineage-24.0/device/samsung/a7y18lte")
UPSTREAM = Path("tests/fixtures/upstream")


def assignment(source: str, variable: str) -> str | None:
    match = re.search(
        rf"^\s*{re.escape(variable)}\s*(?::=|=)\s*(.*?)\s*(?:#.*)?$",
        source, re.MULTILINE
    )
    return match.group(1).strip() if match else None


def check_product(products: str, product: str, launch_api: str) -> list[str]:
    errors = []
    expected = "lineage_a7y18lte-trunk_staging-userdebug"
    if expected not in products:
        errors.append("Android 17 three-component lunch choice is missing")
    if re.search(r"^\s*lineage_a7y18lte-(?:user|eng|userdebug)\s*$", products, re.M):
        errors.append("Legacy two-component lunch choice leaked into Android 17 overlay")
    if "$(LOCAL_DIR)/lineage_a7y18lte.mk" not in products:
        errors.append("AndroidProducts.mk does not register the staged product")
    for name, value in (("PRODUCT_NAME", "lineage_a7y18lte"),
                        ("PRODUCT_DEVICE", "a7y18lte"),
                        ("PRODUCT_BRAND", "samsung")):
        if assignment(product, name) != value:
            errors.append(f"Incorrect {name}; expected {value}")
    inherited = [
        "product/core_64_bit.mk",
        "product/full_base_telephony.mk",
        "product/product_launched_with_p.mk",
        "device/samsung/a7y18lte/device.mk",
        "vendor/lineage/config/common_full_phone.mk",
    ]
    offsets = [product.find(token) for token in inherited]
    if -1 in offsets or offsets != sorted(offsets):
        errors.append("Missing or out-of-order platform/device product inheritance")
    if assignment(launch_api, "PRODUCT_SHIPPING_API_LEVEL") != "28":
        errors.append("Inspected Android 17 launched-with-P source is not API 28")
    if assignment(product, "PRODUCT_SHIPPING_API_LEVEL") is not None:
        errors.append("Shipping API must be inherited, not overridden in the port delta")
    for marker in ("PRODUCT_SHIPPING_API_LEVEL := 37", "SELINUX_IGNORE_NEVERALLOWS",
                   "PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := false"):
        if marker in product:
            errors.append(f"Unsupported compatibility bypass: {marker}")
    return errors


def observed_blockers(root: Path) -> list[str]:
    """Report verified historical constraints, never pass them off as A17 compatibility."""
    fixtures = root / UPSTREAM
    observations = []
    manifests = [fixtures / "device/manifest.xml", fixtures / "common/manifest.xml"]
    for path in manifests:
        level = ET.parse(path).getroot().get("target-level")
        observations.append(f"{path.relative_to(root)} VINTF target-level={level}")
    makefile = (fixtures / "kernel/Makefile").read_text()
    version = ".".join(assignment(makefile, k) or "UNKNOWN"
                       for k in ("VERSION", "PATCHLEVEL", "SUBLEVEL"))
    observations.append(f"historical kernel source version={version}")
    common = (fixtures / "common/BoardConfigCommon.mk").read_text()
    observations.append("historical vendor SELinux dirs declared="
                        + str("BOARD_VENDOR_SEPOLICY_DIRS" in common))
    product = (fixtures / "device/device.mk").read_text()
    observations.append("historical vendor product inherited="
                        + str("a7y18lte-vendor.mk" in product))
    return observations


def main(root: Path = ROOT) -> int:
    products = (root / PORT / "AndroidProducts.mk").read_text()
    product = (root / PORT / "lineage_a7y18lte.mk").read_text()
    launch_api = (root / "tests/fixtures/lineage24/product_launched_with_p.mk").read_text()
    errors = check_product(products, product, launch_api)
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    for fact in observed_blockers(root):
        print(f"UNRESOLVED (historical baseline, not an A17 pass): {fact}")
    if errors:
        return 1
    print("PASS: Android 17 product staging source invariants only.")
    print("NOT VERIFIED: Android 17 compile, kernel compatibility, HAL/VINTF, vendor or SELinux.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
