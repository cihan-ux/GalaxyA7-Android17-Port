# Android 17 Exynos7885 SELinux: first vendor Wi-Fi property type delta

**Status: small, testable source patch only — not a compiled Android 17 policy.**
No handset, firmware blob, privileged identifier or proprietary binary is needed.

## What was verified

Pinned historical source:

- `LineageOS/android_device_samsung_slsi_sepolicy` at
  `9968b62f8f76c22143a8fc7491440aa11c32e6f4`
- `common/vendor/property.te` declares
  `type vendor_wifi_prop, property_type;` without explicit property ownership.
- `common/vendor/property_contexts` assigns both `vendor.wifi.` and
  `ro.vendor.wifi.` to `vendor_wifi_prop`.

Target source:

- `LineageOS/android_system_sepolicy` at
  `d61fd80832f558d52de026097d30d695634e8b0f`
- [public/te_macros](https://github.com/LineageOS/android_system_sepolicy/blob/d61fd80832f558d52de026097d30d695634e8b0f/public/te_macros)
  defines `vendor_public_prop(name)` as a vendor-owned, public property type.
  The macro expands to
  `type name, property_type, vendor_property_type, vendor_public_property_type;`.

## Port delta

`port/lineage-24.0/device/samsung_slsi/sepolicy/patches/0001-exynos7885-typed-vendor-wifi-property.patch`

The patch replaces only the SLSI vendor Wi-Fi property type declaration with
`vendor_public_prop(vendor_wifi_prop)`. It preserves the original two
property-context mappings and does not change `allow`, `neverallow`,
SELinux enforcement, other SLSI property types, or kernel configuration.

`public` is intentionally a compatibility-oriented *candidate* because
cross-partition readers have not been audited. It does **not** assert a
least-privilege policy. A later full policy build may require a narrower
classification after examining actual producer/consumer domains.

## Offline checks

```sh
python3 tools/check_selinux_wifi_property_port.py
python3 -m unittest tests.test_selinux_wifi_property_port -v
```

The checker copies the pinned source text into a temporary tree, applies
`git apply --check` and `git apply`, compares the entire result for a
single-line delta, and uses `m4` to expand the target macro excerpt.
The target snippet is copied with upstream provenance; this is *not*
a substitute for compiling the complete Android 17 system/vendor policy.

## Still blocked

- Android 17 `secilc`/policy compilation, property-context validation,
  neverallow and vendor/platform policy mapping tests have **not** been run.
- Other legacy SLSI property types and `ro.multisim.`/`persist.radio.`
  contexts are not migrated. Their owner and access paths require a separate
  trace; no broad automatic conversion is appropriate.
- The device/common VINTF target-level 3, kernel 4.4.302/BPF gap, and
  HAL/vendor ABI compatibility remain unresolved.
- The historical vendor source references **A750FNXXU5CVG2**, while the
  SM-A750F stock build is **A750FXXU5CVG1**. Neither variants nor
  proprietary files are treated as interchangeable.

This patch would be reviewed against the full checkout and applied to the
pinned SLSI policy source before a full policy build. There is no ROM to flash.
