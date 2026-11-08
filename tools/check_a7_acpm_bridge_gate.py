#!/usr/bin/env python3
"""Fail-closed source audit of A7 ACPM legacy ↔ modern GS101-only support.

Green CI with expected BLOCKED = model-specific transport is NOT implemented.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT / "port/linux-6.15/drivers/firmware/samsung"
LAB_C = LAB_ROOT / "s2mpu08-a7-acpm-frame-lab.c"
LAB_H = LAB_ROOT / "s2mpu08-a7-acpm-frame-lab.h"


def comments_off(src: str) -> str:
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", src, flags=re.S)


def audit(s: dict[str, str]) -> list[str]:
    issues = []
    old_soc = comments_off(s["old_soc"])
    old_board = comments_off(s["old_board"])
    old_mfd_h = comments_off(s["old_mfd_h"])
    old_acpm_mfd = comments_off(s["old_acpm_mfd"])
    modern_acpm = comments_off(s["modern_acpm"])
    modern_pmic = comments_off(s["modern_pmic"])
    modern_mailbox = comments_off(s["modern_mailbox"])
    modern_soc = comments_off(s["modern_soc"])
    lab_c = comments_off(s["lab_c"])
    lab_h = comments_off(s["lab_h"])

    expected = [
        ("old SoC ACPM IPC compatible", 'compatible = "samsung,exynos-acpm-ipc"', old_soc),
        ("old SoC APM SRAM base", "0x02052000", old_soc),
        ("old SoC APM IPC mailbox", "0x11C40000", old_soc),
        ("old Exynos7885 initdata-base", "initdata-base = <0x4B80>", old_soc),
        ("old A7 model PMIC compatible", '"samsung,s2mpu08mfd"', old_board),
        ("old A7 transport channel", "acpm-ipc-channel = <2>", old_board),
        ("old PMIC TYPE shift", "#define SHIFT_TYPE", old_mfd_h),
        ("old PMIC REG shift", "#define SHIFT_REG", old_mfd_h),
        ("old PMIC read function", "FUNC_READ", old_acpm_mfd),
        ("old PMIC command pack", "set_protocol(type, TYPE) | set_protocol(reg, REG)", old_acpm_mfd),
        ("old PMIC reply destination", "read_protocol(config.cmd[1], DEST)", old_acpm_mfd),
        ("modern ACPM GS101 initdata", "ACPM_GS101_INITDATA_BASE", modern_acpm),
        ("modern GS101 base value", "0xa000", modern_acpm),
        ("modern GS101 compatible", '"google,gs101-acpm-ipc"', modern_acpm),
        ("modern GS101-only mailbox", '"google,gs101-mbox"', modern_mailbox),
        ("modern PMIC type encoding", "GENMASK(11, 8)", modern_pmic),
        ("modern PMIC register encoding", "GENMASK(7, 0)", modern_pmic),
        ("modern PMIC channel field", "GENMASK(15, 12)", modern_pmic),
        ("modern PMIC read", "ACPM_PMIC_READ", modern_pmic),
        ("lab read-only packet implementation", "s2mpu08_a7_acpm_pack_read", lab_c),
        ("lab separated ACPM transport channel", "A7_ACPM_TRANSPORT_CHANNEL      2U", lab_h),
        ("lab wire channel zero", "A7_ACPM_PMIC_WIRE_CHANNEL      0U", lab_h),
    ]
    for label, needle, hay in expected:
        if needle not in hay:
            issues.append("Missing source evidence: " + label)
    matches = re.findall(r'\.compatible\s*=\s*"([^"]+)"', modern_acpm)
    if matches != ["google,gs101-acpm-ipc"]:
        issues.append(f"Modern ACPM platform compatible list changed: {matches}")
    mbox_matches = re.findall(r'\.compatible\s*=\s*"([^"]+)"', modern_mailbox)
    if mbox_matches != ["google,gs101-mbox"]:
        issues.append(f"Modern Exynos ACPM mailbox compatible list changed: {mbox_matches}")
    if re.search(r'\bacpm\s*\{|\bexynos-acpm-ipc\b|\bgs101-acpm-ipc\b', modern_soc):
        issues.append("Modern Exynos7885 SoC now has ACPM nodes; re-review compatibility")
    disallowed = re.compile(
        r'\b(?:platform_driver|module_init|acpm_do_xfer|mbox_send_message|'
        r'acpm_pmic_(?:write_reg|update_reg|read_reg)|exynos_acpm_(?:read|write|update)|'
        r'regulator_register|regmap_(?:read|write|update_bits)|i2c_transfer)\b', re.I,
    )
    if disallowed.search(lab_c) or disallowed.search(lab_h):
        issues.append("Research packet lab must not perform real ACPM or regulator I/O")
    if re.search(r'\b(?:write|update|bulk_write)\s*\(', lab_c + lab_h):
        issues.append("Research packet lab must not offer write/update methods")
    return issues


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    names = ["old_soc", "old_board", "old_mfd_h", "old_acpm_mfd",
             "modern_acpm", "modern_pmic", "modern_mailbox", "modern_soc"]
    for name in names:
        cli.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    args = cli.parse_args()
    try:
        sources = {x: getattr(args, x).read_text(encoding="utf-8") for x in names}
        sources["lab_c"] = LAB_C.read_text(encoding="utf-8")
        sources["lab_h"] = LAB_H.read_text(encoding="utf-8")
        problems = audit(sources)
    except OSError as exc:
        print("Source fetch failure: cannot decide ACPM compatibility:", exc, file=sys.stderr)
        return 2
    for error in problems:
        print("RECHECK:", error, file=sys.stderr)
    if problems:
        return 1
    print("PASS: source comparison detects confirmed SM-A750F ACPM transport blocker.")
    print("Legacy Exynos7885: mailbox 0x11c40000, SRAM 0x02052000, initdata 0x4b80.")
    print("Modern ACPM and mailbox: only google,gs101-acpm-ipc / google,gs101-mbox.")
    print("GS101 ACPM uses initdata offset 0xa000; A7 legacy uses 0x4b80.")
    print("Common low-byte PMIC message layout != proof of same Exynos7885 firmware protocol.")
    print("NO kernel ACPM DT binding, firmware mailbox transport, S2MPU08 regulator driver or ROM.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
