#!/usr/bin/env python3
"""Read-only structural audit of the research manifest. No Android build or flashing."""
from pathlib import Path
import sys
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "lineage-18.1-research.xml"
EXPECTED = {
    "device/samsung/a7y18lte": "device_samsung_a7y18lte",
    "device/samsung/exynos7885-common": "device_samsung_exynos7885-common",
    "kernel/samsung/exynos7885": "kernel_samsung_exynos7885",
}
PINNED_REVISIONS = {
    'device/samsung/a7y18lte': 'f17643ba01010c45b628d5acb8f48350ded61606',
    'device/samsung/exynos7885-common': 'f2ce8d2093711026f021cba7036334d381d455ef',
    'kernel/samsung/exynos7885': '6020dfa8315134187f07ca903c9d2ed7ee0256f5'
}
BLOCKERS = [
    "vendor/samsung/a7y18lte",
    "vendor/samsung/exynos7885-common",
    "hardware/samsung_slsi-linaro",
]

def main() -> int:
    try:
        root = ET.parse(MANIFEST).getroot()
    except (OSError, ET.ParseError) as exc:
        print(f"FAIL: manifest cannot be parsed: {exc}")
        return 1
    if root.tag != "manifest":
        print("FAIL: expected <manifest> root")
        return 1
    remotes = {r.get("name"): r.get("fetch") for r in root.findall("remote")}
    if remotes.get("exynos7885-dev") != "https://github.com/exynos7885-dev/":
        print("FAIL: unexpected remote URL")
        return 1
    projects = root.findall("project")
    paths = [p.get("path") for p in projects]
    if len(paths) != len(set(paths)):
        print("FAIL: duplicate project paths")
        return 1
    for path, name in EXPECTED.items():
        match = next((p for p in projects if p.get("path") == path), None)
        if match is None or match.get("name") != name:
            print(f"FAIL: missing or unexpected project at {path}")
            return 1
        if match.get("remote") != "exynos7885-dev":
            print(f"FAIL: unexpected remote at {path}")
            return 1
        if not re.fullmatch(r"[0-9a-f]{40}", match.get("revision") or ""):
            print(f"FAIL: invalid pinned SHA at {path}")
            return 1
        if match.get("revision") != PINNED_REVISIONS[path]:
            print(f"FAIL: unexpected revision at {path}")
            return 1
    if len(projects) != len(EXPECTED):
        print("FAIL: unexpected additional projects")
        return 1
    print("PASS: three known baseline projects pinned to verified SHA revisions.")
    for path in BLOCKERS:
        print(f"BLOCKED: unresolved external dependency: {path}")
    print("RESEARCH ONLY: not a complete build manifest or Android 17 ROM.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
