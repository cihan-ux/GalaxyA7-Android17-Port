#!/usr/bin/env python3
"""Source-only VINTF FCM-3 HAL declaration preflight for Galaxy A7 2018.

Compares TWO pinned source device manifests with the pinned 19.1 framework
matrix. This cannot replace libvintf/checkvintf: merged vendor/ODM runtime
manifests, device SKU, actual service registration and kernel configs are
unknown. Any "observed" status means a plausible XML declaration only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


def root_of(content: str, tag: str) -> ET.Element:
    root = ET.fromstring(content)
    if root.tag != tag:
        raise ValueError(f"Expected XML root {tag}, got {root.tag}")
    return root


def parse_version(value: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"([0-9]+)\.([0-9]+)(?:-([0-9]+))?", value)
    if not match:
        return None
    # The low end of a matrix version range is the minimum requirement.
    return int(match.group(1)), int(match.group(2))


def versions_of(hal: ET.Element) -> list[tuple[int, int]]:
    return [version for v in hal.findall("version")
            if (version := parse_version(v.text or "")) is not None]


def interface_of(hal: ET.Element) -> dict[str, set[str]]:
    interfaces: dict[str, set[str]] = {}
    for interface in hal.findall("interface"):
        name = interface.findtext("name")
        if name:
            instances = {v.text for v in interface.findall("instance") if v.text}
            instances |= {"regex:" + v.text for v in
                          interface.findall("regex-instance") if v.text}
            interfaces.setdefault(name, set()).update(instances)
    return interfaces


def instance_declared(needed: str, observed: set[str]) -> bool:
    if needed in observed:
        return True
    # A manifest's regex-instance can plausibly cover a required fixed name.
    for item in observed:
        if item.startswith("regex:"):
            try:
                if re.fullmatch(item[6:], needed):
                    return True
            except re.error:
                pass
    return False


def matches_required_interface(required: ET.Element, candidates: list[ET.Element]) -> bool:
    for req in required.findall("interface"):
        name = req.findtext("name") or ""
        if not name:
            return False
        observed = set().union(*(interface_of(h).get(name, set()) for h in candidates))
        for fixed in req.findall("instance"):
            if not fixed.text or not instance_declared(fixed.text, observed):
                return False
        # An FCM regex requirement is not an exact instance; here we only
        # establish that an interface with >=1 declared instance exists.
        if req.findall("regex-instance") and not observed:
            return False
        if not req.findall("instance") and not req.findall("regex-instance") and not observed:
            return False
    return True


def audit(device: str, common: str, matrix: str) -> dict:
    dev = root_of(device, "manifest")
    shared = root_of(common, "manifest")
    fcm = root_of(matrix, "compatibility-matrix")
    if any(x.attrib.get("type") != "device" or x.attrib.get("target-level") != "3"
           for x in (dev, shared)):
        raise ValueError("Expected original device manifests, both target-level 3")
    if fcm.attrib.get("type") != "framework" or fcm.attrib.get("level") != "3":
        raise ValueError("Expected framework compatibility matrix level 3")
    declared = [*dev.findall("hal"), *shared.findall("hal")]
    results = []
    for req in fcm.findall("hal"):
        if req.attrib.get("optional", "false") != "false":
            continue
        name = req.findtext("name")
        fmt = req.attrib.get("format")
        if not name or not fmt:
            raise ValueError("Mandatory FCM HAL entry lacks name/format")
        required_versions = versions_of(req)
        if not required_versions:
            raise ValueError(f"Mandatory FCM HAL has no parseable version: {name}")
        candidates = [x for x in declared
                      if x.findtext("name") == name and x.attrib.get("format") == fmt
                      and versions_of(x)]
        match_versions = [x for x in candidates if any(
            actual_major == needed_major and actual_minor >= needed_minor
            for actual_major, actual_minor in versions_of(x)
            for needed_major, needed_minor in required_versions
        )]
        if not candidates:
            status = "not_declared_in_two_sources"
        elif not match_versions:
            status = "version_not_observed"
        elif not matches_required_interface(req, match_versions):
            status = "interface_not_observed"
        else:
            status = "plausible_declaration"
        results.append({
            "hal": name,
            "status": status,
            "required_versions": [v.text for v in req.findall("version")],
            "observed_versions": sorted(set(
                v.text for h in candidates for v in h.findall("version") if v.text)),
        })
    if len(results) != 9 or len({r["hal"] for r in results}) != 9:
        raise ValueError("Unexpected mandatory FCM3 HAL set; review pinned source")
    missing = [r["hal"] for r in results if r["status"] != "plausible_declaration"]
    return {
        "scope": "A7 device and Exynos7885-common XML only; NOT complete VINTF",
        "mandatory_hal_groups": len(results),
        "plausible_declarations": len(results) - len(missing),
        "needs_further_evidence": missing,
        "hal_groups": results,
        "runtime_compatible": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device-manifest", required=True, type=Path)
    parser.add_argument("--common-manifest", required=True, type=Path)
    parser.add_argument("--fcm3", required=True, type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    try:
        report = audit(args.device_manifest.read_text(encoding="utf-8"),
                       args.common_manifest.read_text(encoding="utf-8"),
                       args.fcm3.read_text(encoding="utf-8"))
    except (OSError, ET.ParseError, ValueError) as exc:
        print(f"FAIL: invalid pinned XML / scope: {exc}", file=sys.stderr)
        return 1
    print("SOURCE-ONLY:", report["plausible_declarations"], "/",
          report["mandatory_hal_groups"], "mandatory FCM3 HAL groups declared plausibly")
    for group in report["hal_groups"]:
        print("  ", group["status"], group["hal"])
    print("NOT CHECKVINTF: other vendor manifests, kernel, services and real hardware unverified")
    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
