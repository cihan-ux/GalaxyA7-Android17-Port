# Galaxy A7 2018 (SM-A750F): LineageOS 19.1 / Android 12L bring-up

**Status: source-only research and staged product. No Android 12L image was
built, booted or validated on hardware.** This branch does not change the
working LineageOS 18.1 installation or the Android 17 research branch.

## Exact starting sources

The user-reported successful 18.1 build
[`a7y18lte-20261108`](https://github.com/A2L5E0X1/lineage/releases/tag/a7y18lte-20261108)
is the *behavioral reference*. The device/common/kernel hashes in
[`lineage-18.1-research.xml`](../manifests/lineage-18.1-research.xml)
are independently located historical sources; they are **not attested as
byte-identical sources used to produce that ZIP**.

- 12L platform manifest: [LineageOS/android@74f3868](https://github.com/LineageOS/android/commit/74f3868c0a4e774a8626ba329bc93eb4862e5b48),
  `lineage-19.1`, default AOSP tag `android-12.1.0_r22`.
- 12L build rules: [LineageOS/android_build@ec4184b](https://github.com/LineageOS/android_build/commit/ec4184bcd771e59d3d108115507587444697be38).
- Original maintained A7 tree: [device@f17643b](https://github.com/exynos7885-dev/device_samsung_a7y18lte/commit/f17643ba01010c45b628d5acb8f48350ded61606);
  [common@f2ce8d2](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/commit/f2ce8d2093711026f021cba7036334d381d455ef);
  [kernel@6020dfa](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/commit/6020dfa8315134187f07ca903c9d2ed7ee0256f5).
- 19.1 SELinux repositories use exact inspected 19.1 pins in the local
  manifest, rather than blindly importing 18.1 SEPolicy.

## Intended source checkout (capable Linux build machine only)

```sh
mkdir -p ~/android/lineage-19.1
cd ~/android/lineage-19.1
repo init -u https://github.com/LineageOS/android.git -b lineage-19.1 --git-lfs
mkdir -p .repo/local_manifests
# Copy this repository's manifests/lineage-19.1-a7y18lte-local.xml
# to .repo/local_manifests/a7y18lte.xml, then REVIEW paths and pins.
repo sync -c -j4
```

Do not expect `repo sync` or the product configuration to succeed without
resolving missing modules, legal binary provenance and BSP/API differences.
The manifest fixes local project hashes but the full platform manifest
continues tracking a branch; save `repo manifest -r` for a reproducible
build once a checkout succeeds.

After checking the full upstream device tree and the diff, stage only
`port/lineage-19.1/device/samsung/a7y18lte/{AndroidProducts.mk,lineage_a7y18lte.mk}`
into `device/samsung/a7y18lte/`. These are **overlays**, not substitutes
for `BoardConfig.mk`, `device.mk`, services, fstab, or manifests.

Only when source, licenses, vendor compatibility and build dependencies
are reviewed, attempt `source build/envsetup.sh`,
`lunch lineage_a7y18lte-userdebug` and a **configuration-only**
test. A successful lunch is not a kernel/ROM build.

## Design decisions and blockers

1. 19.1 uses the old `PRODUCT-VARIANT` lunch choice, not the Android
   17 release-aware `PRODUCT-RELEASE-VARIANT` tuple.
2. Inherit the 18.1 64-bit / telephony / device / Lineage order. The old
   product's declared API 28 conflicts with the A7's actual Android 8
   launch. Android 12L build rules provide `product_launched_with_o.mk`
   (API 26); staging this accurate value is **not proof** that legacy
   vendor policy or VINTF will work.
3. The inherited Exynos7885 Linux 4.4 kernel, graphics, camera, radio,
   NFC, Wi-Fi, HWC/OMX, Binder/ashmem, SELinux and VINTF interfaces
   still require 19.1-specific builds and runtime tests.
4. Do not disable SELinux enforcing, neverallow checks, AVB or VINTF
   validation to conceal missing support. Do not reuse the Android 17
   Linux 6.15 mailbox prototype in this 4.4-based bring-up.
5. Until boot and stability are proven, **do not produce flashing
   instructions, OTA updates or claim migration without data loss**.

## Source-only test

```sh
python3 tools/check_lineage19_port.py
python3 -m unittest discover -s tests -p 'test_lineage19_port.py' -v
```

Next technical gate: assemble a full 19.1 build checkout, resolve the first
real Soong/Kati configuration failure, and record its exact logs. Initial
source-only checks do not establish firmware compatibility or a flashable ROM.
