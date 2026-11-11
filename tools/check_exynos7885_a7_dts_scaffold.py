#!/usr/bin/env python3
"""Fail-closed source guard for the non-bootable a7y18lte Linux 6.15 DTS scaffold.

This is an identity/scope check, NOT driver correctness or bootability evidence.
"""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DTS_PATH = ROOT / "port/linux-6.15/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte.dts"


def verify_dts(text: str) -> list[str]:
    # Strip both C-style and C++ comments to avoid treating warnings as data.
    clean = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
    failures = []
    if not re.search(r"^\s*/dts-v1/\s*;", clean, re.M):
        failures.append("missing /dts-v1/ declaration")
    includes = re.findall(r'^\s*#include\s+["<]([^">]+)[">]', clean, re.M)
    if includes != ["exynos7885.dtsi"]:
        failures.append(f"unexpected includes: {includes}")
    if not re.search(r'\bmodel\s*=\s*"Samsung Galaxy A7 \(2018\) SM-A750F \(research-only\)"\s*;', clean):
        failures.append("target model or non-bootable label missing")
    if not re.search(r'\bcompatible\s*=\s*"samsung,a7y18lte"\s*,\s*"samsung,exynos7885"\s*;', clean):
        failures.append("wrong A7/Exynos7885 compatible")
    if not re.search(r'\bchassis-type\s*=\s*"handset"\s*;', clean):
        failures.append("chassis-type missing")
    # These must remain absent until independently confirmed against the A7.
    unsafe = [
        (r'\bmemory(?:@[\da-fA-F]+)?\s*\{', "DRAM map"),
        (r'\breserved-memory\s*\{', "reserved memory"),
        (r'\b(?:reg|ranges)\s*=', "memory/physical address mapping"),
        (r'\b(?:pinctrl-\d+|gpios|gpio|interrupts|interrupt-parent)\s*=', "GPIO/IRQ wiring"),
        (r'\b(?:status|clock-frequency|bus-width|stdout-path|bootargs)\s*=', "unverified enablement/settings"),
        (r'\b(?:regulator|touchscreen|display|panel|modem|wifi|camera|mmc|serial)[\w,@-]*\s*\{', "unverified peripherals"),
        (r'\bjackpotlte\b|\bsamsung,jackpotlte\b', "A8 board identity"),
        (r'\bandroidboot\.selinux\b|\bpermissive\b', "SELinux downgrade"),
        (r'&[a-zA-Z_][\w-]*\s*\{', "peripheral overrides"),
    ]
    for pattern, meaning in unsafe:
        if re.search(pattern, clean, flags=re.I):
            failures.append(f"premature {meaning} in A7 scaffold")
    return failures


def main() -> int:
    problems = verify_dts(DTS_PATH.read_text(encoding="utf-8"))
    if problems:
        for item in problems:
            print("FAIL:", item)
        return 1
    print("PASS: a7y18lte identity with no unverified board wiring; NOT BOOTABLE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
