# Linux 6.15-rc1 ARM64 driver objects: targeted real compile (research only)

The full [Linux 6.15 experimental ARM64 Image job](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42505758584) may be slow because it compiles an entire generic arm64 kernel. A separate [shorter CI](../.github/workflows/a7-linux615-targeted-driver-objects.yml) compiles **seven real, relevant AArch64 objects** from pinned source, to expose concrete compiler issues without declaring Android 17 compatibility.

- `drivers/mmc/host/dw_mmc-exynos.o`: Samsung Exynos MMC controller used by the [A7 eMMC lab DTS](a7y18lte-emmc-modern-source-mapping.md).
- `drivers/clk/samsung/clk-exynos7885.o`: Exynos7885 SoC clock support.
- `drivers/pinctrl/samsung/pinctrl-exynos-arm64.o`: ARM64 Exynos pin mapping.
- `drivers/android/binder.o` and `drivers/android/binderfs.o`: Android process IPC infrastructure.
- `security/selinux/hooks.o`: security hooks in enforcing-capable Linux.
- `kernel/bpf/syscall.o`: modern kernel BPF syscall implementation.

The job checks the resolved `.config` for required options and `readelf` verifies that **each** object actually compiles as AArch64. Compiler logs/checksums are stored; failures must not be reported as successful. It uses pinned [Linux 6.15 Exynos7885 source](https://github.com/Mollomm1/linux-exynos7885/tree/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c) and the reviewed [Android config fragment](../port/linux-6.15/config/android17-research.fragment).

**Crucial limitation:** these objects do not include a working S2MPU08 MFD/regulator, Samsung ACPM/SPEEDY transport, verified A7 memory/carveouts, all vendor drivers, or validated A7 Android 17 userspace. Even seven compiled objects are **not** a working kernel Image or ROM. See [power blocker](a7y18lte-s2mpu08-power-port-blocker.md). No phone is accessed.
