#!/usr/bin/env python3
"""Read-only, offline analysis of a *manually sanitized* Android partition-name list.

Never connects to a phone, changes partitions, or implies that a super partition
is safe to flash. Names alone cannot establish partition size or mapping.
"""
import argparse
from pathlib import Path
import re

EXPECTED = {"boot", "recovery", "system", "vendor", "odm"}
DYNAMIC_HINTS = {"super", "metadata", "product", "system_ext"}

def parse_names(text):
    names = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Only plain names, not ls -l output or device paths.
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", line):
            raise ValueError("Use one lowercase partition name per line (no paths or identifiers)")
        names.add(line)
    return names

def assess(names):
    missing = sorted(EXPECTED - names)
    return [
        "Present expected names: " + (", ".join(sorted(EXPECTED & names)) or "(none)"),
        "Missing or not visible: " + (", ".join(missing) or "(none)"),
        "Dynamic-layout hints: " + (", ".join(sorted(DYNAMIC_HINTS & names)) or "(none visible)"),
        "NOT VERIFIED: partition sizes, super metadata, mount topology, bootloader and flash compatibility.",
        "STOP: do not repartition or flash based on this report.",
    ]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names_file", type=Path)
    args = parser.parse_args()
    try:
        names = parse_names(args.names_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print("\n".join(assess(names)))

if __name__ == "__main__":
    main()
