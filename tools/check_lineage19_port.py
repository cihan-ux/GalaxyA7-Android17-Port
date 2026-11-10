#!/usr/bin/env python3
"""Source-only guard for the *staged*, unbooted a7y18lte LineageOS 19.1 port."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "port/lineage-19.1/device/samsung/a7y18lte"
MANIFEST = ROOT / "manifests/lineage-19.1-a7y18lte-local.xml"

# Repo and SHA from inspected immutable upstream sources; do not treat these
# pins as an attested manifest for A2L5E0X1's released 18.1 ZIP.
EXPECTED = {
    "device/samsung/a7y18lte": ("a7-source", "device_samsung_a7y18lte", "f17643ba01010c45b628d5acb8f48350ded61606"),
    "device/samsung/exynos7885-common": ("a7-source", "device_samsung_exynos7885-common", "f2ce8d2093711026f021cba7036334d381d455ef"),
    "kernel/samsung/exynos7885": ("a7-source", "kernel_samsung_exynos7885", "6020dfa8315134187f07ca903c9d2ed7ee0256f5"),
    "hardware/samsung": ("a7-source", "hardware_samsung", "082709ec235fd60f55bff0fb0deb8eae12bf0622"),
    "hardware/samsung_slsi-linaro/config": ("a7-source", "hardware_samsung_slsi-linaro_config", "c7a3ba8a1d8e9a467284f8e4e36672b33494e5f8"),
    "hardware/samsung_slsi-linaro/exynos": ("a7-source", "hardware_samsung_slsi-linaro_exynos", "f05f00d0280b5e84678a444a195ff6ccdb95d813"),
    "hardware/samsung_slsi-linaro/exynos5": ("a7-source", "hardware_samsung_slsi-linaro_exynos5", "6dff1105f24bb5a7d96806f9c61265658e836e25"),
    "hardware/samsung_slsi-linaro/graphics": ("a7-source", "hardware_samsung_slsi-linaro_graphics", "7c28107c046cd666b01adef06617482e26311ab7"),
    "hardware/samsung_slsi-linaro/openmax": ("a7-source", "hardware_samsung_slsi-linaro_openmax", "bf76218765ae6b3636acf0d898bdc81c1a912968"),
    "device/lineage/sepolicy": ("a7-lineage", "android_device_lineage_sepolicy", "0ece4d9fd0fc05129d8120d26083edd6ad106ec7"),
    "device/samsung_slsi/sepolicy": ("a7-lineage", "android_device_samsung_slsi_sepolicy", "b86bdaaa5aef70c51d28bc882b9867c3e88dd57d"),
    "vendor/samsung/a7y18lte": ("a7-source", "proprietary_vendor_samsung_a7y18lte", "5e79a4f2536f755a1356636794df4b1bf0cfe780"),
    "vendor/samsung/exynos7885-common": ("a7-source", "proprietary_vendor_samsung_exynos7885-common", "51a9202e8b6d5e4852fdfbb31e5cd1e6769599af"),
}

NEEDED_INHERITS = (
    "$(SRC_TARGET_DIR)/product/core_64_bit.mk",
    "$(SRC_TARGET_DIR)/product/full_base_telephony.mk",
    "$(SRC_TARGET_DIR)/product/product_launched_with_o.mk",
    "device/samsung/a7y18lte/device.mk",
    "vendor/lineage/config/common_full_phone.mk",
)

def validate(manifest: str, registration: str, product: str) -> list[str]:
    problems: list[str] = []
    try:
        root = ET.fromstring(manifest)
    except ET.ParseError as exc:
        return ["invalid local manifest XML: " + str(exc)]
    if root.tag != "manifest":
        problems.append("local manifest must have a manifest root")
    remotes = {r.get("name"): r.get("fetch") for r in root.findall("remote")}
    if remotes != {
        "a7-source": "https://github.com/exynos7885-dev/",
        "a7-lineage": "https://github.com/LineageOS/",
    }:
        problems.append("remote definitions must reference reviewed GitHub organizations")
    projects: dict[str, tuple[str | None, str | None, str | None]] = {}
    for p in root.findall("project"):
        path = p.get("path")
        if not path or path in projects:
            problems.append("duplicate or empty local manifest project path")
        else:
            projects[path] = (p.get("remote"), p.get("name"), p.get("revision"))
    if projects != EXPECTED:
        problems.append("project names, paths or immutable revisions differ from reviewed pins")
    for path, row in projects.items():
        if not re.fullmatch(r"[a-f0-9]{40}", row[2] or ""):
            problems.append("nonimmutable source revision at " + path)
    if "lineage_a7y18lte-userdebug" not in registration or \
       "lineage_a7y18lte-trunk_staging-userdebug" in registration or \
       "$(LOCAL_DIR)/lineage_a7y18lte.mk" not in registration:
        problems.append("use LineageOS 19.1's original PRODUCT-VARIANT lunch format")
    if re.search(r"lineage_a7y18lte-(?:eng|user)(?!debug)", registration):
        problems.append("research stage must expose only userdebug")
    positions = [product.find("$(call inherit-product, " + p + ")") for p in NEEDED_INHERITS]
    if -1 in positions or positions != sorted(positions):
        problems.append("19.1 product must preserve 64-bit, telephony, Oreo, device, Lineage ordering")
    if "PRODUCT_NAME := lineage_a7y18lte" not in product or \
       "PRODUCT_DEVICE := a7y18lte" not in product:
        problems.append("unexpected device or product name")
    if re.search(r"(?m)^\s*PRODUCT_SHIPPING_API_LEVEL\s*[:+?]?=", product):
        problems.append("shipping API must derive from reviewed Oreo product include")
    unsafe = ("SELINUX_IGNORE_NEVERALLOWS", "BOARD_SEPOLICY_VERS", "BUILD_BROKEN_TREBLE_SYSPROP_NEVERALLOW")
    if any(token in product or token in registration for token in unsafe):
        problems.append("do not bypass vendor/SELinux validation to claim compatibility")
    return problems

def main() -> int:
    errors = validate(MANIFEST.read_text(), (STAGE / "AndroidProducts.mk").read_text(),
                      (STAGE / "lineage_a7y18lte.mk").read_text())
    if errors:
        for error in errors:
            print("FAIL: " + error, file=sys.stderr)
        return 1
    print("PASS: immutable 18.1 baseline + LineageOS 19.1 SELinux pins, lunch, source-only product")
    print("LIMIT: this does NOT validate Soong, VINTF, kernel, blobs, ROM or boot")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
