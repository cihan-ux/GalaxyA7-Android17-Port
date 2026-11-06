# First scoped kernel source port: a7y18lte BPF syscall candidate

**Status: source-only research patch.** Neither the kernel nor Android 17 has
been built, loaded, flashed, booted, or validated on any phone.

## Evidence at pinned revisions

- Source: `exynos7885-dev/kernel_samsung_exynos7885` at
  `6020dfa8315134187f07ca903c9d2ed7ee0256f5`; Makefile is **4.4.302**.
- `arch/arm64/configs/lineage_a7y18lte_defconfig` currently has
  `CONFIG_BPF=y` and `CONFIG_ANON_INODES=y` but
  `# CONFIG_BPF_SYSCALL is not set`. Binder IPC and SELinux are already enabled.
- The upstream 4.4.302 `init/Kconfig` defines `BPF_SYSCALL` and selects
  `ANON_INODES` and `BPF`; thus enabling the syscall is a defined
  config delta, not a new subsystem backport.
- Source patch: [one-line BPF syscall change](../port/lineage-24.0/kernel/samsung/exynos7885/patches/0001-a7y18lte-bpf-syscall-research.patch)
  (relative link from this document is illustrative; see repository path below).
- Actual staged patch path:
  `port/lineage-24.0/kernel/samsung/exynos7885/patches/0001-a7y18lte-bpf-syscall-research.patch`.

## How it is checked (no kernel download or full platform sync)

```sh
python3 tools/check_kernel_bpf_port.py
python3 -m unittest tests.test_kernel_bpf_port -v
```

The checker temporarily copies the pinned defconfig fixture, runs
`git apply --check` and `git apply`, then compares the result against the
original with **exactly one** expected setting changed. Regression tests
reject an older 4.4.177 Makefile, changed context and extra policy/config edits.

This patch is intentionally **not** applied to a full checked-out kernel;
in a future checkout it must first be reviewed and applied to the exact
pinned kernel with `git apply`, followed by `olddefconfig`, compilation,
and feature/SELinux checks. Do not ship a kernel enabling an extra syscall
without validating verifier behavior, security and unprivileged BPF controls.

## Why this is not an Android 17 compatibility fix

AOSP's Android eBPF stack needs much more than a syscall switch, including
specific cgroup, netfilter and map/program support. Android's connectivity
BPF loader checks kernel versions newer than **4.4** in its Android S/T/U/V
paths: <https://android.googlesource.com/platform/packages/modules/Connectivity/+/5f020a5ab853acf2a5a3ece263de716987c3f0d0/bpf/loader/NetBpfLoad.cpp>.
This pin is **not proved viable for Android 17**. Do not spoof the kernel
version, disable bpfloader enforcement, or weaken SELinux to make a green test.

Other independently open blockers:

- **SM-A750F / A750FXXU5CVG1** firmware differs from the observed
  **A750FNXXU5CVG2** vendor source baseline. HAL/ABI compatibility is
  unverified; proprietary blobs are not included.
- Exynos7885 common BoardConfig imports vendor SELinux plus Samsung SLSI
  and Lineage Exynos policy; no Android 17 compiled policy or neverallow test
  exists. This change does not alter any SELinux `allow` or bypass enforcement.
- Legacy device and common manifests still declare VINTF target-level 3.
  Android 17 FCM, kernel and vendor service compatibility is unresolved.

**Success criterion for this increment:** patch applies exactly to
the reviewed kernel source fixture and passes offline CI, not that a
ROM builds or hardware works.
