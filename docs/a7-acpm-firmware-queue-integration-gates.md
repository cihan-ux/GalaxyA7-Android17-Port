# Exynos7885 ACPM firmware queue: integration gates (not implemented)

Status: **BLOCKED for runtime**. This is a source-backed implementation contract,
not a working Android 17 transport. The A7 mailbox prototype and in-memory
read planner are independently compilable; they do not exchange messages.

## Historical source and ABI inputs

- Old Samsung kernel: `exynos7885-dev/kernel_samsung_exynos7885`
  at `6020dfa8315134187f07ca903c9d2ed7ee0256f5`,
  `drivers/soc/samsung/acpm/acpm_ipc.c` and
  `drivers/soc/samsung/acpm/fw_header/framework.h`.
- Research kernel: `Mollomm1/linux-exynos7885`
  at `c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c`.
- A7 firmware initdata offset `0x4b80`; expected SRAM window `0x1b000`.
  ACPM PMIC transport channel is **2**; it is *not* the four-bit PMIC
  wire-channel field in the S2MPU08 message.
- AP→APM doorbell: `INTGR0=0x08`, value `BIT(2)<<16`.
  Do not substitute modern GS101 mailbox register addresses.
- Old RX completion logic is sequence-oriented; our offline extra checks
  on echoed PMIC identity and duplicate replies are conservative and must
  be checked against firmware before live use.

## Required controller implementation (all presently missing)

1. **Resource ownership:** identify the real A7 firmware SRAM and mailbox
   resource ranges from verified A7 DTS and boot firmware. Prove they are
   not concurrently owned by an existing ACPM driver. Never map physical
   addresses copied from another Exynos model.
2. **Read-only discovery first:** map with appropriate I/O accessors,
   copy the firmware prefix into a local snapshot, verify bounds and
   descriptor count, and snapshot channel 2's complete 72-byte descriptor.
   Revalidate offsets, queue element size, type, ID and ring indices.
   Avoid direct C struct dereferences of MMIO and torn multiword snapshots.
3. **Concurrency and queue ownership:** establish a per-channel lock
   protecting sequence allocation, TX front updates, RX rear updates,
   outstanding request state and timeout quarantine. Define memory
   ordering between payload writes, queue index publication and the
   doorbell. The offline planner has **no lock or barrier semantics**.
4. **IRQ and polling:** verify APM→AP interrupt direction, status and
   acknowledgement from A7 source and actual hardware evidence. Never
   clear interrupt registers merely because an offline ring scan matched.
   Handle shared IRQs, spurious notifications and multiple replies.
5. **Timeout/recovery:** use kernel monotonic time, ensure no late response
   is confused with a reused six-bit sequence, and define an explicit
   firmware reset/recovery policy. The offline quarantine can exhaust
   all 63 sequence IDs and intentionally has no automatic reset.
6. **Firmware reply contract:** confirm whether firmware echoes PMIC
   command bits 15:0, returns error bits in the assumed position, and
   permits duplicate responses. A synthetic match is not a wire proof.
7. **Power and boot dependencies:** prove regulator/clock availability
   and ordering before any PMIC write. Keep all S2MPU08 voltage-changing
   operations disabled until this evidence exists.

## Stop conditions

Do not add a production DTS compatible, enable a driver by default, register
an active PMIC regulator, or flash a kernel while any gate is unresolved.
Build-only CI may compile a **default-off, unbound** research object. A
successful `.o` or `built-in.a` is not an ACPM transaction or ROM.

## Minimal next source milestone

Implement a **read-only, bounds-checked firmware descriptor snapshot**
in a separately gated controller file, with host tests for inconsistent
snapshots and malformed SRAM bounds. Keep IRQ, queue index writes,
doorbells and regulator writes entirely out of that stage. Follow with
an A7-specific DTS ownership review before any physical mapping.
