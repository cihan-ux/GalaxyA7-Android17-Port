# Pinned source partition audit — SM-A750F compatibility gate

**Status: BLOCKED — no device-specific partition verification.** This is a source-level comparison, not a dump of the user's phone.

## Source provenance

- [Device BoardConfig.mk at f17643b](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/f17643ba01010c45b628d5acb8f48350ded61606/BoardConfig.mk)
- [Common BoardConfigCommon.mk at f2ce8d2](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/BoardConfigCommon.mk)

The pinned device tree defines `BOARD_SUPER_PARTITION_METADATA_DEVICE := SYSTEM` and `BOARD_SUPER_PARTITION_BLOCK_DEVICES := SYSTEM VENDOR ODM`. It also defines `BOARD_SUPER_PARTITION_SIZE := 4882169856` and `BOARD_SAMSUNG_DYNAMIC_PARTITIONS_SIZE := 4878169856`, a **4,000,000-byte difference**. The three declared physical block-device sizes sum to **4,882,169,856 bytes**, matching the declared super size. These are **source constants**, not measurements of SM-A750F.

The common tree declares logical dynamic partitions `odm product system system_ext vendor`, uses custom Samsung boot image creation and separated DT, and references external `hardware/samsung_slsi-linaro` and Samsung boot-image tooling. The device tree's `ODM_MANIFEST_SKUS` explicitly lists `SM-A750FN` and `SM-A750GN` for NFC manifests, **not** `SM-A750F`. This alone does not prove SM-A750F unsupported; it prevents assuming the same SKU-specific configuration.

## Required before any flashing

1. Obtain read-only partition-name **and size** evidence for the exact SM-A750F/U5 firmware, without uploading private partitions or serial numbers.
2. Verify actual physical partition layout, super metadata approach, and recovery/boot image requirements against the pinned tree.
3. Resolve vendor blobs and external BSP projects, keeping proprietary binaries out of the public repository.
4. Verify Android 17 platform and HAL/VINTF/SELinux/kernel compatibility separately; LineageOS 18.1 source is not an Android 17 port.
5. Confirm independently tested recovery and complete user backup before any device-changing operation.

**No repartitioning, OEM unlock, root, flash or data wipe is authorized by this audit.**
