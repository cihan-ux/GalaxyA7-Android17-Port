# Real kernel-build evidence and next integration gate

**Updated 2026-11-06. Kernel Image outputs are not boot images, flashable ROMs, or proof of Android 17 compatibility.**

## Two successful ARM64 kernel builds

- Baseline: [CI 41951781918](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/41951781918) compiled pinned Exynos7885 Linux **4.4.302** (`6020dfa8315134187f07ca903c9d2ed7ee0256f5`) using `lineage_a7y18lte_defconfig`, Ubuntu Clang **18.1.3** and two narrowly scoped legacy Clang signature fixes. `Image` **23,807,080 bytes**, SHA-256 `eb7a3871afd7b31ff09ea7199ace397b793cde6bbaeabf6105118ca3c9f31bd6`. This Image did not contain the later BPF syscall delta.
- BPF-enabled: [CI 42235116992](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42235116992) applied the scoped `CONFIG_BPF_SYSCALL=y` source patch and the two legacy signature fixes, then compiled a **complete ARM64 kernel Image**, `vmlinux` and `kernel/bpf/syscall.o`. `Image` **23,840,488 bytes**, SHA-256 `069302468615291875fd6a3e6139a4af0f3c4e6ae02875a8348cd0c427f0cb79`. BPF object architecture and image existence passed. The job uploaded logs and a **NON-FLASHABLE** kernel Image.

Both jobs emitted legacy RWX link segment warnings. Success establishes reproducible kernel compilation, not device boot, kernel security or Android version compatibility.

## Confirmed Android 17 BPF loader version blocker

[LineageOS 24.0 source audit](android17-netbpf-kernel-gate.md): the actual Connectivity `NetBpfLoad` refuses Linux 4.4, starting with its unconditional >=4.9 test. For Android 17 API full 3700 its version checks require >=5.10, and for API full 3710 >=5.15. Enabling `BPF_SYSCALL` is insufficient; do not bypass version/security checks.

## Next engineering decision

1. Explore whether a **credible >=5.10 kernel tree for Exynos7885 and SM-A750F** exists, with driver/device tree compatibility. An upstream version alone is not hardware compatibility.
2. If no credible kernel upgrade exists, document the extensive forward-port/backport surface; do not keep declaring trivial 4.4 edits Android 17 progress.
3. Reconstruct the complete LineageOS 18.1 device/vendor/SLSI/boot-tooling/SELinux dependency set and **build an actual baseline ROM** before promising A17.
4. Validate Android 17's assembled framework/vendor VINTF, SELinux policy, BPF features, hardware HAL services and extracted vendor ABI on a suitable build host; do not fabricate passing results.
5. No phone flashing, recovery changes, bootloader unlock, EFS access or proprietary firmware distribution.

Keep kernel compiler success, Android 17 viability and phone boot validation as strictly separate milestones.
