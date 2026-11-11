# Isolated SELinux CIL compiler gate — Galaxy A7 Android 17 research

**Status: compiler-backed minimal fragment, not a full Android 17 policy compilation.**

## Verified pinned inputs
- Samsung SLSI lineage-24.0 at 224e135300fbb07ee12968cc57ad053a267e3ce4 uses vendor_internal_prop(vendor_wifi_prop), with a Wi-Fi HAL read access.
- LineageOS Android 17 system_sepolicy at d61fd80832f558d52de026097d30d695634e8b0f defines vendor-internal property type and conditional neverallow restrictions.
- The reduced local m4 macro fixture uses the strict branch of treble_sysprop_neverallow and is not a complete upstream policy.

## New genuine compiler smoke gate
tools/check_slsi_wifi_cil.py verifies the pinned source declarations and macro expansion. Then it constructs a *standalone miniature CIL policy* with explicit vendor-internal property attributes and tests the Linux secilc compiler.

1. Positive: a permitted Wi-Fi property reader must compile.
2. Negative: granting a forbidden core-domain type Wi-Fi write permission must be rejected, with a neverallow diagnostic.

The reduced CIL policy models one representative forbidden core-domain type. It is not a faithful conversion of all Android 17 neverallow rules and does not include full platform/vendor CIL or property_contexts. It is intentionally isolated to keep CI lightweight.

GitHub Actions Ubuntu 24.04 installs the secilc package and runs these tests on Python 3.11 and 3.14. No full Android platform, firmware, vendor blob or device access is needed.

Commands:
    python tools/check_selinux_wifi_property_port.py
    python tools/check_slsi_wifi_cil.py
    python -m unittest discover -s tests -v

Requires m4, git, secilc and Python 3.11+.

**Not verified:** assembled Android 17 SELinux compilation, complete neverallow compatibility, VINTF, kernel 4.4/BPF, SM-A750F vendor ABI, device boot or flashability. Never disable SELinux or use secilc -N to bypass neverallows.
