# Proprietary vendor extraction baseline and variant mismatch

**BLOCKED:** the upstream device blob list is explicitly labeled `A750FNXXU5CVG2`, while the user's SM-A750F stock build was recorded as `A750FXXU5CVG1`. The suffix, model variant and provenance differ. Similar U5 versions **do not prove** binary compatibility.

## Verified upstream source

[proprietary-files.txt, pinned device tree](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/f17643ba01010c45b628d5acb8f48350ded61606/proprietary-files.txt)

The upstream list includes proprietary audio, camera and camera-device shared libraries (both 32-bit and 64-bit entries), plus vendor audio configurations. These entries are **references to files**, not binaries included in this project. The upstream extraction script is not a license to redistribute Samsung blobs.

## Safe provenance workflow

1. Record the exact model and build string from the device (do not collect serial, IMEI, EFS or modem NV).
2. Verify the source firmware image is intended for the same exact model and bootloader revision; do not use FN/GN firmware as an F firmware substitute.
3. Keep original firmware and extracted vendor binaries **outside this public GitHub repository**; record non-sensitive hashes and source version locally.
4. Verify each extracted file against its source manifest, architecture and vendor partition placement before any build attempt.
5. Validate Samsung HAL dependencies and VINTF against the target Android platform. Android 11-compatible vendor libraries cannot be assumed Android 17-compatible.

## Open blockers

- No verified SM-A750FXXU5CVG1 vendor extraction has been completed.
- No licensing review for redistribution of proprietary binaries.
- No complete matching vendor tree or proven Android 17 HAL compatibility.
- No verified SM-A750F recovery or partition layout.

**No firmware download, flashing, unlocking or extraction from the user's phone has occurred.**
