# Exynos7885 ACPM mailbox integration into *real* Linux 6.15 Kbuild, disabled by default

This milestone moves beyond manually compiling a single C file: it tests whether our [A7-specific mailbox driver prototype](a7-exynos7885-acpm-mailbox-prototype.md) can participate in the pinned Linux 6.15 build system as an **opt-in, AArch64 built-in object**.

The [staging script](../tools/stage_exynos7885_mailbox_kernel_integration.py) adds `CONFIG_EXYNOS7885_ACPM_MBOX_LAB` to an ephemeral pinned Linux 6.15 checkout's `drivers/mailbox/Kconfig`, and wires it to `obj-$(CONFIG_EXYNOS7885_ACPM_MBOX_LAB) += exynos7885-acpm-mbox-prototype.o` in `drivers/mailbox/Makefile`. The option **defaults to n**, is available only when ARCH_EXYNOS and OF are enabled, and is never enabled in a production source tree or device.

[The CI integration workflow](../.github/workflows/a7-acpm-mailbox-kbuild-integration.yml) must verify:
- The option is OFF after real ARM64 `defconfig`.
- An explicit test-only enable survives `olddefconfig` and resolves all Kconfig dependencies.
- A real `make ARCH=arm64 LLVM=1 drivers/mailbox/built-in.a` contains `exynos7885-acpm-mbox-prototype.o` as an AArch64 object, rather than only compiling the file out-of-tree.
- No DT board node matches the prototype's nonproduction compatible; the pinned original GS101 driver is unchanged.
- Correct A7 AP→APM doorbell `INTGR0=0x08` with `BIT(channel)<<16` (not the earlier wrong-direction `INTGR1=0x1C`), and no unverified IRQ-mask register writes. Source comparisons verify the original Samsung `apm_interrupt_gen()` implementation.

This is **not** a fully linked `vmlinux` or a functional kernel/ROM. A7's monolithic historical ACPM firmware node, IRQ ownership, power clocks, memory/SRAM channel queues, the S2MPU08 regulators and their revision-specific safety mechanisms remain unresolved.

Neither phone flashing, `main` branch merging, repo visibility changes, nor Kconfig promotion to a production build is authorized by this compile-only experiment.
