#!/usr/bin/env python3
"""Check A7 S2MPU08 Linux 6.15 lab against pinned Samsung PMIC enum/voltage source."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "port/linux-6.15/drivers/regulator/s2mpu08-a7-voltage-lab.h"
EXPECTED_ENUM = {
    "LDO1": 0,
    "LDO2": 1,
    "LDO14": 13,
    "LDO33": 14,
    "LDO34": 15,
    "LDO35": 16,
    "LDO36": 17,
    "LDO37": 18,
    "BUCK1": 19,
    "BUCK8": 26,
}
LEGACY_CONST = {
    "S2MPU08_PMIC_REG_L2CTRL1": 0x2D,
    "S2MPU08_PMIC_REG_L35CTRL": 0x4F,
    "S2MPU08_LDO_MIN3": 1800000,
    "S2MPU08_LDO_STEP2": 25000,
    "S2MPU08_LDO_VSEL_MASK": 0x3F,
}
LAB_CONST = {
    "S2MPU08_A7_LDO2_LEGACY_ENUM_ID": 1,
    "S2MPU08_A7_LDO35_LEGACY_ENUM_ID": 16,
    "S2MPU08_A7_LDO2_VSEL_REG": 0x2D,
    "S2MPU08_A7_LDO35_VSEL_REG": 0x4F,
    "S2MPU08_A7_MIN_UV": 1800000,
    "S2MPU08_A7_STEP_UV": 25000,
    "S2MPU08_A7_VSEL_MASK": 0x3F,
}


def remove_comments(source: str) -> str:
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)


def parse_enum(source: str) -> dict[str, int]:
    code = remove_comments(source)
    enums = re.findall(r"\benum\s+S2MPU08_regulators\s*\{(.*?)\}\s*;", code, re.S)
    if len(enums) != 1:
        raise ValueError("Expected exactly one S2MPU08_regulators enum")
    result = {}
    index = 0
    for item in enums[0].split(","):
        token = item.strip()
        if not token:
            continue
        match = re.fullmatch(r"S2MPU08_((?:LDO|BUCK)\d+|REG_MAX)(?:\s*=\s*(\d+))?", token)
        if not match:
            raise ValueError(f"Unsupported enum syntax: {token!r}")
        if match.group(2) is not None:
            index = int(match.group(2))
        name = match.group(1)
        if name in result:
            raise ValueError(f"Duplicate enum entry {name}")
        result[name] = index
        index += 1
    return result


def read_define(source: str, name: str) -> int:
    code = remove_comments(source)
    pattern = rf"^\s*#define\s+{re.escape(name)}\s+(0[xX][0-9a-fA-F]+|\d+)[uU]?\s*$"
    match = re.findall(pattern, code, re.M)
    if len(match) != 1:
        raise ValueError(f"Expected one integer macro for {name}")
    return int(match[0], 0)


def audit(legacy: str, lab: str) -> list[str]:
    problems = []
    try:
        enum_values = parse_enum(legacy)
        for name, actual in EXPECTED_ENUM.items():
            if enum_values.get(name) != actual:
                problems.append(f"Historical enum {name} changed: {enum_values.get(name)}, expected {actual}")
        if any(f"LDO{k}" in enum_values for k in range(15, 33)):
            problems.append("Unexpected active LDO15..LDO32 enum values (sparse IDs changed)")
        for name, actual in LEGACY_CONST.items():
            if read_define(legacy, name) != actual:
                problems.append(f"Historical {name} source value changed")
        for name, actual in LAB_CONST.items():
            if read_define(lab, name) != actual:
                problems.append(f"Lab {name} differs from historical A7 values")
    except ValueError as exc:
        problems.append(str(exc))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-header", required=True, type=Path)
    options = parser.parse_args()
    try:
        failures = audit(options.legacy_header.read_text(encoding="utf-8"),
                         LAB.read_text(encoding="utf-8"))
    except OSError as exc:
        print("ERROR: cannot load pinned historical source:", exc)
        return 2
    if failures:
        for issue in failures:
            print("FAIL:", issue)
        return 1
    print("PASS: pinned S2MPU08 historical enum LDO2=1 LDO35=16, registers, min/step/mask")
    print("Legacy LDO2=channel 2, enum ID 1; LDO35=channel 35, enum ID 16.")
    print("Source identity only; NOT an operational S2MPU08 ACPM/regulator driver.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
