#!/usr/bin/env python3
"""Compile a tiny source-gated CIL SELinux Wi-Fi policy and negative test.

This is an isolated compiler smoke test, NOT the Android 17 assembled policy.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MACROS = ROOT / "tests/fixtures/selinux/android17-property-macros.m4"
POLICY = ROOT / "port/lineage-24.0/device/samsung_slsi/sepolicy/patches/0001-exynos7885-typed-vendor-wifi-property.patch"
UPSTREAM = ROOT / "tests/fixtures/selinux/lineage24-slsi-property.te"
UPSTREAM_HAL = ROOT / "tests/fixtures/selinux/lineage24-slsi-hal_wifi_default.te"
SOURCE_CALL = "vendor_internal_prop(vendor_wifi_prop)"
TYPE_LINE = "type vendor_wifi_prop, property_type, vendor_property_type, vendor_internal_property_type;"
GUARD = "neverallow { coredomain -init -dumpstate } vendor_wifi_prop:file no_rw_file_perms;"

# Minimal CIL policy adapted from upstream CIL reference-guide examples.
# This models one member of the forbidden coredomain set. It is NOT the
# Android 17 type universe, Android neverallow rule, or property contexts.
CIL_SMOKE = """\
(handleunknown deny)
(mls true)
(category c0)
(categoryorder (c0))
(sensitivity s0)
(sensitivityorder (s0))
(sensitivitycategory s0 (c0))
(user system_u)
(role system_r)
(userrole system_u system_r)
(userlevel system_u (s0))
(userrange system_u ((s0) (s0)))
(type kernel_t)
(roletype system_r kernel_t)
(sid kernel)
(sidorder (kernel))
(sidcontext kernel (system_u system_r kernel_t ((s0) (s0))))
(class file (open read write getattr))
(classorder (file))
(type vendor_wifi_prop)
(type init)
(type dumpstate)
(type wifi_daemon)
(type coredomain_test)
(typeattribute vendor_property_type)
(typeattribute vendor_internal_property_type)
(typeattributeset vendor_property_type (vendor_wifi_prop))
(typeattributeset vendor_internal_property_type (vendor_wifi_prop))
(typeattribute coredomain)
(typeattributeset coredomain (init dumpstate coredomain_test))
(allow wifi_daemon vendor_wifi_prop (file (read open getattr)))
(allow init vendor_wifi_prop (file (read)))
(neverallow coredomain_test vendor_wifi_prop (file (read write open)))
"""
FORBIDDEN_ACCESS = "(allow coredomain_test vendor_wifi_prop (file (write)))\n"


def source_gate(macros: str, patch: str, upstream: str, upstream_hal: str) -> list[str]:
    errors = []
    if patch.count("+" + SOURCE_CALL) != 1:
        errors.append("staged policy patch must use exactly one vendor_internal_prop Wi-Fi declaration")
    if "vendor_public_prop(vendor_wifi_prop)" in patch:
        errors.append("staged patch must not broaden Wi-Fi property to public")
    if upstream.splitlines().count(SOURCE_CALL) != 1:
        errors.append("official pinned LineageOS 24.0 reference must use vendor internal")
    if "get_prop(hal_wifi_default, vendor_wifi_prop)" not in upstream_hal:
        errors.append("pinned Wi-Fi HAL reader source changed")
    if errors:
        return errors
    try:
        expanded = subprocess.run(
            ["m4"], input=macros + "\n" + SOURCE_CALL + "\n",
            text=True, capture_output=True, check=False, timeout=10
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [f"m4 unavailable: {exc}"]
    normalized = re.sub(r"\s+", " ", expanded.stdout)
    if expanded.returncode or TYPE_LINE not in normalized or GUARD not in normalized:
        errors.append("upstream-derived m4 internal Wi-Fi type or neverallow expansion missing")
    return errors


def compile_smoke(policy: str, compiler: str = "secilc") -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="a7-slsi-secilc-") as tmp:
        source = Path(tmp) / "wifi.cil"
        binary = Path(tmp) / "wifi.policy"
        contexts = Path(tmp) / "contexts"
        source.write_text(policy)
        # Never use -N: it disables neverallow checks.
        command = [compiler, "-M", "true", "-c", "30", "-o",
                   str(binary), "-f", str(contexts), str(source)]
        try:
            result = subprocess.run(command, text=True, capture_output=True,
                                    check=False, timeout=20)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return 127, str(exc)
        return result.returncode, result.stdout + result.stderr


def verify(compiler: str = "secilc") -> list[str]:
    if not shutil.which(compiler):
        return [f"{compiler} is required for real CIL compilation; not installed"]
    errors = source_gate(MACROS.read_text(), POLICY.read_text(),
                         UPSTREAM.read_text(), UPSTREAM_HAL.read_text())
    if errors:
        return errors
    good_rc, good_log = compile_smoke(CIL_SMOKE, compiler)
    if good_rc != 0:
        return ["valid standalone Wi-Fi CIL smoke policy did not compile: " + good_log[-1400:]]
    bad_rc, bad_log = compile_smoke(CIL_SMOKE + FORBIDDEN_ACCESS, compiler)
    if bad_rc == 0:
        errors.append("forbidden core-domain Wi-Fi access compiled: neverallow did not block it")
    elif "neverallow" not in bad_log.lower():
        errors.append("forbidden access failed for a reason other than neverallow: "
                      + bad_log[-1400:])
    return errors


def main() -> int:
    errors = verify()
    for error in errors:
        print("FAIL:", error, file=sys.stderr)
    if errors:
        return 1
    print("PASS: source-bound minimal Wi-Fi CIL compiles; negative neverallow rejected by secilc.")
    print("NOT VERIFIED: assembled Android 17 policy, platform/vendor CIL mapping, SM-A750F HALs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
