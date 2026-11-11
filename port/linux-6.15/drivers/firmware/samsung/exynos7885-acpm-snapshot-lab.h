/* SPDX-License-Identifier: GPL-2.0-only */
/* Offline SRAM snapshot validation; no MMIO, IRQ, driver or queue writes. */
#ifndef A7_ACPM_SNAPSHOT_LAB_H
#define A7_ACPM_SNAPSHOT_LAB_H
#include "exynos7885-acpm-sram-abi-lab.h"
struct a7_acpm_snapshot {
	struct a7_legacy_framework_prefix framework;
	struct a7_legacy_ipc_channel channel;
	struct a7_acpm_queue_layout layout;
	unsigned int descriptor_offset;
	unsigned int channel_count;
};
int a7_acpm_snapshot_pmic(const unsigned char *first,
			  const unsigned char *second,
			  unsigned int size_bytes,
			  struct a7_acpm_snapshot *out);
#endif
