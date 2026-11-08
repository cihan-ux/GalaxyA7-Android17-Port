# Galaxy A7 2018 (SM-A750F) — Android 17 port research

**Status: source-level Android 17 prototype, NOT buildable or flashable as an Android 17 ROM.** Both the historical Linux 4.4.302 and an experimental Linux **6.15-rc1 ARM64 kernel Image** have now been compiled in GitHub CI. The newer Image is a **non-bootable, non-flashable research artifact**; Android 17 runtime/kernel compatibility on SM-A750F is NOT established.

Target: Samsung Galaxy A7 (2018), **a7y18lte**, Exynos 7885. Historical stock baseline: Android 10, firmware A750FXXU5CVG1 (U5), Linux 4.4.177, arm64 ABI. The user subsequently confirmed that [LineageOS 18.1 build 2026-11-08 (Android 11)](docs/working-lineage18-20261108-reference.md) works on the handset. That is useful legacy source evidence, **not proof of Android 17 compatibility**. This repository has not accessed the phone.

## Verified kernel build milestone

- [Baseline ARM64 kernel Image build](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/41951781918) passed with pinned Linux 4.4.302 and Clang 18.1.3.
- [Full ARM64 kernel Image with BPF syscall enabled](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42235116992) passed: **23,840,488 bytes**, SHA-256 `069302468615291875fd6a3e6139a4af0f3c4e6ae02875a8348cd0c427f0cb79`. Output is **NOT FLASHABLE**.
- **Linux 6.15.0-rc1 ARM64 Image compiled successfully** in [CI 42505758584](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42505758584): **39,526,912 bytes**, SHA-256 `160355fbd5dd321112cf791fe103db4d76d7fe6f6e34e0cb760e10c6ca840755`. CI also verified real Exynos MMC/clock/pinctrl, Binder/binderfs and SELinux ARM64 objects. This is a generic, **NOT BOOTABLE / NOT FLASHABLE** research Image with no complete A7 board integration.
- [LineageOS 24.0 NetBpfLoad source requirements](docs/android17-netbpf-kernel-gate.md) expose a **confirmed version gate mismatch** for historical 4.4.302: Android 17.0 requires kernel >=5.10 and 17.1 >=5.15. Modern 6.15 passes **the version checks only** in CI 42505758584, not the runtime feature/VINTF/vendor prerequisites.

## Source candidates (not yet verified as a complete build set)

