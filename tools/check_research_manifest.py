#!/usr/bin/env python3
"""Read-only structural audit of the research manifest. No Android build or flashing."""
from pathlib import Path
import sys
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "lineage-18.1-research.xml"
PROJECTS = {
    "device/samsung/a7y18lte": ("device_samsung_a7y18lte", "exynos7885-dev", "f17643ba01010c45b628d5acb8f48350ded61606"),
    "device/samsung/exynos7885-common": ("device_samsung_exynos7885-common", "exynos7885-dev", "f2ce8d2093711026f021cba7036334d381d455ef"),
    "kernel/samsung/exynos7885": ("kernel_samsung_exynos7885", "exynos7885-dev", "6020dfa8315134187f07ca903c9d2ed7ee0256f5"),
    "vendor/samsung/a7y18lte": ("proprietary_vendor_samsung_a7y18lte", "exynos7885-dev", "5e79a4f2536f755a1356636794df4b1bf0cfe780"),
    "vendor/samsung/exynos7885-common": ("proprietary_vendor_samsung_exynos7885-common", "exynos7885-dev", "51a9202e8b6d5e4852fdfbb31e5cd1e6769599af"),
    "hardware/samsung": ("hardware_samsung", "exynos7885-dev", "082709ec235fd60f55bff0fb0deb8eae12bf0622"),
    "device/lineage/sepolicy": ("android_device_lineage_sepolicy", "lineageos", "02f04d2b0a57f1c7435dc9f2ce8fac2640b38782"),
    "device/samsung_slsi/sepolicy": ("android_device_samsung_slsi_sepolicy", "lineageos", "9968b62f8f76c22143a8fc7491440aa11c32e6f4"),
    "hardware/samsung_slsi-linaro/config": ("hardware_samsung_slsi-linaro_config", "exynos7885-dev", "c7a3ba8a1d8e9a467284f8e4e36672b33494e5f8"),
    "hardware/samsung_slsi-linaro/exynos": ("hardware_samsung_slsi-linaro_exynos", "exynos7885-dev", "f05f00d0280b5e84678a444a195ff6ccdb95d813"),
    "hardware/samsung_slsi-linaro/exynos5": ("hardware_samsung_slsi-linaro_exynos5", "exynos7885-dev", "6dff1105f24bb5a7d96806f9c61265658e836e25"),
    "hardware/samsung_slsi-linaro/graphics": ("hardware_samsung_slsi-linaro_graphics", "exynos7885-dev", "7c28107c046cd666b01adef06617482e26311ab7"),
    "hardware/samsung_slsi-linaro/openmax": ("hardware_samsung_slsi-linaro_openmax", "exynos7885-dev", "bf76218765ae6b3636acf0d898bdc81c1a912968"),
}
EXPECTED = {path: value[0] for path, value in PROJECTS.items()}
PINNED_REVISIONS = {path: value[2] for path, value in PROJECTS.items()}
BLOCKERS = ["hardware/samsung_slsi-linaro/interfaces", "hardware/samsung_slsi/scsc_wifibt"]


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
    if remotes.get("lineageos") != "https://github.com/LineageOS/":
        print("FAIL: unexpected LineageOS remote URL")
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
        if match.get("remote") != PROJECTS[path][1]:
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
    print(f"PASS: {len(PROJECTS)} research projects pinned to verified SHA revisions.")
    for path in BLOCKERS:
        print(f"BLOCKED: unresolved external dependency: {path}")
    print("RESEARCH ONLY: not a complete build manifest or Android 17 ROM.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
