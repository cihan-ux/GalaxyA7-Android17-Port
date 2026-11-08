# First A7-specific mainline DTS scaffold — syntax only

Target: Samsung Galaxy A7 (2018), **SM-A750F / a7y18lte**. Kernel candidate: Linux **6.15-rc1**, [Mollomm1/linux-exynos7885@c9639f4](https://github.com/Mollomm1/linux-exynos7885/tree/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c).

This stage begins a real, separately named A7 board source file rather than copying the `jackpotlte` Galaxy A8 board. The file [`exynos7885-a7y18lte.dts`](../port/linux-6.15/arch/arm64/boot/dts/exynos/exynos7885-a7y18lte.dts) inherits only the newer Exynos7885 SoC description and declares the correct target identity.

## Why intentionally minimal?

The historical [SM-A750F rev00/rev01/rev03 board evidence](a7y18lte-legacy-dts-port-inventory.md) contains different touch controllers/GPIO/fingerprint variants. We have not matched the handset's physical board revision or proved its DRAM topology and reserved-memory map. The available Linux 6.15 tree includes an A8 board example, but its memory ranges, GPIOs, clocks and MMC wiring are **not A7 evidence**.

The new A7 DTS intentionally has **no memory node**, no reserved-memory declaration, no enabled storage/serial/input devices, no invented addresses or firmware dependencies. It **cannot boot**. Its value is establishing an independently compiled A7-specific modern SoC description and a safe baseline for incremental hardware mapping.

## Real source build gate

[Experimental A7 syntax CI](../.github/workflows/exynos7885-a7-dtb-scaffold.yml) will:

1. Check exact model/compatible against negative tests that reject A8 names, DRAM guesses, enabled unverified hardware and permissive SELinux.
2. Fetch the exact Linux 6.15 source commit, copy only this A7 DTS into the build tree and append a new Exynos7885 DTB target.
3. Run an actual ARM64 `defconfig` and `dtbs` compilation using Clang.
4. Use `fdtget` to verify the compiled DTB identifies **a7y18lte**, **not jackpotlte**, and that a memory map has not accidentally appeared.
5. Label the output **NOT BOOTABLE / NOT FLASHABLE**.

This CI compile is a source integration milestone only. It does not validate board hardware, kernel Image, vendor drivers, Android 17 runtime, eBPF features, SELinux policy or VINTF.

## Next meaningful changes

- Verify A7 hardware rev identity, memory layout and reserved-memory against model-specific legal sources; cross-check against the older board DTS and secure firmware constraints.
- Carefully port an individually verified minimal peripheral (for example, storage controller and required regulator/pinctrl) rather than copying the A8 board.
- Investigate a maintainable modern Samsung Exynos7885 driver set and legacy blob interface compatibility. Do not weaken security checks.
- Keep the working Android 11 ROM untouched and test only source in GitHub CI until an independently bootable and recoverable image exists.
