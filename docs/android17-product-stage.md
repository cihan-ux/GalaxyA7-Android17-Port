# Galaxy A7 / LineageOS 24.0 (Android 17) experimental product stage

**State:** actual Android makefile source staged under
`port/lineage-24.0/device/samsung/a7y18lte/`, but **not yet
integrated, compiled, booted, or flashable**. No phone, private files, or
proprietary vendor binaries were accessed.

## Changed source: product registration and shipping API

- `AndroidProducts.mk` registers
  `lineage_a7y18lte-trunk_staging-userdebug` for the release-aware Android 17
  `lunch PRODUCT-RELEASE-VARIANT` command. This is a *staged choice*, not
  a claim that the complete target configuration resolves.
- `lineage_a7y18lte.mk` maintains the historical 64/32-bit, telephony, device
  and LineageOS product inheritance, but uses the Android 17 target's
  `product_launched_with_o.mk` for original Android 8 (API 26) shipping.
- The pinned legacy 18.1 product says `PRODUCT_SHIPPING_API_LEVEL := 28`.
  This is **not** the first-release API for SM-A750F: Samsung's historical
  [SM-A750F update record](https://doc.samsungmobile.com/SM-A750F/002230181115/eng.html)
  lists Android 8.0 firmware from November 2018.
  Target [product_launched_with_o.mk](https://github.com/LineageOS/android_build/blob/90d006387398ae6899145e6531a304500cfa0f70/target/product/product_launched_with_o.mk)
  sets API 26. The transition from legacy 28 to device-observed original
  26 requires vendor compatibility checks and **could still block a build**.
  It is not a vendor-API compatibility workaround.

The research tree is pinned to a historical 18.1 device product; these two
files are a **delta** to stage in a future checkout at
`device/samsung/a7y18lte/`, not a replacement for `device.mk`,
`BoardConfig.mk`, `manifest.xml` or vendor blobs.
A LineageOS 24.0 target manifest is described in
[Android 17 source compatibility](android17-source-compatibility.md).

## Explicit kernel / vendor / SELinux blockers

| Subsystem | What source actually proves | Still required |
| --- | --- | --- |
| Kernel | Pinned kernel 4.4.302 defconfig enables Android Binder IPC; BPF syscall is disabled | Evaluate target kernel expectations and a testable kernel configuration / patches; do not assert BPF availability or boot support |
| VINTF | Both historical device and common manifests declare target-level 3 | Check actual Android 17 framework matrices and implement viable compatibility; **do not** just change the manifest number |
| Vendor | Historical device inherits `a7y18lte-vendor.mk`; previously observed vendor source names A750FNXXU5CVG2 | Establish legally usable SM-A750F / A750FXXU5CVG1 vendor compatibility, symbols, firmware and HAL behavior |
| SELinux | Common BoardConfig references vendor SEPolicy and Samsung/Lineage policy includes | Port policy to the target platform, compile and check neverallows/VINTF; do not disable enforcement |

## Fast reproducible source-only test

```sh
python3 tools/check_android17_product_port.py
python3 -m unittest discover -s tests -v
```

The checker validates the staged Makefiles against reviewed upstream
source snapshots and reports historical constraints. A green result does
**not** mean that Android 17's Soong configuration, kernel, HALs, graphics,
radio, SELinux, boot or recovery works.

Next engineering change: gather a target module and policy inventory and
build an explicit SM-A750F vendor compatibility matrix before editing
HAL/VINTF levels or SELinux allow rules.
