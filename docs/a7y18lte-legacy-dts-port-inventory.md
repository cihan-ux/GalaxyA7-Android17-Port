# Galaxy A7 SM-A750F: legacy board DTS evidence for a future mainline port

**2026-11-06 — read-only source inventory, not a compiled or verified A7 Linux 6.15 device tree.**

## Historical baseline and exact revision

The maintained LineageOS 18.1 Exynos7885 kernel source is pinned to
[\`exynos7885-dev/kernel_samsung_exynos7885@6020dfa8315134187f07ca903c9d2ed7ee0256f5\`](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/tree/6020dfa8315134187f07ca903c9d2ed7ee0256f5).
The historical tree is Linux **4.4.302**. Its \`arch/arm64/boot/dts/exynos/\` contains independent A7-specific sources:

| Original source | What was observed; NOT verified as actual handset revision |
|---|---|
| [\`exynos7885-a7y18lte_eur_open_00.dts\`](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_eur_open_00.dts) | Board \`model_info-hw_rev=0\`, includes A7 common, GPIO rev00, fingerprint rev00; explicitly describes a Samsung touchscreen controller at I²C address \`0x48\`, with firmware path \`tsp_sec/y661_a750f.fw\`. This is a reference, not a redistributable firmware image. |
| [\`exynos7885-a7y18lte_eur_open_01.dts\`](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_eur_open_01.dts) | \`model_info-hw_rev=1..2\`, includes GPIO rev01 and fingerprint rev00; enables inherited \`touchscreen@50\` node. |
| [\`exynos7885-a7y18lte_eur_open_03.dts\`](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_eur_open_03.dts) | \`model_info-hw_rev=3..255\`, includes GPIO rev03 and fingerprint rev03; enables inherited \`touchscreen@50\` node. |
| [\`exynos7885-a7y18lte_common.dtsi\`](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_common.dtsi) | Pulls A7 display, modem, battery, motor, Mali and reserved-memory descriptions. These include legacy Samsung-specific interfaces. |
| [\`exynos7885-a7y18lte_eur_open_gpio_00.dtsi\`](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_eur_open_gpio_00.dtsi) | Extensive A7 pin and sleep-state configuration; model- and board-dependent, not interchangeable with Galaxy A8 pins. |

**Important safety issue:** The historical common DTS includes a bootargs string containing
\`androidboot.selinux=permissive\`. **DO NOT copy this bootargs string into a proposed
mainline or Android 17 tree**; do not downgrade SELinux enforcement to make a port boot.

The historical A7 DTS has additional platform-specific memory regions, regulators,
peripherals and Samsung firmware assumptions. Those addresses, reserved-memory sizes,
pin assignments, and Android-boot properties are *evidence to audit*, not a verified modern
SM-A750F memory map. No on-device hardware revision has been measured or supplied here.

## What is available in the newer source

[\`Mollomm1/linux-exynos7885@c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c\`](https://github.com/Mollomm1/linux-exynos7885/tree/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c)
provides Linux 6.15-rc1 and a modern Exynos7885 SoC \`exynos7885.dtsi\`,
pinctrl and clock source. Its included board file is
[\`exynos7885-jackpotlte.dts\`](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/arch/arm64/boot/dts/exynos/exynos7885-jackpotlte.dts):
**Galaxy A8 SM-A530F**. It cannot be renamed to \`a7y18lte\` and treated as a hardware port.

The separately triggered [Linux 6.15 A8 DTB CI build](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42245058620) is a compile feasibility probe. It does **not** assemble an A7-specific tree.

## Required engineering mapping before any A7 board DTS

1. **Board revision identification:** source contains rev00/rev01/rev03 variants, but no tested handset-specific hardware rev. Keep variant selection explicit.
2. **Trusted boot fundamentals:** determine actual A7 memory/reserved-memory, clocks, regulators, pinctrl, UART and eMMC/SD hardware using A7-specific source and legitimate supporting data; do not import A8 RAM/GPIO as A7 configuration.
3. **Display and input:** map the A7 panel, touch firmware/controller, brightness and power sequencing; distinguish the I²C rev00 / later revisions. Do not distribute proprietary firmware.
4. **Essential peripherals:** Wi-Fi/BT, audio, charging/battery, fingerprint, camera, Mali GPU and modem require independent device-specific drivers and vendor interfaces. A successful DTB is not proof of any of them.
5. **Android 17 platform closure:** verify kernel BPF *features*, VINTF/FCM, SELinux neverallows, init, HAL services and native/vendor ABI. Kernel version alone is insufficient.
6. **Safety:** keep all outputs research-only and non-flashable until a full model-matched backup/recovery plan and explicit device-test approval exists.

**Next valuable source change:** begin a mechanically checkable mapping of legacy A7 revisions to the modern SoC node set, marking *unknown/unsupported* rather than inventing missing regulators, GPIO or memory ranges. A minimal proof-of-syntax A7 DTS, if written, must not be presented as a bootable kernel or ROM.
