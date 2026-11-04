# HAL and VINTF compatibility audit — 2026-11-05

Sources:
- [Current common VINTF manifest](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/lineage-18.1/manifest.xml)
- [Current device VINTF manifest](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/lineage-18.1/manifest.xml)
- [Current common product makefile](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/lineage-18.1/exynos7885.mk)
- [Current device product makefile](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/lineage-18.1/device.mk)

## Confirmed baseline declarations (not Android 17 compatibility claims)

| Subsystem | HIDL version |
|---|---|
| Audio | 4.0 |
| Bluetooth | 1.0 |
| Camera provider | 2.5 |
| Graphics allocator | 2.0 |
| Graphics composer | 2.4 |
| Health | 2.1 |
| GNSS | 2.1 and 1.1 |
| Radio | 1.4 |
| Sensors | 1.0 |
| Fingerprint (device) | 2.1 |
| Keymaster (device) | 3.0 |

Both manifests specify `target-level="3"`. Whether an Android 17 framework compatibility matrix can accept this device/vendor combination requires actual VINTF and build testing. **Do not silently change the target level** to bypass checks.

## Missing build dependencies identified

- Device product: `vendor/samsung/a7y18lte/a7y18lte-vendor.mk`
- Common product: `vendor/samsung/exynos7885-common/exynos7885-common-vendor.mk`
- Common product and board: `hardware/samsung_slsi-linaro/config/config.mk` and `hardware/samsung_slsi-linaro/config/BoardConfig7885.mk`
- Additional Samsung/Lineage hardware and sepolicy projects referenced by the common tree.

These paths are not yet populated by the research manifest. No proprietary blobs are committed.

## Engineering gates

1. Reconstruct a *complete* known-good LineageOS 18.1 checkout.
2. Identify compatible blob extraction sources for SM-A750F, with explicit permission and licensing.
3. Run build-system dependency and VINTF checks on a capable Linux builder.
4. Only then assess forward-port changes toward Android 17.

Do not flash or repartition the phone.
