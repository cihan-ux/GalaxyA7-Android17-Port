# S2MPU08 voltage-metadata first C source port — Linux 6.15, SM-A750F

This is the **first bounded C-language source contribution** toward modern S2MPU08 regulator support. It is **not** a functional PMIC driver.

Hardware source: [Samsung A7 historical regulator source (GPL-2.0-or-later)](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/drivers/regulator/s2mpu08.c), [historical register constants](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/include/linux/mfd/samsung/s2mpu08-private.h), [A7 common DTS regulator constraints](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_common.dtsi).

## Exact model-specific voltage math

| A7 rail | Legacy regulator ID | VSEL register | Selector | LDO step | A7 voltage constraint | Allowed selector range |
| --- | --- | --- | --- | --- | --- | --- |
| `LDO2` → `vqmmc` | 2 | `0x2D` | 6-bit (`0x3F`) | 25,000 µV | 1,800,000–3,375,000 µV | 0–63 |
| `LDO35` → `vmmc` | 35 | `0x4F` | 6-bit (`0x3F`) | 25,000 µV | 1,800,000–3,000,000 µV | 0–48 |

The chip supports 64 selector values per LDO, but the **A7 board** constrains LDO35 to a lower maximum; we must not interpret the full 6-bit range as permission to exceed 3.0 V. Neither rail is proven to operate on real hardware without ACPM transport and physical electrical validation.

## Staged source and proof

- [`s2mpu08-a7-voltage-lab.h`](../port/linux-6.15/drivers/regulator/s2mpu08-a7-voltage-lab.h): **host- and kernel-compilable** pure selector-to-voltage and voltage-to-selector conversion with strict board bounds. Includes a rev0 LDO35/36 integration guard, **not** the special sequence itself.
- [`s2mpu08-a7-voltage-lab.c`](../port/linux-6.15/drivers/regulator/s2mpu08-a7-voltage-lab.c): real modern `struct regulator_desc` data plus **read-only calculation** operations for two rails. No platform driver, module init, Kconfig selection, regulator registration, enable/disable or register I/O.
- [Actual host C unit test](../tests/native/test_s2mpu08_a7_voltage_lab.c) runs every valid selector and rejects out-of-bound and non-step voltages.
- [Kernel ARM64 CI compile](../.github/workflows/a7-s2mpu08-voltage-lab.yml) stages this source into pinned Linux 6.15-rc1 **only for an explicit object build** and checks that the result is genuine AArch64. Tests can fail and must be fixed before counting this gate as PASS.

## The crucial unsolved dependencies

Modern Linux 6.15 does not have the inspected legacy **S2MPU08 MFD core, ACPM message protocol or S2MPU08 register driver**, and the checked SoC DTS does not define legacy `speedy@11ce0000`. The Samsung historical driver has a **rev0 LDO35/LDO36 coupled workaround** with special register sequences. The lab deliberately performs **no reads or writes** so it cannot inadvertently control phone power or produce a falsely flashable result.

Next: establish correct ACPM/SPEEDY transport and modern regulator/IRQ APIs, then implement the revision-specific guarded write sequence and test *without any hardware flash*. **Do not copy register layouts from S2MPU02/05, assume fixed voltages, or touch the working Android 11 phone.**
