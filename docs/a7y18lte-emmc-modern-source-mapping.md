# A7 2018 eMMC bridge into experimental Linux 6.15 DTS

**Purpose:** map one actual A7 legacy hardware source into a Linux 6.15 eMMC DTB **syntax probe**, without borrowing Galaxy A8 board values or implying a bootable Android 17 system.

## Source evidence (immutable)

- [A7 historical common DTS, lines 482–533](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_common.dtsi#L482-L533) **enables dwmmc0@13500000** with 8-bit eMMC, HS200/HS400, non-removable, 26 MHz oscillator in the same file, and sd0 pinctrl group.
- [Historical SoC DTS](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885.dtsi) defines `dwmmc_0` with register base **0x13500000** and interrupt **146**.
- [Modern Exynos7885 SoC DTS](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/arch/arm64/boot/dts/exynos/exynos7885.dtsi) exposes `mmc_0`, also at **0x13500000**, interrupt **146**, disabled by default.
- [Modern Exynos7885 pinctrl DTS](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/arch/arm64/boot/dts/exynos/exynos7885-pinctrl.dtsi) retains `sd0_clk`, `sd0_cmd`, `sd0_rdqs`, `sd0_bus1`, `sd0_bus4`, `sd0_bus8` labels.

These are concrete SoC/controller matches, not proof that the new MMC driver works with this A7's power circuitry, bootloader or storage firmware.

## Implementation

An independent [A7 eMMC lab DTS](../port/linux-6.15/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte-emmc-lab.dts) includes the intentionally unbootable A7 base and enables only `mmc_0` with limited historical A7-derived settings and an A7-proven 26 MHz oscillator. No board memory map, regulators, flash partitions, other peripherals, or A8 device identity are introduced.

[Static fail-closed guard](../tools/check_exynos7885_a7_emmc_stage.py) and [negative tests](../tests/test_exynos7885_a7_emmc_stage.py) reject wrong model imports, guessed supplies, other peripheral changes, incorrect oscillator and missing pins.

The [Linux 6.15 DTB GitHub Actions job](../.github/workflows/exynos7885-a7-dtb-scaffold.yml) compiles the base DTS and this additional eMMC lab DTS separately. After compilation it checks the `mmc@13500000` node is enabled only in the lab DTB with 8-bit bus width and that both builds lack verified memory nodes. **Even a passing eMMC DTB compile cannot demonstrate real eMMC I/O, correct voltage rails, actual hardware or Android 17 boot.**

## A7 versus A8 memory warning

The legacy A7 common DTS lists a first memory bank size of **0x3D500000** while the modern A8 example includes **0x3DA00000** for the comparable bank; the subsequent regions are also not sufficient to infer the A7's physical RAM and secure carveouts. Neither is copied into these A7 prototypes. They need a model-specific memory/reserved-memory investigation before any bootable port.

No firmware, vendor partition, boot image or phone data is accessed or redistributed.
