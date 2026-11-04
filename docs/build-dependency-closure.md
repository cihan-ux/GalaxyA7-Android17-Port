# Build dependency closure — pinned LineageOS 18.1 baseline

**Status: incomplete; do not start a full ROM build or flash.** This is an inventory of dependencies referenced by pinned upstream source files, not a working Android 17 manifest.

## Confirmed source repositories

| Local path | Source | Revision |
|---|---|---|
| `device/samsung/a7y18lte` | `exynos7885-dev/device_samsung_a7y18lte` | `f17643ba01010c45b628d5acb8f48350ded61606` |
| `device/samsung/exynos7885-common` | `exynos7885-dev/device_samsung_exynos7885-common` | `f2ce8d2093711026f021cba7036334d381d455ef` |
| `kernel/samsung/exynos7885` | `exynos7885-dev/kernel_samsung_exynos7885` | `6020dfa8315134187f07ca903c9d2ed7ee0256f5` |

These three are pinned in `manifests/lineage-18.1-research.xml`.

## Referenced dependencies not supplied by the three-project manifest

| Path | Evidence | Status |
|---|---|---|
| `vendor/samsung/a7y18lte` | Device `device.mk` inherits `a7y18lte-vendor.mk` | Proprietary vendor tree missing |
| `vendor/samsung/exynos7885-common` | Common `exynos7885.mk` inherits common vendor makefile | Proprietary vendor tree missing |
| `hardware/samsung_slsi-linaro` | Common `BoardConfigCommon.mk` includes `config/BoardConfig7885.mk` | BSP dependency unresolved |
| `hardware/samsung` | Common `BoardConfigCommon.mk` points to `mkbootimg.mk` | Must resolve matching Samsung boot tooling |
| `device/lineage/sepolicy/exynos` | Common `BoardConfigCommon.mk` includes `sepolicy.mk` | Must resolve matching platform tree |
| `device/samsung_slsi/sepolicy` | Common `BoardConfigCommon.mk` includes `sepolicy.mk` | Must resolve matching BSP policy |
| `hardware/samsung_slsi/scsc_wifibt` | Common `exynos7885.mk` names WPA supplicant CFI path | Must resolve or justify absence |
| `hardware/google/interfaces`, `hardware/google/pixel` | Common `exynos7885.mk` references components | Confirm availability in chosen ROM base |
| `hardware/samsung/aidl/power-libperfmgr` | Common `exynos7885.mk` references power support | Confirm availability in chosen ROM base |

Evidence:
- [Pinned device BoardConfig](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/f17643ba01010c45b628d5acb8f48350ded61606/BoardConfig.mk)
- [Pinned common BoardConfig](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/BoardConfigCommon.mk)
- [Device makefile](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/f17643ba01010c45b628d5acb8f48350ded61606/device.mk)
- [Common makefile](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/exynos7885.mk)

## Next build gates

1. Find **matching, licensed and revision-specific** BSP sources; do not silently use unrelated newer HALs.
2. Verify extraction scripts and obtain vendor binaries only from firmware/device owned by the builder. **Never commit proprietary blobs or private partition data to this public repository.**
3. Construct a *separate complete* LineageOS 18.1 baseline manifest and validate source checkout before attempting any Android 17 adaptation.
4. Reconcile the SM-A750F/U5 partition layout, variant-specific NFC manifests, and recovery plan with the pinned tree.
5. For Android 17, separately address kernel 4.4, HIDL/VINTF, SELinux, graphics and vendor API compatibility.

**A successful XML/unit test run does not satisfy any of these build gates.**

## Discovery update (2026-11-05)

Three repository candidates have since been **located** under `exynos7885-dev`: `hardware_samsung`, `proprietary_vendor_samsung_a7y18lte`, and `proprietary_vendor_samsung_exynos7885-common` (all expose a `lineage-18.1` branch and expected top-level files). See [upstream-repository-discovery.md](upstream-repository-discovery.md). Their existence reduces *discovery uncertainty*, **not** the build blockers: matching revisions, licensing, SM-A750F firmware provenance, and compatibility are still unverified. Do not add proprietary blobs to this public repository. The SLSI BSP dependency remains unresolved.
