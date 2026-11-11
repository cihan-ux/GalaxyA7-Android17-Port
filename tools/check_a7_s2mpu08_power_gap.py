#!/usr/bin/env python3
"""Reproduce the S2MPU08 PMIC/regulator driver gap against immutable kernel files.

A *passing* run with --expected-status blocked means a real Android 17 board
power prerequisite is MISSING from inspected modern sources, not that a
PMIC driver, kernel or ROM works.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

LEGACY_COMMIT = "6020dfa8315134187f07ca903c9d2ed7ee0256f5"
MODERN_COMMIT = "c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c"
MFD_OPTION = "MFD_S2MPU08"
REG_OPTION = "REGULATOR_S2MPU08"
DT_COMPAT = "samsung,s2mpu08mfd"
REGULATOR_RAILS = {"vqmmc": "LDO2", "vmmc": "LDO35"}


def config_declares(content: str, name: str) -> bool:
    return re.search(rf"^config\s+{re.escape(name)}\s*$", content, re.M) is not None


def makefile_references(content: str, name: str) -> bool:
    return re.search(rf"^\s*obj-\$\(CONFIG_{re.escape(name)}\)\s*[+:]?=\s*.+$",
                     content, re.M) is not None


def pmic_node_and_rails(dts: str) -> list[str]:
    errors = []
    if re.search(r'compatible\s*=\s*"samsung,s2mpu08mfd"\s*;', dts) is None:
        errors.append("A7 legacy PMIC compatible not found")
    if re.search(r'\bacpm-ipc-channel\s*=\s*<2>\s*;', dts) is None:
        errors.append("A7 PMIC ACPM channel not found")
    for rail_name, node_name in REGULATOR_RAILS.items():
        # Source contains named LDO2 and LDO35 regulators under S2MPU08.
        pattern = (rf'\b(?:l\d+_reg):\s*{re.escape(node_name)}\s*\{{'
                   rf'[^{{}}]*?\bregulator-name\s*=\s*"{re.escape(rail_name)}"\s*;')
        if re.search(pattern, dts, re.S) is None:
            errors.append(f"A7 {node_name}/{rail_name} source mapping absent")
    return errors


def audit_sources(sources: dict[str, str]) -> tuple[str, list[str]]:
    issues = pmic_node_and_rails(sources["legacy_dts"])
    for kind, option in (("mfd", MFD_OPTION), ("reg", REG_OPTION)):
        old_kconfig = sources[f"legacy_{kind}_kconfig"]
        old_makefile = sources[f"legacy_{kind}_makefile"]
        new_kconfig = sources[f"modern_{kind}_kconfig"]
        new_makefile = sources[f"modern_{kind}_makefile"]
        if not config_declares(old_kconfig, option):
            issues.append(f"Legacy Kconfig lacks {option}")
        if not makefile_references(old_makefile, option):
            issues.append(f"Legacy Makefile lacks {option}")
        if config_declares(new_kconfig, option) or makefile_references(new_makefile, option):
            issues.append(f"Modern source now has {option}; reassess instead of reporting blocked")
    for key, marker in (
        ("legacy_mfd_core", "exynos_acpm_read_reg"),
        ("legacy_regulator", "S2MPU08_LDO35"),
        ("legacy_regulator", "S2MPU08_LDO36"),
        ("legacy_mfd_core", "s2mpu08_read_reg"),
    ):
        if marker not in sources[key]:
            issues.append(f"Missing historical driver evidence: {key}: {marker}")
    modern_core = sources["modern_sec_core"]
    if DT_COMPAT in modern_core or "s2mpu08" in modern_core.lower():
        issues.append("Modern sec-core has S2MPU08 reference; re-audit support")
    if "s2mpu02" not in modern_core.lower():
        issues.append("Modern SEC core source unexpectedly lacks reference to S2MPU02")
    status = "blocked" if not issues else "source-evidence-changed"
    return status, issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in (
        "legacy_dts", "legacy_mfd_kconfig", "legacy_mfd_makefile",
        "legacy_reg_kconfig", "legacy_reg_makefile",
        "legacy_mfd_core", "legacy_regulator",
        "modern_mfd_kconfig", "modern_mfd_makefile",
        "modern_reg_kconfig", "modern_reg_makefile", "modern_sec_core",
    ):
        parser.add_argument("--" + key.replace("_", "-"), required=True, type=Path)
    parser.add_argument("--expected-status", choices=("blocked",), required=True)
    args = parser.parse_args()
    try:
        sources = {key: getattr(args, key).read_text(encoding="utf-8")
                   for key in (
                       "legacy_dts", "legacy_mfd_kconfig", "legacy_mfd_makefile",
                       "legacy_reg_kconfig", "legacy_reg_makefile",
                       "legacy_mfd_core", "legacy_regulator",
                       "modern_mfd_kconfig", "modern_mfd_makefile",
                       "modern_reg_kconfig", "modern_reg_makefile", "modern_sec_core",
                   )}
        status, issues = audit_sources(sources)
    except OSError as exc:
        print(f"ERROR: missing pinned source: {exc}", file=sys.stderr)
        return 2
    print(f"Legacy A7 kernel: {LEGACY_COMMIT}")
    print(f"Experimental modern kernel: {MODERN_COMMIT}")
    print(f"A7 PMIC: {DT_COMPAT}; ACPM IPC=2; rails LDO2/vqmmc and LDO35/vmmc")
    print(f"S2MPU08 source-port STATUS: {status.upper()}")
    for issue in issues:
        print(f"REVIEW REQUIRED: {issue}", file=sys.stderr)
    print("No S2MPU08 MFD/regulator integration was established in the inspected Linux 6.15 Kconfigs, Makefiles or SEC core.")
    print("This check only covers pinned source paths. It does not prove complete source absence or runtime electrical behavior.")
    print("DO NOT substitute S2MPU02/05 register layouts, inject fake fixed-voltage supplies, or flash.")
    return 0 if status == args.expected_status and not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
