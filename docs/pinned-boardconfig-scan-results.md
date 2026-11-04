# Pinned BoardConfig static scan — corrected shared dependency

Verified upstream source files:
- [exynos7885-dev common BoardConfigCommon.mk @ f2ce8d2](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/BoardConfigCommon.mk)
- [universal7885 common BoardConfigCommon.mk @ 98009b1](https://github.com/MacBookPro34-comma-7/android_device_samsung_universal7885-common/blob/98009b1e310f04ca940bf6c1ef1cc0cc144bdb02/BoardConfigCommon.mk)

Both source files contain:
```make
include device/lineage/sepolicy/exynos/sepolicy.mk
include device/samsung_slsi/sepolicy/sepolicy.mk
```

The pinned Linaro source **also** contains:
```make
include hardware/samsung_slsi-linaro/config/BoardConfig7885.mk
```

**Correction to earlier analysis:** Samsung SLSI sepolicy is a *shared* dependency, not a BSP-only discriminator. The BSP source explicitly declares `TARGET_SLSI_VARIANT := bsp`; the pinned Linaro source includes the Linaro board config. The scanner now detects a literal `TARGET_SLSI_VARIANT` assignment separately from include paths. The regression tests reproduce only the verified relevant source lines.

**Limitations:** static scans are not complete Makefile evaluation. In particular `BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk` is a variable assignment, not an `include` directive; the scanner must not silently treat it as an include. Its separate build dependency still requires manual closure. No sources imported and no phone access.
