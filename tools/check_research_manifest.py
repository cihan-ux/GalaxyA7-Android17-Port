#!/usr/bin/env python3
"""Read-only structural audit of the research manifest. No Android build or flashing."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "lineage-18.1-research.xml"
EXPECTED = {
    "device/samsung/a7y18lte": "device_samsung_a7y18lte",
    "device/samsung/exynos7885-common": "device_samsung_exynos7885-common",
    "kernel/samsung/exynos7885": "kernel_samsung_exynos7885",
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
        if match.get("revision") != "lineage-18.1":
            print(f"FAIL: unexpected revision at {path}")
            return 1
    print("PASS: three known baseline projects mapped to expected paths.")
    for path in BLOCKERS:
        print(f"BLOCKED: unresolved external dependency: {path}")
    print("RESEARCH ONLY: not a complete build manifest or Android 17 ROM.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
