# Exynos7885 ACPM firmware SRAM ABI: Linux 4.4 vs Linux 6.15

## Important positive source finding

The historical [Samsung Exynos7885 `framework.h`](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/drivers/soc/samsung/acpm/fw_header/framework.h) and the modern [Linux 6.15 `exynos-acpm.c`](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/drivers/firmware/samsung/exynos-acpm.c) contain **matching offsets for the shared-memory fields required by the channel parser**:

| Concept | Legacy firmware | Linux 6.15 parser | Byte offset |
| --- | --- | --- | --- |
| Channel-array pointer (SRAM-relative) | `acpm_framework.ipc_channels` | `acpm_shmem.chans` | 8 |
| Application CPU channel count | `acpm_framework.ipc_ap_max` | `acpm_shmem.num_chans` | 24 |
| Channel ID | `ipc_channel.id` | `acpm_chan_shmem.id` | 0 |
| APM-to-AP queued pointers and base | `ch.tx_{rear,front,base}` | `{tx_rear,tx_front,tx_base}` | 40/44/48 |
| AP-to-APM queued pointers and base | `ch.rx_{rear,front,base}` | `{rx_rear,rx_front,rx_base}` | 16/20/24 |
| Queue length and message bytes | `ch.q_len`, `ch.q_elem_size` | `qlen`, `mlen` | 52/56 |
| Poll completion | `ap_poll` | `poll_completion` | 68 |

Both channel descriptions have an expected **72-byte** ABI. This agrees with how the old kernel [`channel_init()`](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/drivers/soc/samsung/acpm/acpm_ipc.c) reverses firmware TX/RX queue naming for the application CPU. **The similarity is in the measured C field layout, not proof of equivalent real-world firmware or hardware behavior.** The modern code intentionally ignores old channel `type`, `field`, `owner`, `credit`, `mbox_addr` metadata; whether that is safe for the PMIC channel requires independent evidence.

### Actual source and runtime tests

- [ABI C source](../port/linux-6.15/drivers/firmware/samsung/exynos7885-acpm-sram-abi-lab.c) includes compile-time `_Static_assert` for the old and modern layouts, explicit queue-field offsets and exact size. This is real C source that can compile as a Linux 6.15 AArch64 object without implementing any device driver.
- [C test](../tests/native/test_a7_acpm_sram_abi.c) verifies synthetic old/new byte-layout equivalence, invalid channel counts, SRAM offset overflow/misalignment, record size, and the application CPU RX/TX reversal.
- [Source checker](../tools/check_a7_acpm_sram_layout.py) compares names and ordering against two immutably pinned *actual* source files, failing if either source layout changes.
- [CI workflow](../.github/workflows/a7-acpm-sram-abi.yml) fetches those exact files, executes host C tests and builds the source as a genuine Linux 6.15 ARM64 object.

Legacy board sources define SRAM size `0x1B000`, firmware initdata offset `0x4B80`, AP2APM mailbox `0x11C40000`, SRAM physical base `0x02052000`, and S2MPU08 request IPC channel 2. These are **historical source coordinates**, not an instruction to map or write those addresses.

## Still blocking real integration

The existing modern Linux 6.15 [ACPM controller](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/drivers/firmware/samsung/exynos-acpm.c) matches only `google,gs101-acpm-ipc` with firmware initdata offset `0xA000`; its [mailbox driver](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/drivers/mailbox/exynos-mailbox.c) matches only `google,gs101-mbox` and uses **different mailbox interrupt register offsets** from the old Exynos7885 driver (old `INTGR1=0x1C`, modern `INTGR1=0x40`). The old channel's `type`, mailbox `field`, firmware readiness, SRAM bounds, queue initialization and concurrency must all be verified before adding an Exynos7885 ACPM platform match.

**Do not add `samsung,exynos-acpm-ipc` to GS101's platform match table, copy GS101 mailbox registers, fabricate fixed regulators, map physical addresses or flash an image.** Current work is read-only source/ABI verification; the user’s working Android 11 phone is untouched.
