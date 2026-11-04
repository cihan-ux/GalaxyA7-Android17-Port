# Device-specific vendor and partition compatibility — 2026-11-05

## Source inspection
Current device tree: https://github.com/exynos7885-dev/device_samsung_a7y18lte/tree/lineage-18.1

- `device.mk` explicitly imports **`vendor/samsung/a7y18lte/a7y18lte-vendor.mk`**. The common tree also requires `vendor/samsung/exynos7885-common/exynos7885-common-vendor.mk`. Both are missing from the three-project research manifest.
- `proprietary-files.txt` header identifies **A750FNXXU5CVG2** as its blob baseline, while the target handset is **SM-A750F / A750FXXU5CVG1**. These must not be treated as identical without comparison.
- `extract-files.sh` delegates to the common extraction script and patches audio, camera, sensor, baseband and NFC binaries.
- `device.mk` references fingerprint HAL 2.1, keymaster 3.0, NFC HAL 1.2 and USB HAL 1.0. Android 17 support is unverified.
- `lineage_a7y18lte.mk` sets `PRODUCT_SHIPPING_API_LEVEL := 28`, unlike the older tree's 26. This requires validation against the device's actual launch API and build rules; do not change it blindly.
- `BoardConfig.mk` includes a dynamic super partition layout, even though the handset's actual partition table has not been read.

## Immediate blockers
1. Obtain **non-sensitive partition information** from the device before choosing a dynamic partition layout. Do not ask for EFS/IMEI dumps, credentials, or private data.
2. Verify correct stock firmware and extraction provenance for **SM-A750F**, especially NFC differences.
3. Find and audit matching vendor extraction outputs and Samsung SLSI hardware trees, without publishing proprietary binaries.
4. Pin known-good source commits after a baseline build is established.

## Safety gate
Do not run repartitioning, OEM unlocking, flashing, or wiping commands. No Android 17 ROM exists in this repository.
