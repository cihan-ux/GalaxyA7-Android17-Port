/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * SM-A750F offline ACPM queue/read-request planner.
 * Never maps SRAM, writes registers or interacts with firmware/hardware.
 */
#ifndef EXYNOS7885_ACPM_READ_PLAN_LAB_H
#define EXYNOS7885_ACPM_READ_PLAN_LAB_H
#include "exynos7885-acpm-sram-abi-lab.h"
#include "s2mpu08-a7-acpm-frame-lab.h"

/* Pinned firmware enum shard_buffer_type: TYPE_QUEUE=1, TYPE_BUFFER=2. */
#define A7_ACPM_QUEUE_TYPE 1U
#define A7_ACPM_BUFFER_TYPE 2U
#define A7_ACPM_READ_SEQUENCE_MIN 1U
#define A7_ACPM_READ_SEQUENCE_MAX 63U
#define A7_ACPM_READ_SEQUENCE_SHIFT 16U
#define A7_ACPM_DOORBELL_INTGR0_OFFSET 0x0008U
#define A7_ACPM_READ_PLAN_ERROR (-1)
#define A7_ACPM_REPLY_NOT_FOUND 1
#define A7_ACPM_READ_RESPONSE_STATUS_SHIFT 24U
#define A7_ACPM_READ_RESPONSE_VALUE_SHIFT 8U
#define A7_ACPM_READ_RESPONSE_BYTE_MASK 0xffU

struct a7_acpm_read_plan {
	unsigned int queue_entry_offset;
	unsigned int next_front;
	unsigned int channel_id;
	unsigned int sequence;
	unsigned int doorbell_offset;
	unsigned int doorbell_value;
	struct s2mpu08_a7_acpm_frame request;
};

/*
 * front/rear/seq are artificial snapshots supplied by the caller.
 * This plans queue offsets ONLY; it does not read or modify actual SRAM.
 * The caller must not use this output for physical I/O.
 */
int a7_acpm_prepare_s2mpu08_read(
	const struct a7_legacy_framework_prefix *framework,
	const struct a7_legacy_ipc_channel *channel,
	unsigned int transport_channel,
	unsigned int pmic_type, unsigned int reg, unsigned int seq,
	unsigned int front, unsigned int rear,
	struct a7_acpm_read_plan *out);
/*
 * Offline match for a simulated reply-ring snapshot, never actual SRAM.
 * A successful match is NOT proof of an actual transaction or firmware ack.
 * The historical reader dequeues a matched slot by moving the rear entry
 * into its place, then increments rear. Only report the intended actions.
 */
struct a7_acpm_reply_decision {
	unsigned int matched_index;
	unsigned int next_rear;
	unsigned int requires_rear_swap;
	unsigned int would_clear_irq_if_empty;
	unsigned int firmware_status;
	unsigned int response_value;
};

/* 0=matching reply in synthetic ring, 1=no match, -1=invalid input. */
int a7_acpm_match_s2mpu08_read_reply(
	const struct a7_acpm_read_plan *request,
	const struct s2mpu08_a7_acpm_frame *ring,
	unsigned int ring_count, unsigned int rear, unsigned int front,
	struct a7_acpm_reply_decision *out);

/*
 * A synthetic request lifecycle with explicit caller-supplied time samples.
 * No sleeping, clocks, IRQs, firmware transactions, SRAM access or locks.
 * A time limit is a test policy, NOT a proven Samsung firmware timeout.
 */
#define A7_ACPM_WAIT_TIMEOUT_MAX_MS 60000U
#define A7_ACPM_WAIT_PENDING       0U
#define A7_ACPM_WAIT_SUCCESS       1U
#define A7_ACPM_WAIT_FIRMWARE_ERR  2U
#define A7_ACPM_WAIT_EXPIRED       3U
#define A7_ACPM_WAIT_ALREADY_DONE  1

struct a7_acpm_read_lifecycle {
	unsigned int state;
	unsigned int sequence;
	unsigned int command_word0;
	unsigned int start_ms;
	unsigned int last_observed_ms;
	unsigned int timeout_ms;
	unsigned int firmware_status;
	unsigned int response_value;
	/* Block expired sequences until externally verified firmware drain. */
	unsigned int quarantined_sequence_low;
	unsigned int quarantined_sequence_high;
};

/*
 * Zero-initialize before the first begin. A pending request cannot be
 * replaced. A terminal request can restart only with a non-quarantined
 * sequence. No unverified automatic quarantine-clearing API is provided.
 */
int a7_acpm_begin_read_lifecycle(
	const struct a7_acpm_read_plan *request,
	unsigned int start_ms, unsigned int timeout_ms,
	struct a7_acpm_read_lifecycle *lifecycle);

/*
 * Advance from a synthetic RX snapshot at a caller-supplied u32 timestamp.
 * Elapsed time is evaluated modulo 2^32, with a <=60s timeout budget.
 * Backward or otherwise ambiguous timestamps are REJECTED without changing
 * state. Both consecutive and total age must be <2^31ms. Caller supplies
 * samples; this is not a real hardware monotonic time source.
 * Once timed out or completed, a delayed/stale reply cannot change state.
 *
 * Return 0 for a valid update (including still pending);
 * 1 for an already terminal state; -1 for invalid input.
 */
int a7_acpm_advance_read_lifecycle(
	struct a7_acpm_read_lifecycle *lifecycle,
	const struct a7_acpm_read_plan *request,
	const struct s2mpu08_a7_acpm_frame *reply_ring,
	unsigned int ring_count, unsigned int rear, unsigned int front,
	unsigned int observed_ms);

/*
 * Synthetic 1..63 sequence allocator, skipping timed-out IDs.
 * Returns 0 and next sequence, -1 when invalid, pending or exhausted.
 * It never clears quarantine and never modifies the request or firmware.
 */
int a7_acpm_next_unquarantined_sequence(
	const struct a7_acpm_read_lifecycle *lifecycle,
	unsigned int previous_sequence, unsigned int *next_sequence);

/*
 * Atomically plan (in caller RAM only) a sequential synthetic PMIC read:
 * choose a non-quarantined 1..63 sequence, check ring capacity/board
 * geometry, then start a bounded lifecycle. On ANY failure none of the
 * caller-visible output plan, sequence or lifecycle objects change.
 *
 * No MMIO, mailbox/SRAM write, firmware lock, physical PMIC I/O or kernel
 * driver registration is implemented by this research-only composition.
 */
int a7_acpm_prepare_begin_s2mpu08_read(
	const struct a7_legacy_framework_prefix *framework,
	const struct a7_legacy_ipc_channel *channel,
	unsigned int pmic_type, unsigned int reg,
	unsigned int previous_sequence,
	unsigned int front, unsigned int rear,
	unsigned int start_ms, unsigned int timeout_ms,
	struct a7_acpm_read_lifecycle *lifecycle,
	struct a7_acpm_read_plan *out_plan,
	unsigned int *out_sequence);

#endif
