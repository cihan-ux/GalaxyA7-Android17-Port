# Android 17 target source compatibility audit

Observed 2026-11-04 UTC. **No Android 17 checkout, ROM build, VINTF run, or device test has been completed.** These are concrete source comparisons, not a compatibility verdict.

## Target identified without changing the research manifest

The observed `LineageOS/android` `lineage-24.0` head is `e4b71068f6ee045ff30e4865a8d82f4047eb78ea`. Its [default.xml](https://github.com/LineageOS/android/blob/e4b71068f6ee045ff30e4865a8d82f4047eb78ea/default.xml) selects `refs/tags/android-17.0.0_r1` for AOSP projects and `refs/heads/lineage-24.0` for Lineage projects. This supplies an identifiable Android 17 research target. It does not establish Galaxy A7 support.

Additional observed `lineage-24.0` heads used below:

| Repository | Commit |
|---|---|
| `LineageOS/android_build` | `90d006387398ae6899145e6531a304500cfa0f70` |
| `LineageOS/android_hardware_interfaces` | `a0221f11248a924532444fc7de85d41998b9fe1e` |
| `LineageOS/android_system_sepolicy` | `d61fd80832f558d52de026097d30d695634e8b0f` |

The top-level manifest still contains branch references. This table records inspected snapshots; it is not a fully frozen `repo manifest -r` output. The existing three-project LineageOS 18.1 research manifest is unchanged.

## Source differences requiring engineering work

| Area | Pinned A7/common/kernel source | Inspected Android 17 target | Consequence |
|---|---|---|---|
| VINTF | Device and common manifests declare `target-level="3"` | [Compatibility matrix build definitions](https://github.com/LineageOS/android_hardware_interfaces/blob/a0221f11248a924532444fc7de85d41998b9fe1e/compatibility_matrices/Android.bp) install A17 FCMs `7`, `8`, `202404`, `202504`, `202604`; they provide no FCM 3 module | The inspected target does not supply the baseline's matrix level. A complete framework/vendor compatibility path must be designed and tested; changing the number alone cannot implement missing HAL behavior. |
| Kernel matrix | Kernel Makefile reports `4.4.302`; device defconfig exists | The same target matrix definitions list kernel configurations starting at 4.14 for FCM 7 and newer kernels for subsequent FCMs | No supported 4.4 matrix path was found in these definitions. This does not prove that every custom legacy-device port is impossible, nor that launch-device kernel requirements automatically apply to this upgrade. |
| SELinux | Common BoardConfig imports Lineage Exynos and Samsung SLSI vendor policy | [Target core/config.mk](https://github.com/LineageOS/android_build/blob/90d006387398ae6899145e6531a304500cfa0f70/core/config.mk#L910) lists platform policy compatibility versions from `31.0` onward. [Target policy Android.bp](https://github.com/LineageOS/android_system_sepolicy/blob/d61fd80832f558d52de026097d30d695634e8b0f/Android.bp) installs corresponding compatibility modules | The listed target compatibility set omits Android 10/11 policy versions. Actual extracted vendor policy version and rebuilt policy must be checked; source branch names do not establish policy compatibility. |
| Vendor and graphics | Common product selects Samsung SLSI gralloc/HWC, OMX and proprietary vendor makefiles | These vendor and BSP implementations are absent from the project's three-project manifest | Module availability, native symbols, VNDK assumptions and SELinux remain unresolved even where an interface definition survives in the target. |

Baseline facts can be reproduced from the source-only fixtures in `tests/fixtures/upstream/{device,common,kernel}` and their provenance inventory. The kernel's version is a source Makefile value, not the version running on the user's phone.

## Checks that prevented unsupported blockers

The target still defines [`android.hardware.keymaster@3.0-impl` and `android.hardware.keymaster@3.0-service`](https://github.com/LineageOS/android_hardware_interfaces/blob/a0221f11248a924532444fc7de85d41998b9fe1e/keymaster/3.0/default/Android.bp), both requested by the A7 product. It also defines [`android.hardware.graphics.allocator@2.0-impl` and its service](https://github.com/LineageOS/android_hardware_interfaces/blob/a0221f11248a924532444fc7de85d41998b9fe1e/graphics/allocator/2.0/default/Android.bp). Therefore, the age of HIDL alone is insufficient evidence that these modules have been removed. Source definitions do not establish that they compile or work with Samsung's vendor libraries.

The target [core/Makefile](https://github.com/LineageOS/android_build/blob/90d006387398ae6899145e6531a304500cfa0f70/core/Makefile#L2884) still includes `$(BOARD_CUSTOM_BOOTIMG_MK)`. The baseline's custom Samsung boot-image path is consequently a missing dependency/integration task, not evidence that Android 17 removed this build hook.

The pinned A7 product declares `PRODUCT_SHIPPING_API_LEVEL := 28`. Target [product_config.mk](https://github.com/LineageOS/android_build/blob/90d006387398ae6899145e6531a304500cfa0f70/core/product_config.mk#L660) derives `VSR_VENDOR_API_LEVEL` from shipping API information; [core/config.mk](https://github.com/LineageOS/android_build/blob/90d006387398ae6899145e6531a304500cfa0f70/core/config.mk#L450) chooses 4 KiB ELF alignment for vendor API levels below 34. A blanket claim that this legacy target must use a 16 KiB kernel is not supported by these sources. Final evaluated configuration and native-library checks remain necessary.

## Next source/build validation

1. Close the maintained LineageOS 18.1 dependency inventory at exact revisions, including SLSI config, siblings, sepolicy and Samsung boot tooling. Keep vendor provenance and binary licensing separate from public source availability.
2. Reproduce an 18.1 configuration/build on a suitable builder before changing the Android platform. Record the full manifest and toolchain; the pinned common configuration requests Clang.
3. Freeze the candidate Android 17 platform checkout. Produce a module inventory and run source configuration, SELinux compilation and VINTF checks against the intended vendor manifests and kernel information. Preserve actual failures as evidence.
4. Resolve FCM 3/4.4 and vendor-policy gaps with an explicit supported implementation or documented legacy compatibility work. Do not suppress validation or raise shipping/target levels to conceal the gaps.
5. Evaluate graphics, camera, radio, keymaster, media and native ABI behavior separately. Passing Python tests establishes scanner behavior and evidence integrity only.

Phone access, flashing and repartitioning are outside this work. Source inspection cannot settle SM-A750F partition topology or runtime hardware behavior.
