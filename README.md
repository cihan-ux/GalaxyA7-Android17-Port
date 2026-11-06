# Galaxy A7 2018 (SM-A750F) — Android 17 port research

**Status: source-level Android 17 prototype, NOT buildable or flashable as an Android 17 ROM.** A pinned historical Linux 4.4.302 ARM64 kernel **has** been compiled, including a BPF-enabled variant, but Android 17 runtime/kernel support is **not** established.

Target: Samsung Galaxy A7 (2018), **a7y18lte**, Exynos 7885. Previously recorded handset baseline: Android 10, firmware A750FXXU5CVG1 (U5), Linux 4.4.177, arm64 ABI. No phone has been accessed.

## Verified kernel build milestone

- [Baseline ARM64 kernel Image build](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/41951781918) passed with pinned Linux 4.4.302 and Clang 18.1.3.
- [Full ARM64 kernel Image with BPF syscall enabled](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42235116992) passed: **23,840,488 bytes**, SHA-256 `069302468615291875fd6a3e6139a4af0f3c4e6ae02875a8348cd0c427f0cb79`. Output is **NOT FLASHABLE**.
- [LineageOS 24.0 NetBpfLoad source requirements](docs/android17-netbpf-kernel-gate.md) expose a **confirmed version gate mismatch**: Android 17.0 requires kernel >=5.10 and 17.1 >=5.15 at this loader; the historical 4.4.302 source fails even its unconditional 4.9 check. Kernel BPF syscall support alone cannot fix this.

## Source candidates (not yet verified as a complete build set)

- [Pinned maintained LineageOS 18.1 device tree](https://github.com/exynos7885-dev/device_samsung_a7y18lte/tree/f17643ba01010c45b628d5acb8f48350ded61606)
- [Pinned common tree](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/tree/f2ce8d2093711026f021cba7036334d381d455ef)
- [Pinned kernel, source version 4.4.302](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/tree/6020dfa8315134187f07ca903c9d2ed7ee0256f5)
- [Alternative device tree](https://github.com/nnhra/android_device_samsung_a7y18lte)
- [Device recovery/GSI notes](https://github.com/Hari-Pi/a7y18lte-Resources)
- [LineageOS upstream](https://github.com/LineageOS/android)

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
