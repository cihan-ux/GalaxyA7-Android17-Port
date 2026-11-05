#!/usr/bin/env python3
"""Verify pinned Samsung SLSI SELinux policy-path migration without Android."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests/fixtures/selinux"
LEGACY = FIX / "lineage18-slsi-sepolicy.mk"
TARGET = FIX / "lineage24-slsi-sepolicy.mk"
PATCH = ROOT / "port/lineage-24.0/device/samsung_slsi/sepolicy/patches/0002-slsi-system-ext-policy-partition.patch"
OLD_PUBLIC = "BOARD_PLAT_PUBLIC_SEPOLICY_DIR +="
OLD_PRIVATE = "BOARD_PLAT_PRIVATE_SEPOLICY_DIR +="
NEW_PUBLIC = "SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS +="
NEW_PRIVATE = "SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS +="


def verify(base: str, target: str, patch: str) -> list[str]:
    errors = []
    if base.count(OLD_PUBLIC) != 2 or base.count(OLD_PRIVATE) != 1:
        errors.append("Legacy policy source differs from pinned makefile")
    expected = base.replace(OLD_PUBLIC, NEW_PUBLIC).replace(OLD_PRIVATE, NEW_PRIVATE)
    if expected != target:
        errors.append("LineageOS 24.0 reference differs from exactly three directory edits")
    for marker in ("BOARD_VENDOR_SEPOLICY_DIRS", "BOARD_SEPOLICY_TEE_FLAVOR",
                   "device/samsung_slsi/sepolicy/tee/mobicore/$(POLICY_TYPE)"):
        if marker not in target:
            errors.append("Missing preserved vendor/TEE path: " + marker)
    if errors:
        return errors
    with tempfile.TemporaryDirectory(prefix="a7-slsi-policy-layout-") as name:
        root = Path(name)
        file = root / "sepolicy.mk"
        file.write_text(base)
        patchfile = root / "change.patch"
        patchfile.write_text(patch)
        for cmd in (["git", "apply", "--check", str(patchfile)],
                    ["git", "apply", str(patchfile)]):
            result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
            if result.returncode:
                return ["git apply failed: " + result.stderr.strip()]
        if file.read_text() != target:
            errors.append("Patched source does not exactly match official lineage-24.0")
    return errors


def main() -> int:
    issues = verify(LEGACY.read_text(), TARGET.read_text(), PATCH.read_text())
    for issue in issues:
        print("FAIL:", issue, file=sys.stderr)
    if issues:
        return 1
    print("PASS: SLSI policy-path migration matches pinned LineageOS 24.0 source.")
    print("NOT VERIFIED: full SELinux policy compile, neverallows, VINTF or boot.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
