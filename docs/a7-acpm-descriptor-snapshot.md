# Galaxy A7 2018 ACPM channel-2 descriptor snapshot (read-only lab)

This stage implements source decoding, **not** kernel SRAM mapping. The function
`a7_acpm_snapshot_pmic_descriptor()` consumes **two separate caller-owned
ordinary-RAM buffers** of exactly `0x1b000` bytes; neither argument may be
a live `__iomem` address. No platform probe, interrupt, queue index update,
doorbell, regulator write, or phone access exists in this stage.

The decoder reads the historical firmware prefix at offset `0x4b80`,
validates channel array bounds, decodes the 72-byte channel 2 descriptor
using little-endian words, and requires `TYPE_QUEUE=1`, a 16-byte ring
entry, matching descriptor ID 2 and valid queue geometry. It resolves the
four indirect queue indices, checks each is below `qlen`, and refuses a
result if either observation differs in the prefix, descriptor or indices.
Outputs are not modified on error.

This is **not** an atomic hardware snapshot: the caller must acquire the
two stable RAM copies using a separately designed synchronization mechanism.
A real device still requires a proven Exynos7885 SRAM/DT ownership model,
proper accessor semantics, locks and barriers, IRQ semantics, and a verified
firmware reply contract. A shared lock/firmware generation handshake is
not known yet; the two-view comparison alone cannot prove concurrency safety.

Native C tests cover inconsistent observations, invalid firmware pointers,
descriptor length/type/ID, queue bounds, queue index range and unchanged
output on errors. Source audit rejects accidental live I/O. ARM64 code is
compiled as a **freestanding object**, not a real Linux 6.15 Kbuild or ROM.

See [firmware integration gates](a7-acpm-firmware-queue-integration-gates.md).
