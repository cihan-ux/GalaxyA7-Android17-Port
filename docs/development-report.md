# Development report — evidence-based Android 17 preparation

This work starts from `e38e392c71eefec6b7bce3d703bd8a9c9dbe709a` and is proposed on `dev/evidence-based-source-audit`. It prepares source research and tooling; it does not produce an Android ROM.

## Completed

- Inspected repository tools, tests, manifests, documentation, the starter archive's file listing, and recent GitHub Actions results. The inherited branch already passed 108 tests and its latest CI run; the prior configured-path regex failures had already been repaired.
- Added 21 complete upstream source/license fixtures, with immutable commit/path URLs, upstream Git blob IDs, byte counts and SHA-256. An offline verifier binds device/common/kernel evidence to the research XML and rejects corrupted or incomplete fixture inventories. No vendor binaries or vendor Makefiles were imported.
- Improved both dependency scanners using the full upstream Makefiles: continued lines, whole operands, framework paths, optional includes, unresolved expressions, host tools, and multiple conditional kernel-path candidates. Added JSON output and explicit strict failure status. See [scanner usage and limits](exynos7885-dependency-scanner.md).
- Corrected documentation that mixed historical `old_device_*` trees with the maintained pins. The actual maintained baseline requests Clang, shipping API 28 and a present defconfig in kernel source version 4.4.302. Source facts and integrity handling now have reproducible tests.
- Audited vendor metadata at exact revisions without copying binaries. Located five matching-branch Samsung SLSI repositories and inspected the config source; recorded the concrete `libhwc2.1` versus newer `hwc3` difference. See [source evidence](source-evidence-audit.md) and [SLSI discovery](slsi-matching-source-discovery.md).
- Identified an exact Android 17 target manifest snapshot and compared its matrix, kernel-policy and SELinux build definitions with the baseline. Recorded both compatibility gaps and surviving legacy interfaces/build hooks in the [target comparison](android17-source-compatibility.md).
- Updated CI with pinned Node24 actions, explicit Python 3.11/3.14 jobs, fixture verification, documentation triggers and read-only token permissions. Generated Python bytecode is ignored.

## Validation

The research-manifest check, offline fixture verifier and **153 tests** pass locally on Python 3.12.14. The scanner's strict CLI returns 1 as expected for the full common BoardConfig with an empty availability inventory. Workflow YAML structure and `git diff --check` pass. The [CI verification record](ci-verification.md) describes historical and hosted checks.

[PR #1](https://github.com/cihan-ux/GalaxyA7-Android17-Port/pull/1) is open and unmerged. Its implementation commit `b7f415f210b72df7a000c455682389ad236e60d3` passed the hosted [PR matrix](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/41937998153): **153 tests on each of Python 3.11 and 3.14**, with manifest and source-evidence verification successful.

These results validate source handling and research tooling. No full Android checkout, compiler/kernel build, SELinux compilation, VINTF run, image validation or device test was completed.

## Remaining blockers and realistic next steps

1. **Incomplete baseline checkout.** Trace a complete maintained 18.1 manifest to resolve the interfaces namespace, SLSI/Lineage policy, Wi-Fi integration, boot-tool transitive inputs and compiler revision. Inspect sibling licenses/modules and freeze all revisions; branch-name matches alone are insufficient.
2. **SM-A750F vendor provenance.** Establish exact model/firmware extraction provenance and applicable use rights outside this public repository. Existing FN/GN references do not prove F/U5 compatibility. Audit native dependencies and generated manifests without publishing proprietary artifacts.
3. **No reproduced baseline build.** On a suitably provisioned Linux builder, configure the complete source tree, build the requested kernel and an 18.1 baseline, and preserve the frozen manifest, compiler version and actual error logs. Python CI cannot substitute for these checks.
4. **Android 17 compatibility work.** The inspected target omits the baseline FCM 3/4.4 matrix path and old policy compatibility versions. Freeze the target checkout, evaluate its real product configuration, and run VINTF/SELinux/module/native-ABI checks before implementing incremental changes. Do not relabel target/shipping levels or suppress validation to hide incompatibilities.
5. **Hardware-specific evidence remains external to this task.** Source constants cannot establish SM-A750F partition topology, recovery behavior or runtime hardware function. No phone access, flashing, repartitioning, unlocking or wiping is part of this work.

The three-project research manifest is unchanged. No changes were made to other repositories, and this development branch must not be merged automatically. Android 17 compatibility remains unproven.
