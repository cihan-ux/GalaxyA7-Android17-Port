#!/usr/bin/env python3
"""Stage/check a Linux 6.15 arm64 Android 17 kernel research configuration.

Success means exact source settings, NOT Android runtime feature parity or bootability.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

from check_android17_netbpf_gate import (
    evaluate, kernel_version, parse_loader_gates,
)

ROOT = Path(__file__).resolve().parents[1]
FRAGMENT = ROOT / "port/linux-6.15/config/android17-research.fragment"
ENABLE_ONLY = frozenset({
    "BPF_SYSCALL",
    "BPF_JIT",
    "CGROUP_BPF",
    "ANDROID_BINDER_IPC",
    "ANDROID_BINDERFS",
    "SECURITY_NETWORK",
    "SECURITY_SELINUX",
})
REQUIRED_COMPILED = ENABLE_ONLY | frozenset({
    "BPF", "ARCH_EXYNOS", "MMC", "MMC_DW", "MMC_DW_EXYNOS",
    "EXYNOS_ARM64_COMMON_CLK", "PINCTRL_EXYNOS", "PINCTRL_EXYNOS_ARM64",
})


def parse_fragment(content: str) -> tuple[str, ...]:
    keys = []
    for number, row in enumerate(content.splitlines(), 1):
        row = row.strip()
        if not row or row.startswith("#"):
            continue
        match = re.fullmatch(r"CONFIG_([A-Z0-9_]+)=y", row)
        if not match:
            raise ValueError(f"Unsupported kernel config statement at line {number}: {row}")
        key = match.group(1)
        if key in keys:
            raise ValueError(f"Duplicate kernel config option: {key}")
        keys.append(key)
    if set(keys) != ENABLE_ONLY:
        raise ValueError(f"Expected precisely {sorted(ENABLE_ONLY)}; got {sorted(keys)}")
    return tuple(keys)


def read_config(content: str) -> dict[str, str]:
    values = {}
    for row in content.splitlines():
        match = re.fullmatch(r"CONFIG_([A-Z0-9_]+)=(.+)", row.strip())
        if match:
            if match.group(1) in values:
                raise ValueError(f"Duplicate evaluated .config entry: {match.group(1)}")
            values[match.group(1)] = match.group(2)
    return values


def check_features(content: str) -> list[str]:
    values = read_config(content)
    return [f"CONFIG_{key} expected y, observed {values.get(key, 'unset')}"
            for key in sorted(REQUIRED_COMPILED) if values.get(key) != "y"]


def check_version(makefile: str, loader: str, utils: str) -> dict[int, tuple[bool, tuple[int,int]]]:
    version = kernel_version(makefile)
    if version != (6, 15, 0):
        raise ValueError(f"Unexpected modern kernel version {version}; expected 6.15.0-rc1")
    if not re.search(r"^EXTRAVERSION\s*=\s*-rc1\s*$", makefile, re.M):
        raise ValueError("Expected Linux 6.15.0-rc1 source marker")
    gates = parse_loader_gates(loader, utils)
    results = {api: evaluate(api, version, gates) for api in (3700, 3710)}
    if any(not passed for passed, _minimum in results.values()):
        raise ValueError("Unexpected Android 17 NetBpfLoad version gate failure")
    return results


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    stage = sub.add_parser("stage", help="Enable only the reviewed config options")
    stage.add_argument("--config", type=Path, required=True)
    stage.add_argument("--config-script", type=Path, required=True)
    check = sub.add_parser("check", help="Inspect evaluated .config and pinned source version gates")
    check.add_argument("--config", type=Path, required=True)
    check.add_argument("--makefile", type=Path, required=True)
    check.add_argument("--loader", type=Path, required=True)
    check.add_argument("--utils", type=Path, required=True)
    args = cli.parse_args()
    try:
        options = parse_fragment(FRAGMENT.read_text(encoding="utf-8"))
        if args.command == "stage":
            if not args.config.is_file() or not args.config_script.is_file():
                raise ValueError("Kernel .config or scripts/config missing")
            subprocess.run(
                [str(args.config_script), "--file", str(args.config),
                 *(argument for key in options for argument in ("--enable", key))],
                check=True,
            )
            print(f"STAGED {len(options)} reviewed Android Binder/SELinux/BPF options")
            return 0
        failures = check_features(args.config.read_text(encoding="utf-8"))
        results = check_version(
            args.makefile.read_text(encoding="utf-8"),
            args.loader.read_text(encoding="utf-8"),
            args.utils.read_text(encoding="utf-8"),
        )
        for api, (passed, minimum) in results.items():
            print(f"Android API {api}: Linux version threshold >= {minimum[0]}.{minimum[1]}:"
                  f" {'PASS' if passed else 'BLOCKED'} (version only)")
        for failure in failures:
            print("CONFIG ERROR:", failure, file=sys.stderr)
        if failures:
            return 1
        print(f"CONFIG PASS: {len(REQUIRED_COMPILED)} requested kernel features evaluated to y")
        print("NOT TESTED: runtime BPF, binder services, real A7 hardware, SELinux neverallows, vendor VINTF, Android 17 boot.")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
