# A7/S2MPU08 complete *offline* ACPM read-request planner

This research component links the previously independent [Samsung ACPM SRAM layout validator](a7-exynos7885-acpm-sram-abi.md), [pure S2MPU08 PMIC message encoder](a7-s2mpu08-acpm-frame-lab.md) and the **legacy AP→APM sequence/doorbell semantics** into one guarded mock read-request preparation. It is not a usable ACPM driver.

The source [`exynos7885-acpm-read-plan-lab.c`](../port/linux-6.15/drivers/firmware/samsung/exynos7885-acpm-read-plan-lab.c) implements only a decision from caller-supplied RAM snapshots. It validates A7's 0x1B000-byte historical SRAM allocation, the framework's channel count and descriptor offset, and the source-mapped S2MPU08 **transport channel 2**. It now explicitly requires historical **`TYPE_QUEUE=1`**, refusing `TYPE_BUFFER=2` (the old firmware processes buffer channels separately). The pinned firmware `framework.h` and `acpm_ipc.c` verify these enumerations and behavior in CI. It requires an exact four-word (16-byte) read entry and validates queue-front, queue-rear, length and wraparound. It refuses a full ring, out-of-range channels, non-step type/register inputs and sequence values outside **1–63**. Failures leave the caller's result unchanged.

For a successful mock request, the planner returns only **plain integers**: an in-SRAM relative queue-entry offset, the proposed next front, PMIC command with a six-bit sequence in bits 21:16, and the hardware doorbell **INTGR0=0x08**, value **`BIT(channel)<<16`**. The final two values match the original [Samsung Exynos7885 `acpm_ipc.c`](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/blob/6020dfa8315134187f07ca903c9d2ed7ee0256f5/drivers/soc/samsung/acpm/acpm_ipc.c). The earlier compiled prototype using `INTGR1=0x1C` was wrong-direction and must never be substituted.

[CI](../.github/workflows/a7-acpm-read-queue-plan.yml) runs actual C host tests with 63 successful sequence cases and failing edge cases, compares sequence and doorbell code with pinned historical Samsung source, then compiles **all three C files** as actual Linux 6.15 AArch64 research objects. **All steps passed in [GitHub CI 42614880503](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42614880503)**, including the historical queue-vs-buffer safety check. The compiler output is **not linked into bootable vmlinux**.

## Still missing

No code in this component maps physical A7 SRAM, touches MMIO, sends a mailbox, holds firmware locks, handles IRQs, changes PMIC voltage or registers with a platform device. Real-world ACPM queue concurrency and ownership are not solved by validating synthetic snapshots. The separate [Kbuild mailbox prototype](a7-mailbox-linux615-kbuild-integration.md) remains unbound and must not be flashed. S2MPU08 MFD/regulator integration, RAM carveouts, vendor interfaces, VINTF/SELinux and Android 17 device boot are still blocked.

## Reply matching phase (new)

A second pure C routine, `a7_acpm_match_s2mpu08_read_reply`, examines a **synthetic** four-word response queue, without touching firmware memory or calling a mailbox. Based on historical `check_response()`, it scans from RX rear to front with wraparound, matches the request's six-bit sequence and **also** checks PMIC type/register to avoid accepting an unrelated stale response. It reports matching index, proposed rear advance, whether the legacy reader would swap a rear entry into the matched slot and whether the ring would become empty. It **never performs** a queue mutation or sends an interrupt acknowledgement.

Firmware status is extracted from the high response byte. Failed firmware replies do not return a PMIC value. A missing reply leaves the output unchanged, allowing higher-level code to implement carefully bounded wait/timeout handling later. The tests include a wrapped ring with stale sequence and wrong register, a correct response, firmware error status, an empty queue, invalid indices and null pointers. Source pins in CI check the legacy `check_response()` behavior.

The complete updated reply-matching source **passed [CI 42616562784](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42616562784)**: host C test cases, pinned Samsung old-source assertions and genuine Linux 6.15 AArch64 object compilation. This establishes **algorithm-level compatibility only**. No real firmware response was sampled; it does not validate the hardware queue, locking, synchronization, timeout or PMIC write correctness.


## Offline request lifecycle and timeout policy

A new **pure-C lifecycle model** records an outstanding read, its expected
sequence and exact command, and a caller-supplied millisecond start time.
It rejects replacing a still-pending request, reports a successful synthetic
reply, latches a nonzero firmware error without returning the register value,
or marks the read expired after a **test-configured** timeout (1–60,000 ms).
Once terminal, a late matching reply **cannot** turn the operation into a
success. Unsigned 32-bit sample subtraction is tested across wraparound;
sample intervals beyond half the counter range are out of scope.

