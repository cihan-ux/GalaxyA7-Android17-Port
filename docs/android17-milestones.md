# Android 17 port: evidence-based milestone tracker

This tracker separates actual compiler evidence, source checks and hardware functionality.
**No flashable Android 17 ROM exists. No phone has been accessed.**

| Gate | Status | Evidence / unblock requirement |
|---|---|---|
| G0: Source provenance | PARTIAL | Pinned LineageOS 18.1 device/common/kernel sources, but incomplete historical BSP/vendor provenance |
| G1: Research manifest and offline tests | PASS (research only) | GitHub Actions research-validation checks |
| G2: Partition arithmetic | PASS (source arithmetic only) | Exact on-device partition layout unverified |
| G3: Exact SM-A750F partition topology | BLOCKED | Read-only model-specific device evidence needed |
| G4: SM-A750F vendor provenance | BLOCKED | A750FN reference is not verified interchangeable with SM-A750F firmware |
| G5: Complete historical BSP dependencies | BLOCKED | Samsung SLSI, boot tooling, vendor services, licenses and full platform source closure |
| G6a: Linux 4.4.302 baseline ARM64 kernel Image | PASS (compiled, non-flashable) | [CI 41951781918](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/41951781918), Image size and SHA-256 verified |
| G6b: Linux 4.4.302 BPF-enabled ARM64 kernel Image | PASS (compiled, non-flashable) | [CI 42235116992](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42235116992): 23,840,488 bytes, SHA-256 `069302468615291875fd6a3e6139a4af0f3c4e6ae02875a8348cd0c427f0cb79`; kernel ELF and BPF object verified |
| G6c: Complete LineageOS 18.1 baseline ROM | NOT BUILT | Kernel Image is only one input; G3–G5 remain unresolved |
| G7a: Android 17 NetBpfLoad kernel gate | BLOCKED (verified source requirement) | [Pinned LineageOS 24.0 loader](android17-netbpf-kernel-gate.md) requires >=5.10 for API 3700, >=5.15 for 3710; 4.4.302 fails |
| G7c: Experimental Linux 6.15-rc1 A7 DTS source | PASS (minimal A7 DTB syntax only) | [CI 42503704081](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42503704081) compiled model-correct a7y18lte DTB. No RAM map, storage, or boot support in the minimal DTB; [eMMC-only lab source](a7y18lte-emmc-modern-source-mapping.md) is being tested separately. Not an Android 17 kernel Image/ROM. |
| G7d: Linux 6.15 A7 peripheral and memory validation | PARTIAL (source only) | [eMMC DTB CI 42504144337](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42504144337) passed; [GPIO-keys lab](a7y18lte-gpio-keys-linux615-mapping.md) maps common A7 power/volume pins with dedicated CI. Real RAM carveouts, storage I/O, key electrical polarity, regulators and other drivers are unverified. |
| G7e: Linux 6.15 Android 17 kernel config/Image experiment | PASS (genuine Image compilation only; NOT BOOTABLE) | [Image CI 42505758584](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42505758584) compiled 39,526,912-byte ARM64 Image, SHA-256 `160355fbd5dd321112cf791fe103db4d76d7fe6f6e34e0cb760e10c6ca840755`; Exynos MMC/clock/pinctrl + Binder/binderfs + SELinux objects verified. 6.15 satisfies NetBpfLoad **version check only**; not A7 runtime/ROM. |
| G7f: A7 S2MPU08/ACPM PMIC driver | BLOCKED (source-verified) | [PMIC gap CI 42508771359](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42508771359) confirms old A7 S2MPU08 driver and missing Linux 6.15 MFD/regulator integration in audited paths. LDO2/vqmmc, LDO35/vmmc and ACPM transport must be brought up safely. |
| G7g: Targeted modern ARM64 driver object build | PASS (actual kernel compiler objects only) | [Focused driver CI 42508948297](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42508948297) compiled seven actual AArch64 Exynos MMC/clock/pinctrl, Binder/binderfs, SELinux and BPF objects; not real A7 PMIC support. |
| G7h: S2MPU08 first voltage-only modern C source | PARTIAL (ARM64 object compiles; NO DRIVER) | [CI 42515323634](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42515323634) compiled original LDO2/LDO35 voltage-only metadata as genuine Linux 6.15 object. Follow-up [CI 42515547576](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42515547576) verifies pinned legacy sparse enum IDs and revised board-clamped source. No ACPM I/O, PMIC probe, IRQ, regulator enable or runtime test. |
| G7i: ACPM PMIC protocol read framing | PASS (inert AArch64 object only; transport BLOCKED) | [ACPM CI 42517454955](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42517454955) passed 512 read-only C message vectors and real AArch64 object compilation. Exynos7885 firmware initdata 0x4B80 differs from GS101 0xA000; modern ACPM and mailbox only support GS101 in their compatible tables ([follow-up CI 42517688188](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42517688188)). No live IPC, mailbox port, regulator or working PMIC. |
| G7j: Legacy A7 ↔ modern ACPM SRAM/channel ABI | PASS (offset tests and compiler ONLY) | [ABI CI 42609437249](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42609437249) confirmed pinned old/new 28-byte firmware prefix and 72-byte channel ABI field alignment via native C and AArch64 object compile. Physical SRAM firmware behavior not checked. |
| G7k: Model-specific Exynos7885 mailbox driver source | PASS (corrected AArch64 compile; NO hardware) | [CI 42613382173](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42613382173) compiled revised ARM64 prototype and pinned-source tests confirming AP→APM `INTGR0=0x08`, `BIT(channel)<<16`, not the earlier wrong-direction INTGR1. Still **no DTS binding** or runtime proof. |
| G7l: Experimental Exynos7885 mailbox Kconfig/Kbuild integration | PASS (revised archive, no device) | [CI 42613303553](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42613303553) confirmed default-OFF Kconfig and real Linux 6.15 AArch64 `built-in.a` containing the corrected INTGR0 prototype after CI-only opt-in. No firmware IPC/PMIC device operation. |
| G7m: S2MPU08 complete mock read request/ACPM queue planning | HOST C/SOURCE PASS, ARM64 CHECK PENDING | [CI 42614326343](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42614326343) passed source-anchored legacy sequence/direction checks and host-C synthetic queue cases; AArch64 compile stage is separate. No SRAM mapping, writes or runtime communication. |
| G7b: Android 17 VINTF/SELinux/HAL/vendor port | NOT VALIDATED | Old FCM3/SELinux, legacy HALs, boot/partition path and vendor symbols unresolved |
| G8: Device boot/recovery | NOT STARTED | Explicit approval, backups, hardware and restoration plan required |

## Highest-value next actions

1. Find and evaluate a *real*, technically credible Exynos7885/SM-A750F kernel modernization path. A kernel version label or one BPF syscall flag is not enough.
2. Resolve historical LineageOS 18.1 BSP dependencies and legally usable firmware-specific vendor interfaces to build a genuine baseline ROM.
3. Freeze all target platform sources, then run genuine assembled SELinux, VINTF, BPF feature and native/HAL checks instead of interpreting isolated unit tests as Android 17 readiness.

Do not publish proprietary firmware, EFS or personal partition images in this repository.
