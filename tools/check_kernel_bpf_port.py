#!/usr/bin/env python3
"""Verify the first *candidate* Android 17 BPF kernel config delta offline.

Only proves that a one-line patch applies to pinned kernel 4.4.302's
a7y18lte defconfig. This is NOT an Android 17 BPF, build or boot test.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
KERNEL = ROOT / "tests/fixtures/upstream/kernel"
BASELINE = KERNEL / "arch/arm64/configs/lineage_a7y18lte_defconfig"
PATCH = ROOT / ("port/lineage-24.0/kernel/samsung/exynos7885/patches/"
                "0001-a7y18lte-bpf-syscall-research.patch")
RELATIVE_CONFIG = Path("arch/arm64/configs/lineage_a7y18lte_defconfig")
DISABLED = "# CONFIG_BPF_SYSCALL is not set"
ENABLED = "CONFIG_BPF_SYSCALL=y"


def read_version(makefile: str) -> str:
    def part(name: str) -> str:
        match = re.search(rf"^{name}\s*=\s*(\d+)\s*$", makefile, re.M)
        return match.group(1) if match else "unknown"
    return ".".join(part(name) for name in ("VERSION", "PATCHLEVEL", "SUBLEVEL"))


def verify_patch(config: str, makefile: str, patch_text: str) -> list[str]:
    errors: list[str] = []
    version = read_version(makefile)
    if version != "4.4.302":
        errors.append(f"Unexpected pinned kernel version: {version}")
    if config.count(DISABLED) != 1 or ENABLED in config:
        errors.append("Pinned defconfig must disable CONFIG_BPF_SYSCALL exactly once")
    for symbol in ("CONFIG_BPF=y", "CONFIG_ANON_INODES=y",
                   "CONFIG_ANDROID_BINDER_IPC=y", "CONFIG_SECURITY_SELINUX=y"):
        if symbol not in config.splitlines():
            errors.append(f"Missing pinned dependency or protection: {symbol}")
    if errors:
        return errors

    with tempfile.TemporaryDirectory(prefix="a7-bpf-source-check-") as temp:
        root = Path(temp)
        target = root / RELATIVE_CONFIG
        target.parent.mkdir(parents=True)
        target.write_text(config)
        proposed = root / "bpf.patch"
        proposed.write_text(patch_text)
        for args in (("git", "apply", "--check", str(proposed)),
                     ("git", "apply", str(proposed))):
            result = subprocess.run(args, cwd=root, capture_output=True, text=True,
                                    check=False)
            if result.returncode:
                errors.append(f"Patch did not apply: {result.stderr.strip()}")
                return errors
        changed = target.read_text()
        if changed != config.replace(DISABLED, ENABLED, 1):
            errors.append("Patch changes more than the single BPF_SYSCALL setting")
    return errors


def main() -> int:
    errors = verify_patch(BASELINE.read_text(), (KERNEL / "Makefile").read_text(),
                          PATCH.read_text())
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: one-line BPF_SYSCALL patch applies to pinned 4.4.302 defconfig.")
    print("NOT VERIFIED: kernel compilation, Android 17 bpfloader, SELinux, "
          "vendor HALs, VINTF, device boot, or security.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
