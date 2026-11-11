#!/usr/bin/env python3
"""Fail closed if the S2MPU08 voltage-only research lab gains hardware access."""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "port/linux-6.15/drivers/regulator/s2mpu08-a7-voltage-lab.c"
HEADER = ROOT / "port/linux-6.15/drivers/regulator/s2mpu08-a7-voltage-lab.h"
REQUIRED_CONSTANTS = {
    "S2MPU08_A7_LDO2_CHANNEL": "2U",
    "S2MPU08_A7_LDO35_CHANNEL": "35U",
    "S2MPU08_A7_LDO36_CHANNEL": "36U",
    "S2MPU08_A7_LDO2_LEGACY_ENUM_ID": "1U",
    "S2MPU08_A7_LDO35_LEGACY_ENUM_ID": "16U",
    "S2MPU08_A7_LDO2_VSEL_REG": "0x2dU",
    "S2MPU08_A7_LDO35_VSEL_REG": "0x4fU",
    "S2MPU08_A7_VSEL_MASK": "0x3fU",
    "S2MPU08_A7_MIN_UV": "1800000U",
    "S2MPU08_A7_STEP_UV": "25000U",
    "S2MPU08_A7_LDO2_BOARD_MAX_UV": "3375000U",
    "S2MPU08_A7_LDO35_BOARD_MAX_UV": "3000000U",
}
UNSAFE = re.compile(
    r"\b(?:platform_driver|i2c_driver|module_init|module_platform_driver|"
    r"of_match_table|devm_regulator_register|regulator_register|"
    r"regmap_(?:write|read|update_bits)|i2c_(?:smbus|transfer)|"
    r"exynos_acpm_(?:write|read|update)|gpio_request)\b|"
    r"\.(?:enable|disable|set_voltage_sel|get_voltage_sel|enable_reg|"
    r"enable_mask)\s*=", re.I,
)


def strip_comments(s: str) -> str:
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", s, flags=re.S)


def check_source(c: str, h: str) -> list[str]:
    code, header = strip_comments(c), strip_comments(h)
    failures = []
    if UNSAFE.search(code) or UNSAFE.search(header):
        failures.append("hardware accesses, registration or voltage-changing operations forbidden")
    if re.search(r"\b(?:permissive|jackpotlte|s2mps11)\b", code + header, re.I):
        failures.append("foreign device/PMIC or SELinux bypass")
    for name, value in REQUIRED_CONSTANTS.items():
        if not re.search(rf"^\s*#define\s+{name}\s+{re.escape(value)}\s*$", header, re.M):
            failures.append(f"wrong/missing source-backed {name}")
    if code.count("regulator_list_voltage_linear") != 1 or code.count("regulator_map_voltage_linear") != 1:
        failures.append("kernel descriptors must be voltage calculation only")
    if len(re.findall(r'\.vsel_reg\s*=\s*S2MPU08_A7_LDO(?:2|35)_VSEL_REG\s*,', code)) != 2:
        failures.append("must list exactly LDO2 and LDO35 voltage selectors")
    for rail, legacy in (("2", "1"), ("35", "16")):
        if not re.search(
            rf'\.id\s*=\s*S2MPU08_A7_LDO{rail}_LEGACY_ENUM_ID\s*,', code
        ):
            failures.append(f"incorrect legacy enum ID for LDO{rail}; expected {legacy}")
    if not re.search(
        r"\.n_voltages\s*=\s*\(S2MPU08_A7_LDO35_BOARD_MAX_UV\s*-"
        r"\s*S2MPU08_A7_MIN_UV\)\s*/\s*S2MPU08_A7_STEP_UV\s*\+\s*1U\s*,",
        code,
    ):
        failures.append("LDO35 descriptor may expose more than 3.0V board maximum")
    if not re.search(r"\bs2mpu08_a7_needs_rev0_ldo_guard\s*\(", header):
        failures.append("rev0 LDO35/LDO36 guard not defined")
    if not re.search(r"\bs2mpu08_a7_voltage_to_sel\s*\(", header):
        failures.append("voltage conversion logic missing")
    if not re.search(r"\bs2mpu08_a7_sel_to_voltage\s*\(", header):
        failures.append("reverse selector validation missing")
    return failures


if __name__ == "__main__":
    bad = check_source(SOURCE.read_text(encoding="utf8"), HEADER.read_text(encoding="utf8"))
    if bad:
        for error in bad:
            print("FAIL:", error)
        raise SystemExit(1)
    print("PASS: standalone S2MPU08 voltage-only A7 source (no hardware writes or registration)")
