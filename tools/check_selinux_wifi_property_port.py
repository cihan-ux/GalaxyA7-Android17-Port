#!/usr/bin/env python3
"""Offline source-level gate for a *candidate* Android 17 Exynos vendor property port.

Applies a narrowly scoped patch to an exact LineageOS 18.1 Samsung SLSI source
fixture, then expands a pinned Android 17 policy macro excerpt with m4.
Neither this script nor a green CI result constitutes policy compilation.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests/fixtures/selinux"
BASELINE = FIXTURES / "lineage18-slsi-property.te"
CONTEXTS = FIXTURES / "lineage18-slsi-property_contexts"
TARGET_MACROS = FIXTURES / "android17-property-macros.m4"
PATCH = ROOT / ("port/lineage-24.0/device/samsung_slsi/sepolicy/patches/"
                "0001-exynos7885-typed-vendor-wifi-property.patch")
POLICY_PATH = Path("common/vendor/property.te")
LEGACY = "type vendor_wifi_prop, property_type;"
PORT = "vendor_public_prop(vendor_wifi_prop)"
EXPANDED = ("type vendor_wifi_prop, property_type, vendor_property_type, "
            "vendor_public_property_type;")


def validate(baseline: str, contexts: str, macros: str, patch: str) -> list[str]:
    errors: list[str] = []
    if baseline.splitlines().count(LEGACY) != 1 or PORT in baseline:
        errors.append("Pinned Samsung SLSI policy must have exactly one legacy Wi-Fi type")
    for prefix in ("vendor.wifi.", "ro.vendor.wifi."):
        pattern = rf"(?m)^{re.escape(prefix)}\s+u:object_r:vendor_wifi_prop:s0\s*$"
        if not re.search(pattern, contexts):
            errors.append(f"Expected vendor Wi-Fi property label missing: {prefix}")
    if "define(`vendor_public_prop', `define_prop($1, vendor, public)')" not in macros:
        errors.append("Pinned Android 17 vendor_public_prop macro excerpt changed")
    if errors:
        return errors

    with tempfile.TemporaryDirectory(prefix="a7-selinux-source-") as temp:
        root = Path(temp)
        target = root / POLICY_PATH
        target.parent.mkdir(parents=True)
        target.write_text(baseline)
        patch_file = root / "wifi.patch"
        patch_file.write_text(patch)
        for args in (("git", "apply", "--check", str(patch_file)),
                     ("git", "apply", str(patch_file))):
            result = subprocess.run(args, cwd=root, capture_output=True,
                                    text=True, check=False)
            if result.returncode:
                errors.append(f"Source patch rejected: {result.stderr.strip()}")
                return errors
        changed = target.read_text()
        if changed != baseline.replace(LEGACY, PORT, 1):
            errors.append("SELinux patch must only replace the Wi-Fi type declaration")

    m4 = subprocess.run(["m4"], input=macros + "\n" + PORT + "\n",
                        capture_output=True, text=True, check=False)
    if m4.returncode or EXPANDED not in re.sub(r"\s+", " ", m4.stdout):
        errors.append("Android 17 macro excerpt did not expand to a vendor-owned public type")
    return errors


def main() -> int:
    errors = validate(BASELINE.read_text(), CONTEXTS.read_text(),
                      TARGET_MACROS.read_text(), PATCH.read_text())
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: SLSI Wi-Fi property policy patch applies, m4 type ownership expands.")
    print("NOT VERIFIED: Android 17 policy compilation, neverallows, vendor accesses, "
          "kernel, VINTF, hardware or device boot.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
