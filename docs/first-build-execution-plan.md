# Real kernel-build evidence and next integration gate

**Updated 2026-11-06. Research build outputs are not flashable and are not Android 17 ROMs.**

## Verified historical baseline: kernel Image produced

The existing [kernel build workflow run 41951781918](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/41951781918) succeeded on 2026-11-05 UTC. Unlike an offline unit test, its job actually compiled the pinned Exynos7885 Linux **4.4.302** source at `6020dfa8315134187f07ca903c9d2ed7ee0256f5` using `lineage_a7y18lte_defconfig` and Ubuntu Clang **18.1.3**. The job verified:

- `kernel-out/arch/arm64/boot/Image`: **23,807,080 bytes**, SHA-256 `eb7a3871afd7b31ff09ea7199ace397b793cde6bbaeabf6105118ca3c9f31bd6`.
- `kernel-out/vmlinux`: **205,201,208 bytes**, ELF AArch64.
- The successful run recorded two narrowly scoped legacy C function signature fixes in `drivers/input/input.c` and `drivers/mfd/s2mpu08_irq.c`.
- The linker emitted legacy RWX segment warnings; success does **not** establish security, firmware compatibility, or a bootable device image.

This successful **historical baseline Image** did **not** contain the later staged `CONFIG_BPF_SYSCALL=y` source patch. It must not be described as an Android 17-ready kernel. Earlier project notes saying that no kernel was ever compiled are superseded by this evidence.

## Next concrete gate: full BPF-patched Image

The later [BPF object-group run 42080689936](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42080689936) successfully compiled the kernel's configured `kernel/bpf/` objects for ARM64, including `syscall.o`, but did not compile the complete patched Image.

The [new full BPF-patched Image workflow](../.github/workflows/a7-bpf-kernel-image-build.yml) builds on these two independent results. It checks out the same pinned kernel, applies the exact one-line BPF syscall patch and the two previously necessary legacy Clang compatibility fixes, generates a real ARM64 kernel configuration, and attempts a full `Image` compilation. It records the compiler, full build log and exit code, checks for an AArch64 BPF syscall object, and preserves a successful kernel Image strictly as a **NON-FLASHABLE** research artifact.

**Do not mark this new gate PASS until its specific GitHub Actions run reports a successful full compilation and its artifact checks pass.** No CI build is a boot test.

## Remaining independent blockers

1. **Android 17 eBPF support:** A Linux 4.4 kernel with `BPF_SYSCALL` enabled lacks proof of the modern Android BPF loader and kernel feature requirements. Do not spoof the kernel version or bypass feature/security checks.
2. **Historical LineageOS 18.1 ROM build:** A standalone kernel Image is not a complete baseline ROM. A fully pinned Samsung SLSI/HAL/sepolicy/boot-tooling dependency checkout and appropriate Linux builder are still required.
3. **SM-A750F vendor provenance:** Existing model-variant vendor metadata cannot prove firmware-matched proprietary ABI compatibility. Do not include proprietary images or personal device data in this repository.
4. **Android 17 forward-port:** Reconcile VINTF/FCM, SELinux neverallows, HAL service compatibility, partition layout and current platform APIs with the actual assembled sources.
5. **Hardware validation:** Device-specific recovery/partition evidence, backups and explicit approval would be required for any future device work. This project stage performs no flash, unlock, wipe or phone access.

Avoid treating static tests, isolated object builds or a standalone Image as evidence that Android 17 boots on SM-A750F.
