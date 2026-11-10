#!/usr/bin/env python3
"""Audit read-only A7 ACPM decoder; no live SRAM or device binding."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "port/linux-6.15/drivers/firmware/samsung"
SRC = BASE / "exynos7885-acpm-descriptor-snapshot-lab.c"
HDR = BASE / "exynos7885-acpm-descriptor-snapshot-lab.h"

BLOCKED = re.compile(
    r"\b(?:readl|writel|ioremap|devm_ioremap|memcpy_toio|memcpy_fromio|"
    r"mbox_send_message|regmap_write|spin_lock|mutex_lock|request_irq|"
    r"platform_driver_register|module_init|__raw_readl|__raw_writel|"
    r"volatile)\b", re.I
)


def scrub(source):
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)


def audit(source, header):
    code = scrub(source + "\n" + header)
    errors = []
    if BLOCKED.search(code):
        errors.append("snapshot decoder must never access live hardware or kernel locks")
    for required in (
        "first == second",
        "size_bytes != A7_ACPM_SRAM_BYTES",
        "a7_same_bytes(first, second, A7_ACPM_INITDATA_OFFSET",
        "a7_acpm_validate_fw_prefix(",
        "a7_same_bytes(first, second, offset, sizeof(*ch))",
        "ch->type != A7_ACPM_LEGACY_QUEUE_TYPE",
        "a7_acpm_validate_pmic_channel(",
        "result.layout.mlen != 16U",
        "first != second || first >= qlen",
        "a7_same_index(first, second, ch->ch.rx_rear",
        "a7_same_index(first, second, ch->ch.rx_front",
        "a7_same_index(first, second, ch->ch.tx_rear",
        "a7_same_index(first, second, ch->ch.tx_front",
        "*out = result",
    ):
        if required not in code:
            errors.append("required fail-closed guard missing: " + required)
    return errors


if __name__ == "__main__":
    problems = audit(SRC.read_text(), HDR.read_text())
    for item in problems:
        print("FAIL:", item)
    if problems:
        raise SystemExit(1)
    print("PASS: offline ACPM SRAM snapshot decoder has no live hardware access")
