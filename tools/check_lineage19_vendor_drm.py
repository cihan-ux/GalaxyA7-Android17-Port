#!/usr/bin/env python3
"""Check source evidence for an A7 DRM 1.3 VINTF fragment without shipping blobs.

It is possible for a fragment to exist in a vendor repository and yet be
absent from an actual device image. Registration != installation != runtime.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

MODULE = "manifest_android.hardware.drm@1.3-service.widevine"
SRC = "proprietary/vendor/etc/vintf/manifest/" + MODULE + ".xml"
WIDEVINE_BINARY = "android.hardware.drm@1.3-service.widevine"


def analyze(fragment: str, blueprint: str, vendor_make: str,
            common_make: str) -> dict:
    root = ET.fromstring(fragment)
    if root.tag != "manifest" or root.attrib.get("type") != "device":
        raise ValueError("Expected pinned vendor DRM device-manifest fragment")
    hals = [h for h in root.findall("hal")
            if h.findtext("name") == "android.hardware.drm"
            and h.attrib.get("format") == "hidl"]
    if len(hals) != 1:
        raise ValueError("Expected one HIDL DRM declaration in vendor XML")
    fqs = {q.text for q in hals[0].findall("fqname") if q.text}
    expected_fqs = {"@1.3::ICryptoFactory/widevine", "@1.3::IDrmFactory/widevine"}
    if not expected_fqs.issubset(fqs):
        raise ValueError("Widevine 1.3 FQNames missing in vendor fragment")
    mods = re.findall(r"\bprebuilt_etc_xml\s*\{([^{}]+)\}", blueprint, re.S)
    matched = [m for m in mods if re.search(
        r'\bname\s*:\s*"' + re.escape(MODULE) + r'"', m)]
    if len(matched) != 1:
        raise ValueError("One prebuilt_etc_xml registration required")
    module = matched[0]
    if (f'src: "{SRC}"' not in module or 'sub_dir: "vintf/manifest"' not in module
            or "soc_specific: true" not in module):
        raise ValueError("DRM prebuilt registration lacks vetted vendor VINTF path")
    # Explicit module reference check is intentionally limited to TWO mk
    # files. Other inherited makefiles and VINTF fragments are not inspected.
    declared_in_product_mk = (MODULE in vendor_make or MODULE in common_make)
    vendor_binary_listed = WIDEVINE_BINARY in vendor_make
    clearkey_product_listed = "android.hardware.drm@1.3-service.clearkey" in common_make
    return {
        "vendor_xml_has_drm_1_3_fqnames": True,
        "vendor_android_bp_prebuilt_registered": True,
        "explicit_prebuilt_module_reference_in_two_makefiles": declared_in_product_mk,
        "widevine_binary_copy_listed_in_vendor_makefile": vendor_binary_listed,
        "clearkey_product_listed_in_common_makefile": clearkey_product_listed,
        "fragment_confirmed_in_android_12l_output": None,
        "runtime_drm_operational": None,
        "scope": "four pinned text source files only; no assembled vendor or ODM images",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("fragment", "blueprint", "vendor-make", "common-make"):
        ap.add_argument("--" + name, type=Path, required=True)
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()
    try:
        info = analyze(
            args.fragment.read_text(encoding="utf-8"),
            args.blueprint.read_text(encoding="utf-8"),
            args.vendor_make.read_text(encoding="utf-8"),
            args.common_make.read_text(encoding="utf-8"))
    except (OSError, ET.ParseError, ValueError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        return 1
    print("SOURCE CONFIRMED: DRM @1.3 Widevine fragment and prebuilt_etc_xml registered")
    print("ASSEMBLY UNKNOWN: not explicitly listed in the two inspected makefiles")
    print("NO RUNTIME CLAIM: the actual vendor image and checkvintf remain untested")
    if args.json_out:
        args.json_out.write_text(json.dumps(info, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
