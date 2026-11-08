# Working LineageOS 18.1 reference: a7y18lte build 2026-11-08

This note records a **user-reported successful boot and update** of LineageOS 18.1 (Android 11) on Samsung Galaxy A7 (2018), **SM-A750F / a7y18lte**. This is a *legacy baseline*, not an Android 17 device test.

## Release and provenance

- Maintainer/build distribution: [A2L5E0X1/lineage release a7y18lte-20261108](https://github.com/A2L5E0X1/lineage/releases/tag/a7y18lte-20261108)
- OTA manifest: [a7y18lte.json](https://github.com/A2L5E0X1/lineage/blob/13dca30e595001129d453e0656b2eae9c1650124/a7y18lte.json)
- ZIP: `lineage-18.1-20261108-UNOFFICIAL-A2L5E0X1-a7y18lte.zip`
- ZIP size: **742,826,234 bytes**; GitHub release asset digest: `sha256:926cd48efb2a4b024e85bec06cdfedcbb9ca34ed4db9c458c6949b8a606d6c0d`
- Release published 2026-11-08 02:21:31 UTC. Metadata also tracked in [machine-readable reference](../references/lineage18-a7y18lte-20261108.json).
- Developer's [2026-11-08 change notes](https://github.com/A2L5E0X1/lineage/blob/master/docs/changes/exynos7885/exynos7885.md) mention November 2026 security patches, an initial-boot splash hang fix, and a computer-standby USB deadlock fix.

## Directly verified public kernel source delta

The historical pinned research kernel is [exynos7885-dev/kernel_samsung_exynos7885@6020dfa8](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/tree/6020dfa8315134187f07ca903c9d2ed7ee0256f5). Its current `lineage-18.1` branch was **one commit ahead** when inspected:

- [2a074fb85d78 — usb: dwc3: gadget: release spin lock during gadget resume](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/commit/2a074fb85d78d065df5c529d7c0d748454bcaa3a), committed 2026-11-08 00:17:55 UTC by A2L5E0X1.
- Only `drivers/usb/dwc3/gadget.c` changes. The handler releases `dwc->lock` before calling the gadget resume callback and reacquires it afterwards.
- [Reference patch](../port/lineage-24.0/kernel/samsung/exynos7885/patches/0002-usb-dwc3-gadget-resume-unlock-reference.patch) is an exact two-insertion adaptation of the publicly visible diff, targeted **only at the pinned Linux 4.4.302 source**.
- The release was published after this source commit, but a matching timestamp is **not a reproducible-build attestation**. We do not claim that the released ZIP necessarily includes these exact source bytes.

## Safe engineering reuse

1. Retain the historical `lineage-18.1-research.xml` kernel pin so checksumed fixtures and past tests remain reproducible. Treat the new kernel commit as an **optional delta** on that baseline.
2. The patch can be validated against the historical 4.4.302 source without modifying the phone; the unit test checks patch applicability to an exact-function context. It does not compile or boot the kernel.
3. Use the functioning ROM as a **source of names and interface evidence**, e.g. `init*.rc`, `ueventd*.rc`, VINTF manifests, fstab and declared vendor services, only after obtaining its ZIP separately and evaluating provenance. Do **not** upload, commit or redistribute Samsung firmware blobs, DRM keys, IMEI/EFS, user partitions or credentials.
4. The Android 17 blocker remains: the pinned 4.4 kernel fails the tested LineageOS 24.0 NetBpfLoad kernel-version gate (5.10/5.15). Find a credible modern Exynos7885 kernel port and review whether its USB gadget locking has an equivalent fix. Do not mechanically apply this legacy patch to a modern kernel.
5. The reported first-boot splash fix has no isolated, independently verified source diff in this audit and has **not** been imported.

**Status:** evidence and legacy USB reference only; no Android 17 ROM, device test, vendor-blobs extraction or phone access.
