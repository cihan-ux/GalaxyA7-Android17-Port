# Galaxy A7 2018 — modern GPIO-keys DTB source port (experimental)

The pinned [A7 historical common DTS, lines 703–753](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_common.dtsi#L703-L753) defines **power gpa1-7 (KEY_POWER=116), volume up gpa1-5 (KEY_VOLUMEUP=115), volume down gpa1-6 (KEY_VOLUMEDOWN=114)**. The A7 rev00/01/03 board DTS files all inherit this A7 common source, but actual handset hardware revision is not verified.

The [experimental `keys-lab.dts`](../port/linux-6.15/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte-keys-lab.dts) inherits the A7 source-derived eMMC lab and adds only three GPIO keys. For syntax, it uses the modern Linux Exynos7885 pinctrl naming and GPIO bindings. The legacy Samsung 4.4 GPIO flag `0xf` is NOT the same representation as Linux 6.15 `GPIO_ACTIVE_LOW`; the latter is still a **candidate** until independently validated on the actual SM-A750F electrical wiring. We deliberately do not claim working buttons.

[Source guard](../tools/check_exynos7885_a7_keys_stage.py) rejects wrong keys/pins, foreign A8 identity, fabricated memory configuration, accidental extra GPIOs and security downgrades. A [dedicated GitHub DTB CI](../.github/workflows/exynos7885-a7-dtb-scaffold.yml) separately builds and checks a third named A7 DTB with the keys and source-backed eMMC.

The physical device remains untouched. This is not a bootable or flashable DTB: no verified A7 DRAM/reserved-memory map, voltages, display, boot integration, other drivers or Android 17 ROM exist.