This is **not** a runtime timeout implementation: there is no timer,
interrupt controller, lock, queue ownership or scheduler. The maximum
timeout is a deliberately chosen test constraint, **not a firmware
specification**. All input timestamps and response frames are artificial.


### Six-bit timed-out sequence quarantine

The legacy ACPM protocol only has **63 nonzero sequence IDs**. A reply
from a timed-out request can therefore alias a later read after sequence
wraparound. The offline lifecycle now remembers timed-out IDs in two
32-bit bitmaps, refuses restarting with those IDs, and preserves the
quarantine through subsequent sessions. It deliberately provides **no
automatic release**, because clearing a quarantined ID requires a
separately verified firmware queue drain/reset and synchronization. The
model may eventually exhaust its 63 IDs; this is preferable to falsely
accepting a late reply. No actual firmware reset/drain is implemented.


### Bounded sequence allocator

A companion pure-C function `a7_acpm_next_unquarantined_sequence()`
scans the legacy **1–63** sequence space with wraparound, skipping every
timed-out ID tracked in the two quarantine bitmaps. It refuses allocation
while a request is pending and returns an error if all 63 IDs are blocked,
without overwriting caller output. Tests exercise both bitmap halves,
counter wrap, a single unquarantined high-number slot, and total exhaustion.
It does **not** send a request or guarantee firmware transaction uniqueness
without real channel synchronization.


### CI evidence and limit

The original lifecycle with timeout quarantine and high-bit sequence-63 coverage **passed [CI 42618707342](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42618707342)**, including all C/native and three Linux 6.15 ARM64 object builds. The new allocator is independently exercised in [CI 42619169717](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42619169717); check the final run status before declaring its AArch64 compilation passed. No real ACPM read or write occurs.


### Synthetic clock regression guard

The 32-bit timestamp model now records `last_observed_ms` alongside
`start_ms`, and rejects caller-supplied timestamps that imply a negative
delta (as interpreted under the half-range rule), **without altering the
session or quarantining a sequence**. It also rejects ambiguous total elapsed
time >= 2^31 ms. Tests include backwards observations, a wildly distant
sample, wraparound near `0xffffffff`, timely completion and expiry. This
is a defensive **model-input check**; a real ACPM driver still needs a
verified monotonic clock, proper timeout/synchronization and firmware
queue ownership.


### Atomic, entirely offline request initiation

`a7_acpm_prepare_begin_s2mpu08_read()` is a small integration entry
point which calls the bounded sequence allocator, A7 firmware channel
and ring validator, S2MPU08 read-frame packer and lifecycle initializer.
It prepares local temporary structures first, then updates the caller's
lifecycle, request plan and chosen sequence **only when all checks pass**.
It rejects pending-request replacement and returns without partial writes
on ring full, invalid timeout or malformed device metadata. C tests
simulate a timed-out sequence 9 being quarantined and next choosing 10.
This models the logic *before* a real firmware transaction and still does
not touch physical SRAM, registers, locks or PMIC power.


### Lifecycle integrity and cross-session fake-clock validation

The pure-C research lifecycle now validates the *whole caller-supplied session
state* rather than accepting unknown state enum values as if they were
completed reads. Fresh sessions are zero-initialized apart from optional
preloaded quarantine bits; running and completed sessions must have
internally consistent sequence, command, timestamps, status and timeout
fields. Failed validation leaves all caller-visible outputs untouched.

A new session may not start with a caller-supplied time sample *before* the
previous completed sample (or an ambiguous half-range jump). This prevents
a synthetic stale clock value from silently restarting a read after a
successful/failed prior operation. The C tests explicitly try a corrupt
state enum, non-fresh zero-timeout state, fake expired state, malformed
in-flight status, backwards restart and future half-range jump. These are
algorithm safeguards only, not on-device clock or firmware evidence.


### Latest lifecycle-integrity AArch64 verification

[CI 42705811004](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42705811004) **passed** the entire new lifecycle-integrity check: native C regression cases, historical Samsung source comparisons, offline guards, and three pinned Linux 6.15 AArch64 compiler objects. The tests now also reject corrupted session states and cross-session backwards or ambiguous synthetic-clock restarts. **This is not firmware execution or an Android 17 ROM.**


### Duplicate reply identity rejection

The historical RX reader stops at the first matching six-bit sequence.
The offline simulator deliberately **fails closed** when two queued
responses have the same sequence and PMIC type/register identity.
Otherwise a delayed duplicate could be accepted as the current read.
It scans the full synthetic ring before publishing a result; a duplicate
returns an error and leaves the caller's output untouched. This is a
conservative additional safeguard, not a claim about real firmware
deduplication or queue ownership.
