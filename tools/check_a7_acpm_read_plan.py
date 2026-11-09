#!/usr/bin/env python3
"""Fail closed on MMIO or wrong-channel additions to the offline ACPM read planner."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "port/linux-6.15/drivers/firmware/samsung/exynos7885-acpm-read-plan-lab.c"
HDR = ROOT / "port/linux-6.15/drivers/firmware/samsung/exynos7885-acpm-read-plan-lab.h"
BLOCKED = re.compile(
    r"\b(?:writel|readl|__raw_writel|__raw_readl|ioremap|devm_ioremap|"
    r"mbox_send_message|acpm_do_xfer|regmap_write|regmap_read|"
    r"module_init|platform_driver_register|regulator_register)\s*\(",
    re.I,
)


def scrub(src):
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", src, flags=re.S)


def audit(source, header):
    code = scrub(source + "\n" + header)
    failures = []
    if BLOCKED.search(code):
        failures.append("offline C helper unexpectedly reaches physical I/O or registers a driver")
    for needle in (
        "a7_acpm_validate_fw_prefix(",
        "a7_acpm_validate_pmic_channel(",
        "s2mpu08_a7_acpm_pack_read(",
        "A7_ACPM_DOORBELL_INTGR0_OFFSET",
        "seq << A7_ACPM_READ_SEQUENCE_SHIFT",
        "(1U << channel->id) << 16",
        "layout.mlen != sizeof(frame)",
        "channel->type != A7_ACPM_QUEUE_TYPE",
        "next_front == rear",
        "a7_acpm_match_s2mpu08_read_reply(",
        "(word & 0x0fffU) == (request->request.word[0] & 0x0fffU)",
        "decision.firmware_status = status",
        "decision.next_rear = (rear + 1U) % ring_count",
        "decision.requires_rear_swap = position != rear",
    ):
        if needle not in code:
            failures.append("source-validated request guard missing: " + needle)
    if re.search(r'\b(?:memcpy|memmove|spin_lock|mutex_lock)\s*\(', code):
        failures.append("offline response plan must not mutate queue or take runtime locks")
    if not re.search(r"#define\s+A7_ACPM_QUEUE_TYPE\s+1U\b", code):
        failures.append("Historical firmware TYPE_QUEUE=1 guard missing")
    if not re.search(r"#define\s+A7_ACPM_DOORBELL_INTGR0_OFFSET\s+0x0008U\b", code):
        failures.append("A7 doorbell must refer to historical INTGR0=0x08")
    return failures


if __name__ == "__main__":
    errors = audit(SRC.read_text(encoding="utf-8"), HDR.read_text(encoding="utf-8"))
    if errors:
        for error in errors:
            print("FAIL:", error)
        raise SystemExit(1)
    print("PASS: mock ACPM read planner invokes only bounded host-memory helpers")
