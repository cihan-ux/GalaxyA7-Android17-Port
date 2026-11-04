# Kernel and vendor dependency audit — 2026-11-05

## Confirmed from LineageOS 18.1 sources

- Device tree: https://github.com/exynos7885-dev/old_device_samsung_a7y18lte/tree/lineage-18.1
- Common tree: https://github.com/exynos7885-dev/old_device_samsung_exynos7885-common/tree/lineage-18.1
- Common BoardConfig sets `TARGET_KERNEL_SOURCE := kernel/samsung/exynos7885`.
- Device BoardConfig requests `TARGET_KERNEL_CONFIG := lineage_a7y18lte_defconfig`.
- Common BoardConfig uses `BOARD_CUSTOM_BOOTIMG := true`, Samsung `hardware/samsung/mkbootimg.mk`, `Image`, separate DT and `dtbhtoolExynos`.
- Historical kernel build uses GCC 4.9 (`TARGET_KERNEL_CLANG_COMPILE := false`), not a modern Clang-first configuration.
- Common product file inherits `vendor/samsung/exynos7885-common/exynos7885-common-vendor.mk` — proprietary vendor extraction is a separate dependency.
- The historical common tree configures audio HIDL 4.0, camera provider 2.5, graphics allocator 2.0, graphics composer 2.1, fingerprint 2.1, radio 1.4 and keymaster 3.0. These are **legacy interface versions**; Android 17 compatibility has not been verified.
- Proprietary extraction script contains binary fixes for audio, camera, sensor and NFC components, indicating vendor compatibility work already existed on Android 11.

## Kernel candidate check

Candidate: https://github.com/AKSharma87/android_kernel_samsung_a7y18lte (branch `wip`).

The expected path `arch/arm64/configs/lineage_a7y18lte_defconfig` returned 404 on that branch. **This does not prove the kernel is unsuitable**: the defconfig could live elsewhere or another branch. Do not write a manifest pointing to this kernel until its exact defconfig and buildability are verified.

## Next validation

1. Search common/kernel organization for a kernel repository with matching `lineage_a7y18lte_defconfig`.
2. Inspect branch and tree availability; record commit SHA rather than floating branch for reproducibility.
3. Identify extraction sources and required Samsung stock firmware version without committing proprietary binaries.
4. Compare old HIDL and VINTF declarations with the actual Android 17 build requirements.
5. Do not change the device, unlock the bootloader or flash experimental images.

**Status: dependency research, no ROM build, no device tests.**
