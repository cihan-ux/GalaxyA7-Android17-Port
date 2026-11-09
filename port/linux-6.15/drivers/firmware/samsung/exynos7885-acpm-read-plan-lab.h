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
#endif
