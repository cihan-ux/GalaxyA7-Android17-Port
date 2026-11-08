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
| G7e: Linux 6.15 Android 17 kernel config/Image experiment | CONFIG SOURCE CHECK PASS, IMAGE BUILD NOT YET VERIFIED | [Image CI 42505758584](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42505758584) configures ARM64 Binder/BPF/SELinux and attempts a real Image build; follow CI result for pass/fail. Kernel version-only loader gate is not Android runtime compatibility. |
| G7b: Android 17 VINTF/SELinux/HAL/vendor port | NOT VALIDATED | Old FCM3/SELinux, legacy HALs, boot/partition path and vendor symbols unresolved |
| G8: Device boot/recovery | NOT STARTED | Explicit approval, backups, hardware and restoration plan required |

## Highest-value next actions

1. Find and evaluate a *real*, technically credible Exynos7885/SM-A750F kernel modernization path. A kernel version label or one BPF syscall flag is not enough.
2. Resolve historical LineageOS 18.1 BSP dependencies and legally usable firmware-specific vendor interfaces to build a genuine baseline ROM.
3. Freeze all target platform sources, then run genuine assembled SELinux, VINTF, BPF feature and native/HAL checks instead of interpreting isolated unit tests as Android 17 readiness.

Do not publish proprietary firmware, EFS or personal partition images in this repository.
