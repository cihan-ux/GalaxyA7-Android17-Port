#!/usr/bin/env python3
"""Guard a strictly bounded A7-only eMMC research DTS against foreign board settings."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "port/linux-6.15/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte-emmc-lab.dts"


def check_source(source: str) -> list[str]:
    content = re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)
    errors = []
    if re.findall(r'^\s*#include\s+"([^"]+)"', content, re.M) != ["exynos7885-a7y18lte.dts"]:
        errors.append("requires only the A7 base DTS")
    if re.search(r'\bjackpotlte\b|\bpermissive\b', content, re.I):
        errors.append("foreign board or weakened SELinux")
    if re.search(r'\b(?:memory(?:@[\da-fA-F]+)?|reserved-memory|chosen)\s*\{', content):
        errors.append("unverified memory/boot data")
    # Whitelist precisely the verified high-level A7 legacy MMC0 mapping.
    blocks = re.findall(r'&([a-zA-Z_][\w]*)\s*\{([^{}]*)\}\s*;', content, re.S)
    if [b[0] for b in blocks] != ["oscclk", "mmc_0"]:
        errors.append("unexpected SoC peripheral override")
    else:
        osc, mmc = blocks[0][1], blocks[1][1]
        if not re.search(r'\bclock-frequency\s*=\s*<26000000>\s*;', osc):
            errors.append("A7 26 MHz source oscillator missing")
        if re.findall(r'\b([\w,-]+)\s*(?:=|;)', osc) != ["clock-frequency"]:
            errors.append("unexpected oscillator data")
        required = [
            r'\bstatus\s*=\s*"okay"\s*;',
            r'\bnon-removable\s*;',
            r'\bbus-width\s*=\s*<8>\s*;',
            r'\bmmc-hs200-1_8v\s*;',
            r'\bmmc-hs400-1_8v\s*;',
            r'\bmmc-hs400-enhanced-strobe\s*;',
            r'\bpinctrl-0\s*=\s*<&sd0_clk\s+&sd0_cmd\s+&sd0_rdqs\s+&sd0_bus1\s+&sd0_bus4\s+&sd0_bus8>\s*;',
        ]
        if any(re.search(p, mmc) is None for p in required):
            errors.append("incomplete A7 eMMC source-derived configuration")
        allowed = {
            "status", "non-removable", "bus-width", "cap-mmc-highspeed",
            "mmc-hs200-1_8v", "mmc-hs400-1_8v", "mmc-hs400-enhanced-strobe",
            "card-detect-delay", "samsung,dw-mshc-ciu-div",
            "pinctrl-names", "pinctrl-0",
        }
        names = set(re.findall(r'\b([\w,-]+)\s*(?:=|;)', mmc))
        if names - allowed:
            errors.append("unexpected MMC settings: " + ", ".join(sorted(names-allowed)))
    if not re.search(r'\bmmc0\s*=\s*&mmc_0\s*;', content):
        errors.append("MMC0 alias missing")
    if re.search(r'\b(?:reg|ranges|vmmc-supply|vqmmc-supply|gpios|bootargs)\s*=', content):
        errors.append("unverified physical mapping/supplies")
    return errors


if __name__ == "__main__":
    failures = check_source(PATH.read_text(encoding="utf-8"))
    if failures:
        for error in failures:
            print("FAIL:", error)
        raise SystemExit(1)
    print("PASS: bounded A7-source eMMC DTS probe; NOT BOOTABLE")
