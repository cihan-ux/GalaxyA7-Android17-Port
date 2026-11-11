# A7 S2MPU08 ACPM low-level PMIC command lab — real C, strictly offline

## Actual discovery: there **is** a modern ACPM driver — for a different SoC

The pinned Linux 6.15 Exynos7885 candidate includes upstream Samsung
[`drivers/firmware/samsung/exynos-acpm.c`](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/drivers/firmware/samsung/exynos-acpm.c)
and [`exynos-acpm-pmic.c`](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/drivers/firmware/samsung/exynos-acpm-pmic.c).
**This corrects an oversimplification:** there is generic modern ACPM source, but its platform match table only lists **`google,gs101-acpm-ipc`**, with a hard-coded GS101 `0xa000` SRAM configuration offset. The [modern Exynos mailbox controller](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/drivers/mailbox/exynos-mailbox.c) also matches only **`google,gs101-mbox`**. The current Exynos7885 modern SoC DTS does not instantiate an ACPM node or a wired Exynos7885-specific ACPM mailbox. Merely enabling `CONFIG_EXYNOS_ACPM_PROTOCOL` and `CONFIG_EXYNOS_MBOX` is not an SM-A750F port.

The pinned [legacy Exynos7885 SoC DTS](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885.dtsi) instead defines **`samsung,exynos-acpm-ipc`**, AP2APM mailbox base **`0x11C40000`**, SRAM base **`0x02052000`**, and firmware channel configuration offset **`0x4B80`**. [Galaxy A7-specific DTS](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte_common.dtsi) specifies `samsung,s2mpu08mfd` and **`acpm-ipc-channel = <2>`**. Source-derived offsets are not a verified, safe modern memory map or ACPM firmware compatibility.

## First implemented protocol source

- [`s2mpu08-a7-acpm-frame-lab.h`](../port/linux-6.15/drivers/firmware/samsung/s2mpu08-a7-acpm-frame-lab.h)
- [`s2mpu08-a7-acpm-frame-lab.c`](../port/linux-6.15/drivers/firmware/samsung/s2mpu08-a7-acpm-frame-lab.c)
- [`test_s2mpu08_a7_acpm_frame.c`](../tests/native/test_s2mpu08_a7_acpm_frame.c)

These implement a pure **read-only** PMIC command-word packer and reply decoder, based on
[legacy Samsung ACPM MFD](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/drivers/soc/samsung/acpm/acpm_mfd.c)
and the modern ACPM PMIC wire representation. It supports only legacy TOP (`type=0`) and PMIC (`type=1`) reads, with 32-bit command words; it rejects other transport channels, unsupported types and register addresses beyond `0xff`. Failed replies leave the read buffer unchanged.

**Important protocol detail:** legacy `acpm-ipc-channel=<2>` identifies a firmware **transport** channel; the modern PMIC command's in-word **wire-channel** field is a separate field, and the old implementation leaves it zero. The packer keeps these concepts separate rather than incorrectly encoding channel 2 into the 12–15 command bits. Similar low command fields do **not** imply the old Exynos7885 mailbox/SRAM protocol matches GS101.

The [ACPM source-compatibility checker](../tools/check_a7_acpm_bridge_gate.py) fetches the exact pinned Samsung and modern sources, confirms both **controller and mailbox** match mismatches, and rejects any hardware I/O in this research component. The [CI workflow](../.github/workflows/a7-acpm-read-frame-lab.yml) runs **512 host-native C vectors**, negative cases, source mismatch verification, and compiles the **actual new C file** into a real Linux 6.15 AArch64 object. This first version **passed [CI 42517454955](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42517454955)**; [follow-up 42517688188](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42517688188) additionally verifies the GS101-only mailbox model match table.

## Still blocked

ACPM mailbox controller (GS101 model != Exynos7885), 0x4B80 memory initdata layout safety, firmware protocol framing, actual S2MPU08 PMIC MFD and IRQ devices, rev0 LDO35/LDO36 voltage sequencing, regulators, physical verification, full Android 17 ROM.

**No platform driver, no DT changes, no `acpm_do_xfer`, no hardware reads/writes, no regulator enable, no boot artifacts or phone modifications** are part of this first source port. This is a compiler and packet-format test only.
