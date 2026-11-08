# S2MPU08 PMIC + ACPM: concrete Galaxy A7 Android 17 kernel bring-up blocker

## Verified hardware provenance

The pinned [Galaxy A7 2018 historical Exynos7885 common DTS](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_common.dtsi) used by the working Android 11 generation declares:
- `samsung,s2mpu08mfd` under Samsung SPEEDY with `acpm-ipc-channel = <2>` and the PMIC IRQ on `gpa2-0`.
- `l2_reg: LDO2` identified `vqmmc` (1.8–3.375 V).
- `l35_reg: LDO35` identified `vmmc` (1.8–3.0 V).
- A7 `dwmmc0@13500000` is enabled with 8-bit HS200/HS400; actual supply routing and live voltage **are not verified from a phone**.

The pinned [historical PMIC MFD core](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/drivers/mfd/s2mpu08_core.c) uses Samsung-specific `exynos_acpm_read_reg` and related register IPC, not an ordinary generic I2C-only register model. The legacy [S2MPU08 voltage regulator driver](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/drivers/regulator/s2mpu08.c) includes a PMIC revision-0 **LDO35/LDO36 interaction workaround**. Blindly cloning generic S2MPS11 or S2MPU02 driver logic would lose important constraints.

## What the experimental Linux 6.15 source actually supports

The pinned [Linux 6.15-rc1 Exynos7885 experiment](https://github.com/Mollomm1/linux-exynos7885/tree/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c) contains Exynos MMC, clocks, pinctrl, and [Samsung SEC PMIC core](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/drivers/mfd/sec-core.c) with support for other S2MPS/S2MPU models such as **S2MPU02 and S2MPU05**. Its inspected `drivers/mfd/{Kconfig,Makefile}` and `drivers/regulator/{Kconfig,Makefile}` **do not define** `MFD_S2MPU08` or `REGULATOR_S2MPU08`. Its SEC core does not match the legacy A7 `samsung,s2mpu08mfd` compatible.

This is a missing **board power driver integration**, not proof no possible external S2MPU08 implementation exists. Kernel 6.15 version compliance alone cannot solve the missing PMIC transport and regulator control.

## Reproducible blocker test

[`check_a7_s2mpu08_power_gap.py`](../tools/check_a7_s2mpu08_power_gap.py) runs against real, immutably pinned A7 old/modern kernel files in [CI](../.github/workflows/a7-s2mpu08-android17-power-gap.yml). It requires:
1. A7 legacy compatible, ACPM channel and MMC voltage-rail provenance.
2. Old driver source/Kconfig/Makefile presence and ACPM register transport.
3. Modern lack of the specific S2MPU08 Kconfig/Makefile registration; if it appears later, fail closed and re-audit.

A green check means **confirmed blocker**, not compatibility. These sources do not establish working phone hardware.

## Engineering actions before a bootable board DTS

1. Review Samsung S2MPU08 MFD and regulator GPL source/headers for license, portability and modern `regmap`/platform/interrupt APIs; verify transport dependencies (ACPM or equivalent).
2. Determine what Samsung ACPM IPC and SPEEDY bus support exists in the modern kernel. A compatible PMIC I2C ID without those transports is inadequate.
3. Implement real S2MPU08 regulator and IRQ logic preserving chip revision 0 LDO35/LDO36 handling; compile actual driver objects before enabling a physical board node.
4. Validate the modern regulator bindings against the A7 source and then trace MMC power supplies, remaining buck/ldo dependencies, suspend/resume and charging.
5. Only after verified A7 memory carveouts, power + storage drivers, display, security policy and full ROM platform dependencies should hardware flashing be considered.

**Never guess voltage rails, substitute another PMIC chip, weaken SELinux or touch the user's successful Android 11 device in this research phase.**
