#!/usr/bin/env python3
"""Compare pinned LineageOS 18.1 common/device HAL XML declarations offline.

This is a *source-level* review of explicit A7 overrides. It is not an Android
17 libvintf compatibility check or a merged, runtime device manifest.
"""

import argparse
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "tests/fixtures/upstream/common/manifest.xml"
DEVICE = ROOT / "tests/fixtures/upstream/device/manifest.xml"

CRITICAL = frozenset({
    "android.hardware.audio",
    "android.hardware.bluetooth",
    "android.hardware.camera.provider",
    "android.hardware.graphics.composer",
    "android.hardware.nfc",
    "android.hardware.radio",
    "android.hardware.biometrics.fingerprint",
    "android.hardware.keymaster",
    "vendor.lineage.touch",
})


def _child_text(element, name):
    found = element.find(name)
    return (found.text or "").strip() if found is not None else ""


def _parse_declaration(hal):
    name = _child_text(hal, "name")
    if not name:
        raise ValueError("HAL declaration missing name")
    kind = hal.get("format", "hidl")
    if kind not in {"hidl", "aidl", "native"}:
        raise ValueError("unexpected HAL format")
    override = hal.get("override", "false")
    if override not in {"true", "false"}:
        raise ValueError("invalid override attribute")
    versions = sorted({(node.text or "").strip() for node in hal.findall("version") if (node.text or "").strip()})
    fqnames = sorted({(node.text or "").strip() for node in hal.findall("fqname") if (node.text or "").strip()})
    interfaces = []
    for interface in hal.findall("interface"):
        interface_name = _child_text(interface, "name")
        if not interface_name:
            raise ValueError("HAL interface missing name")
        for instance in interface.findall("instance"):
            value = (instance.text or "").strip()
            if not value:
                raise ValueError("HAL instance is empty")
            interfaces.append(interface_name + "/" + value)
        for regex_instance in interface.findall("regex-instance"):
            value = (regex_instance.text or "").strip()
            if not value:
                raise ValueError("HAL regex-instance is empty")
            interfaces.append(interface_name + "/regex:" + value)
    return {
        "name": name,
        "format": kind,
        "override": override == "true",
        "versions": versions,
        "fqnames": fqnames,
        "interfaces": sorted(set(interfaces)),
        "has_service_declaration": bool(versions or fqnames or interfaces),
    }


def _parse_manifest(path):
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise ValueError("cannot parse manifest XML") from exc
    if root.tag != "manifest" or root.get("type") != "device":
        raise ValueError("expected a device VINTF manifest")
    target_level = root.get("target-level")
    if not target_level or not target_level.isdigit():
        raise ValueError("missing or invalid target-level")
    declarations = [_parse_declaration(hal) for hal in root.findall("hal")]
    if not declarations:
        raise ValueError("no HAL declarations")
    return target_level, declarations


def audit(common_path=COMMON, device_path=DEVICE):
    """Produce evidence only; do not claim libvintf has assembled this XML."""
    common_level, common = _parse_manifest(common_path)
    device_level, device = _parse_manifest(device_path)
    if common_level != device_level:
        raise ValueError("different target-level values; source merge cannot be inferred")
    names = sorted({entry["name"] for entry in common + device})
    results = []
    for name in names:
        base = [entry for entry in common if entry["name"] == name]
        specific = [entry for entry in device if entry["name"] == name]
        overrides = [entry for entry in specific if entry["override"]]
        if overrides and any(not entry["has_service_declaration"] for entry in overrides):
            effect = "device_empty_override"
        elif overrides:
            effect = "device_declares_override"
        elif specific and base:
            effect = "device_adds_declaration"
        elif specific:
            effect = "device_only"
        else:
            effect = "common_only"
        results.append({
            "name": name,
            "source_effect": effect,
            "common": base,
            "device": specific,
            "critical_for_port": name in CRITICAL,
        })
    return {
        "schema_version": 1,
        "research_only": True,
        "target_level": common_level,
        "common_hal_entries": len(common),
        "device_hal_entries": len(device),
        "hal_names": len(names),
        "declarations": results,
        "caveats": [
            "Override labels summarize pinned source XML only; official libvintf assembly was not run.",
            "A declaration is not proof that the HAL service exists, works, or is supported by Android 17.",
            "Framework compatibility matrices, vendor binaries, and device runtime were not checked.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--common", type=Path, default=COMMON, help="pinned common XML source")
    parser.add_argument("--device", type=Path, default=DEVICE, help="pinned A7 XML source")
    args = parser.parse_args(argv)
    try:
        report = audit(args.common, args.device)
    except ValueError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
