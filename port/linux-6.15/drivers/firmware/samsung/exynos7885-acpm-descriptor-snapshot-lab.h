/* SPDX-License-Identifier: GPL-2.0-only */
/* A7 ACPM: host-memory snapshots ONLY. Never pass __iomem pointers. */
#ifndef A7_ACPM_DESCRIPTOR_SNAPSHOT_LAB_H
#define A7_ACPM_DESCRIPTOR_SNAPSHOT_LAB_H

#include "exynos7885-acpm-sram-abi-lab.h"

#define A7_ACPM_DESCRIPTOR_SNAPSHOT_ERROR (-1)
#define A7_ACPM_LEGACY_QUEUE_TYPE 1U

struct a7_acpm_descriptor_snapshot {
	struct a7_legacy_framework_prefix framework;
	struct a7_legacy_ipc_channel pmic_channel;
	struct a7_acpm_queue_layout layout;
	unsigned int descriptor_offset;
	/* Indexed from the legacy APM perspective (AP TX = APM RX). */
	unsigned int ap_tx_rear;
	unsigned int ap_tx_front;
	unsigned int ap_rx_rear;
	unsigned int ap_rx_front;
};

/*
 * first and second are independent, caller-owned, ordinary-RAM copies
 * of the entire A7 firmware SRAM window. They must NOT be MMIO pointers.
 * The caller must guarantee both copies are readable for size_bytes bytes.
 * This does not provide physical atomicity, mapping or firmware ownership.
 * On error, out is untouched.
 */
int a7_acpm_snapshot_pmic_descriptor(
	const unsigned char *first, const unsigned char *second,
	unsigned int size_bytes, struct a7_acpm_descriptor_snapshot *out);

#endif
