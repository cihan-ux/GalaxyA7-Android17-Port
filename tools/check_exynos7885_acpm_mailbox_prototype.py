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
    "EXYNOS7885_ACPM_INTGR0": 0x08,
    "EXYNOS7885_ACPM_INTMR0": 0x10,
    "EXYNOS7885_ACPM_INTMR1": 0x24,
    "EXYNOS7885_ACPM_MAX_CHANNELS": 16,
    "EXYNOS7885_ACPM_PMIC_CHANNEL": 2,
}


def define_value(src, name):
    # The pinned GS101 mailbox source includes /* explanatory register comments */
    # on the same line as #define. Strip C comments before matching exact tokens.
    src = re.sub(r"/\*.*?\*/|//[^\n]*", "", src, flags=re.S)
    match = re.search(r"^\s*#define\s+" + re.escape(name) +
                      r"\s+(0[xX][a-fA-F0-9]+|[0-9]+)[uU]?\s*$", src, re.M)
    return None if match is None else int(match.group(1), 0)


def audit(proto, old, modern, kconfig, makefile, old_ipc_impl):
    problems = []
    for name, value in REQUIRED.items():
        if define_value(proto, name) != value:
            problems.append(f"prototype {name} differs from historical Exynos7885 value")
    for old_name, new_name in (
        ("INTGR0", "EXYNOS7885_ACPM_INTGR0"),
        ("INTMR0", "EXYNOS7885_ACPM_INTMR0"),
        ("INTMR1", "EXYNOS7885_ACPM_INTMR1"),
    ):
        if define_value(old, old_name) != REQUIRED[new_name]:
            problems.append(f"Historical mailbox {old_name} changed")
    historical_send = (
        r"static\s+void\s+apm_interrupt_gen\s*\(\s*unsigned\s+int\s+id\s*\)"
        r"\s*\{[^}]*__raw_writel\s*\(\s*\(\s*1\s*<<\s*id\s*\)"
        r"\s*<<\s*16\s*,\s*acpm_ipc->intr\s*\+\s*INTGR0\s*\)\s*;"
    )
    if not re.search(historical_send, old_ipc_impl, re.S):
        problems.append("Historical AP->APM apm_interrupt_gen() source no longer matches INTGR0")
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
    if "msg->chan_id != EXYNOS7885_ACPM_PMIC_CHANNEL" not in proto or \
       "id != EXYNOS7885_ACPM_PMIC_CHANNEL" not in proto:
        problems.append("Only source-confirmed ACPM PMIC transport channel 2 may be exposed")
    if "chan != &chan->mbox->chans[msg->chan_id]" not in proto:
        problems.append("Doorbell send channel identity must match allocated channel")
    if "args->args_count != 1" not in proto or "id = args->args[0]" not in proto or \
       "return &mbox->chans[id]" not in proto or \
       "id >= EXYNOS7885_ACPM_MAX_CHANNELS" not in proto:
        problems.append("Mailbox xlate must select explicit bounded channel ID")
    if "msg->chan_id >= EXYNOS7885_ACPM_MAX_CHANNELS" not in proto:
        problems.append("Mailbox channel range check missing")
    correct_send = (
        r"writel\s*\(\s*BIT\s*\(\s*msg->chan_id\s*\)\s*<<\s*16\s*,"
        r"\s*mb->regs\s*\+\s*EXYNOS7885_ACPM_INTGR0\s*\)\s*;"
    )
    if not re.search(correct_send, proto):
        problems.append("Send must write BIT(channel)<<16 to INTGR0=0x08")
    if "exynos7885-acpm-mbox-prototype" in kconfig + makefile:
        problems.append("Prototype accidentally integrated into Linux kernel build")
    if proto.count("writel(") != 1:
        problems.append("Prototype must only write doorbell; firmware IRQ masks unverified")
    if "mb->regs + EXYNOS7885_ACPM_INTMR0" in proto or \
       "mb->regs + EXYNOS7885_ACPM_INTMR1" in proto:
        problems.append("IRQ mask register access is not ready for this prototype")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--old-header", required=True, type=Path)
    ap.add_argument("--old-implementation", required=True, type=Path)
    ap.add_argument("--modern-mailbox", required=True, type=Path)
    ap.add_argument("--kernel-kconfig", required=True, type=Path)
    ap.add_argument("--kernel-makefile", required=True, type=Path)
    args = ap.parse_args()
    result = audit(
        SOURCE.read_text(), args.old_header.read_text(),
        args.modern_mailbox.read_text(),
        args.kernel_kconfig.read_text(), args.kernel_makefile.read_text(),
        args.old_implementation.read_text(),
    )
    for issue in result:
        print("FAIL:", issue)
    if result:
        raise SystemExit(1)
    print("PASS: historical AP->APM INTGR0=0x08 with BIT(channel)<<16 validated against Samsung source")
    print("BLOCKED: prototype unregistered/unbound, no Exynos7885 ACPM queue integration or real hardware test")


if __name__ == "__main__":
    main()
