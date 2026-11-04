# HAL and VINTF compatibility audit — reviewed 2026-11-04 UTC

Sources:
- [Pinned common VINTF manifest](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/manifest.xml)
- [Pinned device VINTF manifest](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/f17643ba01010c45b628d5acb8f48350ded61606/manifest.xml)
- [Pinned common product makefile](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/exynos7885.mk)
- [Pinned device product makefile](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/f17643ba01010c45b628d5acb8f48350ded61606/device.mk)

These complete XML/Makefile files are retained as [checksummed source evidence](source-evidence-audit.md). They are inputs to a future assembled-manifest check; static inspection does not perform VINTF compatibility validation.

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
