#!/usr/bin/env python3
"""Compare pinned old and modern ACPM C struct declarations to the ABI lab.

No host or kernel code maps SRAM or enables a mailbox/controller.
"""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "port/linux-6.15/drivers/firmware/samsung/exynos7885-acpm-sram-abi-lab.c"


def scrub(src):
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", src, flags=re.S)


def fields(src, name):
    chunks = re.findall(r"\bstruct\s+" + re.escape(name) + r"\s*\{(.*?)\}\s*;", scrub(src), re.S)
    if len(chunks) != 1:
        raise ValueError("Missing/ambiguous struct " + name)
    body = re.sub(r"^\s*#(?:ifn?def|else|endif).*?$", "", chunks[0], flags=re.M)
    return re.findall(r"\b([a-zA-Z_]\w*)\s*(?:\[[0-9]+\])?\s*;", body)


def audit(old_fw, modern_fw, lab):
    errors = []
    try:
        f = fields(old_fw, "acpm_framework")
        g = fields(modern_fw, "acpm_shmem")
        oi = fields(old_fw, "ipc_channel")
        och = fields(old_fw, "channel_info")
        ng = fields(modern_fw, "acpm_chan_shmem")
    except ValueError as exc:
        return [str(exc)]
    expect = {
        "old firmware first 7": (f[:7], ["plugins", "num_plugins", "ipc_channels", "num_ipc_channels", "pid_framework", "pid_max", "ipc_ap_max"]),
        "modern fw first fields": (g, ["reserved", "chans", "reserved1", "num_chans"]),
        "old IPC header": (oi, ["id", "field", "owner", "type", "ch", "ap_poll"]),
        "old channel_info": (och, ["rx_rear", "rx_front", "rx_base", "rx_indr_buf", "rx_indr_buf_base", "rx_indr_buf_size", "tx_rear", "tx_front", "tx_base", "q_len", "q_elem_size", "credit", "mbox_addr"]),
        "modern IPC channel": (ng, ["id", "reserved", "rx_rear", "rx_front", "rx_base", "reserved1", "tx_rear", "tx_front", "tx_base", "qlen", "mlen", "reserved2", "poll_completion"]),
    }
    for label, (actual, goal) in expect.items():
        if actual != goal:
            errors.append(f"ABI drift in {label}: {actual}")
    for symbol in (
        "sizeof(struct a7_legacy_ipc_channel) == 72",
        "sizeof(struct a7_modern_ipc_channel) == 72",
        "ch.q_elem_size",
        "poll_completion",
        "a7_acpm_validate_pmic_channel",
    ):
        if symbol not in lab:
            errors.append("ABI static check missing: " + symbol)
    if re.search(r"\b(?:ioremap|writel|readl|mbox_send_message|acpm_do_xfer|platform_driver|module_init|regmap_write)\s*\(", scrub(lab)):
        errors.append("Physical ACPM access forbidden in ABI research")
    return errors


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--old-framework", type=Path, required=True)
    ap.add_argument("--new-acpm", type=Path, required=True)
    args = ap.parse_args()
    issues = audit(args.old_framework.read_text(), args.new_acpm.read_text(), LAB.read_text())
    for e in issues:
        print("FAIL:", e)
    if issues:
        raise SystemExit(1)
    print("PASS: pin-verified 7-word ACPM framework prefix and 72-byte channel memory layout")
    print("Only ABI offset alignment is validated; Exynos7885 physical mailbox/firmware still BLOCKED")