- [Pinned maintained LineageOS 18.1 device tree](https://github.com/exynos7885-dev/device_samsung_a7y18lte/tree/f17643ba01010c45b628d5acb8f48350ded61606)
- [Pinned common tree](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/tree/f2ce8d2093711026f021cba7036334d381d455ef)
- [Pinned kernel, source version 4.4.302](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/tree/6020dfa8315134187f07ca903c9d2ed7ee0256f5)
- [Alternative device tree](https://github.com/nnhra/android_device_samsung_a7y18lte)
- [Device recovery/GSI notes](https://github.com/Hari-Pi/a7y18lte-Resources)
- [LineageOS upstream](https://github.com/LineageOS/android)

## Experimental modern Exynos7885 mainline investigation

A pinned [experimental Linux 6.15-rc1 Exynos7885 tree](docs/exynos7885-mainline-kernel-candidate.md) contains a SoC DTS, clock/pinctrl support and a **Galaxy A8 / jackpotlte** board definition. It does **NOT** provide a verified Galaxy A7 / a7y18lte hardware port. The [real A8-only ARM64 DTB build probe](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42245058620) was successful **for A8 only**.

A newly staged [A7-specific SoC/DTB scaffold](docs/a7y18lte-linux615-dtb-scaffold.md) **compiled as a real ARM64 DTB** in [CI 42503704081](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42503704081) with model `SM-A750F` and compatible `samsung,a7y18lte`. Its deliberately missing memory and board wiring make it **NOT BOOTABLE / NOT FLASHABLE**. An independent [A7-derived MMC0/eMMC mapping lab](docs/a7y18lte-emmc-modern-source-mapping.md) compiled in [CI 42504144337](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42504144337), proving DTB syntax and the A7-source controller mapping only, NOT functioning storage or a bootable modern kernel. A separate [power/volume GPIO-keys lab](docs/a7y18lte-gpio-keys-linux615-mapping.md) now has independent A7 legacy source checks and a real DTB compile test; electrical polarity and function on SM-A750F remain unverified.

The [Linux 6.15 ARM64 kernel Image experiment](docs/exynos7885-linux615-android-kernel-first-compile.md) **compiled successfully** in [CI 42505758584](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42505758584) with Binder/binderfs, SELinux and eBPF plus Exynos MMC/clock/pinctrl sources. The [seven-object ARM64 driver compile](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42508948297) **also passed**. Crucially, the source-backed [S2MPU08 PMIC/ACPM audit](docs/a7y18lte-s2mpu08-power-port-blocker.md) **confirmed a missing Linux 6.15 driver integration** in [CI 42508771359](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42508771359).

First [S2MPU08 LDO2/LDO35 voltage-only C source port](docs/a7-s2mpu08-voltage-lab.md) now compiles as a **real AArch64 Linux 6.15 object** in [CI 42515323634](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42515323634). A follow-up fixed Samsung's sparse enum IDs (LDO2=1, LDO35=16), clamped LDO35 to the A7 3.0 V board maximum and added a pinned Samsung header-check gate in [CI 42515547576](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42515547576). **No driver registration, ACPM transport, physical voltage control or Android 17 boot support exists yet.**

The user reports that the [2026-11-08 LineageOS 18.1 Android 11 release](docs/working-lineage18-20261108-reference.md) boots successfully on SM-A750F. Both the source-traced USB DWC3 resume fix and encrypted-data first-boot TEE SELinux fix are documented; no phone was accessed through this repository.

The [pinned Galaxy A7 4.4.302 DTS revision inventory](docs/a7y18lte-legacy-dts-port-inventory.md) identifies distinct board rev00/rev01/rev03 source, GPIO, touch and fingerprint variants. Do not reuse A8-specific memory/pins, copy legacy `androidboot.selinux=permissive` bootargs or claim a successful DTB is an Android 17 ROM.

## Android 17 staged product source (experimental)

A first LineageOS 24.0 **device-tree source delta** lives under
[`port/lineage-24.0/device/samsung/a7y18lte/`](port/lineage-24.0/device/samsung/a7y18lte/).
It stages a release-aware Android 17 product/lunch definition and SM-A750F's original Android 8 (API 26) shipping level. The older device tree uses API 28; the vendor compatibility implications are unverified. See [product notes](docs/android17-product-stage.md).

**No complete Android 17 checkout, assembled SELinux/VINTF validation, ROM image or on-device boot exists.** Kernel modernization, FCM 3, vendor provenance and SELinux forward-port gaps remain.

## Milestones and next engineering work

See the [evidence-based milestone tracker](docs/android17-milestones.md),
[kernel build evidence](docs/first-build-execution-plan.md) and
[Android 17 loader gate](docs/android17-netbpf-kernel-gate.md).
Next steps are to evaluate a credible Exynos7885-capable modern kernel,
reconstruct an actual LineageOS 18.1 baseline ROM and verify vendor/SELinux/VINTF support.

Do not confuse **a7y18lte** (2018) with **a7y17lte** (2017). Do not upload proprietary firmware, credentials, or personal data.

## Reproduce research checks

Python 3.11+; offline research checks (without Android checkout):

```sh
python3 tools/check_research_manifest.py
python3 tools/check_source_evidence.py
python3 -m unittest discover -s tests -v
```

A separate [Android 17 loader-version CI](.github/workflows/a7-android17-netbpf-gate.yml)
fetches pinned public source inputs to **confirm the expected incompatibility**.
A green source gate means the issue was detected correctly, **not** that a ROM can boot.
