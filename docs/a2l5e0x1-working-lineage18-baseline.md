# Working Android 11 baseline: A2L5E0X1 a7y18lte

Recorded 2026-11-10. **Research only; not an Android 17 boot claim.**

## User-confirmed runtime baseline

The user reports that the 2026-10-17 LineageOS 18.1 (Android 11) build by A2L5E0X1 boots and works successfully on their Samsung Galaxy A7 2018 **SM-A750F** (`a7y18lte`). This is stronger practical evidence than a repository's branch label, but does **not** establish that every hardware feature was tested. No phone access or extraction has been performed.

## Public OTA records

- 2026-10-17: [OTA metadata history](https://github.com/A2L5E0X1/lineage/commit/d2629c97a7d7374c079cea83de3d01de3ed3b199). This is the user's reported working build date.
- 2026-11-08: [Release a7y18lte-20261108](https://github.com/A2L5E0X1/lineage/releases/tag/a7y18lte-20261108), artifact `lineage-18.1-20261108-UNOFFICIAL-A2L5E0X1-a7y18lte.zip`, 742826234 bytes, SHA-256 `926cd48efb2a4b024e85bec06cdfedcbb9ca34ed4db9c458c6949b8a606d6c0d`. **This newer release was not reported as installed or tested by the user.**
- [Release changelog](https://github.com/A2L5E0X1/lineage/blob/master/docs/changes/exynos7885/exynos7885.md) reports 2026-11-08 fixes for first-boot splash stalls and a PC wake/USB deadlock, plus security patches. These are maintainer statements, not independently reproduced tests.
- [Device metadata](https://github.com/A2L5E0X1/lineage/blob/master/docs/_data/devices/a7y18lte.yml) lists SM-A750F/FN/G/GN, Exynos 7885, Mali-G71 and original Android 8.0. This supports the Android 8 launch/API-26 research direction, not binary interchangeability.

## Existing source baseline to correlate

Our research manifest already pins `exynos7885-dev/device_samsung_a7y18lte@f17643ba01010c45b628d5acb8f48350ded61606`, `device_samsung_exynos7885-common@f2ce8d2093711026f021cba7036334d381d455ef`, and `kernel_samsung_exynos7885@6020dfa8315134187f07ca903c9d2ed7ee0256f5`. **Do not assert that the A2L5E0X1 release was built from these exact commits** without release build provenance. A newer kernel branch head exists and needs diff review; do not repin automatically.

## Next actionable compatibility investigation

1. Acquire the **public** October 17 ROM zip (or a local copy of the user's installed ROM) and verify the ZIP SHA-256 against its published release checksum before inspecting contents. Do not assume the November archive matches the installed October system.
2. Offline, list ZIP entries and inspect `META-INF/com/android/metadata`, `payload_properties.txt` / `payload.bin` or `system.new.dat*` as applicable. Record actual packaging layout before selecting extraction tools.
3. Where legally permissible and with consent, inspect extracted boot image and vendor partition *locally* for kernel release, DTB/DTBO identifiers, firmware paths, `/vendor/etc/vintf` manifests, HAL names, SELinux contexts and library dependencies. Keep proprietary binary blobs, EFS, IMEI, radio calibration and personal data **out of this public repository**. Commit only sanitized inventories and reproducible public-source references.
4. Compare device-tree `BoardConfig`, kernel defconfig, DTS revisions, Wi-Fi/BT, graphics, camera, audio, RIL and fingerprint interfaces against Android 17's actual build requirements. Use a compatibility matrix with verified, unknown and blocked statuses, not inferred success.
5. The pinned historical 4.4.302 kernel still fails the LineageOS 24.0 NetBpfLoad minimum kernel-version gate (5.10 for API 3700, 5.15 for 3710). A working Android 11 ROM does **not** bypass this Android 17 blocker. Prioritize credible modern Exynos7885 kernel/board support and genuine assembled VINTF/SELinux tests.

## Safety and scope

No flashing, bootloader changes, ROM installation, repartitioning, private file uploads or PR merges. The source-level Android 17 prototype remains non-flashable. Preserve the user's functioning Android 11 installation.
