#!/usr/bin/env python3
"""Integrate the unbound A7 ACPM mailbox prototype into a PINNED kernel Kbuild.

This edits a GitHub Actions *temporary checkout*, not this repository's main
branch or a device. It never changes a DTS, installs or runs a driver.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "port/linux-6.15/drivers/mailbox/exynos7885-acpm-mbox-prototype.c"
OPTION = "EXYNOS7885_ACPM_MBOX_LAB"
DRIVER = "exynos7885-acpm-mbox-prototype.c"
KCONFIG_STANZA = """
config EXYNOS7885_ACPM_MBOX_LAB
    bool "Exynos7885 ACPM mailbox prototype (unbound, research only)"
    depends on ARCH_EXYNOS && OF
    default n
    help
      Compiles an Exynos7885-specific AP2APM mailbox driver prototype
      for development builds only. It does not provide a production
      device-tree binding or a working ACPM firmware transport.
      Never enable it in a ROM intended for a physical device.
"""
MAKEFILE_LINE = "obj-$(CONFIG_EXYNOS7885_ACPM_MBOX_LAB) += exynos7885-acpm-mbox-prototype.o"


def stage_kbuild_text(kconfig: str, makefile: str, source: str) -> tuple[str, str]:
    if (OPTION in kconfig + makefile or DRIVER in kconfig + makefile or
            "config EXYNOS_MBOX" not in kconfig or
            "obj-$(CONFIG_EXYNOS_MBOX)" not in makefile):
        raise ValueError("Unpinned/duplicate mailbox Kconfig or Makefile")
    if not re.search(r"(?m)^if MAILBOX\s*$", kconfig):
        raise ValueError("Expected upstream MAILBOX Kconfig guard missing")
    parts = kconfig.rpartition("\nendif\n")
    if not parts[1] or parts[2].strip():
        raise ValueError("Expected final mailbox Kconfig endif missing")
    if source.count('"samsung,exynos7885-acpm-mbox-prototype"') != 1:
        raise ValueError("Source no longer uses exactly one research-only compatible")
    if re.search(r'\.compatible\s*=\s*"samsung,exynos-acpm-ipc"', source):
        raise ValueError("Source must not claim the legacy A7 monolithic ACPM node")
    if source.count("writel(") != 1:
        raise ValueError("Source must not write unverified mailbox mask registers")
    doorbell = (
        r"writel\s*\(\s*BIT\s*\(\s*msg->chan_id\s*\)\s*<<\s*16\s*,"
        r"\s*mb->regs\s*\+\s*EXYNOS7885_ACPM_INTGR0\s*\)\s*;"
    )
    if not re.search(doorbell, source) or not re.search(
        r"#define\s+EXYNOS7885_ACPM_INTGR0\s+0x0008\b", source
    ):
        raise ValueError("AP->APM doorbell requires INTGR0=0x08 and BIT(channel)<<16")
    if re.search(r"\b(?:CONFIG_EXYNOS7885_ACPM_MBOX_LAB|CONFIG_EXYNOS_MBOX)\b", source):
        raise ValueError("Hardcoded Kconfig coupling detected inside driver")
    new_kconfig = parts[0] + "\n" + KCONFIG_STANZA.rstrip() + parts[1] + parts[2]
    new_makefile = makefile.rstrip("\n") + "\n\n" + MAKEFILE_LINE + "\n"
    if "default n" not in new_kconfig or MAKEFILE_LINE not in new_makefile:
        raise ValueError("Staging did not preserve required opt-in controls")
    return new_kconfig, new_makefile


def stage_tree(tree: Path) -> None:
    kernel_dir = tree / "drivers/mailbox"
    kconfig = kernel_dir / "Kconfig"
    makefile = kernel_dir / "Makefile"
    target = kernel_dir / DRIVER
    if target.exists():
        raise ValueError("Driver already exists in upstream tree; re-audit before staging")
    source = SOURCE.read_text(encoding="utf-8")
    old_kconfig, old_makefile = (p.read_text(encoding="utf-8") for p in
                                  (kconfig, makefile))
    new_kconfig, new_makefile = stage_kbuild_text(old_kconfig, old_makefile, source)
    kconfig.write_text(new_kconfig, encoding="utf-8")
    makefile.write_text(new_makefile, encoding="utf-8")
    target.write_text(source, encoding="utf-8")
    print("PASS: opt-in default-off Kconfig and actual Kbuild object wired in temporary tree")
    print("NO A7 DT node, no production compatible, no runtime driver enabled by default.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kernel-tree", type=Path, required=True)
    args = p.parse_args()
    stage_tree(args.kernel_tree)


if __name__ == "__main__":
    main()
