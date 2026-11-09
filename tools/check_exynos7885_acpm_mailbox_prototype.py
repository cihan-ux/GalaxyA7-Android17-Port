#!/usr/bin/env python3
"""Ensure the isolated Exynos7885 mailbox source uses pinned register offsets.

Passing static checks + compiler tests is NOT a bootable ACPM transport.
"""
from pathlib import Path
import argparse
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "port/linux-6.15/drivers/mailbox/exynos7885-acpm-mbox-prototype.c"
REQUIRED = {
    "EXYNOS7885_ACPM_INTGR1": 0x1c,
    "EXYNOS7885_ACPM_INTMR0": 0x10,
    "EXYNOS7885_ACPM_MAX_CHANNELS": 16,
    "EXYNOS7885_ACPM_ALL_IRQS_MASK": 0xffff,
}


def define_value(src, name):
    # The pinned GS101 mailbox source includes /* explanatory register comments */
    # on the same line as #define. Strip C comments before matching exact tokens.
    src = re.sub(r"/\*.*?\*/|//[^\n]*", "", src, flags=re.S)
    match = re.search(r"^\s*#define\s+" + re.escape(name) +
                      r"\s+(0[xX][a-fA-F0-9]+|[0-9]+)[uU]?\s*$", src, re.M)
    return None if match is None else int(match.group(1), 0)


def audit(proto, old, modern, kconfig, makefile):
    problems = []
    for name, value in REQUIRED.items():
        if define_value(proto, name) != value:
            problems.append(f"prototype {name} differs from historical Exynos7885 value")
    for old_name, new_name in (
        ("INTGR1", "EXYNOS7885_ACPM_INTGR1"),
        ("INTMR0", "EXYNOS7885_ACPM_INTMR0"),
    ):
        if define_value(old, old_name) != REQUIRED[new_name]:
            problems.append(f"Historical mailbox {old_name} changed")
    # This variant must not accidentally be mistaken for the modern GS101 register map.
    if define_value(modern, "EXYNOS_MBOX_INTGR1") != 0x40:
        problems.append("Pinned GS101 INTGR1 unexpectedly changed")
    if define_value(modern, "EXYNOS_MBOX_INTMR0") != 0x28:
        problems.append("Pinned GS101 INTMR0 unexpectedly changed")
    if proto.count('"samsung,exynos7885-acpm-mbox-prototype"') != 1:
        problems.append("Research-only compatible must not bind real A7 DT")
    if re.search(r'\.compatible\s*=\s*"samsung,exynos-acpm-ipc"', proto):
        problems.append("Accidental binding to legacy monolithic A7 protocol node")
    if "devm_clk_get_optional_enabled" not in proto:
        problems.append("Old A7 tree has no named pclk; optional clock path missing")
    if "msg->chan_type != EXYNOS_MBOX_CHAN_TYPE_DOORBELL" not in proto:
        problems.append("Doorbell-type safety check missing")
    if "msg->chan_id >= EXYNOS7885_ACPM_MAX_CHANNELS" not in proto:
        problems.append("Mailbox channel range check missing")
    if "EXYNOS7885_ACPM_INTGR1" not in proto.split("writel(")[1]:
        problems.append("Send operation missing original INTGR1 offset")
    if "exynos7885-acpm-mbox-prototype" in kconfig + makefile:
        problems.append("Prototype accidentally integrated into Linux kernel build")
    if "writel(" not in proto:
        problems.append("No real mailbox send operation in prototype")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--old-header", required=True, type=Path)
    ap.add_argument("--modern-mailbox", required=True, type=Path)
    ap.add_argument("--kernel-kconfig", required=True, type=Path)
    ap.add_argument("--kernel-makefile", required=True, type=Path)
    args = ap.parse_args()
    result = audit(
        SOURCE.read_text(), args.old_header.read_text(),
        args.modern_mailbox.read_text(),
        args.kernel_kconfig.read_text(), args.kernel_makefile.read_text(),
    )
    for issue in result:
        print("FAIL:", issue)
    if result:
        raise SystemExit(1)
    print("PASS: Exynos7885 0x1c/0x10 mailbox offsets and guarded AArch64 doorbell driver prototype")
    print("BLOCKED: prototype unregistered/unbound, no Exynos7885 ACPM queue integration or real hardware test")


if __name__ == "__main__":
    main()
