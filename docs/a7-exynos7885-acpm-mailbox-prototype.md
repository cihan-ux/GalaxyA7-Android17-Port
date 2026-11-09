# Linux 6.15 Exynos7885 ACPM mailbox — isolated A7 prototype

This is the first **model-specific kernel mailbox platform-driver C source** for the port, saved as [`exynos7885-acpm-mbox-prototype.c`](../port/linux-6.15/drivers/mailbox/exynos7885-acpm-mbox-prototype.c). Unlike earlier pure message packers, it has a genuine doorbell `writel()` path and a Linux mailbox controller registration function. But **it is not included in kernel Kconfig/Makefile and no DTS node binds it**. Running or flashing it has **not** been attempted; this is compiler-only research.

## Source-based changes from the Linux 6.15 GS101-only mailbox

- The old [Exynos7885 ACPM IPC register header](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/drivers/soc/samsung/acpm/acpm_ipc.h) gives `INTGR1=0x1C` and `INTMR0=0x10`. The modern [GS101 Exynos mailbox driver](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/drivers/mailbox/exynos-mailbox.c) gives `INTGR1=0x40` and `INTMR0=0x28`. The prototype correctly uses Exynos7885's **old** hardware register offsets, not GS101's.
- The old firmware interface creates doorbell notifications at `BIT(channel_id)`; the prototype limits channel IDs to 0–15 and enforces `EXYNOS_MBOX_CHAN_TYPE_DOORBELL`. The old code configures polling-channel interrupt masks through `INTMR1=0x24`; the prototype **deliberately does not write any IRQ mask registers** before validating firmware interrupt semantics. Only its send callback contains a `writel()` operation.
- The original A7 `acpm_ipc` DT has no `pclk` name. The prototype tries `devm_clk_get_optional_enabled` rather than making GS101's `pclk` assumption.
- It deliberately uses a **research-only, unbound** `samsung,exynos7885-acpm-mbox-prototype` compatible so it cannot accidentally claim the legacy `samsung,exynos-acpm-ipc` firmware controller node. This is **not** a standardized device-tree binding.

## Verification

[`check_exynos7885_acpm_mailbox_prototype.py`](../tools/check_exynos7885_acpm_mailbox_prototype.py) cross-checks the original Samsung and modern register sources and verifies that Kconfig/Makefile do not integrate this driver. The [mailbox CI](../.github/workflows/a7-acpm-mailbox-prototype.yml) compiles the **real C source** directly in the immutably pinned Linux 6.15 tree, checks AArch64 ELF, and saves logs and checksums. A source or compile pass is NOT a PMIC/MMIO runtime pass.

## What remains before even an isolated boot smoke test

The modern [ACPM firmware memory ABI](a7-exynos7885-acpm-sram-abi.md) has compatible channel-descriptor offsets, but runtime safety requires firmware initialization and IPC queue validation, a real Exynos7885 DT binding design (including how mailbox and ACPM controller share registers and resource ownership), correct IRQ behavior, clocks, locking, power domains, and verified S2MPU08/ACPM channel 2. The prototype does NOT implement a full ACPM client, regulator, S2MPU08 IRQ, or rev0 LDO35/LDO36 sequencing. Never activate it based solely on a compiler result.

**Do not touch the working Android 11 phone; do not merge into main, flash, or publish the repository.**
