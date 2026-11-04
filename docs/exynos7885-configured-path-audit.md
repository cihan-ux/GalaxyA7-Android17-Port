# Exynos7885 pinned source dependency scan — configured paths

Source commits:
- [Common BoardConfigCommon.mk](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/BoardConfigCommon.mk)
- [Common exynos7885.mk](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/exynos7885.mk)
- [A7 device.mk](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/f17643ba01010c45b628d5acb8f48350ded61606/device.mk)

The static scanner previously missed `BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk` because this is a path-valued variable assignment rather than an include directive. The updated scanner recognizes an **explicit allowlist** of file-path variables. It does not interpret all Make assignments as file dependencies.

Verified file-level references include:
- `hardware/samsung_slsi-linaro/config/BoardConfig7885.mk` — direct include
- `hardware/samsung/mkbootimg.mk` — configured boot image Makefile
- `device/samsung_slsi/sepolicy/sepolicy.mk` — direct include
- `hardware/samsung_slsi-linaro/config/config.mk` — inherited product
- `vendor/samsung/exynos7885-common/exynos7885-common-vendor.mk` — inherited product
- `vendor/samsung/a7y18lte/a7y18lte-vendor.mk` — inherited product

The `PRODUCT_CFI_INCLUDE_PATHS` entry for `hardware/samsung_slsi/scsc_wifibt/wpa_supplicant_lib` is a **directory path**, not a Makefile include; it must be checked by a separate directory-level dependency audit. The source-only tests assert these distinctions using excerpts from the exact pinned source files.

These references are *not proof that the paths exist* in a complete checkout or that their revisions are Android 17-compatible. No source import, build, partition changes, or phone operations were performed.
