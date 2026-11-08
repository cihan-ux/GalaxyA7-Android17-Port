#!/usr/bin/env python3
"""Fail-closed validator for nonbootable Galaxy A7 Linux 6.15 GPIO key lab."""
from __future__ import annotations
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "port/linux-6.15/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte-keys-lab.dts"


def check_source(text: str) -> list[str]:
    source = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
    errors = []
    includes = re.findall(r"^\s*#include\s+([^\n]+)", source, re.M)
    expected = ['"exynos7885-a7y18lte-emmc-lab.dts"',
                '<dt-bindings/gpio/gpio.h>', '<dt-bindings/input/input.h>']
    if [i.strip() for i in includes] != expected:
        errors.append("incorrect A7-only includes")
    if re.search(r"\bjackpotlte\b|\bandroidboot\.selinux\b|\bpermissive\b", source, re.I):
        errors.append("foreign A8 board or SELinux bypass")
    if re.search(r"\bmemory(?:@[\da-fA-F]+)?\s*\{|\breserved-memory\s*\{|\bbootargs\s*=", source):
        errors.append("unverified memory or boot configuration")
    if re.search(r"\b(?:reg|ranges|clock-frequency|vmmc-supply|vqmmc-supply)\s*=", source):
        errors.append("unverified physical addresses or power rails")
    if len(re.findall(r'\bcompatible\s*=\s*"gpio-keys"\s*;', source)) != 1:
        errors.append("expected exactly one gpio-keys device")
    if len(re.findall(r'&pinctrl_alive\s*\{', source)) != 1:
        errors.append("expected one alive pinctrl override")
    for node, symbol, pin in (
        ("volume-up", "KEY_VOLUMEUP", 5),
        ("volume-down", "KEY_VOLUMEDOWN", 6),
        ("power", "KEY_POWER", 7),
    ):
        pattern = rf'\b{node}\s*\{{([^{{}}]*)\}}\s*;'
        match = re.search(pattern, source, re.S)
        if match is None:
            errors.append(f"missing {node}")
            continue
        body = match.group(1)
        if not re.search(rf'\blinux,code\s*=\s*<{symbol}>\s*;', body):
            errors.append(f"incorrect {node} keycode")
        if not re.search(rf'\bgpios\s*=\s*<&gpa1\s+{pin}\s+GPIO_ACTIVE_LOW>\s*;', body):
            errors.append(f"incorrect {node} GPIO")
        if node == "power" and not re.search(r'\bwakeup-source\s*;', body):
            errors.append("power wakeup-source missing")
        if node != "power" and re.search(r'\bwakeup-source\b', body):
            errors.append("unexpected wakeup-source")
        pin_pattern = rf'\ba7_key_{"volup" if pin==5 else "voldown" if pin==6 else "power"}\s*:\s*a7-key-[\w-]+-pins\s*\{{([^{{}}]*)\}}\s*;'
        matches = re.findall(pin_pattern, source, re.S)
        if len(matches) != 1 or not re.search(rf'\bsamsung,pins\s*=\s*"gpa1-{pin}"\s*;', matches[0]):
            errors.append(f"missing A7 source-backed pin group for {node}")
    if len(re.findall(r'\bgpios\s*=', source)) != 3:
        errors.append("unexpected GPIO peripherals")
    if len(re.findall(r'\bsamsung,pins\s*=', source)) != 3:
        errors.append("unexpected pinctrl pins")
    return errors


if __name__ == "__main__":
    problems = check_source(PATH.read_text(encoding="utf-8"))
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        raise SystemExit(1)
    print("PASS: A7 gpa1-5/6/7 key mapping source gate (not bootable)")
