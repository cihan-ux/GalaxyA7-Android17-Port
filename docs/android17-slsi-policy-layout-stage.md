# Android 17 Samsung SLSI policy directory migration

**Actual source patch staged; Android 17 build and SELinux policy compiler not run.**

Compared immutable `LineageOS/android_device_samsung_slsi_sepolicy/sepolicy.mk` versions:

- LineageOS 18.1 baseline commit `9968b62f8f76c22143a8fc7491440aa11c32e6f4`.
- LineageOS 24.0 reference commit `224e135300fbb07ee12968cc57ad053a267e3ce4`.

Three literal makefile assignments differ, and only those:

- Both `BOARD_PLAT_PUBLIC_SEPOLICY_DIR +=` lines become `SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS +=`.
- The single `BOARD_PLAT_PRIVATE_SEPOLICY_DIR +=` line becomes `SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS +=`.

The vendor policy directory and mobicore/teegris conditional trees remain unchanged. The staged patch is `port/lineage-24.0/device/samsung_slsi/sepolicy/patches/0002-slsi-system-ext-policy-partition.patch`. Full source fixtures record exact original and target files for offline regression.

Run `python3 tools/check_slsi_sepolicy_layout_port.py`. The test invokes `git apply --check`, applies the patch to the pinned original, and verifies byte-for-byte equality with the upstream target, rejecting unrelated changes.

This does not validate actual Android 17 make-variable evaluation, policy compilation with `secilc`, neverallow resolution, vendor mapping or boot. Kernel 4.4/BPF, missing VINTF level 3 support, vendor model differences and proprietary blob rights remain separate blockers.
