#!/usr/bin/env python3
"""Offline validator for a user-supplied, privacy-minimized device report.

No ADB, network, firmware access, or flashing. Does not collect device identifiers.
"""
import argparse
from pathlib import Path
import re
import sys

EXPECTED_MODEL = "SM-A750F"
EXPECTED_DEVICE = "a7y18lte"
FIELDS = (
    "ro.product.model",
    "ro.product.device",
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.boot.bootloader",
    "ro.boot.dynamic_partitions",
    "ro.boot.super_partition",
)

def parse_report(raw):
    values = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            raise ValueError("Only KEY=VALUE lines are accepted")
        key, value = (s.strip() for s in line.split("=", 1))
        if key not in FIELDS or key in values:
            raise ValueError(f"Unsupported or duplicate key: {key}")
        if len(value) > 128 or not re.fullmatch(r"[A-Za-z0-9_.+:/-]*", value):
            raise ValueError(f"Invalid value for {key}")
        values[key] = value
    return values

def evaluate(values):
    issues = []
    if values.get("ro.product.model") != EXPECTED_MODEL:
        issues.append("STOP: model is missing or not SM-A750F")
    if values.get("ro.product.device") != EXPECTED_DEVICE:
        issues.append("CHECK: device codename is missing or unexpected")
    if values.get("ro.build.version.sdk") != "29":
        issues.append("CHECK: stock Android 10/API 29 baseline not confirmed")
    bootloader = values.get("ro.boot.bootloader", "")
    if bootloader and "A750F" not in bootloader.upper():
        issues.append("CHECK: bootloader does not identify expected A750F family")
    issues.append("UNVERIFIED: actual partition table, firmware provenance and Android 17 compatibility")
    return issues

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Locally prepared allowlisted KEY=VALUE text")
    args = parser.parse_args()
    try:
        values = parse_report(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"INVALID REPORT: {exc}", file=sys.stderr)
        return 2
    for item in evaluate(values):
        print(item)
    return 0 if values.get("ro.product.model") == EXPECTED_MODEL else 1

if __name__ == "__main__":
    sys.exit(main())
