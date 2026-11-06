# Android 17 NetBpfLoad kernel-version incompatibility — verified source gate

**Status (2026-11-06): known blocker; not an Android 17 kernel or ROM.**

The pinned Exynos7885 Linux 4.4.302 successfully compiled as an ARM64 `Image` with
`CONFIG_BPF_SYSCALL=y` in [CI run 42235116992](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42235116992).
The produced `Image` is **23,840,488 bytes**, SHA-256
`069302468615291875fd6a3e6139a4af0f3c4e6ae02875a8348cd0c427f0cb79`.
The same job compiled ARM64 `kernel/bpf/syscall.o` and `vmlinux`.
Linker RWX warnings remain. This Image was **not** flashed or booted.

## Actual Android 17 loader minimum

Inspected immutable LineageOS 24.0 Connectivity commit
[`7c04d866538e6f689823b769fb5c1e614ca0e295`](https://github.com/LineageOS/android_packages_modules_Connectivity/tree/7c04d866538e6f689823b769fb5c1e614ca0e295):

- [`bpf/loader/NetBpfLoad.cpp` lines 1549–1587](https://github.com/LineageOS/android_packages_modules_Connectivity/blob/7c04d866538e6f689823b769fb5c1e614ca0e295/bpf/loader/NetBpfLoad.cpp#L1549-L1587) checks kernel >=4.9 unconditionally, >=4.14 for U, >=4.19 for V, >=5.4 for 25Q2, >=5.10 for 25Q4, and >=5.15 for 26Q4.
- [`bpf/headers/include/bpf/BpfUtils.h` lines 148–161](https://github.com/LineageOS/android_packages_modules_Connectivity/blob/7c04d866538e6f689823b769fb5c1e614ca0e295/bpf/headers/include/bpf/BpfUtils.h#L148-L161) defines 25Q4 as full API >=3610, 26Q2 (Android 17.0) as >=3700, and 26Q4 (Android 17.1) as >=3710.

Therefore the **version gate alone** requires Linux >=5.10 for Android 17.0 (full API 3700) and >=5.15 for Android 17.1 (full API 3710). Exynos7885's 4.4.302 fails *even the unconditional 4.9 gate*. It is not fixed by enabling a legacy BPF syscall.

## Reproducible CI

The [`a7-android17-netbpf-gate.yml`](../.github/workflows/a7-android17-netbpf-gate.yml) workflow downloads precisely the two immutable upstream source files and uses [`check_android17_netbpf_gate.py`](../tools/check_android17_netbpf_gate.py) to extract required thresholds from the real C++ source, rather than hard-coding a success claim. It explicitly expects a **blocked** result for both Android 17 API levels. If upstream code changes or no longer matches the expected gate structure, the check fails closed. Offline regression tests cover the parsing and version comparisons.

**A green gate CI means the incompatibility was successfully detected, not that Android 17 compatibility was achieved.** A future kernel at or above the version threshold would still require cgroup/eBPF capability checks, vendor driver support, VINTF, full SELinux, and a real ROM build.

## Engineering choice

1. Investigate a credible, actively maintained Exynos7885-capable >=5.10 kernel **with Samsung hardware driver coverage and SM-A750F-specific DT support**, not merely a generic upstream Linux kernel.
2. If none exists, estimate a substantial kernel/driver modernization (or fully implemented, reviewable feature backports); record the scope explicitly. Do not fake `uname`, modify `NetBpfLoad.cpp` to suppress enforcement, weaken SELinux or change VINTF levels to conceal missing functionality.
3. In parallel, finish a reproducible **LineageOS 18.1 baseline ROM build** and resolve device/vendor provenance. The compiled 4.4 Image only proves part of this prerequisite.
4. Treat source candidate availability as a **lead**, not a validated Android 17 kernel. Do not access or flash the handset without a separate user-approved safety plan.

No known verified >=5.10 SM-A750F Android kernel has been established by this audit.
