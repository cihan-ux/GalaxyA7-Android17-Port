#!/usr/bin/env python3
"""Check the pinned Android 17 NetBpfLoad kernel-version gate from actual source.

This checks one loader precondition, NOT kernel runtime features or ROM bootability.
No network access is required when given the two pinned source files.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
KERNEL_MAKEFILE = ROOT / "tests/fixtures/upstream/kernel/Makefile"

# The two inputs are loaded from the same pinned LineageOS 24.0 source revision.
PINNED_CONNECTIVITY_COMMIT = "7c04d866538e6f689823b769fb5c1e614ca0e295"
GATE_NAMES = ("isAtLeastU", "isAtLeastV", "isAtLeast25Q2",
              "isAtLeast25Q4", "isAtLeast26Q4")


def kernel_version(makefile: str) -> tuple[int, int, int]:
    parts = []
    for key in ("VERSION", "PATCHLEVEL", "SUBLEVEL"):
        matches = re.findall(rf"^\s*{key}\s*=\s*(\d+)\s*$", makefile, re.M)
        if len(matches) != 1:
            raise ValueError(f"Expected one kernel Makefile {key} entry")
        parts.append(int(matches[0]))
    return tuple(parts)


def parse_loader_gates(loader: str, utils: str) -> list[tuple[int, tuple[int, int]]]:
    """Require the actual upstream minimum-kernel check and its SDK threshold.

    Reject renamed/missing gates rather than silently assuming the old source
    still describes the current Android 17 branch.
    """
    base = re.findall(
        r"if\s*\(\s*!isAtLeastKernelVersion\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*\)",
        loader,
    )
    if (4, 9) not in [(int(a), int(b)) for a, b in base]:
        raise ValueError("Unconditional kernel >=4.9 loader gate not found")
    gates = [(0, (4, 9))]
    for name in GATE_NAMES:
        sdk = re.findall(
            rf"const\s+bool\s+{name}\s*=\s*\(\s*api_level_full\s*>=\s*(\d+)\s*\)",
            utils,
        )
        kernel = re.findall(
            rf"if\s*\(\s*{name}\s*&&\s*!isAtLeastKernelVersion\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*\)",
            loader,
        )
        if len(sdk) != 1 or len(kernel) != 1:
            raise ValueError(f"Required version gate {name} is missing/ambiguous")
        gates.append((int(sdk[0]), (int(kernel[0][0]), int(kernel[0][1]))))
    thresholds = [sdk for sdk, _ in gates]
    if thresholds != sorted(thresholds) or len(set(thresholds)) != len(thresholds):
        raise ValueError("Version gates are not ordered or contain duplicates")
    minimums = [major * 1000 + minor for _, (major, minor) in gates]
    if minimums != sorted(minimums):
        raise ValueError("Loader kernel minima are not monotonic")
    return gates


def minimum_loader_kernel(api_level_full: int,
                          gates: list[tuple[int, tuple[int, int]]]) -> tuple[int, int]:
    if api_level_full <= 0:
        raise ValueError("Invalid api_level_full")
    return max((minimum for threshold, minimum in gates
                if api_level_full >= threshold), default=(0, 0))


def evaluate(api_level_full: int, source_kernel: tuple[int, int, int],
             gates: list[tuple[int, tuple[int, int]]]) -> tuple[bool, tuple[int, int]]:
    minimum = minimum_loader_kernel(api_level_full, gates)
    return source_kernel[:2] >= minimum, minimum


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", required=True, type=Path)
    parser.add_argument("--utils", required=True, type=Path)
    parser.add_argument("--target-api-full", type=int, default=3700)
    parser.add_argument("--expected-status", choices=("blocked", "version-gate-pass"),
                        required=True)
    args = parser.parse_args()
    try:
        gates = parse_loader_gates(args.loader.read_text(), args.utils.read_text())
        version = kernel_version(KERNEL_MAKEFILE.read_text())
        passes, minimum = evaluate(args.target_api_full, version, gates)
    except (OSError, ValueError) as exc:
        print(f"ERROR: cannot verify pinned source requirements: {exc}", file=sys.stderr)
        return 2
    status = "version-gate-pass" if passes else "blocked"
    print(f"PINNED LineageOS Connectivity: {PINNED_CONNECTIVITY_COMMIT}")
    print(f"TARGET api_level_full={args.target_api_full}")
    print(f"KERNEL source={'.'.join(map(str, version))}")
    print(f"REQUIRED by NetBpfLoad version checks >= {minimum[0]}.{minimum[1]}")
    print(f"RESULT: {status.upper()}")
    print("NOT TESTED: BPF feature support, HALs, VINTF, vendor ABI, boot or Android 17 ROM.")
    if args.expected_status != status:
        print(f"Unexpected gate result: expected {args.expected_status}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
