# First real build attempt — decision and execution plan

**Decision (2026-11-05):** Stop adding generic audit tooling. The next useful milestone is a reproducible **LineageOS 18.1 baseline kernel build**, followed by a baseline ROM build. This is not an Android 17 build. Do not flash any image.

## What we already have

- Device, common device and kernel are pinned in `manifests/lineage-18.1-research.xml`.
- The kernel contains `arch/arm64/configs/lineage_a7y18lte_defconfig`; its source Makefile identifies 4.4.302.
- The common device tree requests Clang and Samsung custom boot-image tooling.
- Five matching-branch SLSI repository candidates have been located; the `interfaces` namespace remains unverified.
- CI tests static evidence only; they cannot build a kernel or Android ROM.

## Next build gates — in execution order

1. **Build environment:** provision a disposable, adequately sized Linux builder. Record CPU, RAM, free disk, OS, available Clang/LLVM versions and build logs. Do not attempt a full AOSP checkout on a 4 GB laptop.
2. **Kernel-only baseline:** checkout pinned `kernel_samsung_exynos7885` commit `6020dfa8315134187f07ca903c9d2ed7ee0256f5`. Verify the defconfig exists. Establish the **actual historical compiler/toolchain** required by the pinned kernel and its configuration; don't assume the host's latest Clang works.
3. **Compile and preserve errors:** run the kernel build in the disposable environment, capture the full command line, compiler identity, exit status and first reproducible failure. Never call a successful kernel build a bootable ROM.
4. **Baseline source closure:** resolve `hardware/samsung`, `device/lineage/sepolicy`, `device/samsung_slsi/sepolicy`, SLSI interfaces and Wi-Fi/Bluetooth providers, vendor extraction provenance, and other transitive modules. Pin only verified compatible revisions and review licenses.
5. **LineageOS 18.1 ROM build:** after closure, attempt a full baseline build on the builder. Preserve `repo manifest -r` and exact errors. No phone flashing.
6. **Android 17 port:** only after baseline evidence, address target VINTF/FCM, SELinux, HAL and toolchain incompatibilities incrementally. A passing Python test suite is not evidence of Android 17 support.

## Hard stop conditions

- No verified compiler/toolchain: record blocker, do not invent a kernel build command.
- No lawful, model-matched SM-A750F vendor extraction: do not publish blobs or substitute A750FN blobs as if equivalent.
- No confirmed phone partition/recovery/bootloader state: do not produce installation instructions or flash images.
- No suitable hosted builder: report environment blocker rather than claiming a build happened.

## Immediate measurable deliverable

A kernel build attempt with **actual compiler version, command, exit status and logs** is the next engineering result worth reporting. If this cannot be executed, the exact missing resource and upstream dependency must be recorded. Avoid reporting new static tests as progress toward a bootable ROM.
