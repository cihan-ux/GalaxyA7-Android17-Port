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

#endif
