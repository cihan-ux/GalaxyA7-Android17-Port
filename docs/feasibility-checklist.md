# Android 17 feasibility checklist

- [ ] Confirm upstream Android 17 / LineageOS branch naming and build requirements
- [ ] Audit lineage-18.1 device tree and exynos7885-common dependency
- [ ] Locate matching kernel defconfig and source revision
- [ ] Identify proprietary vendor blobs without redistributing them
- [ ] Confirm partition layout, recovery, boot image format and Treble properties
- [ ] Evaluate Linux 4.4 compatibility, HALs, SELinux and VNDK
- [ ] Reproduce known-working baseline before forward porting
- [ ] Test radio, Wi-Fi, Bluetooth, camera, audio, GPS, fingerprint, sensors, encryption and USB
- [ ] Verify stock firmware recovery and backup plan before any device modification

**No working Android 17 ROM has been demonstrated for this project.**
